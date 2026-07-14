# Standard library imports:
import warnings

#Third party imports:
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit.transpiler.exceptions import TranspilerError # For bug workaround

# Project-related imports:
from ..data_structures.instance_data import InstanceData
from ...exceptions import SimulationError
from ...project_variables import ERROR_MESSAGES

# Imports only used for type definition:
from ..data_structures.experiment_instance import ExperimentInstance
from ..data_structures.job_instance import Job
from qiskit import QuantumCircuit
from typing import Callable


SHOT_BATCH_SIZE = 1000
# Related to Qiskit transpile bug: 'HighLevelSynthesis is unable to synthesize "measure"'
# It sometimes fails to transpile the circuit and returns this error if the 
# optimization level for the transpilation process is set above 0.
# A hacky solution for it would be to attempt the transpilation process
# multiple times, ignoring the exception, until it finally works.
MAX_TRANSPILATION_ATTEMPTS = 100


class SimulationManager:
    # =========================================================================
    # Table of Contents for SimulationManager
    # =========================================================================
    # 1. Initialization (constructor method).
    # 2. Class properties.
    # 3. Queue management.
    # 4. Queue execution.
    # =========================================================================

    # =========================================================================
    # 1. Initialization (constructor method).
    # =========================================================================

    def __init__(self) -> None:
        """Constructor method."""
        self._simulation_queue: list[ExperimentInstance] = []
        self.is_executing: bool = False

    # =========================================================================
    # 2. Class properties.
    # =========================================================================

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
            num_queued_incomplete_jobs += experiment.incomplete_jobs
        
        return num_queued_incomplete_jobs

    
    # =========================================================================
    # 3. Queue management.
    # =========================================================================

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
                 experiment.execution_status]
                for experiment in self._simulation_queue
            ]
            actions = ["remove"]

            return InstanceData(columns=columns,
                                rows=rows,
                                actions=actions)
        

    # =========================================================================
    # 4. Queue execution.
    # =========================================================================

    def execute_queue(
        self,
        ui_refresh_callback: Callable[[], None],
        progress_callback: Callable[[float, float, float], None]
    ) -> None:
        """Begins executing the experiment queue in order.

        Args:
            ui_refresh_callback (Callable[[], None]): Callback function for
                updating content on the page `Simulation`.
            progress_callback (Callable[[float, float, float], None]): Callback
                function for updating queue execution progress bars with new
                completion percentage values.
        """
        for experiment in self._simulation_queue:
            experiment.is_executing = True
            # Update that experiment is being executed
            ui_refresh_callback()
            try:
                for job in experiment.jobs.values():
                    # Displays initial job progress
                    self.update_queue_execution_progress(
                        progress_callback, 
                        running_experiment=experiment, 
                        running_job=job)

                    simulator = self._get_simulator_instance(job_instance=job)
                    circuit = self._get_transpiled_circuit(job_instance=job, 
                                                           simulator=simulator)
                    
                    self._run_job(job=job, 
                                  simulator=simulator, 
                                  transpiled_circuit=circuit, 
                                  progress_callback=progress_callback, 
                                  experiment=experiment)
                    # Update that job is complete
                    ui_refresh_callback()
            finally:
                experiment.is_executing = False
                # Update that experiment is complete
                ui_refresh_callback()


    def _run_job(
        self,
        job: Job,
        simulator: AerSimulator,
        transpiled_circuit: QuantumCircuit,
        progress_callback: Callable[[float, float, float], None],
        experiment: ExperimentInstance
    ) -> None:
        """Executes current job instance in batches of shots, progressively 
        adding up to the job result.

        Shot batch is determined by the `SHOT_BATCH_SIZE` constant.

        Args:
            job (Job): Current job instance that will be executed.
            simulator (AerSimulator): Simulator instance that the current
                job will be using.
            transpiled_circuit (QuantumCircuit): Transpiled circuit that the 
                simulator will be running.
            progress_callback (Callable[[float, float, float], None]): Callback
                function for updating queue execution progress bars with new
                completion percentage values.
            experiment (ExperimentInstance): Current experiment instance being
                executed. (Only used as `progress_callback` argument)
        """
        while not job.is_complete:
            shot_batch = min(SHOT_BATCH_SIZE, job.remaining_shots)
            
            aer_job = simulator.run(circuits=transpiled_circuit, 
                                    shots=shot_batch)
            
            job.add_results(new_results=aer_job.result().get_counts())

            self.update_queue_execution_progress(progress_callback, 
                                                 running_experiment=experiment, 
                                                 running_job=job)


    def _get_simulator_instance(
        self,
        job_instance: Job
    ) -> AerSimulator:
        """Creates and returns a simulator instance that the current job
        instance will be using.

        Args:
            job_instance (Job): Current job instance that will be
                executed.

        Returns:
            AerSimulator: Created simulator instance that the current job
                instance will be using.
        """
        # Noisy simulation requires specific AerSimulator 
        # configuration.
        if job_instance.noise_model:
            return AerSimulator(
                coupling_map=job_instance.noise_model.coupling_map,
                noise_model=job_instance.noise_model.noise_model)
        # Noiseless simulation is just with the default AerSimulator.
        else:
            return AerSimulator()


    def _get_transpiled_circuit(
        self,
        job_instance: Job,
        simulator: AerSimulator
    ) -> QuantumCircuit:
        """Creates and returns a transpiled circuit that can be run on
        the specific simulator instance.

        Args:
            job_instance (Job): Current job instance that will be
                executed.
            simulator (AerSimulator): Simulator instance that the current
                job will be using.

        Returns:
            QuantumCircuit: Transpiled circuit that the simulator will be
                running.
        """
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

            # If there is no noise, optimization level is not allowed
            # to be set, thus, it should be set to 0 (INS default).
            optimization_level = job_instance.optimization_level or 0

            # Required in order to avoid the following exception:
            # "HighLevelSynthesis is unable to synthesize 'measure'"
            # Attempt loop for HighLevelSynthesis bug workaround:
            for _ in range(MAX_TRANSPILATION_ATTEMPTS):
                try:
                    return transpile(
                        circuits=job_instance.circuit.circuit,
                        backend=simulator,
                        coupling_map=simulator.coupling_map,
                        optimization_level=optimization_level)
                except TranspilerError: pass
            # Raises error if none of the set attempts were successful:
            raise SimulationError(ERROR_MESSAGES["sim_transpilation_bug"],
                                  transpilation_attempt_count=MAX_TRANSPILATION_ATTEMPTS)


    def update_queue_execution_progress(
        self,
        progress_callback: Callable[[float|str, float|str, float|str], None],
        running_experiment: ExperimentInstance | None = None,
        running_job: Job | None = None
    ) -> None:
        """Calculates new progress percentage values and calls progress 
        callback function to update all progress bars.

        If the running experiment and job are not given, progress will be calculated
        based on the currently created experiment queue. If there are no experiments
        in the queue, the progress callback function is called with `--` as arguments
        instead of actual percentage values to serve as placeholders.

        Args:
            progress_callback (Callable[[float|str, float|str, float|str], None]): 
                Callback function for updating queue execution progress bars with 
                new completion percentage values.
            running_experiment (ExperimentInstance | None): Experiment instance
                currently being executed. (Default: `None`)
            running_job (Job | None): Job instance currently being executed.
                (Default: `None`)
        """
        # If simulation queue is empty, there are no percentage values to calculate.
        if not self._simulation_queue:
            progress_callback("--", "--", "--")
        else:
            # Calculates total complete and in general shots.
            total_shots = 0
            total_complete_shots = 0
            for experiment in self._simulation_queue:
                total_shots += experiment.total_shots
                total_complete_shots += experiment.total_completed_shots
            # Calculates returnable percentage values.
            overall_percentage = (total_complete_shots / total_shots) * 100.0
            overall_percentage = round(overall_percentage, 2)
            if running_experiment and running_job:
                experiment_percentage = running_experiment.completion_percentage
                job_percentage = running_job.completion_percentage
            else:
                first_experiment = self._simulation_queue[0]
                first_job = next(iter(first_experiment.jobs.values()))
                experiment_percentage = first_experiment.completion_percentage
                job_percentage = first_job.completion_percentage
            # Calls progress callback function to update all 3x progress bars.
            progress_callback(overall_percentage, 
                              experiment_percentage,
                              job_percentage)
