# =========================================================================
# This file contains helper functions for the class NoiseDataManager.
#
# The following methods are used for modifying obtained dataframes after
# they are made from imported CSV files.
# =========================================================================

# Third party imports:
import numpy, pandas

# Project-related imports:
from ....data._data import (
    CONFIG, CSV_COLUMNS
)


def add_additional_columns(dataframe: pandas.DataFrame) -> None:
    """Adds additional columns for noise data storage.

    Adds 2 additional columns to the dataframe for:
    - storing information about neighboring qubits;
    - storing reset operation time.
    Values for the neighboring qubits column are retrieved in another 
    method: `__modify_dataframe_data`.
    Since the reset operation time is not currently available in the 
    CSV files, a default value of 1300 nanoseconds is set. It is 
    possible to get these gate times by other means from other ready 
    noise models, which is where the value 1300 came from.

    Args:
        dataframe (pandas.DataFrame): Dataframe to which the new
            columns will be added.
    """
    # Initializing new column for neighboring qubits
    neighboring_qubits_column = CSV_COLUMNS["neighboring_qubits"]["csv_name"]
    dataframe[neighboring_qubits_column] = numpy.nan
    # This is done so that dataframe can store lists
    dataframe[neighboring_qubits_column] = dataframe[
        neighboring_qubits_column].astype(object)
    
    # This might change, if they add this information in the CSV files
    # at some point in time
    dataframe[CSV_COLUMNS["reset_time"]["csv_name"]] = 1300


def modify_dataframe_data(dataframe: pandas.DataFrame) -> None:
    """Modifies all multi data columns in the dataframe.

    Some of the data columns in the CSV file are initially designed
    to store multiple values in one row as strings, where each one 
    is divided by ";". This method goes through each of these columns
    and separates each of the values, changing the data type to a 
    `dictionary: {target_qubit: value}`
    
    This is done for simpler actions down the road in regards to 
    using these columns.
    
    A list of all multi-data columns that this method goes through is 
    available in the configuration file `config.json`.

    Alongside this, neighboring qubits are also retrieved during this 
    process since you iterate through each qubit, for which you see all 
    target qubits in these multi-data columns.

    Args:
        dataframe (pandas.DataFrame): Data from this dataframe will 
            be modified.
    """
    neighboring_qubits_column = CSV_COLUMNS["neighboring_qubits"]["csv_name"]

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
                    dataframe.at[
                        current_qubit, column_name] = modified_data
                    dataframe.at[
                        current_qubit, 
                        neighboring_qubits_column] = found_neighbors
                    # Only need to go through one multi-value column to 
                    # find neighbors
                    are_neighbors_found = True


def remove_unnecessary_collumns( 
        dataframe: pandas.DataFrame
) -> None:
    """Removes data columns that are not used to simulate noise.

    Not all columns in the provided CSV files are used in the
    creation of errors for a noise model, therefore they are 
    removed. A list of all removable columns is available in the 
    configuration file `config.json` as `not_required_columns`.

    Args:
        dataframe (pandas.DataFrame): Dataframe from which the 
            columns will be removed.
    """
    for column in CONFIG["not_required_columns"]:
        if column in dataframe.columns:
            dataframe.pop(column)
