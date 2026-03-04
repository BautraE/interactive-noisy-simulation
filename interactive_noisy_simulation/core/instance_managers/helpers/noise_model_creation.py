# =========================================================================
# This file contains helper functions for the class NoiseCreator.
#
# The following methods are used for adding specific errors to a noise 
# model, as well as obtaining a list of basis gates and the coupling map.
# =========================================================================

#Third party imports:
import pandas
from qiskit.transpiler import CouplingMap
from qiskit_aer.noise import (
    NoiseModel,
    ReadoutError,
    depolarizing_error,
    thermal_relaxation_error
)

# Project-related imports:
from ....data._data import (
    CONFIG, CSV_COLUMNS
)

# Imports only used for type definition:
from pandas.core.series import Series


# --------------------------------------------------------------
# Obtaining list of basis gates and coupling map
# --------------------------------------------------------------

def get_basis_gates(
        noise_dataframe: pandas.DataFrame
) -> list[str]:
    """Helps to create and return a list of basis gates.

    Creates a list of basis gates that is based on the current noise 
    data. All possible base gates are taken from the configuration 
    file `config.json`, after which they are filtered based on what 
    kind of columns does the noise data table have. The basis gate 
    list is required when creating a `NouiseModel` object. If no basis 
    gates are presented during the creation, it will pick a set of 
    default basis gates. If you add the basis gates later, it will 
    add them together with the default basis gates instead of 
    replacing them.

    Args:
        noise_dataframe (pandas.DataFrame): The current noise data
            instance dataframe that is being used to create a noise
            model.
    
    Returns:
        list[str]: A list of basis gate names in the form that they 
            are accepted. For example: `["id", "ecr", "rz"]`
    """ 
    basis_gate_list = CONFIG["non_gate_instructions"]

    for gate in CONFIG["single_qubit_gates"]:
        if CSV_COLUMNS[gate]["csv_name"] in noise_dataframe.columns:
            basis_gate_list.append(CSV_COLUMNS[gate]["code_name"])
    
    for gate in CONFIG["two_qubit_gates"]:
        if CSV_COLUMNS[gate]["csv_name"] in noise_dataframe.columns:
            basis_gate_list.append(CSV_COLUMNS[gate]["code_name"])

    return basis_gate_list


def get_coupling_map(
        noise_dataframe: pandas.DataFrame
) -> CouplingMap:
    """Helps tp create a coupling map.

    Creates a coupling map that is based on the noise data. The 
    created coupling map object `CouplingMap` is to be used along 
    with the `NoiseModel` object when creating a `AerSimulator` 
    simulator instance.
    
    noise_dataframe (pandas.DataFrame): The current noise data
            instance dataframe that is being used to create a noise
            model.

    Returns:
        CouplingMap: Representation of the created coupling map.
    """
    coupled_qubits = []

    for qubit, columns in noise_dataframe.iterrows():
        neighboring_qubits = columns[CSV_COLUMNS["neighboring_qubits"]
                                                ["csv_name"]]
        if isinstance(neighboring_qubits, list):
            for paired_qubit in neighboring_qubits:
                coupled_qubits.append([qubit, paired_qubit])

    return CouplingMap(couplinglist=coupled_qubits)


# --------------------------------------------------------------
# Adding errors
# --------------------------------------------------------------

def add_readout_error(
        qubit: int, 
        columns: Series, 
        noise_model: NoiseModel
) -> None:
    """Helps create and add readout errors to provided noise model.

    By using provided noise data, the function creates readout error 
    for the specified qubit and adds it to a the given `NoiseModel` object.

    This code was written based on given examples by IBM on how to 
    create such errors (a link to the web page is available 
    further on).
    Link to IBM documentation on the mention topic:
    https://qiskit.github.io/qiskit-aer/tutorials/3_building_noise_models.html

    Args:
        qubit (int): The number of the current qubit.
        columns (Series): Table data for the current qubit. Basically 
            a row, however, to access a certain attribute, you must do 
            as follows: `column["attribute_name"]`, where 
            `"attribute_name"` is the column name in the dataframe.
        noise_model (NoiseModel): The noise model object, to which
            the newly created errors will be added.
    """
    m0p1 = columns[CSV_COLUMNS["m0p1"]["csv_name"]]
    m1p0 = columns[CSV_COLUMNS["m1p0"]["csv_name"]]
    readout_error = ReadoutError([[1-m0p1, m0p1], [m1p0, 1-m1p0]])
    noise_model.add_readout_error(readout_error, [qubit])


def add_depolarizing_error(
        qubit: int, 
        columns: Series, 
        noise_model: NoiseModel
) -> None:
    """Helps create and add depolarizing errors to the provided noise model.

    By using provided noise data, the function creates depolarizing 
    errors for every basis gate operating on the specified qubit. 
    The created errors are then added to the provided NoiseModel object. 
    
    The function finds the required data without the help of the existing 
    basis gates list. 
    
    This code was written based on given examples by IBM on how to 
    create such errors (a link to the web page is available 
    further on).
    Link to IBM documentation on the mention topic:
    https://qiskit.github.io/qiskit-aer/tutorials/3_building_noise_models.html

    Args:
        qubit (int): The number of the current qubit.
        columns (Series): Table data for the current qubit. 
            Basically a row, however, to access a certain attribute, 
            you must do as follows: `column["attribute_name"]`, where 
            `"attribute_name"` is the column name in the dataframe
            and CSV file.
        noise_model (NoiseModel): The noise model object, to which
            the newly created errors will be added.
    """
    for gate in CONFIG["single_qubit_gates"]:
        single_qubit_gate = CSV_COLUMNS[gate]
        if single_qubit_gate["csv_name"] in columns:
            error_data = columns[single_qubit_gate["csv_name"]]
            # In one case the single-qubit gate error values were NaN
            # for one qubit. Not sure if this was a bug on their side, 
            # but this validation fixes this issue.
            if not pandas.isna(error_data):
                error = depolarizing_error(
                    param=error_data, 
                    num_qubits=1)
                noise_model.add_quantum_error(
                    error=error, 
                    instructions=single_qubit_gate["code_name"], 
                    qubits=[qubit], 
                    warnings=False)

    for gate in CONFIG["two_qubit_gates"]:
        two_qubit_gate = CSV_COLUMNS[gate]
        if two_qubit_gate["csv_name"] in columns:
            error_data = columns[two_qubit_gate["csv_name"]]
            if not pandas.isna(error_data):
                # Since each row of these columns may contain more
                # than one data entry.
                for target_qubit in error_data.keys():
                    error = depolarizing_error(
                        param=error_data[target_qubit],
                        num_qubits=2)
                    noise_model.add_quantum_error(
                        error=error,
                        instructions=two_qubit_gate["code_name"], 
                        qubits=[qubit, target_qubit],
                        warnings=False)
                    

def add_thermal_error(
        qubit: int, 
        columns: Series, 
        noise_model: NoiseModel,
        noise_dataframe: pandas.DataFrame
) -> None:
    """Helps create and add thermal relaxation error to the provided 
    noise model.

    By using provided noise data, the function creates thermal relaxation 
    errors for every basis gate operating on the specified qubit. 
    The created errors are then added to a NoiseModel object. 
    
    The method finds the required data without the help of the existing 
    basis gates list.
    
    Important things to note:
    - The time-based values (microseconds and nanoseconds) are initially
      provided in the same base unit, which requires them to be 
      proportionally adjusted. In this case, it was decided that they
      would be converted to microseconds and nanoseconds respectively.
    - Some T2 values in the available CSV data from IBM's QPUs are bigger
      than 2*T1 so they need to be truncated (this is also done in the 
      available code example from IBM).
    
    This code was written based on given examples by IBM on how to 
    create such errors (a link to the web page is available 
    further on).
    Link to IBM documentation on the mention topic:
    https://qiskit.github.io/qiskit-aer/tutorials/3_building_noise_models.html

    Args:
        qubit (int): The number of the current qubit.
        columns (Series): Table data for the current qubit. Basically 
            a row, however, to access a certain attribute, you must do 
            as follows: `column["attribute_name"]`, where 
            `"attribute_name"` is the column name in the dataframe.
        noise_model (NoiseModel): The noise model object, to which
            the newly created errors will be added.
        noise_dataframe (pandas.DataFrame): The same dataframe, from 
            which the qubit number and columns attributes are from. 
            It is required here because certain connected qubit noise 
            data must be found to create the thermal relaxation error 
            for two-qubit gates.
    """ 
    t1_time = columns[CSV_COLUMNS["t1_time"]["csv_name"]] * 1e-6
    csv_t2_value = columns[CSV_COLUMNS["t2_time"]["csv_name"]] * 1e-6
    t2_time = min(
        csv_t2_value,
        t1_time * 2)

    # All single-qubit gates have the same thermal relaxation error
    single_qubit_gate_time = columns[
        CSV_COLUMNS["1q_gate_time"]["csv_name"]
    ] * 1e-9
    thermal_error_1q = thermal_relaxation_error(
        t1=t1_time, 
        t2=t2_time, 
        time=single_qubit_gate_time)
    
    for gate in CONFIG["single_qubit_gates"]:
        # RZ gates use a different gate time
        if gate == "rz_gate_error": continue
        single_qubit_gate = CSV_COLUMNS[gate]
        if single_qubit_gate["csv_name"] in columns:
            noise_model.add_quantum_error(
                error=thermal_error_1q,
                instructions=single_qubit_gate["code_name"],
                qubits=[qubit],
                warnings=False)

    # Similarly, all two-qubit gates have the same thermal relaxation error
    two_qubit_gate_time = columns[CSV_COLUMNS["2q_gate_time"]["csv_name"]]
    # Multi-value columns may be emptry in CSV
    if not pandas.isna(two_qubit_gate_time):
        for target_qubit in two_qubit_gate_time.keys():
            # T1 & T2 times for target qubits
            t1_time_q2 = noise_dataframe.at[
                target_qubit, 
                CSV_COLUMNS["t1_time"]["csv_name"]
            ] * 1e-6
            
            csv_t2_value = noise_dataframe.at[
                target_qubit, CSV_COLUMNS["t2_time"]["csv_name"]
            ] * 1e-6
            t2_time_q2 = min(
                csv_t2_value,
                t1_time_q2 * 2)
            
            thermal_error_2q = thermal_relaxation_error(
                t1=t1_time, 
                t2=t2_time, 
                time=two_qubit_gate_time[target_qubit] * 1e-9).expand(
                    thermal_relaxation_error(
                        t1=t1_time_q2, 
                        t2=t2_time_q2, 
                        time=two_qubit_gate_time[target_qubit] * 1e-9))

            for gate in CONFIG["two_qubit_gates"]:
                two_qubit_gate = CSV_COLUMNS[gate]
                if two_qubit_gate["csv_name"] in columns:
                    noise_model.add_quantum_error(
                        error=thermal_error_2q,
                        instructions=two_qubit_gate["code_name"],
                        qubits=[qubit, target_qubit],
                        warnings=False)

    # Creating and adding thermal relax error for measure operation
    readout_time = columns[CSV_COLUMNS["readout_time"]["csv_name"]] * 1e-9
    thermal_error_readout = thermal_relaxation_error(
        t1=t1_time, 
        t2=t2_time, 
        time=readout_time)
    noise_model.add_quantum_error(
        error=thermal_error_readout, 
        instructions="measure", 
        qubits=[qubit],
        warnings=False)

    # Creating and adding thermal relax error for reset operation
    reset_time = columns[CSV_COLUMNS["reset_time"]["csv_name"]] * 1e-9
    thermal_error_reset = thermal_relaxation_error(
        t1=t1_time,
        t2=t2_time,
        time=reset_time)
    noise_model.add_quantum_error(
        error=thermal_error_reset,
        instructions="reset",
        qubits=[qubit],
        warnings=False)

    # Creating and adding thermal relax error for RZ gate
    thermal_error_rz = thermal_relaxation_error(
        t1=t1_time,
        t2=t2_time,
        time=0)
    noise_model.add_quantum_error(
        error=thermal_error_rz,
        instructions="rz", 
        qubits=[qubit],
        warnings=False)
