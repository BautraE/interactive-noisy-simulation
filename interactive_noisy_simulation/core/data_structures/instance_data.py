# Standard library imports:
from dataclasses import dataclass, field


@dataclass
class InstanceData():
    """Dataclass for returned displayable instance data.

    Each `action` results in an additional link in the HTML table for the
    specific instance type (noise data, noise model, etc.)
    
    Attributes:
        columns (list[str]): List of column names for table.
        rows (list[list[str]]): List of rows (also lists) that contain
            table row data.
        actions (str): List of actions that will appear for every
            row of table data in the rendered HTML.
    """
    columns: list[str]
    rows: list[list[str]]
    actions: list[str] = field(default_factory=list)


    def add_collumn(
            self,
            name: str,
            content: list[str]
    ) -> None:
        """Adds new column with content to retrieved instance data.

        Args:
            name (str): Name of column.
            comtemts (list[str]): List of content for new column.
        """
        self.columns.append(name)
        for row, data in zip(self.rows, content):
            row.append(data)


    def to_dict(self) -> dict:
        """Returns contents of self in the form of a dictionary.

        Dictionary keys match the variable names from this dataclass.

        Returns:
            dict: Dataclass contents.
        """
        dictionary = {
            "columns": self.columns,
            "rows": self.rows,
            "actions": self.actions
        }
        return dictionary
