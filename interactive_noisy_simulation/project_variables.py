# =================================================================
# Shared project-level variables and singleton instances.
# =================================================================

# Standard library imports:
from importlib import resources

# Project-related imports:
from .core.logs.log_manager import LogManager
from .core.instance_managers.noise_creator import NoiseCreator
from .core.instance_managers.noise_data_manager import NoiseDataManager


# Project directory paths:
PACKAGE_ROOT = resources.files("interactive_noisy_simulation")

# Sharable manager class objects:
# - Specific instance managers:
noise_data_manager = NoiseDataManager()
noise_creator = NoiseCreator()
# - Log manager:
log_manager = LogManager()
