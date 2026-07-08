# Third party imports:
import eel

# Project-related imports:
from ..general import inform_empty_container
from .js_logs_wrappers import load_log_entry
from ..js_common_wrappers import remove_container_content
from ...data._data import EMPTY_CONTAINER_MESSAGES

# Log manager class object:
from ...project_variables import log_manager as log


# Regular functions (not exposed):

def add_log_message(
    content: str | dict,
    **placeholder_replacements: str
) -> None:
    """Adds a new message entry to log.

    If content is a dictionary, the following key and value pairs are 
    supported:
    - `text` (str): text content of entry
    - `highlightables` (list): list of highlightable text fragments

    After adding the new entry to the log manager, an update to the page 
    content is requested to reflect the changes.

    Args:
        content (str | dict): Content of the new log message entry.
        **placeholder_replacements (str): Keyword arguments that align with
            placeholder variable names. Their values will be replacing the
            placeholders.
    """
    log.add_message(content, **placeholder_replacements)
    show_log_messages()


def add_log_error(
    content: str | dict,
    **placeholder_replacements: str
) -> None:
    """Adds a new error entry to log.

    If content is a dictionary, the following key and value pairs are 
    supported:
    - `text` (str): text content of entry
    - `highlightables` (list): list of highlightable text fragments

    After adding the new entry to the log manager, an update to the page 
    content is requested to reflect the changes.

    Args:
        content (dict): Content of the new log error entry.
        **placeholder_replacements (str): Keyword arguments that align with
            placeholder variable names. Their values will be replacing the
            placeholders.
    """
    log.add_error(content, **placeholder_replacements)
    show_log_errors()


# Exposed functions:

# Log message entries:

@eel.expose
def clear_message(entry_id: str) -> None:
    """Deletes specific message entry from log manager.

    After removing the message, an update to the page content is requested
    to reflect the changes.

    Args:
        entry_id (str): ID of the message entry being removed.
    """
    log.delete_message(entry_id)
    show_log_messages()


@eel.expose
def clear_all_messages() -> None:
    """Deletes all message entries from log manager.

    After removing the messages, an update to the page content is requested
    to reflect the changes.
    """
    log.delete_all_messages()
    show_log_messages()


@eel.expose
def show_log_messages() -> None:
    """Retrieves all message entries from log and requests to display them.

    If there are no entries to display, a message informing this is
    added instead.
    """
    # Removes all currently displayed messages from log:
    remove_container_content(container_id="messages")

    log_messages = log.messages.items()

    if log_messages:
        for id, message in log_messages:
            load_log_entry(entry_id=id,
                           log_entry=message,
                           entry_type="message")
    else:
        inform_empty_container(EMPTY_CONTAINER_MESSAGES["empty_log"],
                               log_type="message",
                               container_id="messages")


# Log error entries:

@eel.expose
def clear_error(error_id: str) -> None:
    """Deletes specific error entry from log manager.

    After removing the error, an update to the page content is requested
    to reflect the changes.

    Args:
        error_id (str): ID of the error entry being removed.
    """
    log.delete_error(error_id)
    show_log_errors()


@eel.expose
def clear_all_errors() -> None:
    """Deletes all error entries from log manager.

    After removing the errors, an update to the page content is requested
    to reflect the changes.
    """
    log.delete_all_errors()
    show_log_errors()


@eel.expose
def show_log_errors() -> None:
    """Retrieves all error entries from log and requests to display them.

    If there are no entries to display, a mesage informing this is
    added instead.
    """
    # Removes all currently displayed messages from log:
    remove_container_content(container_id="errors")

    log_errors = log.errors.items()

    if log_errors:
        for id, error in log_errors:
            load_log_entry(entry_id=id,
                           log_entry=error,
                           entry_type="error")
    else:
        inform_empty_container(EMPTY_CONTAINER_MESSAGES["empty_log"],
                               log_type="error",
                               container_id="errors")
