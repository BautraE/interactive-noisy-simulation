# Standard library imports:
from pathlib import Path

#Third party imports:
import eel, numpy, pandas

# Local project imports:
from ..utils.key_blocker import KeyBlocker
from ..data_structures.noise_data_instance import NoiseDataInstance
from ..exceptions import INSError
from .helpers.csv_modification import (
    add_additional_columns, modify_dataframe_data,
    remove_unnecessary_collumns
)
from ..messages.helpers.text_styling import (
    style_file_path, style_highlight, style_italic
)
from ..utils.checkers import check_instance_key
from ..utils.validators import (
    validate_file_type, validate_instance_name
)
from ..messages._message_manager import message_manager as msg
from ...data._data import (
    CONFIG, CSV_COLUMNS, ERRORS, MESSAGES, OUTPUT_HEADINGS
)


from ...app.content_management import *

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
        self.__key_blocker = KeyBlocker()
        self.__noise_data: dict[str, NoiseDataInstance] = {}  

    
    # =========================================================================
    # 2. Class properties.
    # =========================================================================

    @property
    def key_blocker(self) -> KeyBlocker:
        """Returns a reference to a `KeyBlocker` object
        
        A manager that will be used across all main manager
        classes to keep track of blocked keys:
            - `NoiseDataManager`
            - `NoiseCreator`
            - `SimulatorManager`
        """
        return self.__key_blocker


    @property    
    def noise_data(self) -> pandas.DataFrame:
        """Returns a reference to data structure containing noise 
           data instances."""
        return self.__noise_data
    

    # =========================================================================
    # 3. Noise data instance management - creating new instances, viewing and
    #       deleting existing ones.
    # =========================================================================
    
    def import_csv_data(
        self, 
        reference_key: str,
        file_path: str
    ) -> None:
        reference_key = validate_instance_name(reference_key)
        
        try:
            # Does key exist among created noise data instances
            check_instance_key(reference_key=reference_key,
                            should_exist=False,
                            instances=self.__noise_data,
                            instance_type="noise data instance")
            # Is key being blocked by a noise model instance reference
            self.__key_blocker.check_blocked_key(key=reference_key,
                                                instance_type="noise_data")
            # Makes sure that imported file is CSV type
            validate_file_type(file_path, expected_ext=(".csv", ".CSV"))
        except INSError:
            msg.add_traceback()
            return

        csv_file = Path(file_path)
        file_name = csv_file.name
        full_path = str(csv_file.resolve())

        # Processing imported CSV file:
        dataframe = pandas.read_csv(file_path)
        remove_unnecessary_collumns(dataframe)
        add_additional_columns(dataframe)
        modify_dataframe_data(dataframe)
        
        # Defining new noise data instance
        new_instance = NoiseDataInstance(
            file_name=file_name,
            full_path=full_path,
            dataframe=dataframe)
        self.__noise_data[reference_key] = new_instance
    

    def get_instance_data(self) -> dict:
        instance_data = {
            "has_data": False,
            "columns": [],
            "rows": []
        }
        
        if self.__noise_data:
            instance_data["columns"] = ["Reference key", "Source file", 
                                        "Source file path on device"]

            for key, instance in self.__noise_data.items():
                row = [key, instance.file_name, instance.full_path]
                instance_data["rows"].append(row)
            
            instance_data["has_data"] = True
        
        return instance_data
    

    def remove_noise_data_instance(self, reference_key: str) -> None:
        try:
            # Is there even an instance to delete with given key
            check_instance_key(reference_key=reference_key,
                               should_exist=True,
                               instances=self.__noise_data,
                               instance_type="noise data instance")
        except INSError:
            msg.add_traceback()
            return

        del self.__noise_data[reference_key]


    # =========================================================================
    # 4. Retrieving qubit noise information - showing user noise data for
    #       requested qubits.
    # =========================================================================

    def get_qubit_noise_data(
            self, 
            reference_key: str, 
            qubits: int = None
    ) -> dict:
        instance = self.__noise_data[reference_key]
        
        qubit_noise_data = {}

        if not qubits:
            qubits = instance.get_qubit_count()

        for qubit in range(qubits):
            qubit_noise_data[qubit] = instance.get_qubit_data(qubit)

        return qubit_noise_data


    def __check_qubit_input(
            self, 
            data_instance: NoiseDataInstance, 
            qubits: list[int]
    ) -> None:
        """Validates input qubit numbers for a specific noise data instance.

        Checking functionality comes from NoiseDataInstance class object.

        Args:
            data_instance (NoiseDataInstance): Noise data instance that
                will be checked.
            qubits (list[int]): Qubit numbers that will be validated.
        """
        for qubit in qubits:
            data_instance.validate_qubit_number(qubit)
