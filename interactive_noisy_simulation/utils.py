# =================================================================
# Custom utility functions that are to be used throughout INS
# =================================================================

# Third-party imports:
from psutil import virtual_memory


def optional_int(
    value: str | None
) -> int | None:
    """Converts and returns the correcty type of value in cases of
    optional integer values (either `int` or `None`).

    Fixes issues, where JS sends over integers as strings through
    the functionality of `Python Eel`.

    Custom utility function.

    Args:
        value (str | None): Number in the form of `string`. Could also be
            `None`, as some arguments are optional.

    Returns:
        int | None: Either the value as `int`, or `None` otherwise.
    """
    if not value:
        return None
    return int(value)


# Multiplier for available memory calculations - used for leaving a bit of
# additional memory free, because Qiskit may not want to run circuits if
# the calculations are too precise in cases where the memory requirements
# are reaching the available memory amount.
AVAILABLE_MEMORY_MULTIPLIER = 0.9

def get_available_memory(
    unit: str = "b"
) -> float:
    """Obtains and returns available memory (RAM) on the device. (used for
    defining *Qiskit* simulator restrictions)
    
    This function supports only the following measurement units:
    `b`; `kb`; `mb`.

    Args: 
        unit (str): Measurement unit.

    Returns:
        int: Amount of available memory.    
    """
    memory = float(virtual_memory().available * AVAILABLE_MEMORY_MULTIPLIER)

    units = ["b", "kb", "mb"]
    for current_unit in units:
        if current_unit == unit:
            break
        memory /= 1024

    return memory


def format_message_text(
    message: str,
    **placeholder_replacements: str
) -> str:
    """Replaces all placeholders within the given message text with provided
    placeholder replacement values.

    Args:
        message (str): Message text that will be formatted.
        **placeholder_replacements (str): Actual words or phrases that will
            replace potential placeholders inside of the message text.
    
    Returns:
        str: Formatted message text with replaced placeholders.
    """
    if placeholder_replacements:
        message = message.format(**placeholder_replacements)

    return message
