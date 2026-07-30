# =========================================================================
# This file contains helper functions for the class NoiseCreator.
#
# The following methods are used for adding specific errors to a noise 
# model, as well as obtaining a list of basis gates and the coupling map.
# =========================================================================
# 1. Obtaining list of basis gates and coupling map
# 2. Adding readout errors
# 3. Adding depolarizing errors
# 4. Adding thermal relaxation errors
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
from ....project_variables import (
    SINGLE_QUBIT_GATES, 
    TWO_QUBIT_GATES
)

# Imports only used for type definition:
from pandas.core.series import Series


# --------------------------------------------------------------
# 1. Obtaining list of basis gates and coupling map
# --------------------------------------------------------------

def get_basis_gates(
    noise_dataframe: pandas.DataFrame
) -> list[str]:
    """Creates and returns a list of basis gates from given noise dataframe.

    Creates a list of basis gates that is based on the current noise 
    data. All supported base gates from are taken from `SINGLE_QUBIT_GATES` 
    and `TWO_QUBIT_GATES`, after which they are filtered based on what 
    kind of columns does the noise dataframe have. The basis gate 
    list is required when creating a `NoiseModel` object. If no basis 
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
    basis_gate_list = []

    for gate_code_name, gate_reference in SINGLE_QUBIT_GATES.items():
        if gate_reference in noise_dataframe.columns:
            basis_gate_list.append(gate_code_name)
    
    for gate_code_name, gate_reference in TWO_QUBIT_GATES.items():
        if gate_reference in noise_dataframe.columns:
            basis_gate_list.append(gate_code_name)

    return basis_gate_list


def get_coupling_map(
    noise_dataframe: pandas.DataFrame
) -> CouplingMap:
    """Creates and returns a coupling map from given noise dataframe.

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
        neighboring_qubits = columns["neighboring_qubits"]
        if isinstance(neighboring_qubits, list):
            for paired_qubit in neighboring_qubits:
                coupled_qubits.append([qubit, paired_qubit])

    return CouplingMap(couplinglist=coupled_qubits)


# --------------------------------------------------------------
# 2. Adding readout errors
# --------------------------------------------------------------

def add_readout_error(
    current_qubit: int, 
    columns: Series, 
    noise_model: NoiseModel
) -> None:
    """Creates and adds readout errors to provided noise model.

    By using provided noise data, the function creates a readout error 
    for the specified qubit and adds it to a the given `NoiseModel` object.

    This code was written based on given examples by IBM on how to 
    create such errors (a link to the web page is available 
    further on).
    Link to IBM documentation on the mention topic:
    https://qiskit.github.io/qiskit-aer/tutorials/3_building_noise_models.html

    Args:
        current_qubit (int): Number of the current qubit.
        columns (Series): Table data for the current qubit. Basically 
            a row, however, to access a certain attribute, you must do 
            as follows: `column["attribute_name"]`, where 
            `"attribute_name"` is the column name in the dataframe.
        noise_model (NoiseModel): The noise model object, to which
            the newly created errors will be added.
    """
    m0p1 = columns["m0p1"]
    m1p0 = columns["m1p0"]
    readout_error = ReadoutError([[1-m0p1, m0p1], [m1p0, 1-m1p0]])
    noise_model.add_readout_error(error=readout_error, 
                                  qubits=[current_qubit])


# --------------------------------------------------------------
# 3. Adding depolarizing errors
# --------------------------------------------------------------

def add_depolarizing_error(
    current_qubit: int, 
    columns: Series, 
    noise_model: NoiseModel
) -> None:
    """Creates and adds depolarizing errors to the provided noise model.

    By using provided noise data, the function creates depolarizing 
    errors for every basis gate operating on the specified qubit. 
    The created errors are then added to the provided `NoiseModel` object. 
    
    The function finds the required data without the help of the existing 
    basis gates list. 
    
    This code was written based on given examples by IBM on how to 
    create such errors (a link to the web page is available 
    further on).
    Link to IBM documentation on the mention topic:
    https://qiskit.github.io/qiskit-aer/tutorials/3_building_noise_models.html

    Args:
        current_qubit (int): Number of the current qubit.
        columns (Series): Table data for the current qubit. 
            Basically a row, however, to access a certain attribute, 
            you must do as follows: `column["attribute_name"]`, where 
            `"attribute_name"` is the column name in the dataframe
            and CSV file.
        noise_model (NoiseModel): The noise model object, to which
            the newly created errors will be added.
    """
    for gate_code_name, gate_reference in SINGLE_QUBIT_GATES.items():
        # If the gate is part of the basis gate list of the backend
        if gate_reference in columns:
            error_data = columns[gate_reference]
            # In one case the single-qubit gate error values were NaN
            # for one qubit. Not sure if this was a bug on their side, 
            # but this validation fixes this issue.
            if not pandas.isna(error_data):
                error = depolarizing_error(param=error_data,
                                           num_qubits=1)
                noise_model.add_quantum_error(error=error, 
                                              instructions=gate_code_name, 
                                              qubits=[current_qubit], 
                                              warnings=False)

    for gate_code_name, gate_reference in TWO_QUBIT_GATES.items():
        # If the gate is part of the basis gate list of the backend
        if gate_reference in columns:
            error_data = columns[gate_reference]
            # error data will be nan if there are no connected qubits to the
            # current qubit.
            if not pandas.isna(error_data):
                # Since each row of these columns may contain more
                # than one data entry.
                for connected_qubit, error_parameter in error_data.items():
                    error = depolarizing_error(param=error_parameter,
                                               num_qubits=2)
                    noise_model.add_quantum_error(error=error,
                                                  instructions=gate_code_name, 
                                                  qubits=[current_qubit, connected_qubit],
                                                  warnings=False)


# --------------------------------------------------------------
# 4. Adding thermal relaxation errors
# --------------------------------------------------------------

def add_thermal_error(
    current_qubit: int, 
    columns: Series, 
    noise_model: NoiseModel,
    noise_dataframe: pandas.DataFrame
) -> None:
    """Creates and adds thermal relaxation errors to the provided 
    noise model.

    By using provided noise data, the function creates thermal relaxation 
    errors for every basis gate operating on the specified qubit. 
    The created errors are then added to a `NoiseModel` object. 
    
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

    Args:
        current_qubit (int): Number of the current qubit.
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
    t1_time = columns["t1_time"] * 1e-6
    # Some T2 values in the available CSV data from IBM's QPUs are bigger
    # than 2*T1 so they need to be truncated
    csv_t2_value = columns["t2_time"] * 1e-6
    t2_time = min(csv_t2_value, t1_time * 2)
    
    # Exits function if no T1 or T2 times are provided.
    # There have been situations, where this is the case, which is why
    # this validation exists.
    if pandas.isna(t1_time) | pandas.isna(t2_time): return

    single_qubit_gate_time = columns["1q_gate_time"] * 1e-9
    two_qubit_gate_times = columns["2q_gate_time"]

    _add_single_qubit_gate_thermal_errors(t1_time=t1_time,
                                          t2_time=t2_time,
                                          gate_time=single_qubit_gate_time,
                                          noise_model=noise_model,
                                          current_qubit=current_qubit,
                                          columns=columns)

    _add_two_qubit_gate_thermal_errors(q1_t1_time=t1_time,
                                       q1_t2_time=t2_time,
                                       gate_times=two_qubit_gate_times,
                                       current_qubit=current_qubit,
                                       noise_model=noise_model,
                                       columns=columns,
                                       noise_dataframe=noise_dataframe)
    
    _add_other_operation_thermal_errors(t1_time=t1_time,
                                        t2_time=t2_time,
                                        current_qubit=current_qubit,
                                        noise_model=noise_model,
                                        columns=columns)


def _add_single_qubit_gate_thermal_errors(
    t1_time: float,
    t2_time: float,
    gate_time: float,
    current_qubit: int,
    noise_model: NoiseModel,
    columns: Series
) -> None:
    """Creates and adds thermal relaxation errors to all single-qubit gates of
    the backend.
    
    This code was written based on given examples by IBM on how to 
    create such errors (a link to the web page is available 
    further on).
    Link to IBM documentation on the mention topic:
    https://qiskit.github.io/qiskit-aer/tutorials/3_building_noise_models.html
    
    Args:
        t1_time (float): T1 relaxation time for the current qubit.
        t2_time (float): T2 relaxation time for the current qubit.
        gate_time (float): Single-qubit gate time. This time applies to all
            single-qubit gates for the current qubit.
        current_qubit (int) The number of the current qubit.
        noise_model (NoiseModel): The noise model object, to which
            the newly created errors will be added.
        columns (Series): Table data for the current qubit. Basically 
            a row, however, to access a certain attribute, you must do 
            as follows: `column["attribute_name"]`, where 
            `"attribute_name"` is the column name in the dataframe.
    """
    # All single-qubit gates have the same thermal relaxation error
    thermal_error_1q = thermal_relaxation_error(t1=t1_time, 
                                                t2=t2_time, 
                                                time=gate_time)
    
    for gate_code_name, gate_reference in SINGLE_QUBIT_GATES.items():
        # RZ gates use a different gate time
        # If the gate is part of the basis gate list of the backend
        if gate_reference != "rz_gate_error" and gate_reference in columns:
            noise_model.add_quantum_error(error=thermal_error_1q,
                                          instructions=gate_code_name,
                                          qubits=[current_qubit],
                                          warnings=False)


def _add_two_qubit_gate_thermal_errors(
    q1_t1_time: float,
    q1_t2_time: float,
    gate_times: dict[int, float] | float, # If float, then its nan
    current_qubit: int,
    noise_model: NoiseModel,
    columns: Series,
    noise_dataframe: pandas.DataFrame
) -> None:
    """Creates and adds thermal relaxation errors to all two-qubit gates of the
    backend.
    
    This code was written based on given examples by IBM on how to 
    create such errors (a link to the web page is available 
    further on).
    Link to IBM documentation on the mention topic:
    https://qiskit.github.io/qiskit-aer/tutorials/3_building_noise_models.html

    Args:
        q1_t1_time (float): T1 relaxation time for the current qubit.
        q1_t2_time (float): T2 relaxation time for the current qubit.
        gate_times (dict[int, float] | float): Two-qubit gate tims. This time 
            applies to all two-qubit gates for each specific connected qubit 
            pair. The value will be a `dictionary` in the case of there being
            one or more connected qubits to the current qubit. The value will
            be a `float` if there are no connected qubits to the current qubit
            , thus it will be `nan`
        current_qubit (int): The number of the current qubit.
        noise_model (NoiseModel): The noise model object, to which
            the newly created errors will be added.
        columns (Series): Table data for the current qubit. Basically 
            a row, however, to access a certain attribute, you must do 
            as follows: `column["attribute_name"]`, where 
            `"attribute_name"` is the column name in the dataframe.
        noise_dataframe (pandas.DataFrame): The same dataframe, from 
            which the qubit number and columns attributes are from. 
            It is required here because certain connected qubit noise 
            data must be found to create the thermal relaxation error 
            for two-qubit gates.
    """
    # Multi-value columns may be emptry in CSV
    if not pandas.isna(gate_times):
        for connected_qubit, gate_time in gate_times.items():
            # T1 & T2 times for target qubits
            q2_t1_time = noise_dataframe.at[connected_qubit, "t1_time"] * 1e-6
            # Some T2 values in the available CSV data from IBM's QPUs are bigger
            # than 2*T1 so they need to be truncated
            csv_t2_value = noise_dataframe.at[connected_qubit, "t2_time"] * 1e-6
            q2_t2_time = min(csv_t2_value, q2_t1_time * 2)
            
            # Exits function if no T1 or T2 times are provided.
            # There have been situations, where this is the case, which is why
            # this validation exists.
            if pandas.isna(q2_t1_time) | pandas.isna(q2_t2_time): continue
            
            # All two-qubit gates have the same thermal relaxation error
            # (within the scope of a single qubit connection in the backend
            # coupling map)
            thermal_error_2q = thermal_relaxation_error(
                t1=q1_t1_time, 
                t2=q1_t2_time, 
                time=gate_time * 1e-9).expand(
                    thermal_relaxation_error(
                        t1=q2_t1_time, 
                        t2=q2_t2_time, 
                        time=gate_time * 1e-9))

            # Adding created thermal relaxation error for all two-qubit gates
            # for the current qubit pair
            for gate_code_name, gate_reference in TWO_QUBIT_GATES.items():
                # If the gate is part of the basis gate list of the backend
                if gate_reference in columns:
                    noise_model.add_quantum_error(error=thermal_error_2q,
                                                  instructions=gate_code_name,
                                                  qubits=[current_qubit, connected_qubit],
                                                  warnings=False)


def _add_other_operation_thermal_errors(
    t1_time: float,
    t2_time: float,
    current_qubit: int,
    noise_model: NoiseModel,
    columns: Series
) -> None:
    """Creating and adding thermal relaxation errors to other operations
    that are not single- or two-qubit gates.
    
    Such operations include: measure, reset, rz (because it has a gate 
    time of 0).

    This code was written based on given examples by IBM on how to 
    create such errors (a link to the web page is available 
    further on).
    Link to IBM documentation on the mention topic:
    https://qiskit.github.io/qiskit-aer/tutorials/3_building_noise_models.html

    Args:
        t1_time (float): T1 relaxation time for the current qubit.
        t2_time (float): T2 relaxation time for the current qubit.
        current_qubit (int): The number of the current qubit.
        noise_model (NoiseModel): The noise model object, to which
            the newly created errors will be added.
        columns (Series): Table data for the current qubit. Basically 
            a row, however, to access a certain attribute, you must do 
            as follows: `column["attribute_name"]`, where 
            `"attribute_name"` is the column name in the dataframe.
    """
    # Operation name & operation time
    operations = {
        "measure": columns["readout_time"],
        "reset": columns["reset_time"],
        "rz": 0
    }

    for operation, operation_time in operations.items():
        thermal_error = thermal_relaxation_error(t1=t1_time, 
                                                 t2=t2_time, 
                                                 time=operation_time * 1e-9)
        noise_model.add_quantum_error(error=thermal_error, 
                                      instructions=operation, 
                                      qubits=[current_qubit],
                                      warnings=False)
