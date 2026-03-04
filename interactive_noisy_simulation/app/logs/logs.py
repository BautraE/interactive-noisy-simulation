# Third party imports:
import eel

# Project-related imports:
from .js_logs_wrappers import load_log_message
from ..js_common_wrappers import (
    remove_container_content,
    inform_no_instances)
from ...data._data import MESSAGES

# Log manager class object:
from ...project_variables import log_manager as log


# Regular functions (not exposed):

def add_log_message(
        message: str | dict,
        **placeholder_strings: str
) -> None:
    """Adds a new message log instance.

    After adding the new log to the log manager, an update to the page 
    content is requested to reflect the changes.

    Args:
        message (str | dict): Message text
        **placeholder_replacements (str): Keyword arguments that align with
            placeholder variable names. Their values will be replacing the
            placeholders.
    """
    log.add_message(message, **placeholder_strings)
    show_log_messages()


# Exposed functions:

@eel.expose
def clear_message(message_id: str) -> None:
    """Deletes specific message log instance from log manager.

    After removing the message, an update to the page content is requested
    to reflect the changes.

    Args:
        message_id (str): ID of the message being removed.
    """
    log.delete_message(message_id)
    show_log_messages()


@eel.expose
def clear_all_messages() -> None:
    """Deletes all message log instances from log manager.

    After removing the messages, an update to the page content is requested
    to reflect the changes.
    """
    log.delete_all_messages()
    show_log_messages()


@eel.expose
def show_log_messages() -> None:
    """Retrieves all message log instances and requests to display them.

    If there are no instances to display, a mesage informing this is
    added instead.
    """
    # Removes all currently displayed messages from log:
    remove_container_content(container_id="messages")

    log_messages = log.messages.items()

    if log_messages:
        for id, message in log_messages:
            load_log_message(id,
                             message["timestamp"],
                             message["message_text"])
    else:
        message_text = MESSAGES["empty_log"]["text"].format(
            log_type="message")
        inform_no_instances(message_text, 
                            container_id="messages")


@eel.expose
def show_log_errors() -> None:
    """Retrieves all error log instances and requests to display them.

    If there are no instances to display, a mesage informing this is
    added instead.
    """
    remove_container_content(container_id="errors")

    message_text = MESSAGES["empty_log"]["text"].format(
            log_type="error")
    inform_no_instances(message_text, 
                        container_id="errors")
