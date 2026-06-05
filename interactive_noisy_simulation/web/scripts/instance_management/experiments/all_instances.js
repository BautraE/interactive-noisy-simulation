// =================================================================
// Functionality related to a specific page - viewing and managing
// all experiment instances.
// =================================================================
// File contents list:
// 1. Page-specific variables 
// 2. Initial page-specific actions that are performed upon
//    loading in this page.
// 3. Action handling
// 4. New ExperimentInstance creation form functionality
// -----------------------------------------------------------------

// --------------------------------------------------------------
// 1. Page-specific variables
// --------------------------------------------------------------

// Pop-up element variable used for dynamic height adjustment
// (related to pop-up window height changing animation)
let popup;
// Assignment of specific functions that shoul be executed upon loading
// tables and rows for displaying existing instance data.
instanceDataModifications = {
    row: colorStatusCell,
}

// --------------------------------------------------------------
// 2. Initial page-specific actions that are performed upon
//    loading in this page.
// --------------------------------------------------------------

// Loading existing noise data instances
window.addEventListener('load', function() {
    setTimeout(function() {
        eel.view_experiment_instances();
    }, 1);
});


/**
 * Adds specific CSS styles for the status collumn (accomplished through 
 * table rows).
 * 
 * @param {HTMLElement} rowElement - HTML row element that will
 * be modified.
 * @param {Array} rowContent - Array of row content (as strings) that
 * are displayed within the row. Primarily used for obtaining something
 * that will be used during element modification.
 */
function colorStatusCell(rowElement, rowContent) {
    const statusMessageStyles = {
        Completed: "variant-green",
        Partial: "variant-yellow",
        Pending: "variant-grey",
    }

    let statusCell = rowElement.children[3];
    let statusStyle = statusMessageStyles[rowContent[3]];
    if(statusStyle) {
        statusCell.classList.add("status-text", statusStyle);
    }
}


// --------------------------------------------------------------
// 3. Action handling
// --------------------------------------------------------------

/**
 * Redirects action to specific function based on given
 * action type.
 * 
 * @param {string} actionType - type of action expressed as a
 * string ("delete", "view", etc.).
 * @param {string} referenceKey - reference key of the current 
 * experiment instance for which the action must be performed.
 */
function handleAction(actionType, rowId) {
    switch (actionType) {
        case "delete":
            eel.remove_experiment_instance(rowId);
            break;
        case "view":
            window.location.href = `experiment_instance.html?id=${rowId}`
            break;
    }
}


// --------------------------------------------------------------
// 4. New ExperimentInstance creation form functionality
// --------------------------------------------------------------

// --------------------------------------------------------------
// Initializer function

/**
 * Runs additional functionality-related initialization steps for the experiment
 * instance creation form.
 */
function initNewInstanceForm() {
    // -------------------------------------------------------------------------------
    // Adding max length number for form input fields

    const maxLengthSpan = document.getElementById("reference-key-input-max-length");
    maxLengthSpan.textContent = MAX_REFERENCE_KEY_LENGTH;

    // -------------------------------------------------------------------------------
    // Adjusting height of current form window for height change animation

    activePopupElement = document.querySelector('.pop-up');
    adjustHeightOfParent(activePopupElement);
    
    // -------------------------------------------------------------------------------
    // Adding required event listeners to form

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
}


// --------------------------------------------------------------
// Regular functionality

/**
 * Takes input field values and attempts to create a new circuit
 * instance.
 */
async function createInstance() {
    // Obtaining values from input fields:
    const referenceKey = document.getElementById("reference-key").value;

    // Validation definitions and validation process
    const isValid = await validateForm([
        {value: referenceKey, validator: validateReferenceKey}
    ]);

    // New instance creation if all input fields are valid
    if (isValid) {
        eel.create_experiment_instance(referenceKey);
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
    const isUnique = await eel.is_experiment_key_unique(referenceKey)();
    if (!isUnique) {
        addInputErrorStyles({
            outlinedElementId: outlinedElementId,
            messageElementId: messageElementId,
            errorMessageText: "This reference key is already used by another experiment instance!"
        });
        return false;
    }

    // Input field is valid
    return true;
}
