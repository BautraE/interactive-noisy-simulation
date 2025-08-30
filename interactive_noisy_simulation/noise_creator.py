# Standard library imports:
import json
from importlib import resources

#Third party imports:
import pandas
from qiskit.transpiler import CouplingMap
from qiskit_aer.noise import (
    NoiseModel,
    ReadoutError,
    depolarizing_error,
    thermal_relaxation_error
)

# Local project imports:
from . import data
from .messages._message_manager import MessageManager
from .noise_data_manager import NoiseDataManager


with (resources.files(data) / "config.json").open("r", encoding="utf8") as file:
    CONFIG = json.load(file)

with (resources.files(data) / "csv_columns.json").open("r", encoding="utf8") as file:
    CSV_COLUMNS = json.load(file)
    
with (resources.files(data) / "messages.json").open("r", encoding="utf8") as file:
    MESSAGES = json.load(file)


class NoiseCreator:

    def __init__(self) -> None:
        """Constructor method """
        self.__message_manager: MessageManager = MessageManager()
        msg = self.__message_manager
        msg.create_output(MESSAGES["creating_new_object"].format(class_name=self.__class__.__name__))

        self.__noise_model = {}
        self.__noise_data = None

        msg.add_message(MESSAGES["created_new_object"].format(class_name=self.__class__.__name__))
        msg.end_output()


    # Class properties

    @property
    def noise_model(self) -> NoiseModel:
        """Returns a read-only copy of the current noise model (dictionary with NoiseModel and CouplingMap object) """
        self.__check_noise_model()
        return self.__noise_model


    # Public class methods

    def create_noise_model(self) -> None:
        """Creates a new noise model
        
        Method creates a new NoiseModel class object with errors
        based on provided noise data from linked NoiseDataManager class
        object.
        """
        msg = self.__message_manager
        msg.create_output(MESSAGES["creating_noise_model"])
        
        if self.__noise_data is None:
            raise RuntimeError(
                f"{MESSAGES["error_not_linked"].format(class_name=NoiseDataManager.__name__,
                                                       method_name=self.link_noise_data_manager.__name__)}")

        self.__noise_model["noise_model"] = NoiseModel(self.__get_basis_gates())
        self.__get_coupling_map()
        for qubit_nr, columns in self.__noise_data.iterrows():
            self.__add_readout_error(qubit_nr, columns)
            self.__add_depolarizing_error(qubit_nr, columns)
            self.__add_thermal_error(qubit_nr, columns)

        msg.add_message(MESSAGES["created_noise_model"])
        msg.end_output()


    def link_noise_data_manager(self, noise_data_manager: NoiseDataManager) -> None:
        """Links a NoiseDataManager object to gain access to noise data """
        msg = self.__message_manager
        msg.create_output(MESSAGES["linking_object"].format(linked_class=NoiseDataManager.__name__,
                                                            this_class=self.__class__.__name__))
        self.__noise_data = noise_data_manager.noise_data

        msg.add_message(MESSAGES["linking_success"])
        msg.end_output()


    # Private class methods

    def __add_depolarizing_error(self, qubit, columns) -> None:
        """Helps create and add depolarizing error to noise model
        
        Helper method for the class method "create_noise_model".

        By using available noise data, method creates depolarizing 
        errors for every basis gate operating on every specific qubit or qubit
        pair. The created errors are then added to a NoiseModel class object.
        The method finds the required data without the help of the
        existing basis gates list. This code was written based on given
        examples by IBM on how to create such errors (a link to the web page 
        is available further on).
        
        Link to IBM documentation on the mention topic:
        https://qiskit.github.io/qiskit-aer/tutorials/3_building_noise_models.html

        Args:
            qubit: The number of the current qubit.
            columns: Table data for the current qubit. Basically a row, however,
                to access a certain attribute, you must do as follows:
                column["attribute_name"], where "attribute_name" is the column
                name in the dataframe.
        """ 
        noise_model = self.__noise_model["noise_model"]

        for gate in CONFIG["single_qubit_gates"]:
            if CSV_COLUMNS[gate]["csv_name"] in self.__noise_data.columns:
                error_data = columns[CSV_COLUMNS[gate]["csv_name"]]
                # In one case the single-qubit gate error values were NaN for one qubit.
                # Not sure if this was a bug on their side, but this validation fixes this issue.
                if not pandas.isna(error_data):
                    error = depolarizing_error(param=error_data, num_qubits=1)
                    noise_model.add_quantum_error(error=error, instructions=CSV_COLUMNS[gate]["code_name"], 
                                                  qubits=[qubit], warnings=False)

        for gate in CONFIG["two_qubit_gates"]:
            if CSV_COLUMNS[gate]["csv_name"] in self.__noise_data.columns:
                error_data = columns[CSV_COLUMNS[gate]["csv_name"]]
                if not pandas.isna(error_data):
                    # Since each row of these columns may contain more than one data entry
                    for target_qubit in error_data.keys():
                        error = depolarizing_error(param=error_data[target_qubit], num_qubits=2)
                        noise_model.add_quantum_error(error=error, instructions=CSV_COLUMNS[gate]["code_name"], 
                                                      qubits=[qubit, target_qubit], warnings=False)
    

    def __add_readout_error(self, qubit, columns) -> None:
        """Helps create and add readout error to noise model

        Helper method for the class method "create_noise_model".

        By using available noise data, method creates readout errors for
        every qubit and adds them to a class NoiseModel object. This code 
        was written based on givenexamples by IBM on how to create such 
        errors (a link to the web page is available further on).

        Link to IBM documentation on the mention topic:
        https://qiskit.github.io/qiskit-aer/tutorials/3_building_noise_models.html

        Args:
            qubit: The number of the current qubit.
            columns: Table data for the current qubit. Basically a row, however,
                to access a certain attribute, you must do as follows:
                column["attribute_name"], where "attribute_name" is the column
                name in the dataframe.
        """
        noise_model = self.__noise_model["noise_model"]

        m0p1 = columns[CSV_COLUMNS["m0p1"]["csv_name"]]
        m1p0 = columns[CSV_COLUMNS["m1p0"]["csv_name"]]
        readout_error = ReadoutError([[1-m0p1, m0p1], [m1p0, 1-m1p0]])
        noise_model.add_readout_error(readout_error, [qubit])


    def __add_thermal_error(self, qubit, columns) -> None:
        """Helps create and add thermal relaxation error to noise model
        
        Helper method for the class method "create_noise_model".

        By using available noise data, method creates thermal relaxation 
        errors for every basis gate operating on every specific qubit 
        or qubit pair. The created errors are then added to a NoiseModel 
        class object. The method finds the required data without the help of the
        existing basis gates list. This code was written based on given examples 
        by IBM on how to create such errors (a link to the web page is available 
        further on). The available time values (microseconds and nanoseconds) are 
        initially in the form of seconds, which is why they get multiplied in the 
        code to the correct format. Some T2 values in the available CSV data from 
        IBM's QPUs are bigger than 2*T1 so they need to be truncated (this is also 
        done in the available code example from IBM).
        
        Link to IBM documentation on the mention topic:
        https://qiskit.github.io/qiskit-aer/tutorials/3_building_noise_models.html

        Args:
            qubit: The number of the current qubit.
            columns: Table data for the current qubit. Basically a row, however,
                to access a certain attribute, you must do as follows:
                column["attribute_name"], where "attribute_name" is the column
                name in the dataframe.
        """ 
        noise_model = self.__noise_model["noise_model"]
        t1_time = columns[CSV_COLUMNS["t1_time"]["csv_name"]] * 1e-6
        t2_time = min(columns[CSV_COLUMNS["t2_time"]["csv_name"]] * 1e-6, 2 * t1_time)

        # All single-qubit gates have the same thermal relaxation error
        thermal_error_1q = thermal_relaxation_error(t1_time, t2_time, 
                                                    columns[CSV_COLUMNS["1q_gate_time"]["csv_name"]] * 1e-9)
       
        for gate in CONFIG["single_qubit_gates"]:
            # RZ gates use a different gate time
            if gate == "rz_gate_error": continue
            if CSV_COLUMNS[gate]["csv_name"] in self.__noise_data.columns:
                noise_model.add_quantum_error(error=thermal_error_1q, instructions=CSV_COLUMNS[gate]["code_name"], 
                                              qubits=[qubit], warnings=False)

        # Similarly, all two-qubit gates have the same thermal relaxation error
        two_qubit_gate_time = columns[CSV_COLUMNS["2q_gate_time"]["csv_name"]]
        if not pandas.isna(two_qubit_gate_time):
            for target_qubit in two_qubit_gate_time.keys():
                t1_time_q2 = self.__noise_data.at[target_qubit, CSV_COLUMNS["t1_time"]["csv_name"]] * 1e-6
                t2_time_q2 = min(self.__noise_data.at[target_qubit, CSV_COLUMNS["t2_time"]["csv_name"]] * 1e-6,
                                 t1_time_q2 * 2)
                thermal_error_2q = thermal_relaxation_error(t1_time, t2_time, two_qubit_gate_time[target_qubit] * 1e-9).expand(
                        thermal_relaxation_error(t1_time_q2, t2_time_q2, two_qubit_gate_time[target_qubit] * 1e-9))
                for gate in CONFIG["two_qubit_gates"]:
                    if CSV_COLUMNS[gate]["csv_name"] in self.__noise_data.columns:
                        noise_model.add_quantum_error(error=thermal_error_2q, instructions=CSV_COLUMNS[gate]["code_name"], 
                                                      qubits=[qubit, target_qubit], warnings=False)

        # Creating and adding thermal relax error for measure operation
        readout_time = columns[CSV_COLUMNS["readout_time"]["csv_name"]] * 1e-9
        thermal_error_readout = thermal_relaxation_error(t1_time, t2_time, readout_time)
        noise_model.add_quantum_error(error=thermal_error_readout, instructions="measure", 
                                      qubits=[qubit], warnings=False)

        # Creating and adding thermal relax error for reset operation
        reset_time = columns[CSV_COLUMNS["reset_time"]["csv_name"]] * 1e-9
        thermal_error_reset = thermal_relaxation_error(t1_time, t2_time, reset_time)
        noise_model.add_quantum_error(error=thermal_error_reset, instructions="reset", 
                                      qubits=[qubit], warnings=False)

        thermal_error_rz = thermal_relaxation_error(t1_time, t2_time, 0)
        noise_model.add_quantum_error(error=thermal_error_rz, instructions="reset", 
                                      qubits=[qubit], warnings=False)
    
    
    def __check_noise_model(self) -> None:
        """Checks if a noise model exists in the current object of NoiseCreator """
        if not self.__noise_model:
            raise RuntimeError(f"{MESSAGES["error_no_noise_model"]}")

    
    def __get_basis_gates(self) -> list[str]:
        """Helps to create and return a list of basis gates

        Helper method for the class method "create_noise_model".

        Creates a list of basis gates that is based on the current noise data. 
        All possible base gates are taken from the configuration file "config.json", 
        after which they are filtered based on what kind of columns does the noise 
        data table have. The basis gate list is required when creating a NouiseModel 
        object. If no basis gates are presented during the creation, it will 
        pick a set of default basis gates. If you add the basis gates later, it 
        will add them together with the default basis gates.
        
        Returns:
            A list of basis gate names in the form that they are accepted.
            For example:

            ["id", "ecr", "rz"]
        """ 
        basis_gate_list = CONFIG["non_gate_instructions"]

        for gate in CONFIG["single_qubit_gates"]:
            if CSV_COLUMNS[gate]["csv_name"] in self.__noise_data.columns:
                basis_gate_list.append(CSV_COLUMNS[gate]["code_name"])
        
        for gate in CONFIG["two_qubit_gates"]:
            if CSV_COLUMNS[gate]["csv_name"] in self.__noise_data.columns:
                basis_gate_list.append(CSV_COLUMNS[gate]["code_name"])

        return basis_gate_list
    
    
    def __get_coupling_map(self) -> None:
        """Helps tp create a coupling map.

        Helper method for the class method "create_noise_model".

        Creates a coupling map that is based on the noise data. The created 
        coupling map object CouplingMap is to be used along with the NoiseModel 
        object when creating a AerSimulator simulator instance.
        """
        coupled_qubits = []

        for qubit, columns in self.__noise_data.iterrows():
            neighboring_qubits = columns[CSV_COLUMNS["neighboring_qubits"]["csv_name"]]
            if isinstance(neighboring_qubits, list):
                for paired_qubit in neighboring_qubits:
                    coupled_qubits.append([qubit, paired_qubit])

        self.__noise_model["coupling_map"] = CouplingMap(couplinglist=coupled_qubits)
