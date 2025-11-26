# Standard library imports:
import os, re

# Local project imports:
from ..exceptions import FileTypeError
from ..messages._message_manager import message_manager as msg
from ..data._data import (
    ERRORS, MESSAGES
)


def validate_file_type(
        file_path: str,
        expected_ext: tuple[str, ...]
) -> None:
    """Validates user input file types.
    
    Args:
        file_path (str): Path to the selected file.
        expected_ext (tuple[str, ...]): List of acceptable file
            extensions in the form of a string tuple.
    
    Raises:
        FileTypeError: if current file type does not match any of the 
            required ones.
    """
    if not file_path.endswith(expected_ext):
        _, current_ext = os.path.splitext(file_path)
        raise FileTypeError(
            ERRORS["incorrect_file_type"].format(current_ext=current_ext,
                                                 expected_ext=expected_ext))


def validate_instance_name(
        new_instance_key: str
) -> str:
    """Modifies reference key for new instance.

    If there are empty spaces present in the user specified reference
    key, they will be replaced by the symbol "_", as well as an
    additional message stating this will be displayed.

    Args:
        new_instance_key (str): Reference key for a new instance, which
            needs to be checked and potentially modified.

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
