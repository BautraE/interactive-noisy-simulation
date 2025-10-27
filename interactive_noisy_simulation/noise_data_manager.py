# Standard library imports:
from pathlib import Path

#Third party imports:
import numpy, pandas

# Local project imports:
from .messages._message_manager import MessageManager
from .utils.key_availability import check_blocked_key
from .utils.validators import (
    check_instance_key, validate_instance_name
)
from .data._data import (
    CONFIG, CSV_COLUMNS, ERRORS, MESSAGES, OUTPUT_HEADINGS
)


class NoiseDataManager:

    def __init__(self) -> None:
        """Constructor method """
        self.__message_manager: MessageManager = MessageManager()
        msg = self.__message_manager
        
        msg.create_output(OUTPUT_HEADINGS["creating_new_object"].format(
            class_name=self.__class__.__name__))
        
        self.__noise_data: dict[str, str | pandas.DataFrame] = {}

        msg.add_message(MESSAGES["created_new_object"], 
                        class_name=self.__class__.__name__)
        msg.add_message(MESSAGES["import_csv"])
        msg.end_output()

    
    # Class properties

    @property    
    def noise_data(self) -> pandas.DataFrame:
        """Returns a reference to data structure containing noise 
           data instances."""
        return self.__noise_data
    

    # Public class methods

    def get_qubit_noise_information(
            self, 
            reference_key: str, 
            qubits: int | list[int] = None
    ) -> None:
        """Prints out noise data for certain qubits from a specific 
        data instance.
        
        Retrieves and prints out all noise data from a specific noise
        data instance for the selected qubits by the user.

        Args:
            reference_key (str): Key that is used to access a specific 
                noise datainstance from all of the currently available
                ones.
            qubits (int | list[int]): Either a single qubit number or 
                a list of qubit numbers, for which the noise data will 
                be retrieved and printed out so the user can see the 
                specific data.
        
        Raises:
            ValueError: If nothing is passed as the argument `qubits`.
        """
        msg = self.__message_manager
        msg.create_output(
            OUTPUT_HEADINGS["retrieving_qubits"].format(
                qubits=qubits,
                reference_key=reference_key))
        
        try:
            check_instance_key(reference_key=reference_key,
                               should_exist=True,
                               instances=self.__noise_data,
                               instance_type="noise data instance")
            dataframe = self.__noise_data[reference_key]["dataframe"]

            if not qubits:
                raise ValueError(ERRORS["error-no-qubits-numbers"])

            if isinstance(qubits, int):
                qubits = [qubits]

            self.__check_qubit_input(dataframe, qubits)
        except Exception:
            msg.add_traceback()
            return

        msg.add_qubit_noise_data_container()
        for qubit in qubits:
            msg.add_qubit_noise_data_content_box()
            msg.add_qubit_noise_data_row("Qubit number", qubit)
            for column in CSV_COLUMNS.keys():
                if CSV_COLUMNS[column]["csv_name"] in dataframe.columns:
                    name = CSV_COLUMNS[column]["name"]
                    value = dataframe.loc[qubit, 
                                          CSV_COLUMNS[column]["csv_name"]]
                    msg.add_qubit_noise_data_row(name, value)
        
        msg.add_message(MESSAGES["qubit_noise_data_retrieved"],
                        reference_key=reference_key)
        msg.end_output()


    def help_csv_columns(self) -> None:
        """Prints out information about all dataframe columns."""
        msg = self.__message_manager
        msg.create_output(OUTPUT_HEADINGS["csv_information"])
        msg.generic_content_container("Calibration data attributes:")

        for column in CSV_COLUMNS.keys():
            name = CSV_COLUMNS[column]["name"]
            description = CSV_COLUMNS[column]["description"]
            msg.add_message(f"{name}: {description}", [name])
        
        msg.end_output()


    def import_csv_data(self, reference_key: str, file_path: str) -> None:
        """Imports and modifies data from a given calibration data file.
        
        Calibration data files are downloadable from the IBM Quantum 
        platform for every available QPU (even if you do not pay for 
        real access to all of them). These files can be used to create 
        noise models that will have similar results to the real devices. 
        This method reads the imported CSV file, removes unnecessary 
        columns and modifies the data for further use in creating noise 
        models.

        Args:
            file_path (str): Path to the calibration data CSV file.
            reference_key (str): Key that will be used to access specific 
                CSV noise data instances after they are imported.
        """
        msg = self.__message_manager
        msg.create_output(OUTPUT_HEADINGS["importing_csv"])

        reference_key = validate_instance_name(reference_key,
                                               msg)
        
        try:
            # Does key exist among created noise data instances
            check_instance_key(reference_key=reference_key,
                               should_exist=False,
                               instances=self.__noise_data,
                               instance_type="noise data instance")
            # Is key being blocked by a noise model instance reference
            check_blocked_key(key=reference_key,
                              instance_type="noise_data")
        except Exception:
            msg.add_traceback()
            return

        new_instance = {}

        csv_file = Path(file_path)

        file_name = csv_file.name
        new_instance["name"] = file_name
        
        full_path = str(csv_file.resolve())
        new_instance["path"] = full_path

        msg.add_message(
            MESSAGES["import_csv_file_information"],
            file_name=file_name,
            file_path=full_path
        )

        dataframe = pandas.read_csv(file_path)
        self.__remove_unnecessary_collumns(dataframe)
        self.__add_additional_columns(dataframe)
        self.__modify_dataframe_data(dataframe)
        new_instance["dataframe"] = dataframe

        self.__noise_data[reference_key] = new_instance
        
        msg.add_message(
            MESSAGES["successful_csv_import"],
            reference_key=reference_key
        )
        msg.end_output()


    def remove_noise_data_instance(self, reference_key: str) -> None:
        """Removes existing noise data instance by reference key.
        
        Args:
            reference_key (str): Key of the removable noise data
                instance.
        """
        msg = self.__message_manager
        msg.create_output(
            OUTPUT_HEADINGS["remove_instance"].format(
                instance_type="noise data instance",
                reference_key=reference_key))
        
        try:
            check_instance_key(reference_key=reference_key,
                               should_exist=True,
                               instances=self.__noise_data,
                               instance_type="noise data instance")
        except Exception:
            msg.add_traceback()
            return

        del self.__noise_data[reference_key]
        msg.add_message(
            MESSAGES["deleted_instance"],
            instance_type="noise data instance",
            reference_key=reference_key)
        msg.end_output()


    def view_noise_data_instances(self) -> None:
        """Displays all currently available noise data instances.

        If no instances are available, method simply displays a
        message that states this fact.
        The visual output from this method is placed inside of the
        default "message" content container.

        Displayed information includes:
        - Reference key for the current instance;
        - File name, from which the data was imported;
        - Full path to this file on the local device (this does not
          update if the file was moved, it only shows the original
          location from the import process).
        """
        msg = self.__message_manager
        msg.create_output(OUTPUT_HEADINGS["created_instances"].format(
            instance_type="noise data instances"))
        msg.generic_content_container("Noise data instances:")

        if self.__noise_data:

            msg.add_generic_table()
            msg.add_generic_table_row(
                row_content=["Reference key", "Source file", 
                             "Source file path on device"],
                row_type="th")

            for key, instance in self.__noise_data.items():
                file_name = msg.style_italic(instance["name"])
                file_path = msg.style_file_path(instance["path"])
                
                msg.add_generic_table_row(
                    row_content=[key, file_name, file_path],
                    row_type="td")
        else:
            msg.add_message(MESSAGES["no_instances"],
                            instance_type="imported noise data instances")
        
        msg.end_output()


    # Private class methods

    def __add_additional_columns(self, dataframe: pandas.DataFrame) -> None:
        """Adds additional columns for noise data storage.

        Helper methods for class method `import_csv_data`:

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
        self.__message_manager.add_message(MESSAGES["reset_time"])


    def __check_qubit_input(
            self, 
            dataframe: pandas.DataFrame, 
            qubits: list[int]
    ) -> None:
        """Validates input qubit numbers for method 
        `get_qubit_noise_information`.

        Helper method checks if the passed qubit numbers are above 0
        and below the max index of qubits based on the selected dataframe.

        Args:
            datafrane (pandas.DataFrame): The dataframe, from which the 
                information will be extracted from. Here it is only used 
                to check the total number of qubits.
            qubits (list[int]): Numbers of qubits that got passed as
                arguments.

        Raises:
            ValueError:
                - If qubit number is lower than 0;
                - If qubit number exceeds max qubit number.
        """
        qubit_count = len(dataframe) - 1
        for qubit in qubits:
            
            if qubit < 0:
                raise ValueError(
                    ERRORS["error_negative_qubit_number"].format(
                        qubit=qubit))
            
            elif qubit > qubit_count:
                raise ValueError(ERRORS["error_large_qubit_number"].format(
                    qubit=qubit,
                    max_qubits=qubit_count))


    def __modify_dataframe_data(self, dataframe: pandas.DataFrame) -> None:
        """Modifies all multi data columns in the dataframe.

        Helper methods for class method `import_csv_data`.

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


    def __remove_unnecessary_collumns(
            self, 
            dataframe: pandas.DataFrame
    ) -> None:
        """Removes data columns that are not used to simulate noise.

        Helper methods for class method `import_csv_data`.

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
