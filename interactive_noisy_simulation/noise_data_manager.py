# Standard library imports:
from typing import Union

#Third party imports:
import numpy, pandas

# Local project imports:
from .messages._message_manager import MessageManager
from .data._data import (
    CONFIG, CSV_COLUMNS, ERRORS, MESSAGES, OUTPUT_HEADINGS
)


class NoiseDataManager:

    def __init__(self) -> None:
        """Constructor method """
        self.__message_manager: MessageManager = MessageManager()
        msg = self.__message_manager
        
        msg.create_output(OUTPUT_HEADINGS["creating_new_object"].format(class_name=self.__class__.__name__))
        
        self.__dataframe: pandas.DataFrame | None = None

        # msg.add_message(MESSAGES["created_new_object"].format(class_name=self.__class__.__name__))
        msg.add_message(MESSAGES["created_new_object"], class_name=self.__class__.__name__)
        msg.add_message(MESSAGES["import_csv"])
        msg.end_output()

    
    # Class properties

    @property    
    def noise_data(self) -> pandas.DataFrame:
        """Returns a read-only copy of the current dataframe that contains noise data"""
        try:
            self.__check_dataframe()
        except Exception:
            self.__message_manager.add_traceback()
            return

        return self.__dataframe

    
    # Public class methods

    def get_qubit_noise_information(self, qubits: Union[int, list[int]]=None) -> None:
        """Prints out noise data for certain qubits
        
        Retrieves and prints out all noise data from dataframe for the 
        selected qubits by the user.

        Args:
            qubits: either a single qubit number or a list of qubit numbers,
            for which the noise data will be retrieved and printed out for the
            user to see.
        """
        msg = self.__message_manager
        msg.create_output(OUTPUT_HEADINGS["retrieving_qubits"].format(qubits=qubits))
        
        
        try:
            self.__check_dataframe()
            dataframe = self.__dataframe

            if not qubits:
                raise ValueError(ERRORS["error-no-qubits-numbers"])

            if isinstance(qubits, int):
                qubits = [qubits]

            self.__check_qubit_input(dataframe, qubits)
        except Exception:
            # traceback & error message is retrieved inside add_traceback()
            msg.add_traceback()
            return

        msg.add_qubit_noise_data_container()
        for qubit in qubits:
            msg.add_qubit_noise_data_content_box()
            msg.add_qubit_noise_data_row("Qubit number", qubit)
            for column in CSV_COLUMNS.keys():
                if CSV_COLUMNS[column]["csv_name"] in dataframe.columns:
                    name = CSV_COLUMNS[column]["name"]
                    value = dataframe.loc[qubit, CSV_COLUMNS[column]["csv_name"]]
                    msg.add_qubit_noise_data_row(name, value)
        
        msg.end_output()


    def help_csv_columns(self) -> None:
        """Prints out information about all dataframe columns """
        msg = self.__message_manager
        msg.create_output(OUTPUT_HEADINGS["csv_information"])
        msg.generic_content_container("Calibration data attributes:")

        for column in CSV_COLUMNS.keys():
            name = CSV_COLUMNS[column]["name"]
            description = CSV_COLUMNS[column]["description"]
            msg.add_message(f"{name}: {description}", [name])
        
        msg.end_output()


    def import_csv_data(self, file_path: str) -> None:
        """Imports and modifies data from a given calibration data file 
        
        Calibration data files are downloadable from the IBM Quantum platform for
        every available QPU (even if you do not pay for real access to all of them).
        These files can be used to create noise models that will have similar results
        to the real devices. This method reads the imported CSV file, removes 
        unnecessary columns and modifies the data for further use in creating
        noise models.

        Args:
            file_path: path to the calibration data CSV file.
        """
        msg = self.__message_manager
        msg.create_output(OUTPUT_HEADINGS["importing_csv"])

        dataframe = pandas.read_csv(file_path)
        self.__remove_unnecessary_collumns(dataframe)
        self.__add_additional_columns(dataframe)
        self.__modify_dataframe_data(dataframe)
        self.__dataframe = dataframe
        
        msg.add_message(MESSAGES["successful_csv_import"])
        msg.end_output()


    # Private class methods

    def __add_additional_columns(self, dataframe) -> None:
        """Adds additional columns for noise data storage

        Helper methods for class method "import_csv_data":

        Adds 2 additional columns to the dataframe for:
        - storing information about neighboring qubits;
        - storing reset operation time.
        Values for the neighboring qubits column are retrieved in another 
        method: "__modify_dataframe_data".
        Since the reset operation time is not currently available in the CSV 
        files, a default value of 1300 nanoseconds is set. It is possible to 
        get these gate times by other means from other ready noise models, 
        which is where the value 1300 came from.

        Args:
            dataframe: dataframe from which the columns will be removed
        """
        # Initializing new column for neighboring qubits
        neighboring_qubits_column = CSV_COLUMNS["neighboring_qubits"] ["csv_name"]
        dataframe[neighboring_qubits_column] = numpy.nan
        # This is done so that dataframe can store lists
        dataframe[neighboring_qubits_column] = dataframe[neighboring_qubits_column].astype(object)
        
        # This might change, if they add this information in the CSV files at some point in time
        dataframe[CSV_COLUMNS["reset_time"]["csv_name"]] = 1300
        self.__message_manager.add_message(MESSAGES["reset_time"])


    def __check_dataframe(self) -> None:
        """Checks if a dataframe exists in the current object of NoiseDataManager """
        if self.__dataframe is None:
            raise RuntimeError(f"{ERRORS["error_no_dataframe"]}")


    def __check_qubit_input(self, dataframe: pandas.DataFrame, qubits: list[int]) -> None:
        """Validates input qubit numbers for method "get_qubit_noise_information()"

        Helper method checks if the passed qubit numbers are above 0 and below
        the max index of qubits based on the dataframe.

        Args:
            datafrane: The dataframe, from which the information will be extracted
                from.
            qubits: Numbers of qubits that got passed as arguments.
        """
        qubit_count = len(dataframe)
        for qubit in qubits:
            if qubit < 0:
                raise ValueError(f"{ERRORS["error_negative_qubit_number"].format(qubit=qubit)}")
            if qubit >= qubit_count:
                raise ValueError(f"{ERRORS["error_large_qubit_number"].format(qubit=qubit,
                                                                                max_qubits=qubit_count - 1)}")


    def __modify_dataframe_data(self, dataframe) -> None:
        """Modifies all multi data columns in the dataframe

        Helper methods for class method "import_csv_data":

        Some of the data columns in the CSV file are initially designed to store
        multiple values in one row as strings, where each one is divided by ";".
        This method goes through each of these columns and separates each of the 
        values, changing the data type to a dictionary:
            {target_qubit: value}
        This is done for simpler actions down the road in regards to using these
        columns.
        A list of all multi-data columns that this method goes through is available
        in the configuration file "config.json".
        Alongside this, neighboring qubits are also retrieved during this process
        since you iterate through each qubit, for which you see all target qubits
        in these multi-data columns.

        Args:
            dataframe: dataframe from which the columns will be removed
        """
        neighboring_qubits_column = CSV_COLUMNS["neighboring_qubits"] ["csv_name"]

        for current_qubit in range(len(dataframe)):
            found_neighbors = []
            are_neighbors_found = False
            for column in CONFIG["multi_data_columns"]:
                column_name = CSV_COLUMNS[column]["csv_name"]
                if column_name in dataframe.columns:
                    column_values = dataframe.at[current_qubit, column_name]
                    if not pandas.isna(column_values):
                        column_values_list = column_values.split(";")
                        modified_data = {}
                        # Modifying multi-value columns to a better format
                        for column_value in column_values_list:
                            target_qubit, value = column_value.split(":")
                            modified_data[int(target_qubit)] = float(value)
                            if not are_neighbors_found:
                                found_neighbors.append(int(target_qubit))
                        dataframe.at[current_qubit, column_name] = modified_data
                        dataframe.at[current_qubit, neighboring_qubits_column] = found_neighbors
                        # Only need to go through one multi-value column to find neighbors
                        are_neighbors_found = True


    def __remove_unnecessary_collumns(self, dataframe) -> None:
        """Removes data columns that are not used to simulate noise

        Helper methods for class method "import_csv_data":

        Not all columns in the provided CSV files are used in the creation of
        errors for a noise model, therefore they are removed. A list of all 
        removable columns is available in the configuration file "config.json"
        as "not_required_columns".

        Args:
            dataframe: dataframe from which the columns will be removed
        """
        for column in CONFIG["not_required_columns"]:
            if column in dataframe.columns:
                dataframe.pop(column)
