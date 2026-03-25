# =================================================================
# Python wrappers for JS function calling
# Related to: `logs.py`
# =================================================================

# Third party imports:
import eel


def load_log_message(
        message_id: str, 
        message: dict
) -> None:
    """Loads message into log.

    Wrapper function for `Python Eel` JS function call.

    Args:
        message_id (str): id of the message (used for specific log instance
            clearing functionality).
        message (dict): message dictionary containing all required information
            about displayable message (message text, highlightables, 
            timestamp).
    """
    eel.loadLogMessage(message_id, message)
