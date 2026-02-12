# Third party imports:
import eel

# Project-related imports:
from ..project_variables import PACKAGE_ROOT


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
