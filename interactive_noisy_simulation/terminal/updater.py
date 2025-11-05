# Standard library imports:
import subprocess
import sys


def main() -> None:
    """Executes update process for the package."""
    update_url = sys.argv[1]
    print("\nUpdating Interactive Noisy Simulation..")

    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-qq", update_url],
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode == 0:
        print("Package Interactive Noisy Simulation has been updated successfully!")
        print("Press ENTER to continue.")
    else:
        print("Update failed:")
        print(result.stderr.strip())
        print("Press ENTER to continue.")


if __name__ == "__main__":
    main()
