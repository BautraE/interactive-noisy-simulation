# Standard library imports:
from dataclasses import dataclass

# Local project imports:
from ...project_variables import USED_CSV_COLUMNS

# Imports only used for type definition:
from pandas import DataFrame
from typing import Any
from .file import File


@dataclass
class NoiseDataInstance:
    """Class for storing a noise data instance.
    
    Attributes:
        reference_key (str): Key by which the specific object is accessed 
            in other places of the INS app.
        source_file (File): Imported calibration data file used to create 
            this instance.
        dataframe (Dataframe): `Pandas` dataframe that contains all relevant
            calibration data for noise model creation.
    """
    reference_key: str
    source_file: File
    dataframe: DataFrame


    def get_qubit_count(self) -> int:
        """Retrieves qubit count in current dataframe.
        
        Returns:
            int: Number of qubits in dataframe.
        """
        return len(self.dataframe)


    def get_qubit_data(
            self, 
            qubit_nr: int
    ) -> dict[str, Any]:
        """Retrieves and returns all available noise data about for a 
        specific qubit.
        
        Returned format is a dictionary, where:
            Key: name - type of data
            Value: data value

        Args:
            qubit_nr (int): Number of the qubit, for which the data will
                be found. 

        Returns:
            dict[str, Any]: Retrieved noise data for a specific qubit.
        """
        qubit_data = {}

        for column_reference, column in USED_CSV_COLUMNS.items():
            if column_reference in self.dataframe.columns:
                name = column["name"]
                value = self.dataframe.loc[qubit_nr, column_reference]
                qubit_data[name] = value
        
        return qubit_data
