# =================================================================
# Definition of usable variables containing data from 
# project-related static data files.
# =================================================================

# Standard library imports:
import json
from importlib import resources

# Local project imports:
from .. import data


# Configuration data:
with (resources.files(data) / "config.json").open("r", encoding="utf8") as file:
    CONFIG = json.load(file)

# CSV file column information:
with (resources.files(data) / "csv_columns.json").open("r", encoding="utf8") as file:
    CSV_COLUMNS = json.load(file)

# Message texts:    
with (resources.files(data) / "messages.json").open("r", encoding="utf8") as file:
    message_file = json.load(file)
# Informative text that appears in containers if they have no content to display
EMPTY_CONTAINER_MESSAGES = message_file["empty_container"]
# Error log message text
ERROR_MESSAGES = message_file["error"]
# Message log message text
LOG_MESSAGES = message_file["log"]
# Messages that get printed out during terminal command execution
TERMINAL_MESSAGES = message_file["terminal"]
# Decriptions of terminal commands that appear as a result of -h --help
TERMINAL_COMMAND_DESCRIPTION = message_file["terminal_command_descriptions"]
