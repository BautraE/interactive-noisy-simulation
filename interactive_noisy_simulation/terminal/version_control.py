# Standard library imports:
import subprocess
import sys

# Third party imports:
import requests

# Local project imports:
from ..VERSION import __version__


REPOSITORY_URL = "https://github.com/BautraE/interactive-noisy-simulation"
# API for obtaining info on latest release
LATEST_RELEASE_API = "https://api.github.com/repos/BautraE/interactive-noisy-simulation/releases/latest"


# Main functions

def check_version() -> None:
    """Prints out the current version of the package."""
    print(f"Interactive Noisy Simulation v{__version__}")


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
        print(f"The current version is outdated.")
        print(f"Able to update from v{current_version} to v{latest_version}.")

        user_choice = input(f"Do you want to update Interactive Noisy Simulation? [y|n]\n")
        if user_choice == "y":
            update_url = f"{REPOSITORY_URL}/archive/refs/tags/v{latest_version}.zip"
            __install_update(update_url)
        else:
            print("Cancelling update.")
    else:
        print(f"Current version v{current_version} is already up-to-date!")


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
        print(f"An error occured: {e}")
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
