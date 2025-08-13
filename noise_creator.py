import json, pandas
from noise_data_manager import NoiseDataManager
from qiskit.transpiler import CouplingMap
from qiskit_aer.noise import (NoiseModel, ReadoutError, depolarizing_error, thermal_relaxation_error)

with open("data/csv_columns.json", "r") as file:
    CSV_COLUMNS = json.load(file)
with open("data/config.json", "r") as file:
    CONFIG = json.load(file)

class NoiseCreator:
    def __init__(self) -> None:
        print(f"----- Creating {NoiseCreator.__name__} object -----")
        self.__noise_model = None
        self.__noise_data = None
        f"{NoiseCreator.__name__} class object has been created successfully!\n"

    def link_noise_data_manager(self, noise_data_manager: NoiseDataManager) -> None:
        self.__noise_data = noise_data_manager.noise_data

    def create_noise_model(self) -> None:
        if self.__noise_data is None:
            raise RuntimeError("There is no linked NoiseDataManager object! Please use the method link_noise_data_manager(ndm: NoiseDataManager) before creating a noise model!")
        
        self.__noise_model = NoiseModel(self.__get_basis_gates())

        for qubit_nr, columns in self.__noise_data.iterrows():
            self.__add_readout_error(qubit_nr, columns)
            self.__add_depolarizing_error(qubit_nr, columns)
            self.__add_thermal_error(qubit_nr, columns)
    
    def __add_readout_error(self, qubit_nr, columns) -> None:
        m0p1 = columns[CSV_COLUMNS["m0p1"]["csv_name"]]
        m1p0 = columns[CSV_COLUMNS["m0p1"]["csv_name"]]
        readout_error = ReadoutError([[1-m0p1, m0p1], [m1p0, 1-m1p0]])
        self.__noise_model.add_readout_error(readout_error, [qubit_nr])

    def __add_depolarizing_error(self, qubit_nr, columns) -> None:
        for instruction in CONFIG["single_qubit_gates"]:
            if CSV_COLUMNS[instruction]["csv_name"] in self.__noise_data.columns:
                error_data = columns[CSV_COLUMNS[instruction]["csv_name"]]
                # In one case the single-qubit gate error values were NaN for one qubit.
                # Not sure if this was a bug on their side, but this validation fixes this issue.
                if not pandas.isna(error_data):
                    error = depolarizing_error(error_data, 1)
                    self.__noise_model.add_quantum_error(error, CSV_COLUMNS[instruction]["code_name"], [qubit_nr])

        for instruction in CONFIG["two_qubit_gates"]:
            if CSV_COLUMNS[instruction]["csv_name"] in self.__noise_data.columns:
                error_data = columns[CSV_COLUMNS[instruction]["csv_name"]]
                if not pandas.isna(error_data):
                    # Since each row of these columns may contain more than one data entry
                    for target_qubit in error_data.keys():
                        error = depolarizing_error(error_data[target_qubit], 2)
                        self.__noise_model.add_quantum_error(error, CSV_COLUMNS[instruction]["code_name"], [qubit_nr, target_qubit])

    def __add_thermal_error(self, qubit_nr, columns) -> None:
        # Since base value is seconds, converting both to microseconds
        t1_time = columns[CSV_COLUMNS["t1_time"]["csv_name"]] * 1e-6
        # Some T2 values are bigger than 2*T1 so they need to be truncated
        t2_time = min(columns[CSV_COLUMNS["t2_time"]["csv_name"]] * 1e-6, 2 * t1_time)

        # All single-qubit gates have the same thermal relaxation error
        # Also converting all gate time values to nanoseconds since base value is in seconds
        thermal_error_1q = thermal_relaxation_error(t1_time, t2_time, columns[CSV_COLUMNS["1q_gate_time"]["csv_name"]] * 1e-9)
        for instruction in CONFIG["single_qubit_gates"]:
            if CSV_COLUMNS[instruction]["csv_name"] in self.__noise_data.columns:
                self.__noise_model.add_quantum_error(thermal_error_1q, CSV_COLUMNS[instruction]["code_name"], [qubit_nr], warnings=False)

        # Similarly, all two-qubit gates have the same thermal relaxation error
        two_qubit_gate_time = columns[CSV_COLUMNS["2q_gate_time"]["csv_name"]]
        if not pandas.isna(two_qubit_gate_time):
            for target_qubit in two_qubit_gate_time.keys():
                # Since base value is seconds, converting both to microseconds
                t1_time_q2 = self.__noise_data.at[target_qubit, CSV_COLUMNS["t1_time"]["csv_name"]] * 1e-6
                # Some T2 values are bigger than 2*T1 so they need to be truncated
                t2_time_q2 = min(self.__noise_data.at[target_qubit, CSV_COLUMNS["t2_time"]["csv_name"]] * 1e-6, 2 * t1_time_q2)
                thermal_err_2q = thermal_relaxation_error(t1_time, t2_time, two_qubit_gate_time[target_qubit] * 1e-9).expand(
                        thermal_relaxation_error(t1_time_q2, t2_time_q2, two_qubit_gate_time[target_qubit] * 1e-9))
                for instruction in CONFIG["two_qubit_gates"]:
                    if CSV_COLUMNS[instruction]["csv_name"] in self.__noise_data.columns:
                        self.__noise_model.add_quantum_error(thermal_err_2q, CSV_COLUMNS[instruction]["code_name"], [qubit_nr, target_qubit], warnings=False)

        # Creating and adding thermal relax error for measure operation
        readout_time = columns[CSV_COLUMNS["readout_time"]["csv_name"]] * 1e-9
        thermal_err_readout = thermal_relaxation_error(t1_time, t2_time, readout_time)
        self.__noise_model.add_quantum_error(thermal_err_readout, "measure", [qubit_nr])

        # Creating and adding thermal relax error for reset operation
        reset_time = columns[CSV_COLUMNS["reset_time"]["csv_name"]] * 1e-9
        thermal_err_reset = thermal_relaxation_error(t1_time, t2_time, reset_time)
        self.__noise_model.add_quantum_error(thermal_err_reset, "reset", [qubit_nr])

    def __get_basis_gates(self) -> list[str]:
        basis_gate_list = CONFIG["non_gate_instructions"]

        for instruction in CONFIG["single_qubit_gates"]:
            if CSV_COLUMNS[instruction]["csv_name"] in self.__noise_data.columns:
                basis_gate_list.append(CSV_COLUMNS[instruction]["code_name"])
        
        for instruction in CONFIG["two_qubit_gates"]:
            if CSV_COLUMNS[instruction]["csv_name"] in self.__noise_data.columns:
                basis_gate_list.append(CSV_COLUMNS[instruction]["code_name"])

        return basis_gate_list
    
    def get_coupling_map(self) -> CouplingMap:
        coupled_qubits = []
        for qubit, columns in self.__noise_data.iterrows():
            neighboring_qubits = columns[CSV_COLUMNS["neighboring_qubits"]["csv_name"]]
            if isinstance(neighboring_qubits, list):
                for paired_qubit in neighboring_qubits:
                    coupled_qubits.append([qubit, paired_qubit])

        return CouplingMap(couplinglist=coupled_qubits)
