import pandas, json, numpy
from typing import Union

with open("data/csv_columns.json", "r") as file:
    CSV_COLUMNS = json.load(file)
with open("data/noise_data_manager_descriptions.json", "r") as file:
    NOISEDATAMANAGER_METHODS = json.load(file)
with open("data/config.json", "r") as file:
    CONFIG = json.load(file)

class NoiseDataManager:
    def __init__(self) -> None:
        print(f"\033[1m----- Creating {NoiseDataManager.__name__} object -----\033[0m")
        self.__dataframe = None
        print(
            f"{NoiseDataManager.__name__} class object has been created successfully!\n"
            f"Continue by importing the QPU calibration data CSV file: \033[32mobject.import_csv_data('path/to/file.csv')\033[0m\n"
        )

    @property
    def noise_data(self) -> pandas.DataFrame:
        return self.__dataframe

    # For importing calibration data from IBM Quantum QPU's
    def import_csv_data(self, file_path: str) -> None:
        print(f"----- Importing data from the selected CSV file -----")
        self.__dataframe = pandas.read_csv(file_path)
        
        # Removing unnecessary collumns from the table (not used for creating NoiseModel)
        for column in CONFIG["not_required_columns"]:
            if column in self.__dataframe.columns:
                self.__dataframe.pop(column)
        
        # Initializing new column
        column_neighboring_qubits = CSV_COLUMNS["neighboring_qubits"]["csv_name"]
        self.__dataframe[column_neighboring_qubits] = numpy.nan
        self.__dataframe[column_neighboring_qubits].astype(object)

        for qubit in range(len(self.__dataframe)):
            neighboring_qubits = []
            NEIGHBORS_FOUND = False
            for attribute_key in CONFIG["multi_data_columns"]:
                attribute_name = CSV_COLUMNS[attribute_key]["csv_name"]
                # If the attribute value column is in the table and it's value is not a NaN
                if attribute_name in self.__dataframe.columns and isinstance(self.__dataframe.at[qubit, attribute_name], str):
                    attribute_value_list = self.__dataframe.at[qubit, attribute_name].split(";")
                    modified_data = {}
                    # Modifying multi-value columns to a better format
                    for attribute_value in attribute_value_list:
                        target_qubit, value = attribute_value.split(":")
                        modified_data[int(target_qubit)] = float(value)
                        # Adding neighboring qubit to list
                        if not NEIGHBORS_FOUND:
                            neighboring_qubits.append(int(target_qubit))
                    self.__dataframe.at[qubit, attribute_name] = modified_data
                    self.__dataframe.at[qubit, column_neighboring_qubits] = neighboring_qubits
                    NEIGHBORS_FOUND = True

        # This might change, if they add this information in the CSV files at some point in time
        print(f"CSV files currently do not contain Reset operation times. A default value of \033[32m1300 ns\033[0m has been set.")
        self.__dataframe["Reset operation time (ns)"] = 1300
        print(f"Data from CSV file has been imported successfully!\n")

    # For requesting lookup of certain qubit calibration data
    def get_qubit_noise_information(self, qubits: Union[int, list[int]]) -> None:
        # So that individual integers are processed just like lists
        if isinstance(qubits, int):
            qubits = [qubits]
        # Check for negative numbers
        for qubit in qubits:
            if qubit < 0:
                raise ValueError(f"Qubit numbers cannot be lower than 0! The number {qubit} goes against this!")
        # Showing information for selected qubits    
        print(f"----- Retrieving information about qubits {qubits} -----")
        for qubit in qubits:
            print(f"Qubit number: {qubit}")
            for column in CSV_COLUMNS.keys():
                if CSV_COLUMNS[column]["csv_name"] in self.__dataframe.columns:
                    print(f"{CSV_COLUMNS[column]["name"]}: \033[32m{self.__dataframe.loc[qubit, CSV_COLUMNS[column]["csv_name"]]}\033[0m")
            print(f"\n")

    # Explains all CSV calibration data columns to the user
    def help_csv_columns(self) -> None:
        print(f"----- Information on all currently relevant CSV calibration data columns -----")
        for column in CSV_COLUMNS.keys():
            print(f"\033[32m{CSV_COLUMNS[column]["name"]}:\033[0m {CSV_COLUMNS[column]["description"]}")
