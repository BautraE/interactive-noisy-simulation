# Standard library imports:
import argparse

# Local project imports:
from .terminal._console import RichHelpFormatter
from .terminal.version_control import update_version, check_version
from .data._data import TERMINAL_COMMAND_DESCRIPTION


def main() -> None:
    """Provides terminal command functionality.
    
    Currently supports the following commands:
    - `interactive_noisy_simulation [-h | --help]`
    - `interactive_noisy_simulation [-u | --update]`
    - `interactive_noisy_simulation [-v | --version]`
    """
    parser = argparse.ArgumentParser(
        prog="interactive_noisy_simulation",
        description=TERMINAL_COMMAND_DESCRIPTION["help"],
        formatter_class=RichHelpFormatter
    )

    # Possible arguments:
    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "-u", "--update",
        action="store_true",
        help=TERMINAL_COMMAND_DESCRIPTION["update"],
    )

    group.add_argument(
        "-v", "--version",
        action="store_true",
        help=TERMINAL_COMMAND_DESCRIPTION["version"],
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
