# Standard library imports:
import argparse

# Local project imports:
from .terminal.version_control import update_version, check_version

def main() -> None:
    """Provides terminal command functionality.
    
    Currently supports the following commands:
    - `interactive_noisy_simulation [-h | --help]`
    - `interactive_noisy_simulation [-u | --update]`
    - `interactive_noisy_simulation [-v | --version]`
    """
    parser = argparse.ArgumentParser(
        prog="interactive_noisy_simulation",
        description="Interactive Noisy Simulation package.\n Any functionality that is accessed through the terminal is only related to package management and not the functionality that it provides."
    )

    # Possible arguments:
    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "-u", "--update",
        action="store_true",
        help= "Checks if a newer version is available. If yes, the package gets updated."
    )

    group.add_argument(
        "-v", "--version",
        action="store_true",
        help= "Prints current version of package and tells if there is a newer version."
    )

    # Functionality access based on arguments
    args = parser.parse_args()
    if args.update:
        update_version()
    elif args.version:
        check_version()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
