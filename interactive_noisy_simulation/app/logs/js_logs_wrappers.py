# =================================================================
# Python wrappers for JS function calling
# Related to: `logs.py`
# =================================================================

# Third party imports:
import eel


def load_log_entry(
        entry_id: str, 
        log_entry: dict,
        entry_type: str
) -> None:
    """Loads log entry into log.

    Wrapper function for `Python Eel` JS function call.

    Args:
        entry_id (str): id of the log entry (used for specific log entry
            clearing functionality).
        log_entry (dict): log entry dictionary containing all required information
            about displayable entry (text, highlightables, timestamp).
        message_type (str): type of log entry being loaded. (e.g. `message` 
            or `error`).
    """
    eel.loadLogEntry(entry_id, log_entry, entry_type)
