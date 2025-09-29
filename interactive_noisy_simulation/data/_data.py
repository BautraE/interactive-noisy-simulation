# Standard library imports:
import json
from importlib import resources
# Local project imports:
from .. import data


with (resources.files(data) / "config.json").open("r", encoding="utf8") as file:
    CONFIG = json.load(file)

with (resources.files(data) / "csv_columns.json").open("r", encoding="utf8") as file:
    CSV_COLUMNS = json.load(file)
    
with (resources.files(data) / "messages.json").open("r", encoding="utf8") as file:
    message_file = json.load(file)
MESSAGES = message_file["messages"]
OUTPUT_HEADINGS = message_file["output-headings"]
ERRORS = message_file["errors"]
