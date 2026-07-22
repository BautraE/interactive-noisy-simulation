#Third party imports:
import pandas

# Project-related imports:
from ..data_structures.file import File
from ..data_structures.noise_data_instance import NoiseDataInstance
from ..data_structures.instance_data import InstanceData
from .helpers.csv_modification import (
    add_additional_columns, modify_dataframe_data,
    remove_unnecessary_collumns,
    rename_dataframe_columns
)


class NoiseDataManager:

    # =========================================================================
    # Table of Contents for NoiseDataManager
    # =========================================================================
    # 1. Initialization (constructor method).
    # 2. Class properties.
    # 3. Noise data instance management - creating new instances, viewing and
    #       deleting existing ones.
    # 4. Retrieving qubit noise information - showing user noise data for
    #       requested qubits.
    # =========================================================================

    # =========================================================================
    # 1. Initialization (constructor method).
    # =========================================================================

    def __init__(self) -> None:
        """Constructor method """
        self.__noise_data: dict[str, NoiseDataInstance] = {}  

    
    # =========================================================================
    # 2. Class properties.
    # =========================================================================

    @property    
    def noise_data(self) -> dict[str, NoiseDataInstance]:
        """Returns a reference to data structure containing noise 
        data instances.
        
        Returns:
            dict[str, NoiseDataInstance] - dictionary with reference key and 
                instance.
        """
        return self.__noise_data
    

    # =========================================================================
    # 3. Noise data instance management
    # =========================================================================
    
    def import_csv_data(
        self, 
        reference_key: str,
        source_file: File,
    ) -> None:
        """Creates new noise data instance from imported files containing
        supported calibration data.

        This method currently only fully works with the following data files:
        - CSV format calibration data files from the IBM Quantum platform.

        Args:
            reference_key (str): Reference key that will be set for the newly
                created instance.
            source_file (File): Imported calibration data file used to create 
                this instance.
        """
        # Processing imported CSV file:
        dataframe = pandas.read_csv(source_file.path)
        remove_unnecessary_collumns(dataframe)
        rename_dataframe_columns(dataframe)
        add_additional_columns(dataframe)
        modify_dataframe_data(dataframe)

        # Creating new instance:
        new_instance = NoiseDataInstance(
            reference_key=reference_key,
            source_file=source_file,
            dataframe=dataframe)
        self.__noise_data[reference_key] = new_instance
  

    def get_instance_data(self) -> InstanceData | None:
        """Returns data about currently created noise data instances.

        Returned information includes:
        - Reference key for the current instance;
        - Name of the source data file;
        - Full path of source data file on user's device.

        Returns:
            InstanceData: Dataclasss for displayable instance data.
                If there is no data to be displayed, the function returns
                nothing (`None`).
        """
        if self.__noise_data:
            columns = [
                "Reference key", "Source file", 
                "Source file path on device"
            ]
            rows = [
                [instance.reference_key, instance.source_file.name, 
                 instance.source_file.full_path]
                for instance in self.__noise_data.values()
            ]
            actions = ["view", "delete"]
        
            return InstanceData(columns=columns,
                                rows=rows,
                                actions=actions)


    def remove_noise_data_instance(
            self, 
            reference_key: str
    ) -> None:
        """Removes existing noise data instance based on its reference key.

        Args:
            reference_key (str): Reference key of existing deletable noise 
                data instance.
        """
        del self.__noise_data[reference_key]


    # =========================================================================
    # 4. Retrieving qubit noise information
    # =========================================================================

    def get_qubit_noise_data(
            self, 
            reference_key: str
    ) -> dict:
        """Obtains and returns specific qubit noise data from a specified 
        noise data instance.

        Args:
            referemce_key (str): Reference key of the specified noise
                data instance, from which the qubit data will be retrieved.

        Returns:
            dict: Retrieved data in the form of a dictionary, where the key
                is the qubit number, and the value is another dictionary
                containing calibration data attribute names and values as
                key and value pairs respectively.
        """
        instance = self.__noise_data[reference_key]
        qubit_noise_data = {}

        for qubit in range(instance.get_qubit_count()):
            qubit_noise_data[qubit] = instance.get_qubit_data(qubit)

        return qubit_noise_data
