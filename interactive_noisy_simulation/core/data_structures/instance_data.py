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
    actions: str = field(default_factory=list)
