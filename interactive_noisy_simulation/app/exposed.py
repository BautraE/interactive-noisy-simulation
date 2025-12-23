# Third party imports:
import eel

# Project-related imports:
from ..core.instance_managers.noise_data_manager import NoiseDataManager
from .content_management import *
from ..data._data import MESSAGES

# Manager class objects:
ndm = NoiseDataManager()


# Exposed methods:
@eel.expose
def view_noise_data_instances() -> None:
    # Table action button definitions
    actions = [
        {
            "type": "delete",
            "name": "Delete"
        }, {
            "type": "view",
            "name": "View"
        }
    ]
    # Retrieves displayable data about created noise data instances
    instance_data = ndm.get_instance_data()

    # Removes any previous content in container
    remove_container_content("content-box")
    
    # If data exists, creates table
    if instance_data["has_data"]:
        add_table(container_id="content-box", 
                  table_id="noise-data-instances",
                  columns=instance_data["columns"],
                  has_actions=True)
        for data_row in instance_data["rows"]:
            add_table_row(table_id="noise-data-instances",
                          row_content=data_row,
                          actions=actions)
    # If not, adds message stating this
    else:
        add_message(container_id="content-box",
                    message=MESSAGES["no_instances"],
                    instance_type="imported noise data instances")


@eel.expose
def import_csv_calibration_data(
    reference_key: str, 
    file_path: str
) -> None:
    # Create new noise data instance:
    ndm.import_csv_data(reference_key, file_path)
    # Reload instance table data after adding new instance:
    view_noise_data_instances()


@eel.expose
def remove_noise_data_instance(
    reference_key: str
) -> None:
    # Remove existing noise data instance:
    ndm.remove_noise_data_instance(reference_key)
    # Reload instance table data after adding new instance:
    view_noise_data_instances()


@eel.expose
def view_qubit_data(
    reference_key: str
) -> None:
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
