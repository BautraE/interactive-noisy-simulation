# =================================================================
# Python wrappers for JS function calling
# Related to: no specific file as these functions are commonly
# used.
# =================================================================

# Third party imports:
import eel


# --------------------------------------------------------------
# Container management
# --------------------------------------------------------------

def remove_container_content(
        container_id: str
) -> None:
    """Clears (deletes) all child elements from a parent element based on
    its ID.

    Wrapper function for `Python Eel` JS function call.

    Args:
        container_id (str): ID of container whose child elements will be
            cleared.
    """
    eel.removeContainerContent(container_id)


def add_content_box(
        container_id: str,
        box_id: str
) -> None:
    """Adds content box inside specific container for the purpose housing
    some kind of data or information.

    Wrapper function for `Python Eel` JS function call.

    Args:
        container_id (str): ID of the container element where the newly
            created content box will be placed.
        box_id (str): Id of the newly created content box.
    """
    eel.createContentBox(container_id, box_id)


# --------------------------------------------------------------
# Data table creation
# --------------------------------------------------------------

def add_table(
        container_id: str, 
        table_id: str,
        columns: list[str] = [],
        has_actions: bool = False
) -> None:
    """Adds table inside specific container for the purpose of displaying
    some kind of data.

    Wrapper function for `Python Eel` JS function call.

    Args:
        container_id (str): ID of the container element where the newly
            created table will be placed.
        table_id (str): ID attribute value that will be set for the table
            so that it can be accessed further on.
        columns (list[str]): List of column names that will be set in the
            header row of the table. If none are given, no table header row
            is created (`Default = []`).
        has_actions (bool): Boolean flag value for whether or not the table
            should contain an additional column - Actions.
    """
    eel.addTable(container_id, table_id, columns, has_actions)


def add_table_row(
        table_id: str, 
        row_content: list[str],
        actions: list[str] = []
) -> None:
    """Creates new row with given data and adds it to the table with the 
    specified ID.

    Wrapper function for `Python Eel` JS function call.

    Note: There is no validation intended to check whether data row cell
    count exceeds the cell count of the tables header row.

    Args:
        table_id (str): ID of table, to which the new row shall be added.
        row_content (list[str]): List of row table cell content.
        actions (list[str]): List of action strings that serve as both
            visible action link names and action type identifiers.
            (`Default = []`)
    """
    eel.addTableRow(table_id, row_content, actions)


# --------------------------------------------------------------
# General content-related functions
# --------------------------------------------------------------

def add_empty_container_message(
        message: str, 
        container_id: str
) -> None:
    """Calls JS function to display specific message that notifies 
    that there is nothing to currently display in a specific 
    container.

    Wrapper function for `Python Eel` JS function call.

    Args:
        message (str): Text of the message that will be shown.
        container_id (str): ID of the HTML element to which the message 
            will be added to.
    """
    eel.addEmptyContainerMessage(message, container_id)
