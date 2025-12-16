# Local project imports:
from ..exceptions import KeyExistanceError
from ..messages.helpers.text_styling import style_text_status
from ..messages._message_manager import message_manager as msg
from ...data._data import ERRORS

# Imports only used for type definition:
from typing import Any


def check_source_availability(
        source_reference_key: str,
        source_instances: dict[str, Any]
) -> str:
    """Checks if the source instance with the specified reference key
    still exists.
    
    Additionally, respective status text styling is added.

    Args:
        source_reference_key (str): Reference key of source instance.
        source_instances (dict[str, Any]): Data structure containing
            all currently created source instances.
    
    Returns:
        str: Availability status message with respective styling:
            - "Available" with green text color.
            - "Removed" with red text color.
    """
    if check_instance_key(reference_key=source_reference_key,
                          instances=source_instances,
                          should_exist=True,
                          instance_type="",
                          raise_error=False):
        availability = style_text_status("Available", "SUCCESS")
    else: 
        availability = style_text_status("Removed", "FAILED")
    
    return availability


def check_instance_key(
        reference_key: str,
        should_exist: bool,
        instances: dict,
        instance_type: str,
        raise_error: bool = True 
) -> bool:
    """Checks if the given key is linked to an existing instance.

    Args:
        reference_key (str): The reference key that will be checked.
        should_exist (bool): Should the reference key exist among the
            current instances (switches between two modes of checking).
        instances (dict): Data structure containing instances that need
            to be checked based on the given `reference_key` (does that
            instance exist or not).
        instance_type (str): Message fragment that will be used in the
            case of an exception. The error message is currently made so
            that it can be reused in more than one scenario by replacing
            placeholders with appropriate message fragments.
        raise_error (bool): Should an error be raised (Default = True). 
            If left set as `False`, the bool value `False` will be returned
            instead of an exception.

    Returns:
        bool:
            - `True` if an instance with the requested key exists.
            - `False` if an instance with the requested key does not exist.
 
    Raises:
        KeyExistanceError: If an instance with the requested key does not
            exist and it was not specified to not raise an exception 
            (instead of returning `False`, it will just raise an exception).
    """
    # If key should exist among current instances
    if should_exist:
        if reference_key in instances:
            return True
        
        elif raise_error:
            raise KeyExistanceError(
                    ERRORS["no_key_instance"].format(
                        instance_type=instance_type,
                        reference_key=reference_key))
        else:
            return False
    # If key should not exist among current instances    
    else:
        if not reference_key in instances:
            return True
    
        elif raise_error:
            raise KeyExistanceError(
                    ERRORS["instance_key_exists"].format(
                        instance_type=instance_type,
                        reference_key=reference_key))
        else:
            return False
