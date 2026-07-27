// =================================================================
// Functionality that is common across all instance management-
// related pages.
// =================================================================
// File contents list:
// 1. Global page-specific variables
// 2. Data loading
// 3. Form input validation
// -----------------------------------------------------------------

// --------------------------------------------------------------
// 1. Global page-specific variables
// --------------------------------------------------------------

/**
 * Restriction limit for reference key length. Used for reference
 * key input fields.
 * @type {int}
 */
const MAX_REFERENCE_KEY_LENGTH = 50;
/**
 * HTML element of currently displayed popup element container.
 * If no popup is displayed, value will be `null`.
 * Primarily used for height adjustmend animation through JS due 
 * to existing restrictions with CSS functionality.
 * @type {?HTMLElement}
 */
let activePopupElement = null;
/**
 * Dictionary containing potential functions related to any 
 * modifications of instance data while it is being rendered.
 * @type {Object}
 */
let instanceDataModifications = {};


// --------------------------------------------------------------
// 2. Data loading
// --------------------------------------------------------------

/**
 * Loads available radio input options based on retrieved data.
 * 
 * It is also possible to return empty container messages to this function
 * as a `string` in situations, where there are no available radio input
 * options.
 * 
 * Also works for updating radio input option fields if some condition is met,
 * changing the supported choices. Previously selected value is preserved if
 * that same option is present after the changes.
 * 
 * @param {{
 * containerId: string,
 * inputId: string,
 * dataRetrievalFunction: function(): string[]
 * }} args - Group of indexed arguments in the form of a dictionary.
 * 
 * @param {string} args.containerId - ID of the container element where the
 * loaded radio input options will be placed.
 * @param {string} args.inputId - Value for `id` and `name` attributes for 
 * all radio input options of a radio input field.
 * @param {function(): string[]} args.dataRetrievalFunction - List of radio 
 * input option texts. If no options are available to be added, an empty
 * list (array in JS) is returned.
 * @param {Object} args.dataRetrievalArgs - Dictionary of additional arguments
 * that are passed to the data retrieval function, affecting what kind of
 * data gets returned.
 * 
 * @returns {void}
 */
async function loadRadioInputOptions({
    containerId,
    inputId,
    dataRetrievalFunction,
    dataRetrievalArgs
}) {
    // Obtains available options
    let options;
    if (dataRetrievalArgs) {
        options = await dataRetrievalFunction(dataRetrievalArgs)();
    } else {
        options = await dataRetrievalFunction()();
    }

    let previousSelection;
    if (options.length) {
        // Saves previously selected value if there was one
        previousSelection = document.querySelector(
            `input[name="${inputId}"]:checked`
        )?.value;
    }

    // Removes any previous content in for displayable data update
    removeContainerContent(containerId);

    // If empty container message is returned instead of options, that message
    // is rendered.
    if (typeof options == "string") {
        addEmptyContainerMessage(options, containerId);
        return;
    }
    
    const container = document.getElementById(containerId);
    for(let option of options ?? []) {
        //  Clicking anywhere on label element ensures input activation.
        const label = document.createElement("label");
        label.classList.add("radio-option");

        label.innerHTML = `
            <input type="radio"
                   name="${inputId}"
                   id="${inputId}"
                   value="${option}"
                   ${option === previousSelection ? "checked" : ""}>
            <span class="custom-radio"></span>
            <span class="radio-text">${option}</span>
        `;

        container.appendChild(label);
    }
}


eel.expose(viewInstanceData);
/**
 * Renders data about created instances for an instance-specific management
 * page.
 * 
 * @param {Object} instanceData - Dictionary object containing instance data
 * (for existing instances) of a specific instance type.
 * @param {string} containerId - ID of the container element where the
 * rendered data will be placed.
 * @param {string} tableId - `id` attribute value that will be set for the
 * table element containing instance data.
 * 
 * @returns {void}
 */
function viewInstanceData(
    instanceData, 
    containerId, 
    tableId
) {
    tableElement = addTable(
        containerId, tableId, 
        instanceData.columns,
        instanceData.actions.length === 0 ? false : true
    );
    // Runs table-related modification if defined
    instanceDataModifications.table?.(tableElement);

    const dataRows = instanceData.rows;
    dataRows.forEach(rowData => {
        let rowElement = addTableRow(tableId, rowData, instanceData.actions);
        // Runs table row-related modification if defined
        instanceDataModifications.row?.(rowElement, rowData);
    });
}


// --------------------------------------------------------------
// 3. Form input validation
// --------------------------------------------------------------

/**
 * Validates if values in input fields are valid for use. If not,
 * the user is notified about it.
 * 
 * @param {{
 * value: string, 
 * validator: Function
 * }[]} validations - List of validations that should be completed 
 * for a specific form (its input fields).
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
function addInputErrorStyles({
    outlinedElementId, 
    messageElementId, 
    errorMessageText
}) {
    const outlinedElement = document.getElementById(outlinedElementId);
    outlinedElement.classList.add("input-error");

    const messageElement = document.getElementById(messageElementId);
    messageElement.textContent = errorMessageText;
    messageElement.classList.remove("hidden-element");

    // Adjusts height after adding error-related content
    if(activePopupElement) {
        adjustHeightOfParent(activePopupElement);
    }
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
function removeInputErrorStyles({
    outlinedElementId, 
    messageElementId
}) {
    const outlinedElement = document.getElementById(outlinedElementId);
    outlinedElement.classList.remove("input-error");

    const messageElement = document.getElementById(messageElementId);
    messageElement.textContent = "";
    messageElement.classList.add("hidden-element");

    // Adjusts height after removing error-related content
    if(activePopupElement) {
        adjustHeightOfParent(activePopupElement);
    }
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
