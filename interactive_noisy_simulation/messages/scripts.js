/**
 * =========================================================================
 * Table of Contents for scripts.js file
 * =========================================================================
 * 1. Output box main functionality - setting main heading, adjusting
 *      status, removing used element IDs.
 * 2. Message log functionality - adding messages to message content box.
 * 3. Traceback functionality - adding traceback-related HTML and CSS.
 * 4. Additional content container / box creation - functions used for 
 *      creating content containers and content boxes. This also includes 
 *      additional helper methods used by the two main functions.
 * 5. Creating tables and table content - functions used for adding tables
 *      to content boxes, as well as adding content to these tables.
 * 6. Modification of default message log content container / content box.
 * 7. Miscellaneous additional functions - helper functions that simplify
 *      repetitive actions for certain methods that require more than one
 *      line of code.
 * =========================================================================
 */


// =========================================================================
// 1. Output box main functionality - setting main heading, adjusting
//      status, removing used element IDs.
// =========================================================================

/**
 * Adds the main title to a main class method output box.
 * 
 * @param {string} headingText 
 */
function setOutputHeading(headingText) {
    let outputHeading = document.getElementById("output-heading");
    outputHeading.innerHTML = headingText;
}

/**
 * Changes the status of a main class method output box.
 * This includes the status message and visual style of it.
 * 
 * @param {number} status -
 * - `1` successful execution
 * - `0` failed execution
 */
function setStatus(status) {
    const STATUS_MAP = {
        1: {
            class: "status-completed",
            message: "completed"
        },
        0: {
            class: "status-failed",
            message: "failed"
        }
    };

    let statusMessage = document.getElementById("status");
    statusMessage.classList.remove('status-in-progress');

    statusMessage.classList.add(STATUS_MAP[status].class);
    statusMessage.innerHTML = STATUS_MAP[status].message;
}

/**
 * Removes IDs from HTML elements.
 * 
 * @param {string} idsAsString - IDs that will be removed from elements.
 *      Initially sent as a single string that has to be divided into a
 *      list based on the specific separator string `,SEPARATOR,`.
 */
function unsetIdValues(idsAsString) {
    let ids = idsAsString.split(",SEPARATOR,");

    for (let i = 0; i < ids.length; i++) {
        let element = document.getElementById(ids[i]);
        if (element) {
            element.removeAttribute("id");
        }
    }
}


// =========================================================================
// 2. Message log functionality - adding messages to message content box.
// =========================================================================

/**
 * Adds message to "Message log" content box.
 * @param {string} message 
 */
function addMessage(message) {
    let textElement = document.createElement('p');
    textElement.classList.add("messages-text");
    textElement.innerHTML = message;

    _appendThroughId("messages", textElement);
}


// =========================================================================
// 3. Traceback functionality - adding traceback-related HTML and CSS.
// =========================================================================

/**
 * Adds relevant traceback to a main class method output box, if an error
 * occurred.
 * 
 * @param {string} tracebackCss - CSS code for the automatically syled 
 * custom traceback output.
 * @param {string} tracebackHtml - HTML code for obtained traceback text
 * that is ready to be displayed.
 * @param {string} boxId - Id for the content box that will contain the
 * obtained traceback text.
 */
function addTraceback(tracebackCss, tracebackHtml, boxId) {
    // Dynamically add Python pygments generated CSS for tracebacks
    let style = document.getElementById("traceback-style");
    if(!style) {
        style = document.createElement("style");
        style.id = "traceback-style";
        style.innerHTML = tracebackCss;
        document.head.appendChild(style);
    }

    // Append traceback HTML (requires different appending
    // method than provided by _appendThroughId() function)
    let tracebackContentBox = document.getElementById(boxId);
    tracebackContentBox.classList.add("traceback-boxes")
    tracebackContentBox.insertAdjacentHTML("beforeend", tracebackHtml);
}


// =========================================================================
// 4. Additional content container / box creation - functions used for 
//      creating content containers and content boxes. This also includes 
//      additional helper methods used by the two main functions.
// =========================================================================

/**
 * Creates a content container element for the currently active 
 * main class method output box. 
 * 
 * These containers also come with a title element that is created
 * with the help of the function {@link _createContentTitle}.
 * 
 * Containers are made for wrapping content boxes that are created with
 * the function {@link createContentBox}
 * 
 * @param {string} id 
 * @param {string} elements - elements to append.
 * @returns 
 */
function createContentContainer(id, headingText) {
    let contentContainer = document.createElement("div");
    contentContainer.id = id;
    
    contentTitle = _createContentTitle(headingText);
    contentContainer.appendChild(contentTitle);

    _appendToOutputBox(contentContainer);
}


/**
 * Creates a content title element for a content container.
 * 
 * Helper function that is used by {@link createContentContainer}.
 * 
 * @param {string} titleText - content title text, e.x. *Message log*.
 * 
 * @returns {HTMLParagraphElement} - created title element with requested
 * text as its content.
 */
function _createContentTitle(titleText) {
    let contentTitle = document.createElement("p");
    contentTitle.classList.add("content-headings");
    contentTitle.innerHTML = titleText;
    return contentTitle;
}


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
function createContentBox(boxId, parentId) { 
    let contentBox = document.createElement("div");
    contentBox.classList.add("content-boxes");
    contentBox.id = boxId;

    _appendThroughId(parentId, contentBox);
}


// =========================================================================
// 5. Creating tables and table content - functions used for adding tables
//      to content boxes, as well as adding content to these tables.
// =========================================================================

/**
 * Adds a table element to a specified content box, based
 * on its ID.
 */
function addTable(container_id) {
    let table = document.createElement("table");
    table.id = "table";
    table.classList.add("tables");
    _appendThroughId(container_id, table);
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
function addTableRow(rowAsString, rowType) {
    let row = document.createElement("tr");

    let rowContent = rowAsString.split(",SEPARATOR,");
    for(let cellContent of rowContent) {
        let tableCell = document.createElement(rowType);
        tableCell.innerHTML = cellContent;

        row.appendChild(tableCell);
    }

    if (rowType === "th") row.classList.add("header-rows");
    else row.classList.add("regular-rows");

    _appendThroughId("table", row);
}


// =========================================================================
// 6. Modification of default message log content container / content box.
// =========================================================================

/**
 * Adapts the default *Message log* content heading by chaning it to
 * a different one.
 * 
 * @param {string} headingText - new content title text.
 */
function modifyContentTitle(headingText) {
    let contentTitle = document.getElementById("message-box-heading");
    contentTitle.innerHTML = headingText;
}


// =========================================================================
// 7. Miscellaneous additional functions - helper functions that simplify
//      repetitive actions for certain methods that require more than one
//      line of code.
// =========================================================================

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


/**
 * Appends an element to the currently active main class method output box.
 * 
 * This is a helper function.
 * 
 * @param {HTMLElement} newContainer - container element that gets added to
 * output box.
 */
function _appendToOutputBox(newContainer) {
    let outputBox = document.getElementById("output-box");
    outputBox.insertBefore(newContainer, outputBox.lastElementChild);
}
