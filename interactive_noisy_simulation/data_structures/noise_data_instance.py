# Standard library imports:
from dataclasses import dataclass

# Imports only used for type definition:
from pandas import DataFrame

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
