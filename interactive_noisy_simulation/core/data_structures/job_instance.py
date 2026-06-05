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
        completed_shots (int): Amount of times that the selected circuit
            has been already executed. This acts as a job proggess metric.
    """
    reference_key: str
    circuit: CircuitInstance
    shot_count: int
    hardware: str
    simulation_method: str
    noise_model: NoiseModelInstance | None = None
    optimization_level: int | None = None
    completed_shots: int = 0


    @property
    def status(self) -> str:
        """Returns status of job based on completed shots.
        
        Returns:
            str: Status message.
        """
        if self.completed_shots == 0:
            return "Pending"
        elif self.completed_shots == self.shot_count:
            return "Completed"
        else:
            return "Partial"


    @property
    def is_complete(self) -> bool:
        """Returns job completion state for internal INS functionality
        in the form of a boolean value (`True` or `False`), based on 
        completed shots.
        
        Returns:
            bool: Whether or not the job is completed (if all shots are 
            completed).
        """
        if self.shot_count == self.completed_shots:
            return True
        else:
            return False


    @property
    def remaining_shots(self) -> int:
        """Returns the number of remaining shots that the job has left to 
        complete.
        
        Returns:
            int: Number of remaining shots.
        """
        return self.shot_count - self.completed_shots
