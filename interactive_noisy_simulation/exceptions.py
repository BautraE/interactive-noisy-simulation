# The following classes define project specific errors that get raised
# as part of Interactive Noisy Simulation (INS) functionality.

# Project-related base error classes:
class INSError(Exception):
    """"Base error class for Interactive Noisy Simulation project-related
    end-user-caused errors. Raised in cases of incorrect usage of available 
    functionality."""

class DeveloperError(Exception):
    """"Base error class for Interactive Noisy Simulation project-related
    developer-caused errors."""

# Error subclasses of INSError:

class BlockedKeyError(INSError):
    """Raised when user specified new instance key is currently blocked and
    cannot be used for any new instance of a specific type."""

class InputArgumentError(INSError):
    """Raised when error is related to user method argument input."""

class KeyExistanceError(INSError):
    """Raised when error is related to instance key existance.
    
    This would, for example, include situations where:
    - Key should exist, but does not.
    - Key should not exist, but does.
    """

class MissingLinkError(INSError):
    """Raised when required link between some class objects does not exist."""
