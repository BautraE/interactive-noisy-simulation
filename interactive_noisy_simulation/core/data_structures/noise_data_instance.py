# Standard library imports:
from dataclasses import dataclass

# Local project imports:
from ...data._data import CSV_COLUMNS, ERRORS
from ..exceptions import InputArgumentError

# Imports only used for type definition:
from pandas import DataFrame
from typing import Any

@dataclass
class NoiseDataInstance:
    """Class for storing a noise data instance.
    
    Attributes:
        file_name (str): Name of *CSV* file that calibration data was imported
            from.
        full_path (str): Full local file path to the imported *CSV* file. 
            It is used purely for infomative purposes for the end-user - the
            data is only stored locally on the user's device.
        dataframe (Dataframe): `Pandas` dataframe that contains all relevant
            calibration data for noise model creation.
    """
    file_name: str
    full_path: str
    dataframe: DataFrame


    def get_qubit_count(
            self
    ) -> int:
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
    

    def validate_qubit_number(
            self, 
            qubit_nr: int
    ) -> None:
        """Validates if the specified qubit number refers to a valid
        qubit within the dataframe.

        Method checks if the passed qubit number is above 0 and below 
        the max index of qubits in the current dataframe.

        Args:
            qubit_nr (int): Qubit number that will get checked.

        Raises:
            InputArgumentError:
                - If qubit number is lower than 0;
                - If qubit number exceeds max qubit number.
        """
        qubit_count = self.get_qubit_count() - 1
            
        if qubit_nr < 0:
            raise InputArgumentError(
                ERRORS["negative_qubit_number"].format(
                    qubit=qubit_nr))
        
        elif qubit_nr > qubit_count:
            raise InputArgumentError(ERRORS["large_qubit_number"].format(
                qubit=qubit_nr,
                max_qubits=qubit_count))
