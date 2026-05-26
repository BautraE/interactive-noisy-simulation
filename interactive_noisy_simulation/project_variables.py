# =================================================================
# Shared project-level variables and singleton instances.
# =================================================================

# Functionality-related imports:
# Standard library imports:
from importlib import resources


# Project directory paths:
PACKAGE_ROOT = resources.files("interactive_noisy_simulation")


# Sharable class objects:
# - Specific instance managers:
from .core.instance_managers.noise_data_manager import NoiseDataManager
noise_data_manager = NoiseDataManager()

from .core.instance_managers.noise_creator import NoiseCreator
noise_creator = NoiseCreator()

from .core.instance_managers.circuit_manager import CircuitManager
circuit_manager = CircuitManager()

from .core.instance_managers.experiment_manager import ExperimentManager
experiment_manager = ExperimentManager()

# - Log manager:
from .core.logs.log_manager import LogManager
log_manager = LogManager()

# - Key blocker:
from .core.key_blocker import KeyBlocker
key_blocker = KeyBlocker()


# Static project data:
from .data._data import (
    EMPTY_CONTAINER_MESSAGES,
    LOG_MESSAGES, 
    TERMINAL_MESSAGES,
    TERMINAL_COMMAND_DESCRIPTION
)
