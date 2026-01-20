# Standard library imports:
from datetime import datetime


class LogManager:
    def __init__(self) -> None:
        """Constructor method """
        self._messages: dict = {}
        self._errors: dict = {}


    @property
    def messages(self) -> dict:
        return self._messages


    def add_message(
            self,
            message_text: str | dict,
            **placeholder_strings: str
    ) -> None:
        time = datetime.now()
        timestamp = time.strftime("%Y/%m/%d %H:%M:%S")
        key = time.strftime("%Y%m%d_%H%M%S%f")

        if isinstance(message_text, dict):
            message_text = message_text["text"]
        if placeholder_strings:
            message_text = message_text.format(**placeholder_strings)

        new_message = {}
        new_message["timestamp"] = f"[{timestamp}]"
        new_message["message_text"] = message_text
        
        self.messages[key] = new_message


    def delete_message(
            self, 
            message_id: str
    ) -> None:
        del self._messages[message_id]


    def delete_all_messages(self) -> None:
        self._messages.clear()


log_manager = LogManager()
