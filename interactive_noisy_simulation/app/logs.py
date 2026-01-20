# Third party imports:
import eel

# Project-related imports:
from .content_management import *
from ..core.logs.log_manager import log_manager as log
from ..data._data import MESSAGES


# Regular functions:
def add_log_message(
        message: str | dict,
        **placeholder_strings: str
) -> None:
    # Adds new message to log:
    log.add_message(message, **placeholder_strings)
    # Shows all messages instances from log:
    show_log_messages()


# Exposed functions:
@eel.expose
def clear_message(message_id: str) -> None:
    log.delete_message(message_id)
    # Shows all messages instances from log:
    show_log_messages()


@eel.expose
def clear_all_messages() -> None:
    log.delete_all_messages()
    # Shows all messages instances from log:
    show_log_messages()


@eel.expose
def show_log_messages() -> None:
    # Removes all currently displayed messages from log:
    remove_container_content("messages")

    log_messages = log.messages.items()

    if log_messages:
        for id, message in log_messages:
            eel.loadLogMessage(id,
                               message["timestamp"],
                               message["message_text"])
    else:
        add_message(container_id="messages",
                    message=MESSAGES["empty_log"],
                    log_type="message")
