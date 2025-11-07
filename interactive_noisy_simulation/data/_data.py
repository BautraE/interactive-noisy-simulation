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
ERRORS = message_file["errors"]
MESSAGES = message_file["messages"]
OUTPUT_HEADINGS = message_file["output_headings"]
TERMINAL_COMMAND_DESCRIPTION = message_file["terminal_command_descriptions"]
TERMINAL_MESSAGES = message_file["terminal"]
