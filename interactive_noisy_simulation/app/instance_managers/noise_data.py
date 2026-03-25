# Standard library imports:
from tkinter import Tk, filedialog

# Third party imports:
import eel

# Project-related imports:
from ...core.data_structures.file import File
from ..general import inform_empty_container
from .js_noise_data_wrappers import set_selected_file
from ..js_common_wrappers import (
    add_table, add_table_row,
    add_content_box,
    remove_container_content
)
from ..logs.logs import add_log_message
from ...project_variables import (
    EMPTY_CONTAINER_MESSAGES, 
    LOG_MESSAGES
)

# Manager class object:
from ...project_variables import noise_data_manager as ndm


# --------------------------------------------------------------
# Managing all instances
# --------------------------------------------------------------

# Exposed methods:

@eel.expose
def view_noise_data_instances() -> None:
    """Retrieves and forces to render existing noise data instances.
    
    Exposed function to `Python Eel` for use with JavaScript.
    """
    # Removes any previous content in container
    remove_container_content(container_id="content-box")
    
    # Retrieves displayable data about created noise data instances
    instance_data = ndm.get_instance_data()

    # If data exists, creates table
    if instance_data:
        add_table(container_id="content-box", 
                  table_id="noise-data-instances",
                  columns=instance_data.columns,
                  has_actions=bool(instance_data.actions))
        for data_row in instance_data.rows:
            add_table_row(table_id="noise-data-instances",
                          row_content=data_row,
                          actions=instance_data.actions)
    # If not, adds message stating this
    else:
        inform_empty_container(message=EMPTY_CONTAINER_MESSAGES["no_instances"],
                               instance_type="imported noise data",
                               container_id="content-box")


@eel.expose
def import_csv_calibration_data(
    reference_key: str, 
    file_path: str
) -> None:
    """Calls respective manager class method to create a new noise data
    instance.

    Exposed function to `Python Eel` for use with JavaScript.

    Args:
        reference_key (str): Reference key that will be set for the newly
            created instance.
        file_path (str): Path to importable calibration data file that will
            be used to create a new noise data instance.
    """
    # Create new noise data instance:
    source_file = File(file_path)
    ndm.import_csv_data(reference_key, source_file)
    
    new_instance = ndm.noise_data[reference_key]
    add_log_message(message=LOG_MESSAGES["new_noise_data_instance"],
                    reference_key=reference_key,
                    full_path=new_instance.source_file.full_path)
    
    # Reload instance table after adding new instance:
    view_noise_data_instances()


@eel.expose
def remove_noise_data_instance(
    reference_key: str
) -> None:
    """Calls respective manager class method to delete an existing
    noise data instance.
    
    Exposed function to `Python Eel` for use with JavaScript.

    Args:
        reference_key (str): Reference key of deletable noise data
            instance.
    """
    # Remove existing noise data instance:
    ndm.remove_noise_data_instance(reference_key)

    add_log_message(message=LOG_MESSAGES["deleted_instance"],
                    instance_type="noise data",
                    reference_key=reference_key)

    # Reload instance table data after adding new instance:
    view_noise_data_instances()


@eel.expose
def select_csv() -> None:
    """Opens file explorer for selecting calibration data source file.

    Exposed function to `Python Eel` for use with JavaScript.
    """
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    file_path = filedialog.askopenfilename(
        title="Select calibration data CSV file",
        filetypes=[("CSV files", "*.csv")]
    )

    root.destroy()

    if file_path:
        file = File(file_path)
        set_selected_file(file.name, file.full_path)


# --------------------------------------------------------------
# Managing specific instance
# --------------------------------------------------------------

# Exposed methods:

@eel.expose
def view_qubit_data(
    reference_key: str
) -> None:
    """Retrieves and forces to render specific qubit data from the 
    specified noise data instance.

    Exposed function to `Python Eel` for use with JavaScript.

    Args:
        reference_key (str): Reference key of the noise data instance
            from which qubit data is retrieved.
    """
    # Retrieves noise data about all qubits:
    noise_data = ndm.get_qubit_noise_data(reference_key)
    
    # Generates content based on retrieved data:
    for qubit, data in noise_data.items():
        add_content_box(container_id="qubit-data",
                        box_id=f"qubit-box{qubit}")
        add_table(container_id=f"qubit-box{qubit}", 
                  table_id=f"qubit-table-{qubit}")
        
        for name, value in data.items():
            row_content = [name, str(value)]
            add_table_row(table_id=f"qubit-table-{qubit}",
                          row_content=row_content)
