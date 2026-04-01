// =================================================================
// Functionality related to a specific page - viewing and managing
// all noise data instances.
// =================================================================
// File contents list:
// 1. Action handling
// 2. New NoiseDataInstance creation form functionality
// -----------------------------------------------------------------

// Loading existing noise data instances
window.addEventListener('load', function() {
    setTimeout(function() {
        eel.view_noise_data_instances();
    }, 1);
});


// --------------------------------------------------------------
// 1. Action handling
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
// 2. New NoiseDataInstance creation form functionality
// --------------------------------------------------------------

// --------------------------------------------------------------
// Initializer function

/**
 * Runs additional functionality-related initialization steps for the noise data
 * instance creation form.
 */
async function initNoiseDataForm() {
    // Adding missing dynamic values
    const maxLengthSpan = document.getElementById("reference-key-input-max-length");
    maxLengthSpan.textContent = MAX_REFERENCE_KEY_LENGTH;
    
    // Adding required event listeners for reference key input field
    let outlinedElementId = "reference-key";
    let messageElementId = "reference-key-input-message";
    
    const referenceKeyInput = document.getElementById("reference-key");
    referenceKeyInput.addEventListener('change', () =>
        removeInputErrorStyles({
            outlinedElementId: outlinedElementId, 
            messageElementId: messageElementId
        })
    );
    referenceKeyInput.addEventListener('input', () =>
        referenceKeyInput.value = adjustReferenceKey(referenceKeyInput.value)
    );
    referenceKeyInput.addEventListener('input', () =>
        updateTextContentLength({
            textContent: referenceKeyInput.value,
            maxLength: MAX_REFERENCE_KEY_LENGTH,
            lengthDisplayElementId: "reference-key-input-length",
        })
    );
}


// --------------------------------------------------------------
// Regular functionality

eel.expose(setSelectedCSVFile);
/**
 * Changes appearance of custom file input form field and
 * sets value of hidden input field to the selected file
 * path on device so that Python can use it after submission.
 * 
 * @param {string} fileName - name of selected file that will
 * be displayed to the user for informative purposes.
 * @param {string} path - full file path that will be set
 * as the file input field's value.
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

    // Removes any previous input error-related style
    removeInputErrorStyles({
        outlinedElementId: "csv-file-input", 
        messageElementId: "csv-file-input-message"
    });
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
async function importCSVCalibrationData() {
    const referenceKey = document.getElementById("reference-key").value;
    const filePath = document.getElementById("file-path").value;

    const isValid = await validateForm([
        {value: referenceKey, validator: validateReferenceKey},
        {value: filePath, validator: validateFileInput}
    ]);

    if (isValid) {
        eel.import_csv_calibration_data(referenceKey, filePath);
        hidePopUpWindow();
    }
}


// --------------------------------------------------------------
// Input validation

/**
 * Reference key input value validation function.
 * 
 * The function uses the provided reference key value and goes through
 * all required validation steps.
 * 
 * @param {string} referenceKey - Reference key value that will be
 * validated.
 */
async function validateReferenceKey(referenceKey) {
    const outlinedElementId = "reference-key";
    const messageElementId = "reference-key-input-message";

    // If reference key field is empty
    if (!referenceKey) {
        addInputErrorStyles({
            outlinedElementId: outlinedElementId,
            messageElementId: messageElementId,
            errorMessageText: "Reference key is mandatory!"
        });
        return false;
    }
    // If reference key exceeds maximum length
    if (referenceKey.length > MAX_REFERENCE_KEY_LENGTH) {
        addInputErrorStyles({
            outlinedElementId: outlinedElementId,
            messageElementId: messageElementId,
            errorMessageText: `The reference key is too long! Max length is 
            ${MAX_REFERENCE_KEY_LENGTH} characters!`
        });
        return false;
    }
    // If reference key is already used by same type of instance
    const isUnique = await eel.is_noise_data_key_unique(referenceKey)();
    if (!isUnique) {
        addInputErrorStyles({
            outlinedElementId: outlinedElementId,
            messageElementId: messageElementId,
            errorMessageText: "This reference key is already used by another noise data instance!"
        });
        return false;
    }
    // If reference key is being blocked by another instance
    const blockers = await eel.check_noise_data_key_block(referenceKey)()
    if (blockers) {
        const formattedBlockers = blockers.map(k => `"${k}"`).join("; ");
        addInputErrorStyles({
            outlinedElementId: outlinedElementId,
            messageElementId: messageElementId,
            errorMessageText: `This reference key is currently being blocked 
            by the following noise model instances: ${formattedBlockers}! 
            The key will be unblocked after they are deleted.`
        });
        return false;
    }

    // Input field is valid
    return true;
}


/**
 * CSV file path value validation function.
 * 
 * The function uses the provided file path to the selected CSV calibration
 * data file and goes through all required validation steps for it.
 * 
 * @param {string} filePath - File path that will be validated.
 */
function validateFileInput(filePath) {
    const outlinedElementId = "csv-file-input";
    const messageElementId = "csv-file-input-message";

    // If no file is selected
    if (!filePath) {
        addInputErrorStyles({
            outlinedElementId: outlinedElementId,
            messageElementId: messageElementId,
            errorMessageText: "No CSV calibration data file selected!"
        });
        return false;
    }
    // If file type is not CSV
    if (!filePath.toLowerCase().endsWith(".csv")) {
        addInputErrorStyles({
            outlinedElementId: outlinedElementId,
            messageElementId: messageElementId,
            errorMessageText: "Invalid file type! Only CSV (.csv) files are supported!"
        });
        return false;
    }

    // Input field is valid
    return true;
}
