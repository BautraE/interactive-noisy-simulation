# Standard library imports:
from dataclasses import dataclass

# Local project imports:
from ...data._data import CSV_COLUMNS

# Imports only used for type definition:
from pandas import DataFrame
from typing import Any
from .file import File


@dataclass
class NoiseDataInstance:
    """Class for storing a noise data instance.
    
    Attributes:
        source_file (File): Imported calibration data file used to create 
            this instance.
        dataframe (Dataframe): `Pandas` dataframe that contains all relevant
            calibration data for noise model creation.
    """
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

        for column in CSV_COLUMNS.values():
            if column["csv_name"] in self.dataframe.columns:
                name = column["name"]
                value = self.dataframe.loc[qubit_nr, column["csv_name"]]
                qubit_data[name] = value
        
        return qubit_data
