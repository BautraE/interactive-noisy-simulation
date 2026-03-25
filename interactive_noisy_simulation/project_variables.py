# =================================================================
# Shared project-level variables and singleton instances.
# =================================================================

# Functionality-related imports:
# Standard library imports:
from importlib import resources


# Project directory paths:
PACKAGE_ROOT = resources.files("interactive_noisy_simulation")


# Sharable manager class objects:
# - Specific instance managers:
from .core.instance_managers.noise_data_manager import NoiseDataManager
noise_data_manager = NoiseDataManager()

from .core.instance_managers.noise_creator import NoiseCreator
noise_creator = NoiseCreator()

# - Log manager:
from .core.logs.log_manager import LogManager
log_manager = LogManager()


# Static project data:
from .data._data import (
    EMPTY_CONTAINER_MESSAGES,
    LOG_MESSAGES, 
    TERMINAL_MESSAGES,
    TERMINAL_COMMAND_DESCRIPTION
)
