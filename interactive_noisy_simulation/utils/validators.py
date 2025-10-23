# Standard library imports:
import re

# Local project imports:
from ..data._data import (
    ERRORS, MESSAGES
)

# Imports only used for type definition:
from ..messages._message_manager import MessageManager


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
        KeyError: If an instance with the requested key does not exist and
            it was not specified to not raise an exception (instead of
            returning `False`, it will just raise an exception).
    """
    # If key should exist among current instances
    if should_exist:
        if reference_key in instances:
            return True
        
        elif raise_error:
            raise KeyError(
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
            raise KeyError(
                    ERRORS["instance_key_exists"].format(
                        instance_type=instance_type,
                        reference_key=reference_key))
        else:
            return False


def validate_instance_name(
        new_instance_key: str,
        msg: MessageManager
) -> str:
    """Modifies reference key for new instance.

    If there are empty spaces present in the user specified reference
    key, they will be replaced by the symbol "_", as well as an
    additional message stating this will be displayed.

    Args:
        new_instance_key (str): Reference key for a new instance, which
            needs to be checked and potentially modified.
        msg (MessageManager): Currently used `MessageManager` instance
            through which a message can be added if required.

    Returns:
        str: Reference key that will be used for the newly created 
            instance.
    """
    if " " in new_instance_key:
        new_instance_key = re.sub(
            pattern=r' ', 
            repl='_', 
            string=new_instance_key)
        msg.add_message(MESSAGES["modified_reference_key"],
                        reference_key=new_instance_key)
        
    return new_instance_key
