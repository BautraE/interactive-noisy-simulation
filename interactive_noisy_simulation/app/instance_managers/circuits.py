# Standard library imports:
from tkinter import Tk, filedialog

# Third party imports:
import eel

# Project-related imports:
from ...core.data_structures.file import File
from ..general import inform_empty_container
from ..js_common_wrappers import (
    add_table, add_table_row,
    remove_container_content,
    set_selected_file
)
from ..logs.logs import add_log_message
from ...project_variables import (
    EMPTY_CONTAINER_MESSAGES, 
    LOG_MESSAGES
)

# Manager class object:
from ...project_variables import circuit_manager as cm


# --------------------------------------------------------------
# Managing all instances
# --------------------------------------------------------------

# Exposed functions:

@eel.expose
def view_circuit_instances() -> None:
    """Retrieves and forces to render existing circuit instances.
    
    Exposed function to `Python Eel` for use with JavaScript.
    """
    # Removes any previous content in container
    remove_container_content(container_id="content-box")

    # Retrieves displayable data about created noise data instances
    instance_data = cm.get_instance_data()

    # If data exists, creates table
    if instance_data:
        add_table(container_id="content-box", 
                  table_id="circuit-instances",
                  columns=instance_data.columns,
                  has_actions=bool(instance_data.actions))
        for data_row in instance_data.rows:
            add_table_row(table_id="circuit-instances",
                          row_content=data_row,
                          actions=instance_data.actions)
    # If not, adds message stating this
    else:
        inform_empty_container(message=EMPTY_CONTAINER_MESSAGES["no_instances"],
                               instance_type="circuit",
                               container_id="content-box")


@eel.expose
def create_circuit_instance(
    reference_key: str,
    file_path: str
) -> None:
    """Calls respective manager class method to create a new circuit
    instance.

    Exposed function to `Python Eel` for use with JavaScript.

    Args:
        reference_key (str): Reference key that will be set for the newly
            created instance.
        file_path (str): Path to importable QPY file that contains a 
            quantum circuit.
    """
    # Create new noise data instance:
    source_file = File(file_path)
    cm.create_instance(reference_key, source_file)
    
    new_instance = cm.circuits[reference_key]
    add_log_message(message=LOG_MESSAGES["created_instance_from_file"],
                    instance_type="circuit",
                    reference_key=reference_key,
                    full_path=new_instance.source_file.full_path)
    
    # Reload instance table after adding new instance:
    view_circuit_instances()


@eel.expose
def remove_circuit_instance(
    reference_key: str
) -> None:
    """Calls respective manager class method to delete an existing
    circuit instance.
    
    Exposed function to `Python Eel` for use with JavaScript.

    Args:
        reference_key (str): Reference key of deletable circuit
            instance.
    """
    # Remove existing noise data instance:
    cm.remove_instance(reference_key)

    add_log_message(message=LOG_MESSAGES["deleted_instance"],
                    instance_type="circuit",
                    reference_key=reference_key)

    # Reload instance table data after adding new instance:
    view_circuit_instances()


@eel.expose
def select_qpy() -> None:
    """Opens file explorer for selecting file containing circuit.

    Exposed function to `Python Eel` for use with JavaScript.
    """
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    file_path = filedialog.askopenfilename(
        title="Select QPY file with circuit",
        filetypes=[("QPY files", "*.qpy")]
    )

    root.destroy()

    if file_path:
        file = File(file_path)
        set_selected_file(file.name, file.full_path)


@eel.expose
def is_circuit_key_unique(
    reference_key: str
) -> bool:
    """Checks if the new reference key is already in use for a different
    circuit instance.

    Exposed function to `Python Eel` for use with JavaScript.

    Args:
        reference_key (str): Selected reference key for a new circuit
            instance.

    Returns:
        bool: Is the new key unique (not in use by another instance of
            the same type).
    """
    all_keys = cm.circuits.keys()
    return reference_key not in all_keys
