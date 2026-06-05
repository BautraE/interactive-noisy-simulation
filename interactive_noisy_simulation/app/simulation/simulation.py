# Third party imports:
import eel

# Project-related imports:
from ..js_common_wrappers import (
    remove_container_content,
    update_span_content
)
from ..general import inform_empty_container
from ..instance_managers.js_manager_wrappers import view_instance_data
from ...project_variables import EMPTY_CONTAINER_MESSAGES

# Manager class objects:
from ...project_variables import (
    experiment_manager as em,
    simulation_manager as sm
)


# --------------------------------------------------------------
# Loading in available data.
# --------------------------------------------------------------

@eel.expose
def update_simulation_content() -> None:
    """Forces to render dynamic content for the `Simulation` page.

    This function combines the process for calling all separate
    content rendering functions responsible for specific parts of the
    page.

    Exposed function to `Python Eel` for use with JavaScript.
    """
    view_queueable_experiments()
    view_queued_experiments()
    update_detailed_queue_data()


def view_queueable_experiments() -> None:
    """Retrieves and forces to render existing experiment instances that
    can be added to an experiment queue.
    """
    # Removes any previous content in container
    remove_container_content(container_id="queueable-experiments-container")

    # Retrieves displayable data about created experiment instances
    instance_data = em.get_queueable_instance_data()
    
    # If data exists, creates table
    if instance_data:
        view_instance_data(instance_data=instance_data.to_dict(), 
                           container_id="queueable-experiments-container",
                           table_id="queueable-experiment-instances")
    # If not, adds message stating this
    else:
        inform_empty_container(message=EMPTY_CONTAINER_MESSAGES["no_queueable_experiments"],
                               container_id="queueable-experiments-container")


def view_queued_experiments() -> None:
    """Retrieves and forces to render queued experiment instances."""
    # Removes any previous content in container
    remove_container_content(container_id="queued-experiments-container")

    # Retrieves displayable data about created experiment instances
    instance_data = sm.get_queued_experiment_data()
    
    # If data exists, creates table
    if instance_data:
        view_instance_data(instance_data=instance_data.to_dict(), 
                           container_id="queued-experiments-container",
                           table_id="queued-experiment-instances")
    # If not, adds message stating this
    else:
        inform_empty_container(message=EMPTY_CONTAINER_MESSAGES["no_queued_experiments"],
                               container_id="queued-experiments-container")
        

def update_detailed_queue_data() -> None:
    """Retrieves and forces to render detailed data about the currently
    created experiment queue.
    
    The retrieved data appears on the right side of the page under 
    `QUEUE EXECUTION`.

    Renderable data includes:
    - Total number of queued experiments;
    - Total number of jobs across all queued experiments;
    - Total number of incomplete jobs across all queued experiments.
    """
    total_queued_experiments = sm.queue_lenght
    update_span_content(new_content=total_queued_experiments,
                        span_id="total_queued_experiments")

    total_queued_jobs = sm.total_queued_jobs
    update_span_content(new_content=total_queued_jobs,
                        span_id="total_queued_jobs")

    total_incomplete_jobs = sm.total_queued_incomplete_jobs
    update_span_content(new_content=total_incomplete_jobs,
                        span_id="total_incomplete_jobs")


# --------------------------------------------------------------
# Adding & removing experiments from queue
# --------------------------------------------------------------

@eel.expose
def add_experiment_to_queue(
    reference_key: str
) -> None:
    """Adds existing experiment to the execution queue.
    
    Args:
        reference_key (str): Reference key of experiment instance being
            added to the queue.
    """
    # Adds experiment to queue
    experiment_instance = em.experiments[reference_key]
    sm.add_experiment_to_queue(experiment_instance)
    experiment_instance.is_queued = True
    # Updates UI
    update_simulation_content()


@eel.expose
def remove_experiment_from_queue(
    reference_key: str
) -> None:
    """Removes experiment from the execution queue.
    
    Args:
        reference_key (str): Reference key of experiment instance being
            removed from the queue.
    """
    # Removes experiment from queue
    experiment_instance = em.experiments[reference_key]
    sm.remove_experiment_from_queue(experiment_instance)
    experiment_instance.is_queued = False
    # Updates UI
    update_simulation_content()
