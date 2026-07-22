# =================================================================
# Definition of usable variables containing data from 
# project-related static data files.
# =================================================================

# Standard library imports:
import json
from importlib import resources

# Local project imports:
from .. import data


# CSV file column information:
with (resources.files(data) / "csv_columns.json").open("r", encoding="utf8") as file:
    csv_column_file = json.load(file)
# Usable columns from imported calibration data CSV files.
# Also contains additional information, such as:
# - Displayable name of column; 
# - Name of column in the CSV file; 
# - Description of the column;
# - Gate names that are used in code (for specific gate error columns only)
USED_CSV_COLUMNS: dict[str, dict] = csv_column_file["used_columns"]
# Default CSV columns that contain multiple data entries in a single cell.
# For example, two-qubit gate errors contain errors for all directionally
# connected qubits.
MULTI_DATA_CSV_COLUMNS: list[str] = csv_column_file["multi_data_columns"]
# CSV columns that are not used by INS functionality.
UNNECESSARY_CSV_COLUMNS: list[str] = csv_column_file["unnecessary_columns"]

# Dictionary of single-qubit gates based on data present in `csv_columns.json`.
# Contains: code name of gate as key and name of that column used within 
# `csv_columns.json`.
SINGLE_QUBIT_GATES: dict[str, str] = {
    data["code_name"]: key
    for key, data in USED_CSV_COLUMNS.items()
    if data.get("qubit_count") == 1
}
# Dictionary of two-qubit gates based on data present in `csv_columns.json`.
# Contains: code name of gate as key and name of that column used within 
# `csv_columns.json`.
TWO_QUBIT_GATES: dict[str, str] = {
    data["code_name"]: key
    for key, data in USED_CSV_COLUMNS.items()
    if data.get("qubit_count") == 2
}

# Message texts:    
with (resources.files(data) / "messages.json").open("r", encoding="utf8") as file:
    message_file = json.load(file)
# Informative text that appears in containers if they have no content to display
EMPTY_CONTAINER_MESSAGES: dict[str, str] = message_file["empty_container"]
# Error log message text
ERROR_MESSAGES: dict[str, dict] = message_file["error"]
# Message log message text
LOG_MESSAGES: dict[str, dict] = message_file["log"]
# Messages that get printed out during terminal command execution
TERMINAL_MESSAGES: dict[str, str] = message_file["terminal"]
# Decriptions of terminal commands that appear as a result of -h --help
TERMINAL_COMMAND_DESCRIPTION: dict[str, str] = message_file["terminal_command_descriptions"]
