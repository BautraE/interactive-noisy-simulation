# Standard library imports:
import subprocess
import sys

# Local project imports:
from ._console import console
from ..data._data import TERMINAL_MESSAGES


def main() -> None:
    """Executes update process for the package."""
    update_url = sys.argv[1]
    
    console.print(TERMINAL_MESSAGES["updating_version"])

    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-qq", update_url],
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode == 0:
        console.print(TERMINAL_MESSAGES["update_successful"])
    else:
        console.print(TERMINAL_MESSAGES["update_failed"].format(
            error=result.stderr.strip()
        ))


if __name__ == "__main__":
    main()
