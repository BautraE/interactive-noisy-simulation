# =================================================================
# Python wrappers for JS function calling
# Related to: any of the instance manager-related python files
# inside of `app`.
# =================================================================

# Third party imports:
import eel


# --------------------------------------------------------------
# No specific instance type
# --------------------------------------------------------------

def view_instance_data(
    instance_data: dict,
    container_id: str,
    table_id: str
) -> None:
    """Renders instance all available instance data.

    A generic function that works for all instance types.
    
    Wrapper function for `Python Eel` JS function call.

    Args:
        instance_data (dict): Organized displayable data for existing
            instances
        container_id (str): ID of container where the instance data will
            be displayed
        table_id (str): ID that the newly created table for displaying
            existing instances will use.
    """
    eel.viewInstanceData(instance_data, container_id, table_id)


# --------------------------------------------------------------
# Experiment job instances (experiments.py)
# --------------------------------------------------------------

def view_job_detailed(
        job_data: dict
) -> None:
    """Renders detailed view for a specific experiment job instance
    and changes CSS style of selected instance row in table.
    
    Wrapper function for `Python Eel` JS function call.

    Args:
        job_data (dict): detailed data about a specific experiment job
            instance.
    """
    eel.viewJobDetailedData(job_data)
