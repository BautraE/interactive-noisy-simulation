# Third party imports:
import eel

# Project-related imports:
from .js_common_wrappers import add_empty_container_message
from ..project_variables import PACKAGE_ROOT


# Exposed methods:

@eel.expose
def get_popup(file_name: str) -> str:
    """Retrieves and returns HTML code of relevant pop-up / dialog
    window.
    
    Args:
        file_name (str): Name of HTML file containing popup code (without
            .html extension)

    Returns:
        str: HTML code of relevant pop-up / dialog window.
    """
    path = PACKAGE_ROOT / f"web/html/popups/{file_name}.html"
    return path.read_text(encoding="utf-8")


# Non-exposed methods:

def inform_empty_container(
        message: str,
        container_id: str,
        **placeholder_replacements: str
) -> None:
    """Adds specific message that notifies the user if there is nothing to
    currently display in a specific container.

    Args:
        message (str): Message text that will be displayed.
        container_id (str): ID of HTML element that will have the message
            added to it.
        **placeholder_replacements (str): Actual words or phrases that will
            replace potential placeholders inside of the message text.
    """
    if placeholder_replacements:
        message = message.format(**placeholder_replacements)

    add_empty_container_message(message, container_id)
