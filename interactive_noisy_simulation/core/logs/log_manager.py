# Standard library imports:
from datetime import datetime

# Project-related imports:
from ...utils import format_message_text


class LogManager:
    def __init__(self) -> None:
        """Constructor method."""
        self._messages: dict = {}
        self._errors: dict = {}


    # Class properties
    
    @property
    def messages(self) -> dict:
        """Returns a reference to data structure containing log
        message entries."""
        return self._messages
    

    @property
    def errors(self) -> dict:
        """Returns a reference to data structure containing log
        error entries."""
        return self._errors


    # Reusable functionality

    def _get_displayable_text(
        self,
        text: str,
        highlightables: list[str],
        **placeholder_replacements: str
    ) -> tuple[str, list[str]]:
        """Obtains and returns the final displayable text and list of 
        highlightable fragments for the text.

        Original text may contain placeholders that need to be replaced with 
        actual values - that is the goal of this function.

        Args:
            text (str): Readable text for log entries.
            highlightables (list[str]): List of highlightable text fragments
                (to be used for coloring in these specific fragments).
            **placeholder_replacements (str): Keyword arguments that will
                replace any placeholders in message templates.

        Returns:
            tuple[str, list[str]]: Final displayable text and list of 
                highlightable text fragments.
        """
        text = format_message_text(message=text,
                                   **placeholder_replacements)
        highlightables = [
            hl.format(**placeholder_replacements) for hl in highlightables]
        
        return text, highlightables
    

    def _get_time_info(self) -> tuple[str, str]:
        """Obtains and returns 2x time-based values used for new log entry 
        creation.
        
        The returned values are:
        - `key` of the newly creatable log entry;
        - `timestamp` of the moment, when the specific log entry is being
          created.

        Returns:
            tuple[str, str]: `key` and `timestamp` for the new log entry.
        """
        time = datetime.now()
        timestamp = time.strftime("%Y/%m/%d %H:%M:%S")
        key = time.strftime("%Y%m%d_%H%M%S%f")

        return key, timestamp


    # Log message entry management

    def add_message(
        self,
        content: str | dict,
        **placeholder_replacements: str
    ) -> None:
        """Creates new message entry for log.

        Args:
            content (str | dict): Log entry text. Must be a dictionary
                based on the format seen inside of `messages.json`, under
                the key "log" (required for highlighting functionality).
                String format functionality is primarily for development
                and testing purposes (or any potential specific situations).
            **placeholder_replacements (str): Keyword arguments that will
                replace any placeholders in message templates (from 
                `messages.json`).
        """
        
        key, timestamp = self._get_time_info()
        if isinstance(content, str):
            entry_text, highlightables = self._get_displayable_text(text=content,
                                                                    highlightables=[],
                                                                    **placeholder_replacements)
        else:
            entry_text, highlightables = self._get_displayable_text(text=content["text"],
                                                                    highlightables=content["highlightables"],
                                                                    **placeholder_replacements)

        new_message_entry = {}
        new_message_entry["timestamp"] = f"[{timestamp}]"
        new_message_entry["text"] = entry_text
        new_message_entry["highlightables"] = highlightables
        
        self._messages[key] = new_message_entry


    def delete_message(
        self, 
        entry_id: str
    ) -> None:
        """Deletes a specific message entry from log based on its ID.

        Args:
            entry_id (str): ID of deletable message entry.
        """
        del self._messages[entry_id]


    def delete_all_messages(self) -> None:
        """Deletes all currently stored message entries in log."""
        self._messages.clear()

    
    # Log error management

    def add_error(
        self,
        content: str | dict,
        **placeholder_replacements: str
    ) -> None:
        """Creates new error entry for log.

        Args:
            content (str | dict): Log entry error text. Must be a dictionary
                based on the format seen inside of `messages.json`, under
                the key "error" (required for highlighting functionality).
                String format functionality is primarily for development
                and testing purposes (or any potential specific situations).
            **placeholder_replacements (str): Keyword arguments that will
                replace any placeholders in message templates (from 
                `messages.json`).
        """
        
        key, timestamp = self._get_time_info()
        if isinstance(content, str):
            entry_text, highlightables = self._get_displayable_text(text=content,
                                                                    highlightables=[],
                                                                    **placeholder_replacements)
        else:
            entry_text, highlightables = self._get_displayable_text(text=content["text"],
                                                                    highlightables=content["highlightables"],
                                                                    **placeholder_replacements)

        new_error_entry = {}
        new_error_entry["timestamp"] = f"[{timestamp}]"
        new_error_entry["text"] = entry_text
        new_error_entry["highlightables"] = highlightables
        
        self._errors[key] = new_error_entry


    def delete_error(
        self, 
        error_id: str
    ) -> None:
        """Deletes a specific error entry from log based on its ID.

        Args:
            error_id (str): ID of deletable error instance.
        """
        del self._errors[error_id]


    def delete_all_errors(self) -> None:
        """Deletes all currently stored error entries in log."""
        self._errors.clear()
