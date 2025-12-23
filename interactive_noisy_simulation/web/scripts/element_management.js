// =====================================================================
// Functions for creating and managing HTML elements
// =====================================================================

// =====================================================================
// Messages
// =====================================================================

eel.expose(addMessage);
function addMessage(containerId, messageText) {
    let p = document.createElement("p");
    p.innerHTML = messageText;

    _appendThroughId(containerId, p);
}

// =====================================================================
// Tables
// =====================================================================

/**
 * Adds a table element to a specified content box, based
 * on its ID.
 */
eel.expose(addTable);
function addTable(containerId, tableId, columns, hasActions) {
    let table = document.createElement("table");
    table.id = tableId;
    table.classList.add("tables");

    if (columns.length !== 0) {
        if (hasActions) columns.push("Action");

        let row = document.createElement("tr");
        row.classList.add("header-rows");

        for(let cellContent of columns) {
            let tableCell = document.createElement("th");
            tableCell.innerHTML = cellContent;
            row.appendChild(tableCell);
        }
        
        table.appendChild(row);
    }

    _appendThroughId(containerId, table);
}


/**
 * Adds row to the currently active table inside of
 * the "messages" content box.
 * Table row needs to be specified - either a header
 * row or regular row.
 * All row elements must be passed as string while
 * being divided with a certain symbol. Python does
 * not allow list passing to JavaScript (at least
 * while using the current solution).
 * @param {string} rowAsString 
 * @param {string} rowType 
 */
eel.expose(addTableRow);
function addTableRow(tableId, rowContent, actions) {
    let row = document.createElement("tr");
    row.classList.add("regular-rows");

    for(let cellContent of rowContent) {
        let tableCell = document.createElement("td");
        tableCell.innerHTML = cellContent;
        row.appendChild(tableCell);
    }

    if (actions.length !== 0) {
        let tableCell = document.createElement("td");
        for(let action of actions) {
            let actionButton = document.createElement("button");
            actionButton.innerText = action.name
            actionButton.onclick = () => handleAction(action.type, rowContent[0])
            tableCell.appendChild(actionButton)
        }
        row.appendChild(tableCell)
    }

    _appendThroughId(tableId, row);
}


// =====================================================================
// Helper functions
// =====================================================================

/**
 * Appends an element to another parent element through its ID attribute.
 * 
 * This is a helper function.
 * 
 * @param {string} id - ID of parent element.
 * 
 * @param {HTMLElement} appendableElement  - element to append to parent.
 */
function _appendThroughId(id, appendableElement) {
    let element = document.getElementById(id);
    element.appendChild(appendableElement);
}


// =====================================================================
// Container management
// =====================================================================

/**
 * Creates a content box element & inserts it into a parent content
 * container element through its ID.
 * 
 * Content boxes are div containers that will contain printable content
 * for the user, for example, messages, qubit CSV noise data, etc.
 * These content boxes go inside of content containers created by
 * {@link createContentContainer}.
 * 
 * @param {string} boxId - ID of created content box.
 * @param {string} parentId - ID of parent content container.
 */
eel.expose(createContentBox)
function createContentBox(containerId, boxId) { 
    let contentBox = document.createElement("div");
    contentBox.classList.add("content-boxes");
    contentBox.id = boxId;

    _appendThroughId(containerId, contentBox);
}


eel.expose(removeContainerContent)
function removeContainerContent(containerId) {
    let container = document.getElementById(containerId)
    while (container.firstChild) {
      container.removeChild(container.firstChild);
    }
}
