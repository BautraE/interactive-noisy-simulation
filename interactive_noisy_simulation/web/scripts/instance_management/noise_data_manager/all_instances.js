// =================================================================
// Functionality related to a specific page - viewing and managing
// all noise data instances.
// =================================================================

// Loading existing noise data instances
window.addEventListener('load', function() {
    setTimeout(function() {
        eel.view_noise_data_instances();
    }, 1);
});


// --------------------------------------------------------------
// Action handling
// --------------------------------------------------------------

/**
 * Redirects action to specific function based on given
 * action type.
 * 
 * @param {string} actionType - type of action expressed as a
 * string ("delete" or "view").
 * @param {string} referenceKey - reference key of the current 
 * noise data instance for which the action must be performed.
 */
function handleAction(actionType, rowId) {
    switch (actionType) {
        case "delete":
            removeNoiseDataInstance(rowId);
            break;
        case "view":
            viewSpecificNoiseData(rowId);
            break;
    }
}


/**
 * Calls Python function to remove the specified noise data
 * instance.
 * 
 * @param {string} referenceKey - reference key of the noise 
 * data instance.
 */
function removeNoiseDataInstance(referenceKey) {
    eel.remove_noise_data_instance(referenceKey);
}


/**
 * Redirects to page for viewing detailed information about
 * the specified noise data instance.
 * 
 * @param {string} referenceKey - reference key of the noise 
 * data instance.
 */
function viewSpecificNoiseData(referenceKey) {
    window.location.href = `noise_data_instance.html?id=${referenceKey}`;
}


// --------------------------------------------------------------
// New NoiseDataInstance creation form functionality
// --------------------------------------------------------------

eel.expose(setSelectedCSVFile);
/**
 * Changes appearance of custom file input form field and
 * sets value of hidden input field to the selected file
 * path on device so that Python can use it after submission.
 * 
 * @param {string} fileName - name of selected file that will
 * be displayed to the user for informative purposes.
 * @param {string} path - full file path that will be set
 * as the input field's value.
 */
function setSelectedCSVFile(fileName, path) {
    // Hides button for selecting file
    let addFileButton = document.getElementById("chose-file-button");
    addFileButton.classList.add("hidden-element");
    // Reveals text with selected file name
    let pFileName = document.getElementById("selected-file");
    pFileName.classList.remove("hidden-element");
    pFileName.innerHTML = fileName;
    // Reveals X icon for removing selected file
    let xIcon = document.getElementById("remove-selected-file-icon");
    xIcon.classList.remove("hidden-element");
    // Sets selected file path for input field
    let pathInput = document.getElementById("file-path");
    pathInput.value = path;
}


/**
 * Changes appearance of custom file input form field and
 * unsets value of hidden input field to being empty.
 */
function removeSelectedCSVFile() {
    // Hides text with selected file name
    let pFileName = document.getElementById("selected-file");
    pFileName.classList.add("hidden-element");
    // Hides X icon for removing selected file
    let xIcon = document.getElementById("remove-selected-file-icon");
    xIcon.classList.add("hidden-element");
    // Reveals button for selecting file
    let addFileButton = document.getElementById("chose-file-button");
    addFileButton.classList.remove("hidden-element")
    // Resets selected file path for input field
    let pathInput = document.getElementById("file-path");
    pathInput.value = "";
}


/**
 * Takes input field values and attempts to create a new noise data
 * instance.
 */
function importCSVCalibrationData() {
    var referenceKey = document.getElementById("reference-key").value;
    var filePath = document.getElementById("file-path").value;

    if (!validateInstanceForm(referenceKey, filePath)) {
        eel.import_csv_calibration_data(referenceKey, filePath);
        hidePopUpWindow();
    }
}


/**
 * Validates if values in input fields are valid for use. If not,
 * the user is notified about it.
 * 
 * @param {string} referenceKey - reference key of the new noise
 * data instance.
 * @param {string} filePath - full file path of the selected import
 * file.
 */
function validateInstanceForm(referenceKey, filePath) {
    let error = false;

    let textInput = document.getElementById("reference-key");
    textInput.classList.remove("input-error-outline");


    if (!referenceKey) {
        error = true;    
    }

    if (!filePath) {
        error = true;
    }

    return error;
}
