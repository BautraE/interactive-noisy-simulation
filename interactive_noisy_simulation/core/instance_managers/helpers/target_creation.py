# Third-party imports:
from qiskit.circuit.library import (
    # Specific gates
    CXGate,
    CZGate,
    ECRGate,
    IGate,
    RXGate,
    RZGate,
    RZZGate,
    SXGate,
    XGate,
    # Other instructions
    Reset,
    Measure,
)
from qiskit.circuit import Delay

from qiskit.transpiler import (
    Target, InstructionProperties
)
from pandas import isna

# Project-related imports:
from ....project_variables import (
    SINGLE_QUBIT_GATES, 
    TWO_QUBIT_GATES
)

# Imports only used for type definition:
from pandas import DataFrame
from qiskit.circuit import Instruction


# Instruction init function callables that can be accessed through the short 
# (or in some cases full) names of the specific instructions.
INSTRUCTIONS = {
    "cx": lambda: CXGate(),
    "cz": lambda: CZGate(),
    "ecr": lambda: ECRGate(),
    "id": lambda: IGate(),
    "rx": lambda: RXGate(0.0),
    "rz": lambda: RZGate(0.0),
    "rzz": lambda: RZZGate(0.0),
    "sx": lambda: SXGate(),
    "x": lambda: XGate(),
    
    "reset": lambda: Reset(),
    "measure": lambda: Measure(),
    "delay": lambda: Delay(0)
}


def create_target_from_calibration_data(
    noise_dataframe: DataFrame
) -> Target:
    """Creates and returns `Target` object for circuit transpilation based on
    given noise dataframe.

    `Target` will get its list of instructions based on columns that exist
    within the provided dataframe. Additionally, each instruction will also 
    contain information in the form of properties: instruction `duration` and
    `error`.
    
    Args:
        noise_dataframe (DataFrame): Dataframe, based on which the new 
            `Target` object will be created.

    Returns:
        Target: Target object that is usable during circuit transpilation.
    """
    target = Target(num_qubits=len(noise_dataframe))

    # Adding single-qubit gates as instructions to target:
    for gate_name, gate_reference in SINGLE_QUBIT_GATES.items():
        if gate_reference not in noise_dataframe.columns: continue
        if gate_name == "rz": continue
        inst_properties = {}
        for qubit in range(len(noise_dataframe)):
            gate_time = noise_dataframe.at[qubit, "1q_gate_time"]
            gate_error = noise_dataframe.at[qubit, gate_reference]
            inst_properties[(qubit,)] = InstructionProperties(
                                            duration=gate_time * 1e-9 if not isna(gate_name) else None,
                                            error=gate_error if not isna(gate_error) else None)

        target.add_instruction(_get_instruction(gate_name), inst_properties)

    # Adding two-qubit gates as instructions to target:
    for gate_name, gate_reference in TWO_QUBIT_GATES.items():
        # Checks if gate is part of basis gates from CSV file
        if gate_reference not in noise_dataframe.columns: continue
        inst_properties = {}
        for current_qubit in range(len(noise_dataframe)):
            connected_qubits = noise_dataframe.at[current_qubit, "neighboring_qubits"]
            # Checks if there are any connected qubits to the current qubit
            if not isinstance(connected_qubits, list): continue
            gate_times = noise_dataframe.at[current_qubit, "2q_gate_time"]
            gate_errors = noise_dataframe.at[current_qubit, gate_reference]
            for connected_qubit in connected_qubits:
                gate_time = gate_times.get(connected_qubit, None)
                gate_error = (
                    # Checks if there are any gate errors mentioned in the CSV file
                    gate_errors.get(connected_qubit, None)
                    if not isna(gate_errors)
                    else None
                )
                inst_properties[
                    (current_qubit, connected_qubit)
                ] = InstructionProperties (duration=gate_time * 1e-9 if not isna(gate_name) else None,
                                           error=gate_error)

        target.add_instruction(_get_instruction(gate_name), inst_properties)

    # Other instructions:
    # RZ gate (it's the only gate with a gate time of 0)
    rz_properties = {}
    for qubit in range(len(noise_dataframe)):
        rz_time = 0
        rz_error = noise_dataframe.at[qubit, "rz_gate_error"]
        rz_properties[(qubit,)] = InstructionProperties(
                                      duration=rz_time,
                                      error=rz_error if not isna(rz_error) else None)
    target.add_instruction(_get_instruction("rz"), rz_properties)

    # Reset instruction
    reset_properties = {}
    for qubit in range(len(noise_dataframe)):
        reset_time = noise_dataframe.at[qubit, "reset_time"]
        reset_properties[(qubit,)] = InstructionProperties(
                                        duration=reset_time * 1e-9,
                                        error=None)
    target.add_instruction(_get_instruction("reset"), reset_properties)

    # Measure instruction
    measure_properties = {}
    for qubit in range(len(noise_dataframe)):
        measure_time = noise_dataframe.at[qubit, "readout_time"]
        measure_error = noise_dataframe.at[qubit, "readout_assignment_error"]
        measure_properties[(qubit,)] = InstructionProperties(
                                        duration=measure_time * 1e-9 if not isna(measure_time) else None,
                                        error=measure_error if not isna(measure_error) else None)
    target.add_instruction(_get_instruction("measure"), measure_properties)

    # Delay instruction
    delay_properties = {
        (qubit,): None 
        for qubit in range(len(noise_dataframe))
    }
    target.add_instruction(_get_instruction("delay"),
                           delay_properties)
                         
    return target


def create_basic_target(
    circuit_qubit_count: int
) -> Target:
    """Creates and returns `Target` object for circuit transpilation in cases
    when there is no noise (noiseless experiment job).

    Args:
        circuit_qubit_count (int): Number of qubits in circuit that is assigned
            to the specific job, for which a `Target` object needs to be created.
    
    Returns:
        Target: Target object that is usable during circuit transpilation.
    """
    target = Target(num_qubits=circuit_qubit_count)

    single_qubit_inst_properties = {
        (qubit,): None 
        for qubit in range(circuit_qubit_count)
    }
    two_qubit_inst_properties = {
        (current_q, connected_q): None 
        # Every qubit is connected with each other
        for current_q in range(circuit_qubit_count) 
            for connected_q in range(circuit_qubit_count) 
                if current_q != connected_q
    }

    # Adding single-qubit gates as instructions to target:
    for gate in SINGLE_QUBIT_GATES.keys():
        target.add_instruction(_get_instruction(gate), 
                               single_qubit_inst_properties)

    # Adding two-qubit gates as instructions to target:
    for gate in TWO_QUBIT_GATES.keys():
        target.add_instruction(_get_instruction(gate), 
                               two_qubit_inst_properties)

    # Other instructions:
    # Reset instruction
    target.add_instruction(_get_instruction("reset"), 
                           single_qubit_inst_properties)

    # Measure instruction
    target.add_instruction(_get_instruction("measure"), 
                           single_qubit_inst_properties)

    # Delay instruction
    target.add_instruction(_get_instruction("delay"),
                           single_qubit_inst_properties)

    return target


# --------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------        


def _get_instruction(
    instruction_name: str
) -> Instruction:
    """Creates and returns specific instruction object based on given
    instruction name.
    
    Args:
        instruction_name (str): Code name of the instruction that should
            be found and returned (e.g., "id" or "ecr")

    Returns:
        Instruction: The requested specific instruction object.
    """
    return INSTRUCTIONS[instruction_name]()
