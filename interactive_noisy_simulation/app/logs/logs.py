# Third party imports:
import eel

# Project-related imports:
from ..general import inform_empty_container
from .js_logs_wrappers import load_log_message
from ..js_common_wrappers import remove_container_content
from ...data._data import EMPTY_CONTAINER_MESSAGES

# Log manager class object:
from ...project_variables import log_manager as log


# Regular functions (not exposed):

def add_log_message(
        message: dict,
        **placeholder_replacements: str
) -> None:
    """Adds a new message log instance.

    After adding the new log to the log manager, an update to the page 
    content is requested to reflect the changes.

    Args:
        message (dict): Message text
        **placeholder_replacements (str): Keyword arguments that align with
            placeholder variable names. Their values will be replacing the
            placeholders.
    """
    log.add_message(message, **placeholder_replacements)
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
            load_log_message(message_id=id,
                             message=message)
    else:
        inform_empty_container(EMPTY_CONTAINER_MESSAGES["empty_log"],
                               log_type="message",
                               container_id="messages")


@eel.expose
def show_log_errors() -> None:
    """Retrieves all error log instances and requests to display them.

    If there are no instances to display, a mesage informing this is
    added instead.
    """
    remove_container_content(container_id="errors")
    inform_empty_container(EMPTY_CONTAINER_MESSAGES["empty_log"],
                           log_type="error",
                           container_id="errors")
