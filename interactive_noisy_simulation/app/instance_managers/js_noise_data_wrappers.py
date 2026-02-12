# =================================================================
# Python wrappers for JS function calling
# Related to: Specific JS functions only used in `noise_data.py`
# =================================================================

# Third party imports:
import eel    


def set_selected_file(
        file_name: str,
        full_path: str
) -> None:
    """Changes appearance of custom file input form field and sets value of 
    hidden input field to the selected file path on device so that Python 
    can use it after submission.
    
    Wrapper function for `Python Eel` JS function call.

    Args:
        file_name (str): name of selected file that will be displayed 
            to the user for informative purposes.
        full_path (str): full file path that will be set as the file 
            input field's value.
    """
    eel.setSelectedCSVFile(file_name, full_path)
