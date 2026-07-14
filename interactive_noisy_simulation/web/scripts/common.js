// =================================================================
// Minor miscellaneous functions that are common across almost all
// pages.
// =================================================================
// File contents list:
// 1. Global variables
// 2. Pop-up and form functionality.
// 3. General content-related functions
// 4. Container management
// 5. Data table creation
// 6. Content animation functionality - JS functionality for 
//    something that is not yet available through pure CSS (in
//    other words, hacky workarounds).
// -----------------------------------------------------------------


// --------------------------------------------------------------
// 1. Global variables
// --------------------------------------------------------------

/**
 * CSS style classes that get set for specific actions
 * @type {Object}
 */
const ACTION_STYLES = {
    delete: "variant-red",
    view: "variant-default",
    add: "variant-green",
    remove: "variant-red"
}

// --------------------------------------------------------------
// 2. Pop-up and form functionality
// --------------------------------------------------------------

/**
 * @typedef {() => (Promise<void>|void)} PopupInitializerFunction
 */

/**
 * Hides pop-up / dialog window and removes it from currently active
 * HTML.
 */
function hidePopUpWindow() {
    let popupContainer = document.getElementById("pop-up-container");
    popupContainer.classList.add("hidden-element");
    popupContainer.replaceChildren();
}


/**
 * Loads retrieved HTML code for relevant pop-up / dialog window and
 * makes it visible on the page.
 * 
 * @param {string} popupName - name of pop-up, based on which the
 * HTML code will be retrieved (matches HTML popup code fie name
 * without the exension).
 * @param {PopupInitializerFunction} initializer - reference to additional function
 * that should be executed upon showing a specifc pop-up.
 * `[Default = null]`
 */
async function showPopUpWindow(popupName, initializer=null) {
    let popupContainer = document.getElementById("pop-up-container");
    let popupCode = await eel.get_popup(popupName)();
    popupContainer.innerHTML = popupCode;
    popupContainer.classList.remove("hidden-element");

    if(initializer) await initializer();
}


/**
 * Disables specific form with the given ID.
 * 
 * Also works for specific input fields.
 * 
 * @param {string} formId - ID of the form HTML element that needs all of
 * its input fields to be disabled.
 */
function disableForm(formId) {
    const form = document.getElementById(formId);
    const elements = form.querySelectorAll("input");

    for(const el of elements) {
        el.disabled = true;
    }
}


/**
 * Enables specific form with the given ID.
 * 
 * Also works for specific input fields.
 * 
 * @param {string} formId - ID of the form HTML element that needs all of
 * its input fields to be enabled.
 */
function enableForm(formId) {
    const form = document.getElementById(formId);
    const elements = form.querySelectorAll("input");

    for(const el of elements) {
        el.disabled = false;
    }
}


// --------------------------------------------------------------
// 3. General content-related functions
// --------------------------------------------------------------

eel.expose(addEmptyContainerMessage);
/**
 * Adds specific message that notifies that there is nothing to 
 * currently display in a specific container.
 * 
 * @param {string} messageText - text of the message that will
 * be shown.
 * @param {string} parentElementId - ID of the HTML element to 
 * which the message will be added to.
 */
function addEmptyContainerMessage(messageText, parentElementId) {
    let messageElement = document.createElement("p");
    messageElement.classList.add("empty-container-text");
    messageElement.innerHTML = messageText;

    _appendThroughId(parentElementId, messageElement);
}


eel.expose(updateSpanContent);
/**
 * Updates content of span elements (meant for small text-related
 * values or numbers).
 * 
 * @param {string} newContent - new content that will replace the old.
 * @param {string} spanId - id of span element that will have its content 
 * updated.
 */
function updateSpanContent(newContent, spanId) {
    let spanElement = document.getElementById(spanId);
    spanElement.innerText = newContent;
}


eel.expose(updateProgressBar);
/**
 * Updates current progress percentage values for a specific progress bar
 * based on its id.
 * 
 * @param {number|string} percentage - New progress percentage value.
 * If this value will be of type string, it will be `--` - a placeholder
 * for when there is no calculable percentage value.
 * @param {string} barId - ID of the progress bar being updated.
 */
function updateProgressBar(percentage, barId) {
    const progressBar = document.getElementById(barId);
    const progressLabel = progressBar.nextElementSibling;

    if (typeof percentage === "number") {
        progressBar.style.width = `${percentage}%`;
        progressLabel.innerText = `${percentage}%`;
    } else {
        progressBar.style.width = `100%`;
        progressLabel.innerText = `${percentage}`;
    }
}


eel.expose(activateProgressBar);
/**
 * Activates specific progress bar by removing style class for
 * inactive visual identifiers.
 * 
 * @param {string} barId - ID of the progress bar being activated.
 */
function activateProgressBar(barId) {
    const progressBar = document.getElementById(barId);

    // Removes default inactive class from the progress bar.
    progressBar.classList.remove("inactive");
}


eel.expose(deactivateProgressBar);
/**
 * Deactivates specific progress bar by adding style class for
 * inactive visual identifiers.
 * 
 * @param {string} barId - ID of the progress bar being deactivated.
 */
function deactivateProgressBar(barId) {
    const progressBar = document.getElementById(barId);

    // Adds default inactive class to the progress bar.
    progressBar.classList.add("inactive");
}


// --------------------------------------------------------------
// 4. Container management
// --------------------------------------------------------------

/**
 * Creates a content box element & inserts it into a parent content
 * container element through its ID.
 * 
 * Content boxes are div containers that will contain printable content
 * for the user, for example, qubit CSV noise data, created instances etc.
 * 
 * @param {string} containerId - ID of parent content container.
 * @param {string} boxId - ID of created content box.
 */
eel.expose(createContentBox)
function createContentBox(containerId, boxId) { 
    let contentBox = document.createElement("div");
    contentBox.classList.add("content-box", "variant-light");
    contentBox.id = boxId;

    _appendThroughId(containerId, contentBox);
}


/**
 * Clears (deletes) all child elements from a parent element based on
 * its ID.
 * 
 * @param {string} containerId - ID of container whose child elements will
 * be deleted.
 */
eel.expose(removeContainerContent)
function removeContainerContent(containerId) {
    let container = document.getElementById(containerId)
    while (container.firstChild) {
      container.removeChild(container.firstChild);
    }
}


// --------------------------------------------------------------
// 5. Data table creation
// --------------------------------------------------------------

eel.expose(addTable);
/**
 * Adds table inside specific container for the purpose of displaying
 * some kind of data.
 * 
 * @param {string} containerId - ID of the container element where the
 *  newly created table will be placed.
 * @param {string} tableId - ID attribute value that will be set for 
 * the table so that it can be accessed further on.
 * @param {string[]} columns - List of column names that will be 
 * set in the header row of the table. If none are given, no table 
 * header row is created (`Default = []`).
 * @param {boolean} hasActions - Boolean flag value for whether 
 * or not the table should contain an additional column - Actions
 * (`Default = false`).
 */
function addTable(containerId, tableId, columns=[], hasActions=false) {
    let table = document.createElement("table");
    table.id = tableId;

    if (columns.length !== 0) {
        if (hasActions) columns.push("Actions");

        let row = document.createElement("tr");

        for(let cellContent of columns) {
            let tableCell = document.createElement("th");
            tableCell.innerHTML = cellContent;
            row.appendChild(tableCell);
        }
        
        table.appendChild(row);
    }

    _appendThroughId(containerId, table);
    return table;
}


eel.expose(addTableRow);
/**
 * Creates new row with given data and adds it to the table with the 
 * specified ID.
 * 
 * Note: There is no validation intended to check whether data row 
 * cell count exceeds the cell count of the tables header row.
 * 
 * @param {string} tableId - ID of table, to which the new row shall 
 * be added.
 * @param {string[]} rowContent - List of row table cell content.
 * @param {string[]} actions - List of action strings that serve as 
 * both visible action link names and action type identifiers.
 * (`Default = []`)
 */
function addTableRow(tableId, rowContent, actions=[]) {
    let row = document.createElement("tr");

    // Adds row cell content
    for(let cellContent of rowContent) {
        let tableCell = document.createElement("td");
        addDynamicContentStyle(cellContent, tableCell);
        tableCell.innerHTML = cellContent;
        row.appendChild(tableCell);
    }
    // If given, adds actions to row
    if (actions.length !== 0) {
        let tableCell = document.createElement("td");
        
        let actionDiv = document.createElement("div");
        actionDiv.classList.add("action-container");
        
        for(let action of actions) {
            let actionElement = document.createElement("a");
            actionElement.role = "button";
            actionElement.innerText = action;
            actionElement.classList.add("clickable", "action", ACTION_STYLES[action]);
            actionElement.onclick = () => handleAction(action, rowContent[0]);

            actionDiv.appendChild(actionElement);
        }

        tableCell.appendChild(actionDiv);
        row.appendChild(tableCell);
    }

    _appendThroughId(tableId, row);
    return row;
}


/**
 * Adds specific style to table data cell element based on its content
 * 
 * This fumction currently provides a solution for dynamically applying
 * styles to specific content, for example, boolean-related data.
 * 
 * @param {string} cellContent - Table cell content, based on which a
 * specific style will be applied to the data cell element.
 * @param {HTMLElement} element - Table data cell element that will
 * have a specifc CSS class with style added to it.
 */
function addDynamicContentStyle(cellContent, element) {
    switch (cellContent) {
        case "Available":
            element.classList.add("green-text");
            break;

        case "Removed":
            element.classList.add("red-text");
            break;

        default:
            break;
    }
}


// --------------------------------------------------------------
// 6. Content animation functionality
// --------------------------------------------------------------

/**
 * Adjusts height of an element based on its children and how much space
 * they take up.
 * 
 * This fumction if purely for making CSS-related animations work for
 * height changes as something like this (in this specific situation)
 * is not simply accomplishable through pure CSS.
 * 
 * @param {HTMLElement} parentElement - Element that will have its height
 * adjusted.
 */
function adjustHeightOfParent(parentElement) {
    let totalHeight = 0;

    const children = [...parentElement.children];

    children.forEach(child => {
        if (child.offsetParent === null) return; // skips display:none

        const style = getComputedStyle(child);

        totalHeight += child.offsetHeight;
        totalHeight += parseFloat(style.marginTop);
        totalHeight += parseFloat(style.marginBottom);
    });

    parentElement.style.height = totalHeight + "px";
}
