# Functions used for applying certain styles to texts before they are sent
# to be rendered somewhere in an output box.

# Standard library imports:
import re

# Local project imports:
from ...exceptions import DeveloperError
from ....data._data import ERRORS


def style_text_status(
        text: str,
        status: str
) -> str:
    """Adds specified status style to the given text.

    The status style depends on the passed status int value:
    - 'FAILED': Failed / Unavailable (`red` color)
    - 'SUCCESS': Success / Completed / Available (`green` color)

    NOTE: This function is only used for setting style of content-related
    text. It does not set the status of output box processes (bottom right 
    corner of output box).
    
    Args:
        text (str): Text that needs style added to it.
        status (str): Specified status, based on which the specific
            style will be set.

    Returns:
        str: Modified text with added HTML style elements.
    """
    STATUSES = {
        'FAILED': "removed-instance",
        'SUCCESS': "available-instance"
    }

    if status not in STATUSES:
        valid_statuses = list(STATUSES.keys())
        raise DeveloperError(ERRORS["invalid_status"].format(
            invalid_status=status,
            valid_statuses=valid_statuses))
    
    css_class = STATUSES.get(status)

    return f"<span class='{css_class}'>{text}</span>"


def style_file_path(
        text: str
) -> str:
    """Adds specific custom style for file path text.

    In theory, any text can be passed here, but the specific
    separator symbols will be highlighted only if they are
    present in the text.
    
    Args:
        text (str): Text that needs style added to it.

    Returns:
        str: Modified text with added HTML style elements.
    """
    new_text = re.sub(
        pattern=r'[\\/]', 
        repl=lambda m: 
            f"<span class='path-separators'>{m.group(0)}</span>",
        string=text)
    return f"<span class='path-texts'>{new_text}</span>"


def style_highlight( 
        text: str,
        message: str = "", 
        start_position: int = 0, 
        end_position: int = 0
) -> str:
    """Adds highlight style to given text.

    Accomplished by adding specific `span` *HTML* tags around
    highlightable parts.

    By default (if only the argument `text` is provided), this function
    highlights the entire given text. 

    If the other arguments are given, there will be a different result.
    It will take the current message and add `span` *HTML* tags around 
    the highlightable `message` fragment (argument `text`). This is 
    accomplished with the start and end position of the highlightable 
    part by creating a new message that consists of:
        1. everything before the highlightable part;
        2. the highlightable fragment with added HTML tags;
        3. everything after the highlightable part.

    Args:
        text (str): Text that will be highlighted (highlightable).
        message (str): Message that the `highlightable` text is part of.
            (Default: `""`)
        start_position (int): Start position of the highlightable
            fragment inside of the entire message.(Default: `0`)
        end_position (int): End position of the highlightable
            fragment inside of the entire message.(Default: `0`)
    
    Returns:
        str: Only the highlighted `text` or the entire message, where
            `text` fragments are highlighted.
    """
    highlighted_text = f"<span class='highlighted-text'>{text}</span>"
    return message[:start_position] + highlighted_text + message[end_position:]


def style_italic(
        text: str
) -> str:
    """Adds italic style to the given text.
    
    Args:
        text (str): Text that needs style added to it.

    Returns:
        str: Modified text with added HTML style elements.
    """
    return f"<i>{text}</i>"
