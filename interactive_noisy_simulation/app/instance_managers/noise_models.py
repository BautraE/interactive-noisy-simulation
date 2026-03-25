# Third party imports:
import eel

# Project-related imports:
from ..general import inform_empty_container
from ..logs.logs import add_log_message
from ..js_common_wrappers import (
    add_table, add_table_row,
    remove_container_content
)
from ...project_variables import (
    EMPTY_CONTAINER_MESSAGES, LOG_MESSAGES
)

# Imports only used for type definition:
from ...core.data_structures.instance_data import InstanceData

# Manager class object:
from ...project_variables import noise_creator as nc
from ...project_variables import noise_data_manager as ndm


# --------------------------------------------------------------
# Managing all instances
# --------------------------------------------------------------

# Exposed methods:

@eel.expose
def view_noise_model_instances() -> None:
    """Retrieves and forces to render existing noise model instances.
    
    Exposed function to `Python Eel` for use with JavaScript.
    """
    remove_container_content("content-box")
    
    instance_data = nc.get_instance_data()

    # If data exists, creates table
    if instance_data:
        add_source_data_availability(instance_data)
        add_table(container_id="content-box", 
                  table_id="noise-model-instances",
                  columns=instance_data.columns,
                  has_actions=bool(instance_data.actions))
        for data_row in instance_data.rows:
            add_table_row(table_id="noise-model-instances",
                          row_content=data_row,
                          actions=instance_data.actions)
    # If not, adds message stating this
    else:
        inform_empty_container(message=EMPTY_CONTAINER_MESSAGES["no_instances"],
                               instance_type="created noise model",
                               container_id="content-box")


@eel.expose
def create_noise_model_instance(
    reference_key: str,
    noise_data_reference: str
) -> None:
    """Calls noise model manager object method to create a new noise model
    instance.

    Exposed function to `Python Eel` for use with JavaScript.

    Args:
        reference_key (str): Reference key that will be set for the newly
            created instance.
        noise_data_reference (str): Reference key of source noise data 
            instance.
    """
    noise_data = ndm.noise_data[noise_data_reference]
    nc.create_noise_model(reference_key=reference_key,
                          noise_data=noise_data,
                          progress_callback=update_progress)
    
    add_log_message(message=LOG_MESSAGES["created_instance"],
                    instance_type="noise model",
                    reference_key=reference_key)
    
    view_noise_model_instances()


@eel.expose
def remove_noise_model_instance(
    reference_key: str
) -> None:
    """Calls respective manager class method to delete an existing
    noise model instance.
    
    Exposed function to `Python Eel` for use with JavaScript.

    Args:
        reference_key (str): Reference key of deletable noise model
            instance.
    """
    # Remove existing noise model instance:
    nc.remove_noise_model_instance(reference_key)

    add_log_message(message=LOG_MESSAGES["deleted_instance"],
                    instance_type="noise model",
                    reference_key=reference_key)
    
    # Reload instance table data after adding new instance:
    view_noise_model_instances()


@eel.expose
def get_noise_data_references() -> list[str]:
    """Retrieves list of reference keys for existing noise data
    instances.

    Exposed function to `Python Eel` for use with JavaScript.

    Returns:
        list[str]: List of reference keys for existing noise data
            instances.
    """
    instances = ndm.noise_data
    reference_keys = [
        instance.reference_key for instance in instances.values()
    ]

    if not reference_keys:
        inform_empty_container(message=EMPTY_CONTAINER_MESSAGES["no_noise_data_sources"],
                               container_id="noise-source-container")

    return reference_keys


# Non-exposed methods:

def add_source_data_availability(
        instance_data: InstanceData
) -> None:
    """Adds noise data source availability column to retrieved noise model
    instance data.

    Args:
        instance_data (InstanceData): Retrieved noise model instance
            data, to which the new column will be added.
    """
    column_data = []
    noise_data_instances = ndm.noise_data

    for data_row in instance_data.rows:
        # Source data file reference key is as the 5th row data element
        source_data_ref = data_row[4]
        if source_data_ref in noise_data_instances:
            column_data.append("Available")
        else: 
            column_data.append("Removed")

    instance_data.add_collumn(name="Noise data availability",
                              content=column_data)


def update_progress(
        new_percentage: float
) -> None:
    """Callback function that updates progress status of creating new noise
    model instance with new completion percentage value.

    Args:
        new_percentage (float): New progress percentage value that will 
            replace the old one.
    """
    eel.updateInstanceProgress(new_percentage)
