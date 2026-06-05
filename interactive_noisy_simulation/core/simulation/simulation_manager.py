# Project-related imports:
from ..data_structures.instance_data import InstanceData

# Imports only used for type definition:
from ..data_structures.experiment_instance import ExperimentInstance


class SimulationManager:
    def __init__(self) -> None:
        """Constructor method."""
        self._simulation_queue: list[ExperimentInstance] = []


    @property
    def queue_lenght(self) -> int:
        """Returns number of queued experiment instances.
        
        Returns:
            int: number of queued experiment instances.
        """
        return len(self._simulation_queue)
    

    @property
    def total_queued_jobs(self) -> int:
        """Returns number of jobs across all queued experiment instances.
        
        Returns:
            int: Number of jobs across all queued experiment instances.
        """
        num_queued_jobs = 0
        for experiment in self._simulation_queue:
            num_queued_jobs += experiment.job_count
        
        return num_queued_jobs


    @property
    def total_queued_incomplete_jobs(self) -> int:
        """Returns number of incomplete jobs across all queued experiment
        instances.
        
        Returns:
            int: Number of incomplete jobs across all queued experiment
                instances.
        """
        num_queued_incomplete_jobs = 0
        for experiment in self._simulation_queue:
            num_queued_incomplete_jobs = experiment.complete_jobs
        
        return num_queued_incomplete_jobs

    
    # Queue management:

    def add_experiment_to_queue(
        self,
        experiment_instance: ExperimentInstance
    ) -> None:
        """Adds specific experiment instance to the execution queue.

        Args:
            experiment_instance (ExperimentInstance): Instance that will be 
                added to the queue.
        """
        self._simulation_queue.append(experiment_instance)


    def remove_experiment_from_queue(
        self,
        experiment_instance: ExperimentInstance
    ) -> None:
        """Removes specific experiment instance from the execution queue.

        Args:
            experiment_instance (ExperimentInstance): Instance that will be 
                removed from the queue.
        """
        self._simulation_queue.remove(experiment_instance)


    def get_queued_experiment_data(self) -> InstanceData | None:
        """Returns data about currently queued experiment instances.

        Returned information includes:
        - Reference key for the current instance;
        - Job completion progress;
        - Experiment execution status.

        Returns:
            InstanceData: Dataclasss for displayable instance data.
                If there is no data to be displayed, the function returns
                nothing (`None`).
        """
        if self._simulation_queue:
            columns = [
                "Reference key", "Job progress", 
                "Execution status"
            ]
            rows = [
                [experiment.reference_key, experiment.job_progress, 
                 experiment.status]
                for experiment in self._simulation_queue
            ]
            actions = ["remove"]

            return InstanceData(columns=columns,
                                rows=rows,
                                actions=actions)
