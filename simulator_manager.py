# Used for functionality purposes:
from qiskit_aer import AerSimulator
from qiskit import transpile
# Used for referencing types:
from qiskit_aer.jobs.aerjob import AerJob
from noise_creator import NoiseCreator

class SimulatorManager:
    def __init__(self) -> None:
        print(f"----- Creating {SimulatorManager.__name__} object -----")
        self.__simulator = None
        self.__noise_model = None
        print(f"{SimulatorManager.__name__} class object has been created successfully!\n")

    def link_noise_creator(self, noise_creator: NoiseCreator) -> None:
        self.__noise_model = noise_creator.noise_model

    def create_simulator(self) -> None:
        self.__simulator = AerSimulator(coupling_map=self.__noise_model["coupling_map"], noise_model=self.__noise_model["noise_model"])

    def run_simulator(self, circuit, optimization, shots) -> AerJob:
        transpiled_circuit = transpile(circuit, backend=self.__simulator, coupling_map=self.__noise_model["coupling_map"], optimization_level=optimization)
        result_job = self.__simulator.run(transpiled_circuit, shots = shots)
        return result_job
