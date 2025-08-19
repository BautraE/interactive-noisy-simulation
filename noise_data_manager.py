# Used for functionality purposes:
import json, numpy, pandas
from typing import Union


with open("data/config.json", "r") as file:
    CONFIG = json.load(file)

with open("data/csv_columns.json", "r") as file:
    CSV_COLUMNS = json.load(file)

with open("data/messages.json", "r") as file:
    MESSAGES = json.load(file)

class NoiseDataManager:

    def __init__(self) -> None:
        """Constructor method """
        self.__dataframe: pandas.DataFrame | None = None
        print(
            f"{MESSAGES["creating_new_object"].format(class_name=self.__class__.__name__)}\n"
            f"{MESSAGES["created_new_object"].format(class_name=self.__class__.__name__)}\n"
            f"{MESSAGES["import_csv"]}\n"
        )

    
    @property    
    def noise_data(self) -> pandas.DataFrame:
        """Returns a read-only copy of the current dataframe that contains noise data"""
        return self.__dataframe

    
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
        print(f"{MESSAGES["importing_csv"]}")
        dataframe = pandas.read_csv(file_path)
        self.__remove_unnecessary_collumns(dataframe)
        self.__add_additional_columns(dataframe)
        self.__modify_dataframe_data(dataframe)
        self.__dataframe = dataframe
        print(
            f"{MESSAGES["successful_csv_import"]}\n"
        )

    
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
        print(
            f"CSV files currently do not contain Reset operation times. "
            f"A default value of \033[32m1300 ns\033[0m has been set."
        )


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


    def get_qubit_noise_information(self, qubits: Union[int, list[int]]) -> None:
        """Prints out noise data for certain qubits
        
        Retrieves and prints out all noise data from dataframe for the 
        selected qubits by the user.

        Args:
            qubits: either a single qubit number or a list of qubit numbers,
            for which the noise data will be retrieved and printed out for the
            user to see.
        """
        dataframe = self.__dataframe
        
        if isinstance(qubits, int):
            qubits = [qubits]
        # Check for negative numbers
        for qubit in qubits:
            if qubit < 0:
                raise ValueError(f"{MESSAGES["error_negative_qubit_number"].format(qubit=qubit)}")

        print(f"{MESSAGES["retrieving_qubits"].format(qubits=qubits)}")
        for qubit in qubits:
            print(f"Qubit number: {qubit}")
            for column in CSV_COLUMNS.keys():
                if CSV_COLUMNS[column]["csv_name"] in dataframe.columns:
                    name = CSV_COLUMNS[column]["name"]
                    value = dataframe.loc[qubit, CSV_COLUMNS[column]["csv_name"]]
                    print(f"{name}: \033[32m{value}\033[0m")
            print(f"\n")


    def help_csv_columns(self) -> None:
        """Prints out information about all dataframe columns """
        print(f"{MESSAGES["csv_information"]}")
        for column in CSV_COLUMNS.keys():
            name = CSV_COLUMNS[column]["name"]
            description = CSV_COLUMNS[column]["description"]
            print(f"\033[32m{name}:\033[0m {description}")
        print(f"\n")
