# The following classes define project specific errors that get raised
# as part of Interactive Noisy Simulation (INS) functionality.

# Project-related base error classes:
class INSError(Exception):
    """"Base error class for Interactive Noisy Simulation project-related
    errors."""
    def __init__(self, message: dict, **placeholders: str):
        self.message = message
        self.placeholders = placeholders

        super().__init__("INSError")

# Error subclasses of INSError:

class SimulationError(INSError):
    """Raised when an error occured related to the simulation process."""
