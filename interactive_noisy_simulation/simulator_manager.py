# Standard library imports:
import json, warnings
from importlib import resources

#Third party imports:
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.jobs.aerjob import AerJob

# Local project imports:
from . import data
from .messages._message_manager import MessageManager
from .noise_creator import NoiseCreator


with (resources.files(data) / "messages.json").open("r", encoding="utf8") as file:
    MESSAGES = json.load(file)


class SimulatorManager:

    def __init__(self) -> None:
        """Constructor method """
        self.__message_manager: MessageManager = MessageManager()
        msg = self.__message_manager
        msg.create_output(MESSAGES["creating_new_object"].format(class_name=self.__class__.__name__))

        self.__simulator = None
        self.__noise_model = None

        msg.add_message(MESSAGES["created_new_object"].format(class_name=self.__class__.__name__))
        msg.end_output()


    # Public class methods

    def create_simulator(self) -> None:
        """Creates a AerSimulator object from available data """
        msg = self.__message_manager
        msg.create_output(MESSAGES["creating_simulator"])

        if self.__noise_model is None:
            raise RuntimeError(
                f"{MESSAGES["error_not_linked"].format(class_name=NoiseCreator.__name__,
                                                       method_name=self.link_noise_creator.__name__)}")

        self.__simulator = AerSimulator(coupling_map=self.__noise_model["coupling_map"], 
                                        noise_model=self.__noise_model["noise_model"])
        
        msg.add_message(MESSAGES["created_simulator"])
        msg.end_output()


    def link_noise_creator(self, noise_creator: NoiseCreator) -> None:
        """Links a NoiseCreator class object to gain access to created noise models """
        msg = self.__message_manager
        msg.create_output(MESSAGES["linking_object"].format(linked_class=NoiseCreator.__name__,
                                                            this_class=self.__class__.__name__))
        self.__noise_model = noise_creator.noise_model
        msg.add_message(MESSAGES["linking_success"])
        msg.end_output()


    def run_simulator(self, circuit, optimization, shots) -> AerJob:
        """Runs a created simulator

        Transpiles the given circuit

        Args:
            circuit: the quantum circuit that will be executed.
            optimization: the optimization level that will be used during
                the transpilation process of the given quantum circuit.
            shots: the number of shots (circuit execution times).

        Returns:
            result_job: Job of the simulator execution, from which you can
                extract the result counts and other data associated with the
                completed job.
        """
        msg = self.__message_manager
        msg.create_output(MESSAGES["execute_simulator"])
        self.__check_simulator()

        # While doing everything correctly, there seems to be an error message
        # regarding providing the coupling_map and basis_bates together with
        # backend. I could not currently find a solution as to how it can be removed,
        # which is why this code bit is here - to remove it.
        with warnings.catch_warnings():
            warnings.filterwarnings(
                action="ignore", 
                message="Providing `coupling_map` and/or `basis_gates` along with `backend` is not recommended"
            )
            transpiled_circuit = transpile(circuit, 
                                           backend=self.__simulator, 
                                           coupling_map=self.__noise_model["coupling_map"], 
                                           optimization_level=optimization)
        
        result_job = self.__simulator.run(transpiled_circuit, shots = shots)

        msg.add_message(MESSAGES["execution_complete"])
        msg.end_output()
        return result_job


    # Private class methods

    def __check_simulator(self) -> None:
        """Checks if a simulator exists in the current object of SimulatorManager """
        if self.__simulator is None:
            raise RuntimeError(f"{MESSAGES["error_no_simulator"]}")
