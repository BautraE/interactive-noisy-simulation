# Standard library imports:
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class File:
    """Dataclass for defining and storing information about files.
    
    Attributes:
        path (Path): Path object of the file.
        full_path (str): Full file path on local device as a string.
        name (str): Name of the file (with file extension).
    """
    path: Path = field(init=False)
    full_path: str = field(init=False)


    def __init__(self, path_string: str):
        """Constructor method """
        self.path = Path(path_string)
        self.full_path = str(self.path.resolve())


    @property
    def name(self) -> str:
        """Returns name of file (with file extension)."""
        return self.path.name
