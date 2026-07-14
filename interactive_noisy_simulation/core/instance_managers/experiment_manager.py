# Project-related imports:
from ..data_structures.experiment_instance import ExperimentInstance
from ..data_structures.job_instance import Job
from ..data_structures.instance_data import InstanceData
from ..data_structures.circuit_instance import CircuitInstance
from ..data_structures.noise_model_instance import NoiseModelInstance


class ExperimentManager:
    # =========================================================================
    # Table of Contents for ExperimentManager
    # =========================================================================
    # 1. Initialization (constructor method).
    # 2. Class properties.
    # 3. Experiment instance management - creating new instances, viewing and
    #    deleting existing ones.
    # 4. Job instance management for experiments - creating new instances, 
    #    viewing and deleting existing ones.
    # 5. Functionality related to the `Simulation` page - viewing specific
    #    experiment instances.
    # =========================================================================

    # =========================================================================
    # 1. Initialization (constructor method).
    # =========================================================================

    def __init__(self) -> None:
        """Constructor method."""
        self._experiments: dict[str, ExperimentInstance] = {}

    # =========================================================================
    # 2. Class properties.
    # =========================================================================

    @property
    def experiments(self) -> dict[str, ExperimentInstance]:
        """Returns a reference to data structure containing experiment 
        instances.
        
        Returns:
            dict[str, ExperimentInstance]: Dictionary with reference keys and 
                instances as its data.
        """
        return self._experiments
    

    # =========================================================================
    # 3. Experiment instance management
    # =========================================================================
    
    def create_instance(
        self, 
        reference_key: str
    ) -> None:
        """Creates new experiment instance.

        Args:
            reference_key (str): Reference key that will be set for the newly
                created instance.
        """
        new_instance = ExperimentInstance(
            reference_key=reference_key)
        self._experiments[reference_key] = new_instance


    def get_instance_data(self) -> InstanceData | None:
        """Returns data about currently created experiment instances.

        Returned information includes:
        - Reference key for the current instance;
        - Job count within experiment;
        - Job completion progress;
        - Experiment completion status.

        Returns:
            InstanceData: Dataclasss for displayable instance data.
                If there is no data to be displayed, the function returns
                nothing (`None`).
        """
        if self._experiments:
            columns = [
                "Reference key", "Job count", "Job progress", 
                "Completion status"
            ]
            rows = [
                [instance.reference_key, instance.job_count,
                 instance.job_progress, instance.status]
                for instance in self._experiments.values()
            ]
            actions = ["view", "delete"]
        
            return InstanceData(columns=columns,
                                rows=rows,
                                actions=actions)


    def remove_instance(
        self, 
        reference_key: str
    ) -> None:
        """Removes existing experiment instance based on its reference key.

        Args:
            reference_key (str): Reference key of existing deletable 
                experiment instance.
        """
        del self._experiments[reference_key]


    # =========================================================================
    # 4. Job instance management for experiments
    # =========================================================================

    def create_job(
        self,
        experiment_reference_key: str,
        job_reference_key: str,
        circuit_instance: CircuitInstance,
        noise_model_instance: NoiseModelInstance | None,
        shot_count: int,
        hardware: str,
        simulation_method: str,
        optimization_level: int | None
    ) -> None:
        """Creates a new job instance and adds it to a specific experiment 
        instance.

        Exposed function to `Python Eel` for use with JavaScript.

        Args:
            experiment_reference_key (str): Reference key of experiment 
                instance for which the new job instance will be created.
            job_reference_key (str): Reference key that will be set for
                the newly created job instance.
            circuit_instance (CircuitInstance): Selected circuit instance 
                that the job will execute.
            noise_model_instance (NoiseModelInstance | None): Selected
                noise model instance that will be used during simulation. 
                In case of `None`, it will be a noiseless simulation.
            shot_count (int): Amount of times that the selected circuit 
                will be executed as part of this job instance.
            hardware (str): Hardware option that will be used during 
                simulation (what part of computer hardware will be 
                responsible for the simulator circuit executions - `CPU` 
                or `GPU`).
            simulation_method (str): Simulation method that the simulator
                will use as part of running the specific job instance.
            optimization_level (int | None): Optimization level for the 
                transpilation process (for preparing the selected circuit 
                to be run on a simulator with the selected noise model). 
                `None` will only be set if the simulation is noiseless.
        """
        new_job = Job(
            reference_key=job_reference_key,
            circuit=circuit_instance,
            noise_model=noise_model_instance,
            shot_count=shot_count,
            hardware=hardware,
            simulation_method=simulation_method,
            optimization_level=optimization_level)
         
        experiment = self._experiments[experiment_reference_key]
        experiment.add_job(new_job)
    

    def remove_job(
        self,
        experiment_reference_key: str,
        job_reference_key: str
    ) -> None:
        """Removes job from a specific experiment instance.
        
        Args:
            experiment_reference_key (str): Reference key of experiment
                instance whose job will be deleted.
            job_reference_key (str): Deletable job instance reference key.
        """
        experiment = self._experiments[experiment_reference_key]
        experiment.remove_job(job_reference_key)


    def get_job_simple_data(
        self,
        experiment_reference_key: str,
    ) -> InstanceData | None:
        """Obtains and returns simple data about existing job instances
        for a specific experiment instance.
        
        Args:
            experiment_reference_key (str): Reference key of experiment
                instance whose job data will be compiled and returned.

        Returns:
            InstanceData: Data structure containing simple data about jobs
                from a specific experiment instance. `None` is returned
                if the specific experiment instance has no job instances.
        """
        experiment = self._experiments[experiment_reference_key]
        if experiment.jobs:
            columns = [
                "Reference key", "Completion status"
            ]
            rows = [
                [job.reference_key, job.status]
                for job in experiment.jobs.values()
            ]
        
            return InstanceData(columns=columns,
                                rows=rows)


    def get_job_detailed_data(
        self,
        experiment_reference_key: str,
        job_reference_key: str
    ) -> dict:
        """Obtains and returns detailed data about a specific existing 
        job instances within a specific experiment instance.
        
        Args:
            experiment_reference_key (str): Reference key of experiment
                instance whose job data will be compiled and returned.
            job_reference_key (str): Reference key of job instance whose
                detailed data will be compiled and returned.

        Returns:
            dict: Data structure containing detailed data about a specific
                job from a specific experiment instance.
        """
        experiment = self._experiments[experiment_reference_key]
        job = experiment.jobs[job_reference_key]

        detailed_data = {
            # Job instance data
            "reference_key": job.reference_key,
            "circuit": job.circuit.reference_key,
            # Noise-related settings
            "noise_model": job.noise_model.reference_key if job.noise_model
                           else "Noiseless simulation",
            "optimization_level": job.optimization_level if job.optimization_level is not None
                                  else "No optimization for noiseless simulation",
            # Simulator settings
            "shot_count": job.shot_count,
            "hardware": job.hardware,
            "simulation_method": job.simulation_method,
            # Job progress metrics,
            "completed_shots": job.completed_shots,
            "remaining_shots": job.remaining_shots,
            # Job results:
            "current_result_counts": job.result_counts if job.result_counts
                                     else "No result counts available yet"
        }
        
        return detailed_data


    # =========================================================================
    # 5. Functionality related to the `Simulation` page
    # =========================================================================
    
    def get_queueable_instance_data(self) -> InstanceData | None:
        """Returns data about currently created experiment instances.

        Returned information includes:
        - Reference key for the current instance;
        - Job completion progress;
        - Experiment completion status.

        Returns:
            InstanceData: Dataclasss for displayable instance data.
                If there is no data to be displayed, the function returns
                nothing (`None`).
        """
        if self._experiments:
            rows = [
                [instance.reference_key, instance.job_progress, 
                 instance.status]
                for instance in self._experiments.values()
                if not instance.is_queued
            ]
            # If all existing experiments are not eligible for the experiment
            # execution queue.
            if not rows: 
                return None

            columns = [
                "Reference key", "Job progress", "Completion status"
            ]
            actions = ["add"]
        
            return InstanceData(columns=columns,
                                rows=rows,
                                actions=actions)
