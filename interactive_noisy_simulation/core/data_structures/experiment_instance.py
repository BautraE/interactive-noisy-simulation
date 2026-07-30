# Standard library imports:
from dataclasses import dataclass, field

# Imports only used for type definition:
from .job_instance import Job


@dataclass
class ExperimentInstance:
    """Class for storing an experiment instance.
    
    Attributes:
        reference_key (str): Key by which the specific object is accessed 
            in other places of the INS app.
        jobs (dict[str, JobInstance]): Jobs associated with an experiment
            instance.
        is_queued (bool): Whether or not this experiment is in a queue to
            be executed.
        is_executing (bool): Whether or not this experiment is currently being
            executed.
    """
    reference_key: str
    jobs: dict[str, Job] = field(default_factory=dict)
    is_queued: bool = False
    is_executing: bool = False


    @property
    def job_count(self) -> int:
        """Returns number of jobs currently associated with the specific
        experiment instance.
        
        Returns:
            int: Number of jobs
        """
        return len(self.jobs)
    

    @property
    def complete_jobs(self) -> int:
        """Returns number of complete jobs that belong to this experiment.
        
        Returns:
            int: Number of complete jobs.
        """
        num_complete_jobs = 0
        for job in self.jobs.values():
            if job.is_complete:
                num_complete_jobs += 1
        
        return num_complete_jobs
    

    @property
    def incomplete_jobs(self) -> int:
        """Returns number of incomplete jobs within the experiment instance.
        
        Returns:
            int: Number of incomplete jobs.
        """
        return self.job_count - self.complete_jobs
    

    @property
    def completion_percentage(self) -> float:
        """Returns completion percentage based on completed shots, compared to
        total number of shots (across all jobs within the experiment).
        
        Returns:
            float: Experiment completion percentage.
        """
        percentage = (self.total_completed_shots / self.total_shots) * 100.0
        return round(percentage, 2)
    

    @property
    def total_completed_shots(self) -> int:
        """Returns number of total completed shots across all jobs within the
        experiment instance.
        
        Returns:
            int: Number of total completed shots.
        """
        shots = 0
        for job in self.jobs.values():
            shots += job.completed_shots
        return shots


    @property
    def total_shots(self) -> int:
        """Returns number of total shots across all jobs within the experiment
        instance.
        
        Returns:
            int: Number of total shots.
        """
        shots = 0
        for job in self.jobs.values():
            shots += job.shot_count
        return shots

    
    @property
    def job_progress(self) -> str:
        """Returns job progress if at least one job exists within the
        specific experiment instance.

        If there are no jobs within the experiment, a message stating
        this will be displayed instead.

        Returns:
            str: Job progress text (`No jobs` or e.g. `1/5`).
        """
        total_jobs = self.job_count

        if total_jobs == 0:
            return "No jobs"
        else:
            return f"{self.complete_jobs}/{total_jobs}"


    @property
    def status(self) -> str:
        """Returns status of experiment based on completed jobs.
        
        Returns:
            str: Status message.
        """
        total_jobs = self.job_count
        complete_jobs = self.complete_jobs

        if total_jobs == 0:
            return "no jobs"
        elif complete_jobs == 0:
            return "pending"
        elif complete_jobs == total_jobs:
            return "completed"
        else:
            return "partial"
        
    
    @property
    def execution_status(self) -> str:
        """Returns execution status of experiment.

        This is used by the experiment execution queue.
        
        Returns:
            str: Status message.
        """
        if self.job_count == 0:
            return "no jobs"
        elif self.is_executing:
            return "in progress"
        elif self.job_count == self.complete_jobs:
            return "completed"
        else:
            return "queued"


    def add_job(
        self,
        job: Job
    ) -> None:
        """Adds a new job to the specific experiment instance.
        
        Args:
            job (Job): New Job instance.
        """
        self.jobs[job.reference_key] = job


    def remove_job(
        self,
        reference_key: str
    ) -> None:
        """Removes job from the specific experiment instance based on
        job instance reference key.
        
        Args:
            reference_key (str): Deletable job instance reference key.
        """
        del self.jobs[reference_key]
