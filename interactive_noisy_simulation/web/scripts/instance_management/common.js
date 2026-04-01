// =================================================================
// Functionality that is common across all instance management-
// related pages.
// =================================================================
// File contents list:
// 1. Global page-specific variables
// 2. Form input validation
// -----------------------------------------------------------------

// --------------------------------------------------------------
// 1. Global page-specific variables
// --------------------------------------------------------------

const MAX_REFERENCE_KEY_LENGTH = 50;


// --------------------------------------------------------------
// 2. Form input validation
// --------------------------------------------------------------

/**
 * Validates if values in input fields are valid for use. If not,
 * the user is notified about it.
 * 
 * @param {{
 * value: string, 
 * validator: Function
 * }[]} validations - List of
 * validations that should be completed for a specific form (its input
 * fields).
 */
async function validateForm(validations) {
    let isValid = true;

    for (const { value, validator } of validations) {
        const validationResult = await validator(value);
        if (!validationResult) {
            isValid = false;
        }
    }

    return isValid;
}


/**
 * Adds input error-related styles to a specific form input field. This
 * also includes adding the required error message text, and making it
 * visible in the DOM.
 * 
 * @param {{
 * outlinedElementId: string,
 * messageElementId: string,
 * errorMessageText: string
 * }} args - Group of indexed arguments in the form of a dictionary. It 
 * contains all required information to properly add input error-related 
 * styles to the required elements.
 * 
 * @param {string} args.outlinedElementId - ID of element that needs to have
 * the input error style-related outline added to it.
 * @param {string} args.messageElementId - ID of error message element that
 * needs to be made visible.
 * @param {string} args.errorMessageText - Input error-related message text
 * that will be shown to user.
 */
function addInputErrorStyles({outlinedElementId, messageElementId, errorMessageText}) {
    const outlinedElement = document.getElementById(outlinedElementId);
    outlinedElement.classList.add("input-error");

    const messageElement = document.getElementById(messageElementId);
    messageElement.textContent = errorMessageText;
    messageElement.classList.remove("hidden-element");
}


/**
 * Removes input error-related styles from a specific form input field. This
 * also includes removing the error message text, and making it hidden in 
 * the DOM.
 * 
 * @param {{
 * outlinedElementId: string,
 * messageElementId: string
 * }} args - Group of indexed arguments in the form of a dictionary. It 
 * contains all required information to properly remove input error-related 
 * styles to the required elements.
 * 
 * @param {string} args.outlinedElementId - ID of element that needs the
 * input error style-related outline removed.
 * @param {string} args.messageElementId - ID of error message element that
 * needs to be hidden.
 */
function removeInputErrorStyles({outlinedElementId, messageElementId}) {
    const outlinedElement = document.getElementById(outlinedElementId);
    outlinedElement.classList.remove("input-error");

    const messageElement = document.getElementById(messageElementId);
    messageElement.textContent = "";
    messageElement.classList.add("hidden-element");
}


/**
 * Replaces all spaces with "_" for reference key input field values.
 * 
 * @param {string} referenceKey - Currently written reference key value in
 * input field.
 * 
 * @returns {string} - Updated version of the currently written reference
 * key value.
 */
function adjustReferenceKey(referenceKey) {
    return referenceKey.replace(/\s/g, "_");
}


/**
 * Updates text input field max length counter.
 * 
 * Additionally, number containing current length may change its font color
 * in two occasions:
 * - to yellow: There are 5 (or less) free character spaces left.
 * - to red: There are no remaining free character spaces.
 * 
 * @param {{
 * textContent: string,
 * maxLength: number,
 * lengthDisplayElementId: string
 * }} args - Group of indexed arguments in the form of a dictionary.
 * 
 * @param {string} args.textContent - Currently written text content in the
 * specific text-based input field.
 * @param {string} args.maxLength - Maximum length (character count) for the
 * specific text-based input field.
 * @param {string} args.lengthDisplayElementId - ID of element displaying the
 * max length counter for the specific text-based input field.
 */
function updateTextContentLength({
    textContent,
    maxLength,
    lengthDisplayElementId
}) {
    // Update currentLength number
    const currentLength = textContent.length;
    const lengthDisplayElement = document.getElementById(lengthDisplayElementId);
    lengthDisplayElement.textContent = currentLength;
    // Update currentLength number style if necessary
    lengthDisplayElement.classList.remove("input-warning", "incorrect-input");
    if (currentLength > maxLength) {
        lengthDisplayElement.classList.add("incorrect-input");
    } else if (currentLength >= maxLength-5) {
        lengthDisplayElement.classList.add("input-warning");
    }
}
