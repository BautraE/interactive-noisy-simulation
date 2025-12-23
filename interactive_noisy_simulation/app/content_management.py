# Third party imports:
import eel


def add_table(
        container_id: str, 
        table_id: str,
        columns: list[str] = [],
        has_actions: bool = False
) -> None:
    eel.addTable(container_id, table_id, columns, has_actions)


def add_table_row(
        table_id: str, 
        row_content: list[str],
        actions: list[dict] = []
) -> None:
    eel.addTableRow(table_id, row_content, actions)


def add_message(
        container_id: str,
        message: str | dict,   
        highlightables: list[str] = [],
        **placeholder_strings: str
) -> None:
    if isinstance(message, dict):
        message_text = message["text"]
        highlightables = message["highlightables"]
    else: 
        message_text = message

    if placeholder_strings:
        message_text = message_text.format(**placeholder_strings)
        highlightables = [
            hl.format(**placeholder_strings) for hl in highlightables]

    # message_text = self.__modify_message(message_text, highlightables)
    
    eel.addMessage(container_id, message_text)


def remove_container_content(
        container_id: str
) -> None:
    eel.removeContainerContent(container_id)


def add_content_box(
        container_id: str,
        box_id: str
) -> None:
    eel.createContentBox(container_id, box_id)
