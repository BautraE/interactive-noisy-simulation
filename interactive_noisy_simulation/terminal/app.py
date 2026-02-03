# Standard library imports:
from importlib import resources

# Third party imports:
import eel
from jinja2 import Environment, FileSystemLoader

# Project-related imports:
from ._console import console
from ..data._data import TERMINAL_MESSAGES
from ..VERSION import __version__

# Files with exposed Python functions/methods:
from ..app import exposed, logs


# Path to web folder of the INS app
PATH_APP_WEB = resources.files("interactive_noisy_simulation") / "web"


# =================================================================
#  Functions for starting the INS app
# =================================================================

def start_app() -> None:
    """Starts the Interactive Noisy Simulation (INS) app."""
    console.print(TERMINAL_MESSAGES["starting_app"])

    # Creating all page files from templates
    _build_pages()

    # Initialize Python Eel and point to 'web' folder
    eel.init(str(PATH_APP_WEB))

    # Starting INS
    port = _get_free_port()
    eel.start('generated_html/index.html', port=port, size=(1200, 800))


def _get_free_port() -> int:
    """Returns a usable port number.
    
    Returns:
        int: A currently free port number on the specific device.
    """
    import socket
    for port in range(8000, 8999):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(('localhost', port))
                return port
            except socket.error:
                continue


# =================================================================
#  HTML page file building functionality
# =================================================================

def _build_pages() -> None:
    """Creates final HTML files from templates."""
    RENDERABLE_PAGES = {
        # "noise_data_instances.html":
        "index.html":
        "instance_management/noise_data/all_instances.html",
        "noise_data_instance.html": 
        "instance_management/noise_data/single_instance.html"
    }
    
    with (
        resources.as_file(PATH_APP_WEB / "templates") as path_templates,
        resources.as_file(PATH_APP_WEB / "generated_html") as path_html
    ):
        env = Environment(loader=FileSystemLoader(path_templates))
        
        for html_file, template_file in RENDERABLE_PAGES.items():
            template = env.get_template(template_file)
            html_code = template.render(version=__version__)
            final_file = path_html / html_file
            # Create "html" directory if it does not exist and write content
            # in the final html file that was made from the templates.
            path_html.mkdir(exist_ok=True)
            final_file.write_text(data=html_code, encoding="utf-8")
