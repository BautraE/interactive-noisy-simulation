// =================================================================
// Functionality related to a specific page - viewing and managing
// all noise model instances.
// =================================================================
// File contents list:
// 1. Action handling
// 2. New NoiseModelInstance creation form functionality
// -----------------------------------------------------------------

// Loading existing noise data instances
window.addEventListener('load', function() {
    setTimeout(function() {
        eel.view_noise_model_instances();
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
            eel.remove_noise_model_instance(rowId);
            break;
    }
}


// --------------------------------------------------------------
// 2. New NoiseModelInstance creation form functionality
// --------------------------------------------------------------

/**
 * Runs additional functionality-related initialization steps for the noise model
 * instance creation form.
 */
async function initNoiseDataForm() {
    // Adding missing dynamic values and elements
    await loadRadioInputOptions({
        containerId: "noise-source-container",
        inputId: "noise-data-source",
        dataRetrievalFunction: eel.get_noise_data_references
    });

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

    // Adding required event listeners for noise data source input field
    const container = document.getElementById("noise-source-container");
    container.addEventListener("change", (event) => {
        if (event.target.name === "noise-data-source") {
            removeInputErrorStyles({
                outlinedElementId: "noise-source-container",
                messageElementId: "source-data-input-message"
            });
        }
    });
}


/**
 * Takes input field values and attempts to create a new noise model
 * instance.
 * 
 * Right before creation process begins, action buttons are replaced
 * by a progress bar, and all form elements get disabled.
 */
async function createNoiseModelInstance() {
    // Retrieves form input data
    const referenceKey = document.getElementById("reference-key");
    const noiseDataSource = document.querySelector(
        'input[name="noise-data-source"]:checked'
    );
    
    const isValid = await validateForm([
        {value: referenceKey.value, validator: validateReferenceKey},
        {value: noiseDataSource?.value, validator: validateSourceData}
    ]);

    if (isValid) {
        // Hides actions and shows progress bar
        const actions = document.getElementById("action-buttons");
        const progressBar = document.getElementById("progress-bar");
        progressBar.classList.remove("hidden-element");
        actions.classList.add("hidden-element");

        disableForm("pop-up-form");
        await eel.create_noise_model_instance(referenceKey.value, noiseDataSource.value)();
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
    const isUnique = await eel.is_noise_model_key_unique(referenceKey)();
    if (!isUnique) {
        addInputErrorStyles({
            outlinedElementId: outlinedElementId,
            messageElementId: messageElementId,
            errorMessageText: "This reference key is already used by another noise model instance!"
        });
        return false;
    }

    // Input field is valid
    return true;
}


/**
 * Source data input value validation function.
 * 
 * The function uses the selected source data reference and goes through
 * all required validation steps.
 * 
 * @param {string} sourceData - Reference key for the source data that
 * needs to be validated.
 */
function validateSourceData(sourceData) {
    const outlinedElementId = "noise-source-container";
    const messageElementId = "source-data-input-message";

    // If source data is not selected
    if (!sourceData) {
        addInputErrorStyles({
            outlinedElementId: outlinedElementId,
            messageElementId: messageElementId,
            errorMessageText: "Noise data sourcce must be selected!"
        });
        return false;
    }

    // Input field is valid
    return true;
}
