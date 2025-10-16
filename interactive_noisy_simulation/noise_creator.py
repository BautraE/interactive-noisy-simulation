#Third party imports:
import pandas
from pandas.core.series import Series
from qiskit.transpiler import CouplingMap
from qiskit_aer.noise import (
    depolarizing_error,
    NoiseModel,
    ReadoutError,
    thermal_relaxation_error
)

# Local project imports:
from .messages._message_manager import MessageManager
from .noise_data_manager import NoiseDataManager
from .data._data import (
    CONFIG, CSV_COLUMNS, ERRORS, MESSAGES, OUTPUT_HEADINGS
)


class NoiseCreator:

    def __init__(self) -> None:
        """Constructor method."""
        self.__message_manager: MessageManager = MessageManager()
        msg = self.__message_manager
        msg.create_output(OUTPUT_HEADINGS["creating_new_object"].format(
            class_name=self.__class__.__name__))

        self.__noise_models = {}
        self.__noise_data = None

        msg.add_message(MESSAGES["created_new_object"], 
                        class_name=self.__class__.__name__)
        msg.end_output()


    # Class properties

    @property
    def noise_models(self) -> NoiseModel:
        """Returns a reference to data structure containing noise model 
           instances."""
        return self.__noise_models

    ###############################################################
    # TODO this one will still be edited after a specific style for it is designed
    def view_noise_models(self) -> None:
        msg = self.__message_manager
        msg.create_output(OUTPUT_HEADINGS["noise_model_instances"])

        # Perhaps this needs a check if NoiseDataManager was linked

        if self.__noise_models:
            for noise_model_key, instance in self.__noise_models.items():
                noise_model = instance["noise_model"]
                msg.add_message(f"Basis gates: {noise_model.basis_gates}")
                msg.add_message(noise_model_key)
                data_instance_key = instance["data_source"]
                msg.add_message(data_instance_key)
                if self.__check_data_instance_key(data_instance_key,
                                                  raise_error=False):
                    msg.add_message("Available")
                else: msg.add_message("Removed")
                msg.add_message("-----------------------------------------")
        else:
            msg.add_message("There are currently no created noise noise models!")
        
        msg.end_output()

    # TEMPORARY DEFINITION:

    def __check_data_instance_key(
            self, 
            reference_key: str, 
            raise_error: bool = True
    ) -> bool:
        """Checks if the given key is linked to an existing noise data
           instance. 

        Args:
            reference_key (str): The reference key that will be checked.
            raise_error (bool): Should the error be raised if the key does
                not exist among currently available noise data instances.

        Returns:
            bool: Validation of the searched noise data instances existing.
        """
        if reference_key in self.__noise_data:
            return True
        
        elif raise_error:
            raise KeyError(
                    ERRORS["no_key_noise_data_instance"].format(
                        reference_key=reference_key))
        else:
            return False

        
    def __check_noise_model_instance_key(self, reference_key: str) -> None:
        if not reference_key in self.__noise_models:
            raise KeyError(
                    ERRORS["no_key_noise_model_instance"].format(
                        reference_key=reference_key))
    ###############################################################

    # Public class methods
    
    def create_noise_model(
            self, 
            data_reference_key: str,
            noise_model_reference_key: str
    ) -> None:
        """Creates a new noise model
        
        Method creates a new noise model intance (new NoiseModel
        class object with errors based on proviced noise data from
        linked NoiseDataManager class object + a coupling map based
        on the same data)

        Args:
            data_reference_key (str): Reference key for the noise
                data instance that will be used for creating a new
                noise model.
            noise_model_reference_key (str): Reference key that will
                allow the user to access the created noise model
                afterwards.
        """
        msg = self.__message_manager
        msg.create_output(OUTPUT_HEADINGS["creating_noise_model"])
        
        try:
            self.__check_noise_data_manager_link()
            self.__check_data_instance_key(data_reference_key)
        except Exception:
            msg.add_traceback()
            return

        new_instance = {}
        new_instance["data_source"] = data_reference_key

        noise_dataframe = self.__noise_data[data_reference_key]["dataframe"]
        
        noise_model = NoiseModel(self.__get_basis_gates(noise_dataframe))
        
        msg.add_message(MESSAGES["adding_errors"])
        for qubit_nr, columns in noise_dataframe.iterrows():
            self.__add_readout_error(qubit_nr, columns, noise_model)
            self.__add_depolarizing_error(qubit_nr, columns, noise_model)
            self.__add_thermal_error(qubit_nr, columns, 
                                     noise_model, noise_dataframe)

        new_instance["noise_model"] = noise_model

        coupling_map = self.__get_coupling_map(noise_dataframe)
        new_instance["coupling_map"] = coupling_map

        self.__noise_models[noise_model_reference_key] = new_instance
        
        msg.add_message(
            MESSAGES["created_noise_model"],
            reference_key=noise_model_reference_key)
        msg.end_output()


    def link_noise_data_manager(
            self, 
            noise_data_manager: NoiseDataManager
    ) -> None:
        """Links a NoiseDataManager object to gain access to noise data."""
        msg = self.__message_manager
        msg.create_output(OUTPUT_HEADINGS["linking_object"].format(
            linked_class=NoiseDataManager.__name__, 
            this_class=self.__class__.__name__))
        
        self.__noise_data = noise_data_manager.noise_data

        msg.add_message(MESSAGES["linking_success"])
        msg.end_output()


    def remove_noise_model_instance(self, reference_key: str) -> None:
        """Removes existing noise model instance by reference key.
        
        Args:
            reference_key (str): Key of the removable noise model
                instance.
        """
        msg = self.__message_manager
        msg.create_output(
            OUTPUT_HEADINGS["remove_noise_model_instance"].format(
                reference_key=reference_key))
        
        try:
            self.__check_noise_model_instance_key(reference_key)
        except Exception:
            msg.add_traceback()
            return

        del self.__noise_models[reference_key]
        msg.add_message(
            MESSAGES["deleted_noise_model_instance"],
            reference_key=reference_key)
        msg.end_output()

    # Private class methods

    def __add_depolarizing_error(
            self, 
            qubit: int, 
            columns: Series, 
            noise_model: NoiseModel
        ) -> None:
        """Helps create and add depolarizing error to noise model
        
        Helper method for the class method "create_noise_model".

        By using available noise data, method creates depolarizing 
        errors for every basis gate operating on every specific 
        qubit or qubit pair. The created errors are then added to a 
        NoiseModel class object. The method finds the required data 
        without the help of the existing basis gates list. This code 
        was written based on given examples by IBM on how to create 
        such errors (a link to the web page is available further on).
        
        Link to IBM documentation on the mention topic:
        https://qiskit.github.io/qiskit-aer/tutorials/3_building_noise_models.html

        Args:
            qubit (int): The number of the current qubit.
            columns (Series): Table data for the current qubit. 
                Basically a row, however, to access a certain attribute, 
                you must do as follows: column["attribute_name"], where 
                "attribute_name" is the column name in the dataframe
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
    

    def __add_readout_error(
            self, 
            qubit: int, 
            columns: Series, 
            noise_model: NoiseModel
    ) -> None:
        """Helps create and add readout error to noise model

        Helper method for the class method "create_noise_model".

        By using available noise data, method creates readout errors 
        for every qubit and adds them to a class NoiseModel object. 
        This code was written based on given examples by IBM on how to 
        create such errors (a link to the web page is available 
        further on).

        Link to IBM documentation on the mention topic:
        https://qiskit.github.io/qiskit-aer/tutorials/3_building_noise_models.html

        Args:
            qubit (int): The number of the current qubit.
            columns (Series): Table data for the current qubit. Basically 
                a row, however, to access a certain attribute, you must do 
                as follows: column["attribute_name"], where "attribute_name" 
                is the column name in the dataframe.
            noise_model (NoiseModel): The noise model object, to which
                the newly created errors will be added.
        """
        m0p1 = columns[CSV_COLUMNS["m0p1"]["csv_name"]]
        m1p0 = columns[CSV_COLUMNS["m1p0"]["csv_name"]]
        readout_error = ReadoutError([[1-m0p1, m0p1], [m1p0, 1-m1p0]])
        noise_model.add_readout_error(readout_error, [qubit])


    def __add_thermal_error(
            self, 
            qubit: int, 
            columns: Series, 
            noise_model: NoiseModel,
            noise_dataframe: pandas.DataFrame
    ) -> None:
        """Helps create and add thermal relaxation error to noise model.
        
        Helper method for the class method "create_noise_model".

        By using available noise data, method creates thermal relaxation 
        errors for every basis gate operating on every specific qubit 
        or qubit pair. The created errors are then added to a NoiseModel 
        class object. The method finds the required data without the 
        help of the existing basis gates list. 
        This code was written based on given examples by IBM on how to 
        create such errors (a link to the web page is available further 
        on). 
        The available time values (microseconds and nanoseconds) are 
        initially in the form of seconds, which is why they get multiplied 
        in the code to the correct format. Some T2 values in the available 
        CSV data from IBM's QPUs are bigger than 2*T1 so they need to be 
        truncated (this is also done in the available code example 
        from IBM).
        
        Link to IBM documentation on the mention topic:
        https://qiskit.github.io/qiskit-aer/tutorials/3_building_noise_models.html

        Args:
            qubit (int): The number of the current qubit.
            columns (Series): Table data for the current qubit. Basically 
                a row, however, to access a certain attribute, you must do 
                as follows: column["attribute_name"], where "attribute_name"
                is the column name in the dataframe.
            noise_model (NoiseModel):
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
            instructions="reset", 
            qubits=[qubit],
            warnings=False)
    
    
    def __check_noise_data_manager_link(self) -> None:
        """Checks if a NoiseDataManager class object is linked to this 
           NoiseCreator object."""
        if self.__noise_data is None:
            raise RuntimeError(
                ERRORS["error_not_linked"].format(
                    class_name=NoiseDataManager.__name__,
                    method_name=self.link_noise_data_manager.__name__))

    
    def __get_basis_gates(
            self, 
            noise_dataframe: pandas.DataFrame
    ) -> list[str]:
        """Helps to create and return a list of basis gates

        Helper method for the class method "create_noise_model".

        Creates a list of basis gates that is based on the current noise 
        data. All possible base gates are taken from the configuration 
        file "config.json", after which they are filtered based on what 
        kind of columns does the noise data table have. The basis gate 
        list is required when creating a NouiseModel object. If no basis 
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
            are accepted.For example: ["id", "ecr", "rz"]
        """ 
        msg = self.__message_manager
        msg.add_message(MESSAGES["retrieving_basis_gates"])

        basis_gate_list = CONFIG["non_gate_instructions"]

        for gate in CONFIG["single_qubit_gates"]:
            if CSV_COLUMNS[gate]["csv_name"] in noise_dataframe.columns:
                basis_gate_list.append(CSV_COLUMNS[gate]["code_name"])
        
        for gate in CONFIG["two_qubit_gates"]:
            if CSV_COLUMNS[gate]["csv_name"] in noise_dataframe.columns:
                basis_gate_list.append(CSV_COLUMNS[gate]["code_name"])

        return basis_gate_list
    
    
    def __get_coupling_map(
            self, 
            noise_dataframe: pandas.DataFrame
    ) -> CouplingMap:
        """Helps tp create a coupling map.

        Helper method for the class method "create_noise_model".

        Creates a coupling map that is based on the noise data. The 
        created coupling map object CouplingMap is to be used along 
        with the NoiseModel object when creating a AerSimulator 
        simulator instance.
        
        noise_dataframe (pandas.DataFrame): The current noise data
                instance dataframe that is being used to create a noise
                model.

        Returns:
            CouplingMap: Representation of the created coupling map.
        """
        msg = self.__message_manager
        msg.add_message(MESSAGES["retrieving_coupling_map"])

        coupled_qubits = []

        for qubit, columns in noise_dataframe.iterrows():
            neighboring_qubits = columns[CSV_COLUMNS["neighboring_qubits"]
                                                    ["csv_name"]]
            if isinstance(neighboring_qubits, list):
                for paired_qubit in neighboring_qubits:
                    coupled_qubits.append([qubit, paired_qubit])

        return CouplingMap(couplinglist=coupled_qubits)
