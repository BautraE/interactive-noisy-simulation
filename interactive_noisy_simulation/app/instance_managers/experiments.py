# Third party imports:
import eel

# Project-related imports:
from ..general import inform_empty_container
from ..logs.logs import add_log_message
from ..js_common_wrappers import remove_container_content
from .js_manager_wrappers import (
    view_instance_data,
    view_job_detailed
)
from ...project_variables import (
    EMPTY_CONTAINER_MESSAGES, 
    LOG_MESSAGES
)

# Manager class objects:
from ...project_variables import (
    experiment_manager as em,
    noise_creator as nc,
    circuit_manager as cm
)

# --------------------------------------------------------------
# Managing all instances
# --------------------------------------------------------------

# Exposed functions:

@eel.expose
def view_experiment_instances() -> None:
    """Retrieves and forces to render existing experiment instances.
    
    Exposed function to `Python Eel` for use with JavaScript.
    """
    # Removes any previous content in container
    remove_container_content(container_id="content-box")

    # Retrieves displayable data about created experiment instances
    instance_data = em.get_instance_data()

    # If data exists, creates table
    if instance_data:
        view_instance_data(instance_data=instance_data.to_dict(), 
                           container_id="content-box",
                           table_id="experiment-instances")
    # If not, adds message stating this
    else:
        inform_empty_container(message=EMPTY_CONTAINER_MESSAGES["no_instances"],
                               instance_type="experiment",
                               container_id="content-box")
        

@eel.expose
def create_experiment_instance(
    reference_key: str
) -> None:
    """Calls respective manager class method to create a new experiment
    instance.

    Exposed function to `Python Eel` for use with JavaScript.

    Args:
        reference_key (str): Reference key that will be set for the newly
            created instance.
    """
    # Create new noise data instance:
    em.create_instance(reference_key)
    
    add_log_message(message=LOG_MESSAGES["created_instance"],
                    instance_type="experiment",
                    reference_key=reference_key)
    
    # Reload instance table after adding new instance:
    view_experiment_instances()


@eel.expose
def remove_experiment_instance(
    reference_key: str
) -> None:
    """Calls respective manager class method to delete an existing
    experiment instance.
    
    Exposed function to `Python Eel` for use with JavaScript.

    Args:
        reference_key (str): Reference key of deletable experiment
            instance.
    """
    # Remove existing noise data instance:
    em.remove_instance(reference_key)

    add_log_message(message=LOG_MESSAGES["deleted_instance"],
                    instance_type="experiment",
                    reference_key=reference_key)

    # Reload instance table data after adding new instance:
    view_experiment_instances()


@eel.expose
def is_experiment_key_unique(
    reference_key: str
) -> bool:
    """Checks if the new reference key is already in use for a different
    experiment instance.

    Exposed function to `Python Eel` for use with JavaScript.

    Args:
        reference_key (str): Selected reference key for a new experiment
            instance.

    Returns:
        bool: Is the new key unique (not in use by another instance of
            the same type).
    """
    all_keys = em.experiments.keys()
    return reference_key not in all_keys


# --------------------------------------------------------------
# Managing specific instance
# --------------------------------------------------------------

# Exposed methods:

@eel.expose
def view_experiment_jobs(
    experiment_reference_key: str
) -> None:
    """Retrieves and forces to render existing job instances for a specific
    experiment.
    
    Exposed function to `Python Eel` for use with JavaScript.

    Args:
        experiment_reference_key (str): Reference key of experiment whose
            job instances will be displayed.
    """
    # Removes any previous content in container
    remove_container_content(container_id="job-instances")
    remove_container_content(container_id="detailed-job-view")

    job_data = em.get_job_simple_data(experiment_reference_key)

    if job_data:
        view_instance_data(instance_data=job_data.to_dict(), 
                           container_id="job-instances",
                           table_id="job-instances-table")
        view_experiment_job_detailed(experiment_reference_key)

    else:
        inform_empty_container(message=EMPTY_CONTAINER_MESSAGES["no_experiment_jobs"],
                               container_id="job-instances")
        inform_empty_container(message=EMPTY_CONTAINER_MESSAGES["no_instance_for_detailed_view"],
                               instance_type="jobs",
                               container_id="detailed-job-view")
        

@eel.expose
def view_experiment_job_detailed(
    experiment_reference_key: str,
    job_reference_key: str | None = None,
) -> None:
    """Retrieves and forces to render detailed data for a specific experiment
    job.

    If no job reference key is given, the first job instance in the available
    instance list will be used.
    
    Exposed function to `Python Eel` for use with JavaScript.

    Args:
        experiment_reference_key (str): Reference key of experiment whose
            job instance will be displayed.
        job_reference_key (str | None): Reference key of job instance whose 
            detailed data will be displayed. (Default: None)
    """
    if not job_reference_key:
        experiment = em.experiments[experiment_reference_key]
        first_job = next(iter(experiment.jobs.values()))
        job_reference_key = first_job.reference_key

    detailed_data = em.get_job_detailed_data(experiment_reference_key,
                                             job_reference_key)
    view_job_detailed(job_data=detailed_data)


@eel.expose
def create_job_for_experiment(
    experiment_reference_key: str,
    job_reference_key: str,
    circuit_reference_key: str,
    noise_model_reference_key: str | None,
    shot_count: int,
    hardware: str,
    simulation_method: str,
    optimization_level: int | None,
) -> None:
    """Calls respective manager class method to create a new job instance
    for a specific experiment.

    Exposed function to `Python Eel` for use with JavaScript.

    Args:
        experiment_reference_key (str): Reference key of experiment instance
            for which the new job instance will be created.
        job_reference_key (str): Reference key that will be set for the newly
            created job instance.
        circuit_reference_key (str): Reference key for circuit instance that 
            the job will execute.
        noise_model_reference_key (str | None): Reference key for noise model
            instance that will be used during simulation. In case of `None`,
            it will be a noiseless simulation.
        shot_count (int): Amount of times that the selected circuit will be 
            executed as part of this job instance.
        hardware (str): Hardware option that will be used during simulation
            (what part of computer hardware will be responsible for the 
            simulator circuit executions - `CPU` or `GPU`).
        simulation_method (str): Simulation method that the simulator will 
            use as part of running the specific job instance.
        optimization_level (int | None): Optimization level for the 
            transpilation process (for preparing the selected circuit to be
            run on a simulator with the selected noise model). `None` will
            only be set if the simulation is noiseless.
    """
    # Retrieving additional required data
    circuit_instance = cm.circuits.get(circuit_reference_key)
    noise_model_instance = nc.noise_models.get(noise_model_reference_key)

    em.create_job(experiment_reference_key=experiment_reference_key, 
                  job_reference_key=job_reference_key,
                  circuit_instance=circuit_instance,
                  noise_model_instance=noise_model_instance,
                  shot_count=shot_count,
                  hardware=hardware,
                  simulation_method=simulation_method,
                  optimization_level=optimization_level)
    
    add_log_message(message=LOG_MESSAGES["created_job_instance"],
                    job_reference_key=job_reference_key,
                    experiment_reference_key=experiment_reference_key)
    
    view_experiment_jobs(experiment_reference_key)


@eel.expose
def remove_job_from_experiment(
    experiment_reference_key: str,
    job_reference_key: str
) -> None:
    """Calls respective manager class method to delete an existing
    job instance withing a specific experiment.
    
    Exposed function to `Python Eel` for use with JavaScript.

    Args:
        experiment_reference_key (str): Reference key of experiment instance
            whose job instance will be deleted.
        job_reference_key (str): Reference key of deletable job instance.
    """
    em.remove_job(experiment_reference_key, job_reference_key)

    add_log_message(message=LOG_MESSAGES["deleted_job_instance"],
                    job_reference_key=job_reference_key,
                    experiment_reference_key=experiment_reference_key)
    
    view_experiment_jobs(experiment_reference_key)


@eel.expose
def is_job_key_unique(
    experiment_reference_key: str,
    job_reference_key: str
) -> bool:
    """Checks if the new reference key is already in use for a different
    job instance within the scope of a specific experiment.

    Exposed function to `Python Eel` for use with JavaScript.

    Args:
        experiment_reference_key (str): Reference key of experiment instance
            that will be checked for the existance of the specific job
            reference key.
        job_reference_key (str): Selected reference key for a new experiment
            job instance.

    Returns:
        bool: Is the new key unique (not in use by another instance of
            the same type).
    """
    experiment = em.experiments[experiment_reference_key]
    return job_reference_key not in experiment.jobs.keys()


@eel.expose
def get_circuit_references() -> list[str]:
    """Retrieves list of reference keys for existing circuit
    instances.

    Exposed function to `Python Eel` for use with JavaScript.

    Returns:
        list[str]: List of reference keys for existing circuit
            instances.
    """
    instances = cm.circuits
    reference_keys = [
        instance.reference_key for instance in instances.values()
    ]

    if not reference_keys:
        inform_empty_container(message=EMPTY_CONTAINER_MESSAGES["no_instances_for_job"],
                               instance_type="circuit",
                               container_id="circuit-instance-container")

    return reference_keys


@eel.expose
def get_noise_model_references() -> list[str]:
    """Retrieves list of reference keys for existing noise model
    instances.

    Exposed function to `Python Eel` for use with JavaScript.

    Returns:
        list[str]: List of reference keys for existing noise model
            instances.
    """
    instances = nc.noise_models
    reference_keys = [
        instance.reference_key for instance in instances.values()
    ]

    if not reference_keys:
        inform_empty_container(message=EMPTY_CONTAINER_MESSAGES["no_instances_for_job"],
                               instance_type="noise model",
                               container_id="noise-model-container")

    return reference_keys


@eel.expose
def get_available_hardware_options() -> list[str]:
    """Retrieves list of available hardware options for running
    simulators.

    Currently only returns "CPU", as a method for validating
    "GPU" has not been implemented yet.

    Exposed function to `Python Eel` for use with JavaScript.

    Returns:
        list[str]: List of available hardware options.
    """
    return ["CPU"]


@eel.expose
def get_available_sim_methods() -> list[str]:
    """Retrieves list of available simulation method options for running
    simulators.

    Currently only returns "statevector", "density_matrix", and 
    "matrix_product_state" as a method for validating other options against
    specific requirements and scenarios has not been implemented yet.

    Exposed function to `Python Eel` for use with JavaScript.

    Returns:
        list[str]: List of available simulation method options.
    """
    supported_methods = [
        "statevector",
        "density_matrix",
        "matrix_product_state"
    ]
    return supported_methods


@eel.expose
def get_available_optimization_options() -> list[int]:
    """Retrieves list of available optimization level options for circuit
    transpilation.

    Exposed function to `Python Eel` for use with JavaScript.

    Returns:
        list[str]: List of available optimization level options.
    """
    return [0, 1, 2, 3]
