// =================================================================
// Functionality related to the "Simulation" page.
// =================================================================
// File contents list:
// 1. Page-specific variables 
// 2. Initial page-specific actions that are performed upon
//    loading in this page.
// 3. Action handling
// -----------------------------------------------------------------

// --------------------------------------------------------------
// 1. Page-specific variables
// --------------------------------------------------------------

// Assignment of specific functions that shoul be executed upon loading
// tables and rows for displaying existing instance data.
instanceDataModifications = {
    row: colorStatusCell
}


// --------------------------------------------------------------
// 2. Initial page-specific actions that are performed upon
//    loading in this page.
// --------------------------------------------------------------

window.addEventListener('load', function() {
    setTimeout(function() {
        eel.update_simulation_content();
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

    let statusCell = rowElement.children[2];
    let statusStyle = statusMessageStyles[rowContent[2]];
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
        case "add":
            eel.add_experiment_to_queue(rowId);
            break;
        case "remove":
            eel.remove_experiment_from_queue(rowId);
            break;
    }
}
