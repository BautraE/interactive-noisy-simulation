// =================================================================
// Functionality related to a specific page - viewing and managing
// all circuit instances.
// =================================================================
// File contents list:
// 1. Page-specific variables
// 2. Initial page-specific actions that are performed upon
//    loading in this page.
// 3. Action handling.
// 4. Content management.
// 5. New CircuitInstance creation form functionality.
// -----------------------------------------------------------------


// --------------------------------------------------------------
// 1. Page-specific variables
// --------------------------------------------------------------

// Assignment of specific functions that shoul be executed upon loading
// tables and rows for displaying existing instance data.
instanceDataModifications = {
    row: adjustMemoryRequirements,
}


// --------------------------------------------------------------
// 2. Initial page-specific actions that are performed upon
//    loading in this page.
// --------------------------------------------------------------

// Loading existing noise data instances
window.addEventListener('load', function() {
    setTimeout(function() {
        eel.view_circuit_instances();
    }, 1);
});


// --------------------------------------------------------------
// 3. Action handling
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
// 4. Content management.
// --------------------------------------------------------------

/**
 * Formats the given memory value in bytes to whatever unit is most
 * appropriate for that specific value.
 * 
 * @param {number} bytes - Original memory value in bytes that will be 
 * formatted.
 */
function formatBytes(bytes) {
    let value = bytes;
    if (!value) {
        return `Too large to display`;
    } else {
        const units = {
            "bytes": "B",
            "kilobytes": "KB",
            "megabytes": "MB",
            "gigabytes": "GB",
            "terabytes": "TB",
            "petabytes": "PB",
            "exabytes": "EB",
            "zettabytes": "ZB",
            "yottabytes": "YB",
            "ronnabytes": "RB", // This is so large that it's hilarious
            "quettabytes": "QB" // I'm keeping these here just for fun
        }
        const unitNames = Object.keys(units)

        let i = 0;
        while (value >= 1024 && i < unitNames.length - 1) {
            value /= 1024;
            i++;
        }

        // 'title' gives hover tooltip functionality, which in this case
        // explains what does the specific short version of a memory unit
        // stand for. 
        return `${value.toFixed(2)} 
                <span title="${unitNames[i]}">${units[unitNames[i]]}</span>`;
    }
}


/**
 * Adjusts the displaying of simulation method memory requirements.
 * 
 * @param {HTMLElement} rowElement - HTML row element that will
 * be modified.
 * @param {Array} rowContent - Array of row content (as strings) that
 * are displayed within the row. Primarily used for obtaining something
 * that will be used during element modification.
 */
function adjustMemoryRequirements(rowElement, rowContent) {
    // Memory requirements is the 3rd collumn
    const memoryRow = rowElement.children[2];
    const memoryRequirements = rowContent[2];
    
    const contentLines = [];
    for (const [key, value] of Object.entries(memoryRequirements)) {
        contentLines.push(`<i>${key}</i>:<br><b>${formatBytes(value)}</b>`);
    }

    memoryRow.innerHTML = contentLines.join("<br>");
}


// --------------------------------------------------------------
// 5. New CircuitInstance creation form functionality
// --------------------------------------------------------------

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
    const referenceKeyInput = document.getElementById("reference-key");
    referenceKeyInput.addEventListener('change', () =>
        removeInputErrorStyles({
            outlinedElementId: "reference-key", 
            messageElementId: "reference-key-input-message"
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

    // Adding required event listeners for file select input field
    document.addEventListener("fileSelected", () => {
        // Removes any previous input error-related style
        removeInputErrorStyles({
            outlinedElementId: "circuit-file-input", 
            messageElementId: "circuit-file-input-message"
        });
    });
}


// --------------------------------------------------------------
// Regular functionality

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
