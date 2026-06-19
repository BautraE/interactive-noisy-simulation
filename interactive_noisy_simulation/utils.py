# =================================================================
# Custom utility functions that are to be used throughout INS
# =================================================================

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
