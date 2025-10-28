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
from .messages._message_manager import MessageManager
from .noise_data_manager import NoiseDataManager
from .utils.key_availability import KeyAvailabilityManager
from .utils.validators import (
    check_instance_key, validate_instance_name
)
from .data._data import (
    CONFIG, CSV_COLUMNS, ERRORS, MESSAGES, OUTPUT_HEADINGS
)

# Imports only used for type definition:
from pandas.core.series import Series


class NoiseCreator:

    def __init__(self) -> None:
        """Constructor method."""
        self.__key_manager = None
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
    def key_manager(self) -> KeyAvailabilityManager:
        """Returns a reference to a KeyAvailabilityManager
        
        A manager that will be used across all main manager
        classes to keep track of blocked keys:
            - `NoiseDataManager`
            - `NoiseCreator`
            - `SimulatorManager`
        """
        return self.__key_manager


    @property
    def noise_models(self) -> NoiseModel:
        """Returns a reference to data structure containing noise model 
           instances."""
        return self.__noise_models
    

    # Public class methods
    
    def create_noise_model(
            self,
            noise_model_reference_key: str, 
            data_reference_key: str,
            has_noise: bool = True
    ) -> None:
        """Creates a new noise model.
        
        Method creates a new noise model intance (new `NoiseModel`
        class object with errors based on proviced noise data from
        linked `NoiseDataManager` class object + a coupling map based
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
        msg.create_output(OUTPUT_HEADINGS["creating_noise_model"].format(
            reference_key=data_reference_key))
        
        try:
            self.__check_noise_data_manager_link()
            # Is there a usable noise data instance with the given key
            check_instance_key(reference_key=data_reference_key,
                               should_exist=True, 
                               instances=self.__noise_data,
                               instance_type="noise data instance")
            # Does key exist among created noise model instances
            check_instance_key(reference_key=noise_model_reference_key,
                               should_exist=False, 
                               instances=self.__noise_models,
                               instance_type="noise model instance")
            # Is key being blocked by a simulator instance reference
            self.__key_manager.check_blocked_key(
                                key=noise_model_reference_key,
                                instance_type="noise_models")
        except Exception:
            msg.add_traceback()
            return
        
        noise_model_reference_key = validate_instance_name(
            noise_model_reference_key,
            msg)

        new_instance = {}
        new_instance["data_source"] = data_reference_key

        noise_dataframe = self.__noise_data[data_reference_key]["dataframe"]
        
        noise_model = NoiseModel(self.__get_basis_gates(noise_dataframe))
        
        if has_noise:
            msg.add_message(MESSAGES["adding_errors"])
            for qubit_nr, columns in noise_dataframe.iterrows():
                self.__add_readout_error(qubit_nr, columns, noise_model)
                self.__add_depolarizing_error(qubit_nr, columns, noise_model)
                self.__add_thermal_error(qubit_nr, columns, 
                                        noise_model, noise_dataframe)
        else:
            msg.add_message(MESSAGES["not_adding_errors"])

        new_instance["noise_model"] = noise_model

        coupling_map = self.__get_coupling_map(noise_dataframe)
        new_instance["coupling_map"] = coupling_map

        self.__noise_models[noise_model_reference_key] = new_instance

        # Blocks noise data instance key until this noise model instance
        # gets deleted (noise model has reference to used noise data key)
        self.__key_manager.block_key(key=data_reference_key,
                                     instance_type="noise_data",
                                     blocker_key=noise_model_reference_key)
        
        msg.add_message(
            MESSAGES["created_instance"],
            instance_type="Noise model",
            reference_key=noise_model_reference_key)
        msg.end_output()


    def link_noise_data_manager(
            self, 
            noise_data_manager: NoiseDataManager
    ) -> None:
        """Links a `NoiseDataManager` object to gain access to noise data."""
        msg = self.__message_manager
        msg.create_output(OUTPUT_HEADINGS["linking_object"].format(
            linked_class=NoiseDataManager.__name__, 
            this_class=self.__class__.__name__))
        
        self.__noise_data = noise_data_manager.noise_data
        self.__key_manager = noise_data_manager.key_manager

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
            OUTPUT_HEADINGS["remove_instance"].format(
                instance_type="noise model instance",
                reference_key=reference_key))
        
        try:
            # Is there even an instance to delete with given key
            check_instance_key(reference_key=reference_key,
                               should_exist=True, 
                               instances=self.__noise_models,
                               instance_type="noise model instance")
        except Exception:
            msg.add_traceback()
            return

        # Unblocking referenced noise data key
        instance = self.__noise_models[reference_key]
        data_reference_key = instance["data_source"]
        self.__key_manager.unblock_key(key=data_reference_key,
                                       instance_type="noise_data")
        
        del self.__noise_models[reference_key]

        msg.add_message(
            MESSAGES["deleted_instance"],
            instance_type="noise model instance",
            reference_key=reference_key)
        msg.end_output()

    
    def view_noise_models(self) -> None:
        """Displays all currently available noise model instances.

        If no instances are available, method simply displays a
        message that states this fact.
        The visual output from this method is placed inside of the
        default "message" content container.

        Displayed information includes:
        - Reference key for the current instance;
        - Noise model qubit count; 
        - List of basis gates;
        - Reference key for the source noise data instance that was
          used in the making of the current instance;
        - Availability of the source noise data instance (Available
          or Removed).
        """
        msg = self.__message_manager
        msg.create_output(OUTPUT_HEADINGS["created_instances"].format(
            instance_type="noise models"))
        msg.generic_content_container("Noise model instances:")

        if self.__noise_models:

            msg.add_generic_table()
            msg.add_generic_table_row(
                row_content=["Reference key", "Qubit count", 
                             "Basis gates", "Has noise", 
                             "Source noise data", 
                             "Noise data availability"],
                row_type="th")

            for noise_model_key, instance in self.__noise_models.items():
                
                noise_model = instance["noise_model"]
                coupling_map = instance["coupling_map"]

                qubit_count = str(coupling_map.size())
                basis_gates = "; ".join(noise_model.basis_gates)
                has_noise = self.__has_noise(noise_model)
                
                data_reference_key = instance["data_source"]
                
                if check_instance_key(reference_key=data_reference_key,
                                      should_exist=True,
                                      instances=self.__noise_data,
                                      instance_type="noise data instance",
                                      raise_error=False):
                    availability = "Available"
                else: 
                    availability = "Removed"
                noise_data_availability = msg.style_availability_status(
                    availability)
                
                msg.add_generic_table_row(
                    row_content=[noise_model_key, qubit_count,
                                 basis_gates, has_noise, 
                                 data_reference_key,
                                 noise_data_availability],
                    row_type="td")
        else:
            msg.add_message(MESSAGES["no_instances"],
                            instance_type="created noise models")
        
        msg.end_output()


    # Private class methods

    def __add_depolarizing_error(
            self, 
            qubit: int, 
            columns: Series, 
            noise_model: NoiseModel
        ) -> None:
        """Helps create and add depolarizing error to noise model
        
        Helper method for the class method `create_noise_model`.

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
    

    def __add_readout_error(
            self, 
            qubit: int, 
            columns: Series, 
            noise_model: NoiseModel
    ) -> None:
        """Helps create and add readout error to noise model.

        Helper method for the class method `create_noise_model`.

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
                as follows: `column["attribute_name"]`, where 
                `"attribute_name"` is the column name in the dataframe.
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
        
        Helper method for the class method `create_noise_model`.

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
                as follows: `column["attribute_name"]`, where 
                `"attribute_name"` is the column name in the dataframe.
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
        """Checks if a `NoiseDataManager` class object is linked to this 
        `NoiseCreator` object.
           
        Raises:
            RuntimeError: If `NoiseDataManager` class object is not linked to
                `NoiseCreator` object.
        """
        if self.__noise_data is None:
            raise RuntimeError(
                ERRORS["error_not_linked"].format(
                    class_name=NoiseDataManager.__name__,
                    method_name=self.link_noise_data_manager.__name__))

    
    def __get_basis_gates(
            self, 
            noise_dataframe: pandas.DataFrame
    ) -> list[str]:
        """Helps to create and return a list of basis gates.

        Helper method for the class method `create_noise_model`.

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
                are accepted.For example: `["id", "ecr", "rz"]`
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

        Helper method for the class method `create_noise_model`.

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
    

    def __has_noise(
            self, 
            noise_model: NoiseModel
    ) -> str:
        """Checks if `NoiseModel` object has noise or is it noiseless.
        
        Args:
            noise_model (NoiseModel): Noise model that will be checked.

        Returns:
            str: 
                - "Yes" if it has noise.
                - "No" if it is noiseless.
        """
        if noise_model.is_ideal():
            return "No"
        else:
            return "Yes"
