# Standard library imports:
import warnings

#Third party imports:
from qiskit import transpile
from qiskit_aer import AerSimulator

# Local project imports:
from .messages._message_manager import MessageManager
from .noise_creator import NoiseCreator
from .utils.key_availability import (
    block_key, unblock_key
)
from .utils.validators import (
    check_instance_key, validate_instance_name
)
from .data._data import (
    ERRORS, MESSAGES, OUTPUT_HEADINGS
)

# Imports only used for type definition:
from qiskit_aer.jobs.aerjob import AerJob
from qiskit import QuantumCircuit


class SimulatorManager:

    def __init__(self) -> None:
        """Constructor method."""
        self.__message_manager: MessageManager = MessageManager()
        msg = self.__message_manager
        msg.create_output(OUTPUT_HEADINGS["creating_new_object"].format(
            class_name=self.__class__.__name__))

        self.__simulators = {}
        self.__noise_models = None

        msg.add_message(MESSAGES["created_new_object"], 
                        class_name=self.__class__.__name__)
        msg.end_output()


    # Public class methods
    
    def create_simulator(
            self, 
            noise_model_reference_key: str, 
            simulator_reference_key: str
    ) -> None:
        """Creates an `AerSimulator` simulator instance from specific 
        noise model.

        The created simulators can be then used to run circuits with
        the method `run_simulator`.
        
        Args:
            noise_model_reference_key (str): Reference key to access
                noise model that will be used in the creation of the
                simulator instance.
            simulator_reference_key (str): Reference key for the
                created simulator that will be used to access it.
        """
        msg = self.__message_manager
        msg.create_output(OUTPUT_HEADINGS["creating_simulator"].format(
            reference_key=noise_model_reference_key))
        
        try:
            self.__check_noise_creator_link()
            check_instance_key(reference_key=noise_model_reference_key,
                               should_exist=True, 
                               instances=self.__noise_models,
                               instance_type="noise model instance")
            check_instance_key(reference_key=simulator_reference_key,
                               should_exist=False, 
                               instances=self.__simulators,
                               instance_type="simulator instance")
        except Exception:
            msg.add_traceback()
            return
        
        simulator_reference_key = validate_instance_name(
            simulator_reference_key,
            msg)

        new_instance = {}
        new_instance["noise_model_source"] = noise_model_reference_key

        noise_model_instance = self.__noise_models[noise_model_reference_key]
        
        new_instance["simulator"] = AerSimulator(
            coupling_map=noise_model_instance["coupling_map"], 
            noise_model=noise_model_instance["noise_model"])
        
        self.__simulators[simulator_reference_key] = new_instance

        # Blocks noise model instance key until this simulator instance
        # gets deleted (simulator has reference to used noise model key)
        block_key(key=noise_model_reference_key,
                  instance_type="noise_models",
                  blocker_key=simulator_reference_key)
        
        msg.add_message(
            MESSAGES["created_instance"],
            instance_type="Simulator",
            reference_key=simulator_reference_key)
        msg.end_output()


    def link_noise_creator(self, noise_creator: NoiseCreator) -> None:
        """Links a `NoiseCreator` class object to gain access to 
        created noise models."""
        msg = self.__message_manager
        msg.create_output(OUTPUT_HEADINGS["linking_object"].format(
            linked_class=NoiseCreator.__name__,
            this_class=self.__class__.__name__))
        
        self.__noise_models = noise_creator.noise_models
        
        msg.add_message(MESSAGES["linking_success"])
        msg.end_output()


    def remove_simulator_instance(self, reference_key: str) -> None:
        """Removes existing simulator instance by reference key.
        
        Args:
            reference_key (str): Key of the removable simulator
                instance.
        """
        msg = self.__message_manager
        msg.create_output(
            OUTPUT_HEADINGS["remove_instance"].format(
                instance_type="simulator instance",
                reference_key=reference_key))
        
        try:
            # Is there even an instance to delete with given key
            check_instance_key(reference_key=reference_key,
                               should_exist=True, 
                               instances=self.__simulators,
                               instance_type="simulator instance")
        except Exception:
            msg.add_traceback()
            return

        # Unblocking referenced noise data key
        instance = self.__simulators[reference_key]
        noise_model_reference_key = instance["noise_model_source"]
        unblock_key(key=noise_model_reference_key,
                    instance_type="noise_models")

        del self.__simulators[reference_key]

        msg.add_message(
            MESSAGES["deleted_instance"],
            instance_type="simulator instance",
            reference_key=reference_key)
        msg.end_output()


    def run_simulator(
            self,
            simulator_reference_key: str,
            circuit: QuantumCircuit, 
            optimization: int, 
            shots: int
    ) -> AerJob:
        """Runs a quantum circuit on a created simulator.

        Transpiles the given circuit with the specified optimization
        level and proceeds to execute it on the selected simulator with
        a specified amount of shots.

        Args:
            simulator_reference_key (str): Reference key for the selected
                simulator instance to be used.
            circuit (QuantumCircuit): the quantum circuit that will be 
                executed.
            optimization (int): the optimization level that will be used
                during the transpilation process of the given quantum 
                circuit. Possible levels: 0-3
            shots (int): the number of shots (circuit execution times).

        Returns:
            AerJob: Job of the simulator execution, from which you can
                extract the result counts and other data associated with the
                completed job.
        """
        msg = self.__message_manager
        msg.create_output(OUTPUT_HEADINGS["execute_simulator"].format(
            reference_key=simulator_reference_key))
        
        try:
            self.__validate_optimization_level(optimization)
            check_instance_key(reference_key=simulator_reference_key,
                               should_exist=True, 
                               instances=self.__simulators,
                               instance_type="simulator instance")
        except Exception:
            msg.add_traceback()
            return

        msg.add_message(MESSAGES["transpiling_circuit"],
                        optimization_level=optimization)

        # While doing everything correctly, there seems to be an error 
        # message regarding providing the coupling_map and basis_bates 
        # together with backend. I could not currently find a solution 
        # as to how it can be removed, which is why this code bit is 
        # here - to remove it.
        with warnings.catch_warnings():
            warnings.filterwarnings(
                action="ignore", 
                message=f"Providing `coupling_map` and/or `basis_gates` "
                        f"along with `backend` is not recommended"
            )

            instance = self.__simulators[simulator_reference_key]
            simulator = instance["simulator"]

            transpiled_circuit = transpile(
                circuits=circuit, 
                backend=simulator, 
                coupling_map=simulator.coupling_map, 
                optimization_level=optimization)
        
        msg.add_message(MESSAGES["executing_simulator"],
                        reference_key=simulator_reference_key,
                        qubit_count=str(circuit.num_qubits),
                        shots=str(shots))
        
        result_job = simulator.run(
            circuits=transpiled_circuit, 
            shots = shots)

        msg.add_message(MESSAGES["execution_complete"])
        msg.end_output()
        return result_job
    
    
    def view_simulators(self) -> None:
        """Displays all currently available simulator instances.

        If no instances are available, method simply displays a
        message that states this fact.
        The visual output from this method is placed inside of the
        default "message" content container.

        Displayed information includes:
        - Reference key for the current instance;
        - Maximum circuit qubit count that the simulator instance 
          supports;
        - Reference key for the source noise model instance that was
          used in the making of the current simulator instance;
        - Availability of the source noise model instance (Available
          or Removed).
        """
        msg = self.__message_manager
        msg.create_output(OUTPUT_HEADINGS["created_instances"].format(
            instance_type="simulator instances"))
        msg.generic_content_container("Simulator instances:")

        if self.__simulators:
            
            msg.add_generic_table()
            msg.add_generic_table_row(
                row_content=["Reference key", "Max qubit count",
                             "Has noise", "Source noise model", 
                             "Noise model availability"],
                row_type="th")

            for simulator_key, instance in self.__simulators.items():
                
                simulator = instance["simulator"]
                has_noise = self.__has_noise(simulator)
                # At some point some research would be good as for what
                # exactly does this number mean, because it differs from
                # the max amount of qubits in the noise model.
                qubit_count = str(simulator.num_qubits)

                noise_model_key = instance["noise_model_source"]

                if check_instance_key(reference_key=noise_model_key,
                                      should_exist=True, 
                                      instances=self.__noise_models,
                                      instance_type="noise model instance",
                                      raise_error=False):
                    availability = "Available"
                else: 
                    availability = "Removed"
                noise_model_availability = msg.style_availability_status(
                    availability)
                
                msg.add_generic_table_row(
                    row_content=[simulator_key, qubit_count, has_noise,
                                 noise_model_key, noise_model_availability],
                    row_type="td")
        else:
            msg.add_message(MESSAGES["no_instances"],
                            instance_type="created simulator instances")
        
        msg.end_output()


    # Private class methods

    def __check_noise_creator_link(self) -> None:
        """Checks if a `NoiseCreator` class object is linked to this 
        `SimulatorManager` object.

        Raises:
            RuntimeError: If `NoiseCreator` class object is not linked
                to this `SimulatorManager` object.   
        """
        if self.__noise_models is None:
            raise RuntimeError(
                ERRORS["error_not_linked"].format(
                    class_name=NoiseCreator.__name__,
                    method_name=self.link_noise_creator.__name__))


    def __has_noise(
            self, 
            simulator: AerSimulator
    ) -> str:
        """Checks if `AerSimulator` object has noise or is it noiseless.
        
        Args:
            noise_model (NoiseModel): Noise model that will be checked.

        Returns:
            str: 
                - "Yes" if it has noise.
                - "No" if it is noiseless.
        """
        noise_model = simulator.options.noise_model
        if noise_model.is_ideal():
            return "No"
        else:
            return "Yes"
    
    
    def __validate_optimization_level(
            self, 
            optimization_level: int
    ) -> None:
        """Checks if the given transpilation optimization level 
        is valid."""
        if optimization_level < 0 or optimization_level > 3:
            raise ValueError(ERRORS["invalid_optimization_level"].format(
                    optimization_level=optimization_level))
