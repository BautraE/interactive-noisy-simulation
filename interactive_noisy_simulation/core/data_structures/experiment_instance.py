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
    """
    reference_key: str
    jobs: dict[str, Job] = field(default_factory=dict)


    @property
    def job_count(self) -> int:
        """Returns number of jobs currently associated with the specific
        experiment instance.
        
        Returns:
            int: Number of jobs
        """
        return len(self.jobs)
    

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
