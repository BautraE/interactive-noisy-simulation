// =================================================================
// Functionality related to a specific page - viewing and managing
// all circuit instances.
// =================================================================
// File contents list:
// 1. Action handling
// 2. New CircuitInstance creation form functionality
// -----------------------------------------------------------------

// Loading existing noise data instances
window.addEventListener('load', function() {
    setTimeout(function() {
        eel.view_circuit_instances();
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
 * circuit instance for which the action must be performed.
 */
function handleAction(actionType, rowId) {
    switch (actionType) {
        case "delete":
            eel.remove_circuit_instance(rowId);
            break;
    }
}


// --------------------------------------------------------------
// Initializer function

/**
 * Runs additional functionality-related initialization steps for the circuit
 * instance creation form.
 */
function initNewInstanceForm() {
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

eel.expose(setSelectedFile);
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
function setSelectedFile(fileName, path) {
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
        outlinedElementId: "circuit-file-input", 
        messageElementId: "circuit-file-input-message"
    });
}


/**
 * Changes appearance of custom file input form field and
 * unsets value of hidden input field to being empty.
 */
function removeSelectedFile() {
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
 * Takes input field values and attempts to create a new circuit
 * instance.
 */
async function createInstance() {
    const referenceKey = document.getElementById("reference-key").value;
    const filePath = document.getElementById("file-path").value;

    const isValid = await validateForm([
        {value: referenceKey, validator: validateReferenceKey},
        {value: filePath, validator: validateFileInput}
    ]);

    if (isValid) {
        eel.create_circuit_instance(referenceKey, filePath);
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
    const isUnique = await eel.is_circuit_key_unique(referenceKey)();
    if (!isUnique) {
        addInputErrorStyles({
            outlinedElementId: outlinedElementId,
            messageElementId: messageElementId,
            errorMessageText: "This reference key is already used by another circuit instance!"
        });
        return false;
    }

    // Input field is valid
    return true;
}


/**
 * QPY file path value validation function.
 * 
 * The function uses the provided file path to the selected file and goes 
 * through all required validation steps for it.
 * 
 * @param {string} filePath - File path that will be validated.
 */
function validateFileInput(filePath) {
    const outlinedElementId = "circuit-file-input";
    const messageElementId = "circuit-file-input-message";

    // If no file is selected
    if (!filePath) {
        addInputErrorStyles({
            outlinedElementId: outlinedElementId,
            messageElementId: messageElementId,
            errorMessageText: "No QPY circuit file selected!"
        });
        return false;
    }
    // If file type is not QPY
    if (!filePath.toLowerCase().endsWith(".qpy")) {
        addInputErrorStyles({
            outlinedElementId: outlinedElementId,
            messageElementId: messageElementId,
            errorMessageText: "Invalid file type! Only QPY (.qpy) files are supported!"
        });
        return false;
    }

    // Input field is valid
    return true;
}
