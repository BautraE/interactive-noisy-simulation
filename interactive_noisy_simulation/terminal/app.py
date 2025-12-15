# Standard library imports:
from importlib import resources

# Third party imports:
import eel

# Project-related imports:
from ._console import console
from ..data._data import TERMINAL_MESSAGES


def start_app() -> None:
    """Starts the Interactive Noisy Simulation (INS) app."""
    console.print(TERMINAL_MESSAGES["starting_app"])

    # Initialize Python Eel and point to 'web' folder
    with resources.path("interactive_noisy_simulation", "web") as app_path:
        eel.init(str(app_path))

    # Starting INS
    port = __get_free_port()
    eel.start('index.html', port=port, size=(800, 600))


def __get_free_port() -> int:
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
