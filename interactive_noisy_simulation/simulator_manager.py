# Standard library imports:
import warnings

#Third party imports:
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.jobs.aerjob import AerJob
from qiskit import QuantumCircuit

# Local project imports:
from .messages._message_manager import MessageManager
from .noise_creator import NoiseCreator
from .data._data import (
    ERRORS, MESSAGES, OUTPUT_HEADINGS
)


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

    ####################################################################
    # NEW DEFINITIONS:
    def testt(self):
        for simulator_key, instance in self.__simulators.items():
            simulator = instance["simulator"]
            print(simulator.operation_names)

    def view_simulators(self) -> None:
        msg = self.__message_manager
        msg.create_output(OUTPUT_HEADINGS["simulator_instances"])

        # Perhaps this needs a check if NoiseCreator was linked
        # If not, it will just display a different message:
        # something along the lines of "link so and so first"

        if self.__simulators:
            for simulator_key, instance in self.__simulators.items():
                msg.add_message(simulator_key)
                simulator = instance["simulator"]
                msg.add_message(f"max qubits: {simulator.num_qubits}")
                nm_key = instance["noise_model_source"]
                msg.add_message(nm_key)
                if self.__check_noise_model_instance_key(nm_key,
                                                         raise_error=False):
                    msg.add_message("Available")
                else: msg.add_message("Removed")
                msg.add_message("-----------------------------------------")
        else:
            msg.add_message("There are currently no created noise models!")
        
        msg.end_output()
    
    # TEMPORARY DEFINITIONS:
    def __check_simulator_instance_key(
            self, 
            reference_key: str,
            raise_error: bool = True
    ) -> None:        
        if reference_key in self.__simulators:
            return True
        
        elif raise_error:
            raise KeyError(
                    ERRORS["no_key_simulator_instance"].format(
                        reference_key=reference_key))
        else:
            return False
    

    def __check_noise_model_instance_key(
            self, 
            reference_key: str,
            raise_error: bool = True
    ) -> None:        
        if reference_key in self.__noise_models:
            return True
        
        elif raise_error:
            raise KeyError(
                    ERRORS["no_key_noise_model_instance"].format(
                        reference_key=reference_key))
        else:
            return False

    ####################################################################

    # Public class methods
    
    def create_simulator(
            self, 
            noise_model_reference_key: str, 
            simulator_reference_key: str
    ) -> None:
        """Creates an AerSimulator simulator instance from specific 
           noise model.

        The created simulators can be then used to run circuits with
        the method "run_simulator".
        
        Args:
            noise_model_reference_key (str): Reference key to access
                noise model that will be used in the creation of the
                simulator instance.
            simulator_reference_key (str): Reference key for the
                created simulator that will be used to access it.
        """
        msg = self.__message_manager
        msg.create_output(OUTPUT_HEADINGS["creating_simulator"])

        try:
            self.__check_noise_creator_link()
            self.__check_noise_model_instance_key(noise_model_reference_key)
        except Exception:
            msg.add_traceback()
            return
        
        new_instance = {}
        new_instance["noise_model_source"] = noise_model_reference_key

        noise_model_instance = self.__noise_models[noise_model_reference_key]
        
        new_instance["simulator"] = AerSimulator(
            coupling_map=noise_model_instance["coupling_map"], 
            noise_model=noise_model_instance["noise_model"])
        
        self.__simulators[simulator_reference_key] = new_instance
        
        msg.add_message(
            MESSAGES["created_simulator"],
            reference_key=simulator_reference_key)
        msg.end_output()


    def link_noise_creator(self, noise_creator: NoiseCreator) -> None:
        """Links a NoiseCreator class object to gain access to 
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
            OUTPUT_HEADINGS["remove_simulator_instance"].format(
                reference_key=reference_key))
        
        try:
            self.__check_simulator_instance_key(reference_key)
        except Exception:
            msg.add_traceback()
            return

        del self.__simulators[reference_key]
        msg.add_message(
            MESSAGES["deleted_simulator_instance"],
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
            self.__check_noise_creator_link()
            self.__check_simulator_instance_key(simulator_reference_key)
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


    # Private class methods

    def __check_noise_creator_link(self) -> None:
        """Checks if a NoiseCreator class object is linked to this 
           SimulatorManager object."""
        if self.__noise_models is None:
            raise RuntimeError(
                ERRORS["error_not_linked"].format(
                    class_name=NoiseCreator.__name__,
                    method_name=self.link_noise_creator.__name__))
