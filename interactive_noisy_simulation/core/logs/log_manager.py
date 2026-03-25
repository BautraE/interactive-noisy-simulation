# Standard library imports:
from datetime import datetime


class LogManager:
    def __init__(self) -> None:
        """Constructor method."""
        self._messages: dict = {}


    @property
    def messages(self) -> dict:
        """Returns a reference to data structure containing log
        message instances."""
        return self._messages


    def add_message(
            self,
            message: dict,
            **placeholder_replacements: str
    ) -> None:
        """Creates new message instance for log.

        Args:
            message (dict): Readable message text. Must be a dictionary
                based on the format seen inside of `messages.json`, under
                the key "log" (required for highlighting functionality).
            **placeholder_replacements (str): Keyword arguments that will
                replace any placeholders in message templates.
        """
        time = datetime.now()
        timestamp = time.strftime("%Y/%m/%d %H:%M:%S")
        key = time.strftime("%Y%m%d_%H%M%S%f")

        message_text = message["text"]
        highlightables = message["highlightables"]
        if placeholder_replacements:
            message_text = message_text.format(**placeholder_replacements)
            highlightables = [
                hl.format(**placeholder_replacements) for hl in highlightables]

        new_message = {}
        new_message["timestamp"] = f"[{timestamp}]"
        new_message["message_text"] = message_text
        new_message["highlightables"] = highlightables
        
        self.messages[key] = new_message


    def delete_message(
            self, 
            message_id: str
    ) -> None:
        """Deletes a specific log message instance based on its ID.

        Args:
            message_id (str): ID of deletable message instance.
        """
        del self._messages[message_id]


    def delete_all_messages(self) -> None:
        """Deletes all currently stored log message instances."""
        self._messages.clear()
