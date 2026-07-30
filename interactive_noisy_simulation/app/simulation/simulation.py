# Third party imports:
import eel

# Project-related imports:
from ...exceptions import SimulationError
from ..js_common_wrappers import (
    remove_container_content,
    update_span_content,
    update_progress_bar,
    activate_progress_bar,
    deactivate_progress_bar
)
from ..general import inform_empty_container
from ..instance_managers.js_manager_wrappers import view_instance_data
from ..logs.logs import (
    add_log_message,
    add_log_error
)
from ...project_variables import (
    EMPTY_CONTAINER_MESSAGES,
    LOG_MESSAGES
)

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
    update_progress_bars()
    update_queue_execution_button()


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

    Exposed function to `Python Eel` for use with JavaScript.
    
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

    Exposed function to `Python Eel` for use with JavaScript.
    
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


# --------------------------------------------------------------
# Executing queue.
# --------------------------------------------------------------

def update_queue_execution_button() -> None:
    """Updates style and status of button for executing the experiment
    queue:
    - "unavailable" - Queue cannot be executed because there are
      either no jobs to run, or the queue is empty;
    - "running" - The queue is being executed;
    - "available" - The queue is eligible to be executed.
    """
    if sm.is_executing:
        state = "running"
    elif sm.total_queued_incomplete_jobs == 0:
        state = "unavailable"
    else:
        state = "available"
    
    eel.updateQueueExecutionButton(state)


@eel.expose
def execute_queued_experiments() -> None:
    """Calls SimulationManager object to begin executing the experiment
    queue.

    Exposed function to `Python Eel` for use with JavaScript.
    """
    add_log_message(content=LOG_MESSAGES["queue_execution_started"],
                    queued_experiment_count=f"{sm.queue_lenght}")
    
    update_execution_status(is_executing=True)
    update_queue_execution_button()
    activate_progress_bars()
    try:
        sm.execute_queue(ui_refresh_callback=update_simulation_content,
                         progress_callback=update_progress_bars)
    except SimulationError as e:
        add_log_error(content=e.message, 
                      **e.placeholders)
    else:
        add_log_message(content=LOG_MESSAGES["queue_execution_finished"],
                        queued_experiment_count=f"{sm.queue_lenght}")
    finally:
        update_execution_status(is_executing=False)
        deactivate_progress_bars()
        update_simulation_content()


def update_execution_status(
    is_executing: bool
) -> None:
    """Updates execution status for functionality in the `Simulation` page.
    
    This status is updated: 
    - inside of the `SimulationManager` class;
    - in JS code for formatting information.

    Args:
        is_executing (bool): New status that will be set.
    """
    sm.is_executing = is_executing
    eel.updateQueueExecutionStatus(is_executing)


def update_progress_bars(
    overall_percentage: float | str | None = None,
    experiment_percentage: float | str | None = None,
    job_percentage: float | str | None = None
) -> None:
    """Calls JS function for updating progress bar percentages based on the
    received values.

    If the percentage value arguments are of type `str`, they contain the value
    `--` - a placeholder for when there is no percentage value to calculate.

    If no percentage values are given, the function for calculating these
    percentage values is called and will return the progress values based
    on the currently created queue.
    
    Args:
        overall_percentage (float|str|None): Overall completion percentage of the 
            experiment queue. (Default: `None`)
        experiment_percentage (float|str|None): Current experiment completion 
            percentage. (Default: `None`)
        job_percentage (float|str|None): Current job completion percentage.
            (Default: `None`)
    """
    if (
        overall_percentage is not None 
        and experiment_percentage is not None 
        and job_percentage is not None
    ):
        update_progress_bar(percentage=overall_percentage, 
                            bar_id="execution-overall-progress")
        update_progress_bar(percentage=experiment_percentage, 
                            bar_id="execution-experiment-progress")
        update_progress_bar(percentage=job_percentage, 
                            bar_id="execution-job-progress")
    else:
        sm.update_queue_execution_progress(progress_callback=update_progress_bars)
    

def activate_progress_bars() -> None:
    """Calls JS functions to activate all execution tracking progress bars."""
    activate_progress_bar(bar_id="execution-overall-progress")
    activate_progress_bar(bar_id="execution-experiment-progress")
    activate_progress_bar(bar_id="execution-job-progress")


def deactivate_progress_bars() -> None:
    """Calls JS functions to deactivate all execution tracking progress bars."""
    deactivate_progress_bar(bar_id="execution-overall-progress")
    deactivate_progress_bar(bar_id="execution-experiment-progress")
    deactivate_progress_bar(bar_id="execution-job-progress")
