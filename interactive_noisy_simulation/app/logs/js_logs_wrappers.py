# =================================================================
# Python wrappers for JS function calling
# Related to: `logs.py`
# =================================================================

# Third party imports:
import eel


def load_log_message(
        message_id: str, 
        timestamp: str, 
        message_text: str
) -> None:
    """Loads message into log.

    Wrapper function for `Python Eel` JS function call.

    Args:
        message_id (str): id of the message (used for specific log instance
            clearing functionality).
        timestamp (str): time at which the message was generated.
        message_text (str): log message text.
    """
    eel.loadLogMessage(message_id, timestamp, message_text)
