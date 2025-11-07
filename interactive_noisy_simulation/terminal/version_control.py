# Standard library imports:
import subprocess
import sys

# Third party imports:
import requests

# Local project imports:
from ._console import console
from ..VERSION import __version__
from ..data._data import TERMINAL_MESSAGES


REPOSITORY_URL = "https://github.com/BautraE/interactive-noisy-simulation"
# API for obtaining info on latest release
LATEST_RELEASE_API = "https://api.github.com/repos/BautraE/interactive-noisy-simulation/releases/latest"


# Main functions

def check_version() -> None:
    """Prints out the current version of the package."""
    console.print(TERMINAL_MESSAGES["current_version"].format(
        version=__version__))


def update_version() -> None:
    """Checks for latest version and asks user for update decision.
    
    If there is a newer version available in the *GitHub* repository, the
    user is asked if he wishes to proceed with the update. If the user
    agrees, another function is called for the update process.

    If either there is no newer version in the *GitHub* repository or the
    user does not want to update, nothing happens.
    """
    current_version = __version__
    latest_version = __get_latest_version()
    if latest_version == "error": return

    if __is_version_newer(current_version, latest_version):
        console.print(TERMINAL_MESSAGES["outdated_version"].format(
            current_version=current_version,
            latest_version=latest_version))

        console.print(TERMINAL_MESSAGES["confirm_update"])
        user_choice = input()
        if user_choice == "y":
            update_url = f"{REPOSITORY_URL}/archive/refs/tags/v{latest_version}.zip"
            __install_update(update_url)
        else:
            console.print(TERMINAL_MESSAGES["update_cancelled"])
    else:
        console.print(TERMINAL_MESSAGES["version_up_to_date"].format(
            current_version=current_version))


# Helper functions for main functions in this file

def __get_latest_version() -> str:
    """Retrieves the latest package version from *GitHub*.
    
    Returns:
        str: 
            - Latest package release version on project *GitHub* 
            repository. Version returns in the form of: `x.y.z`
            - In case of error, the string "error" is returned.
    """
    try:
        response = requests.get(url=LATEST_RELEASE_API,
                                timeout=10)
        response.raise_for_status()
        release_data = response.json()
        version = release_data["tag_name"].strip("v")
    except Exception as e:
        console.print(TERMINAL_MESSAGES["error"].format(
            error=e))
        return "error"

    return version


def __install_update(
        update_url: str
) -> None:
    """Creates separate process for updating package.
    
    Current project implementation prohibits removing current package
    version files while it is also running. Thus this workaround is
    required.

    Args:
        update_url (str): URL for downloading the latest package version.
    """
    subprocess.Popen(
        [sys.executable, "-m", 
         "interactive_noisy_simulation.terminal.updater", update_url],
    )
    sys.exit(0)


def __is_version_newer(
        current_version: str,
        latest_version: str
) -> bool:
    """Compares current and latest version from repository.
    
    Args:
        current_version (str): Version of *Interactive Noisy Simulation*
            that is currently installed.
        latest_version (str): Latest version of *Interactive Noisy 
            Simulation* that is available in *GitHub* releases.

    Returns:
        bool: Is latest version newer than current.
    """
    newer = False
    current_numbers = current_version.split(".")
    latest_numbers = latest_version.split(".")

    for i in range(3):
        if int(current_numbers[i]) > int(latest_numbers[i]):
            break
        elif int(current_numbers[i]) < int(latest_numbers[i]):
            newer = True
            break

    return newer
