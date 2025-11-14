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
# Error texts for exceptions related to development process
DEV_ERRORS = message_file["development_errors"]
# Error texts for exceptions related to user actions
ERRORS = message_file["errors"]
# Messages that are printed out as part of the "Message log" content box
MESSAGES = message_file["messages"]
# Output box main heading texts
OUTPUT_HEADINGS = message_file["output_headings"]
# Decriptions of terminal commands that appear as a result of -h --help
TERMINAL_COMMAND_DESCRIPTION = message_file["terminal_command_descriptions"]
# Messages that get printed out during terminal command execution
TERMINAL_MESSAGES = message_file["terminal"]
