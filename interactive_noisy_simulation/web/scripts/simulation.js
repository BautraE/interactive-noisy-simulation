// =================================================================
// Functionality related to the "Simulation" page.
// =================================================================
// File contents list:
// 1. Page-specific variables 
// 2. Initial page-specific actions that are performed upon
//    loading in this page.
// 3. Action handling
// 4. Content & specific element management
// -----------------------------------------------------------------

// --------------------------------------------------------------
// 1. Page-specific variables
// --------------------------------------------------------------

// Assignment of specific functions that shoul be executed upon loading
// tables and rows for displaying existing instance data.
instanceDataModifications = {
    row: modifyDataRow
};

let queueExecuting = false;


// --------------------------------------------------------------
// 2. Initial page-specific actions that are performed upon
//    loading in this page.
// --------------------------------------------------------------

window.addEventListener('load', function() {
    setTimeout(function() {
        eel.update_simulation_content();
    }, 1);
});

// --------------------------------------------------------------
// Instance data modification functions that are executed upon loading
// in instance data.

/**
 * Calls sub-functions that are responsible for making required changes
 * related to the specific table row.
 * 
 * @param {HTMLElement} rowElement - HTML row element that will
 * be modified.
 * @param {Array} rowContent - Array of row content (as strings) that
 * are displayed within the row. Primarily used for obtaining something
 * that will be used during element modification.
 */
function modifyDataRow(rowElement, rowContent) {
    colorStatusCell(rowElement, rowContent);
    validateQueueEligibility(rowElement, rowContent);
}


/**
 * Validates if experiment actions should remain active based on
 * multiple factors.
 * 
 * These factors include:
 * - If the queue is being executed;
 * - If an experiment has no jobs or all jobs are completed.
 * 
 * If actions do get disabled, a tooltip will be added, explaining
 * the reason for disabling them.
 * 
 * @param {HTMLElement} rowElement - HTML row element that will
 * be modified.
 * @param {Array} rowContent - Array of row content (as strings) that
 * are displayed within the row. Primarily used for obtaining something
 * that will be used during element modification.
 */
function validateQueueEligibility(rowElement, rowContent) {
    const actionsCell = rowElement.children[3];
    const actionElement = actionsCell.querySelector("a");
    if (queueExecuting) {
        // Disables action element.
        removeClassesByPrefix(actionElement, "variant-")
        actionElement.classList.add("variant-disabled");
        actionElement.title = "No queue modification is allowed during execution.";
    }
    // Completion status is the 3rd column.
    else if (rowContent[2] === "no jobs" || rowContent[2] === "completed") {
        if (actionElement.innerHTML === "add") {
            // Disables action element.
            removeClassesByPrefix(actionElement, "variant-")
            actionElement.classList.add("variant-disabled");
            actionElement.onclick = null;
            // Adds hover tooltips that explain why input is disabled.
            if (rowContent[2] === "no jobs") {
                actionElement.title = "This experiment contains no jobs.";
            } else if (rowContent[2] === "completed") {
                actionElement.title = "All jobs from this experiment are completed.";
            }
        }   
    }
}


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
        // Shared statuses
        completed: "variant-green",
        "no jobs": "variant-grey",
        // Completion status
        partial: "variant-yellow",
        pending: "variant-grey",
        // Execution status
        queued: "variant-grey",
        "in progress": "variant-yellow"
    }

    // Experiment completion status is located in the 3rd column
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


// --------------------------------------------------------------
// 4. Content & specific element management
// --------------------------------------------------------------

eel.expose(updateQueueExecutionButton);
/**
 * Adds specific relevant CSS style class to the queue execution
 * button, based on the given state:
 * - "unavailable" - Queue cannot be executed because there are
 *   either no jobs to run, or the queue is empty;
 * - "running" - The queue is being executed;
 * - "available" - The queue is eligible to be executed.
 * 
 * @param {string} state - State, based on which the queue execution
 * button will be styled.
 */
function updateQueueExecutionButton(state) {
    const buttonElement = document.getElementById("queue-execution-button");
    switch (state) {
        case "unavailable":
            removeClassesByPrefix(buttonElement, "variant-");
            buttonElement.classList.add("variant-disabled");
            break;
        case "running":
            removeClassesByPrefix(buttonElement, "variant-");
            buttonElement.classList.add("variant-disabled");
            break;
        case "available":
            removeClassesByPrefix(buttonElement, "variant-");
            buttonElement.classList.add("variant-green");
            break;
    }
}


eel.expose(updateQueueExecutionStatus);
/**
 * Updates the queue execution status being stored in the variable
 * `queueExecuting` to whatever is passed to the function as an argument.
 * 
 * @param {boolean} isExecuting - new queue execution status that will be set.
 */
function updateQueueExecutionStatus(isExecuting) {
    queueExecuting = isExecuting;
}
