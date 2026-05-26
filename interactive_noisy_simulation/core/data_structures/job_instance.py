# Standard library imports:
from dataclasses import dataclass

# Imports only used for type definition:
from .circuit_instance import CircuitInstance
from .noise_model_instance import NoiseModelInstance

@dataclass
class Job:
    """Class for storing an experiment job instance.
    
    Attributes:
        reference_key (str): Key by which the specific object is accessed 
            in other places of the `INS` app.
        circuit (QuantumCircuit): Selected circuit instance that will be
            executed by the specific job instance.
        shot_count (int): Amount of times that the selected circuit 
            will be executed as part of this job instance.
        hardware (str): Hardware option that will be used during 
            simulation (what part of computer hardware will be 
            responsible for the simulator circuit executions - `CPU` 
            or `GPU`).
        simulation_method (str): Simulation method that the simulator
            will use as part of running the specific job instance.
        noise_model_instance (NoiseModelInstance | None): Selected
            noise model instance that will be used during simulation. 
            In case of `None`, it will be a noiseless simulation.
        optimization_level (int | None): Optimization level for the 
            transpilation process (for preparing the selected circuit 
            to be run on a simulator with the selected noise model). 
            `None` will only be set if the simulation is noiseless.
    """
    reference_key: str
    circuit: CircuitInstance
    shot_count: int
    hardware: str
    simulation_method: str
    noise_model: NoiseModelInstance | None = None
    optimization_level: int | None = None
