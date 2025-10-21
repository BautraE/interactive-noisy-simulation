/** 
 * HTML element IDs that must be removed once a main class 
 * method is done executing. */
const HTML_IDS = [
    "output-box", "output-heading", "messages", "status", "tracebacks", 
    "qubit-noise-data", "qubit-noise-data-table", "message-box-heading", 
    "table"
];


/**
 * Adds a table element to the "messages" content box.
 * Before adding new table element, removes id attribute
 * from any other table that may be present to avoid any
 * potential conflicts.
 */
function addGenericTable() {
    unsetIdValues(["table"]);
    
    let table = document.createElement("table");
    table.id = "table";
    table.classList.add("tables");
    _appendThroughId("messages", table);
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
function addGenericTableRow(rowAsString, rowType) {
    let row = document.createElement("tr");

    let rowContent = rowAsString.split(",");
    for(let cellContent of rowContent) {
        let tableCell = document.createElement(rowType);
        tableCell.innerHTML = cellContent;

        row.appendChild(tableCell);
    }

    if (rowType === "th") row.classList.add("header-rows");
    else row.classList.add("regular-rows");

    _appendThroughId("table", row);
}


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


/**
 * Adds the relevant traceback to a main class method output box.
 * @param {string} tracebackCss 
 * @param {string} tracebackHtml 
 */
function addTraceback(tracebackCss, tracebackHtml) {
    let tracebackContentBox = _createTracebackContainer();
    
    // Dynamically add Python pygments generated CSS for tracebacks
    let style = document.createElement("style");
    style.id = "traceback-style";
    style.innerHTML = tracebackCss;
    document.head.appendChild(style);

    // Append traceback HTML
    tracebackContentBox.insertAdjacentHTML("beforeend", tracebackHtml);
}


/**
 * Creates and adds container that will contain retrieved qubit CSV 
 * noise data.
 * This container will have content boxes added to it by 
 * {@link addQubitNoiseDataContentBox}.
 */
function addQubitNoiseDataContainer() {
    let contentTitle = _createContentTitle("Retrieved qubits:")
    let contentContainer = _createContentContainer("qubit-noise-data",
                                                   [contentTitle]);
    _appendToOutputBox(contentContainer);
}


/**
 * Adds a content box that will contain retrieved CSV noise data for 
 * a certain qubit. Before this is done, the ID of the previous content
 * box must be removed so that no conflicts occur.
 * The content box is added to the content container created by
 * {@link addQubitNoiseDataContainer}.
 */
function addQubitNoiseDataContentBox() {
    unsetIdValues(["qubit-noise-data-table"]);
    
    let table = document.createElement("table");
    table.classList.add("tables");
    table.id = "qubit-noise-data-table";
    
    let contentBox = _createContentBox();
    contentBox.appendChild(table)

    _appendThroughId("qubit-noise-data", contentBox);
}


/**
 * Adds a row of CSV noise data for a certain qubit.
 * These rows are added to a table that is located in the currently
 * relevant content box created by {@link addQubitNoiseDataContentBox}.
 * @param {string} attributeName 
 * @param {string} value 
 */
function addQubitNoiseDataRow(attributeName, value) {
    let nameCell = document.createElement("td");
    nameCell.classList.add("qubit-noise-data-cells")
    nameCell.innerHTML = attributeName;

    let valueCell = document.createElement("td");
    valueCell.classList.add("highlighted-text");
    valueCell.classList.add("qubit-noise-data-cells")
    valueCell.innerHTML = value;

    let row = document.createElement("tr");
    row.classList.add("qubit-noise-data-rows");
    row.appendChild(nameCell);
    row.appendChild(valueCell);

    _appendThroughId("qubit-noise-data-table", row);
}


/**
 * Adapts the default "Message log" content container for other
 * general use case possibilities. This is achieved by simply renaming
 * the content container heading.
 * @param {string} headingText 
 */
function genericContentContainer(headingText) {
    let contentTitle = document.getElementById("message-box-heading");
    contentTitle.innerHTML = headingText;
}


/**
 * Adds the main title to a main class method output box.
 * @param {string} headingText 
 */
function setOutputHeading(headingText) {
    let outputHeading = document.getElementById("output-heading");
    outputHeading.innerHTML = headingText;
}


/**
 * Changes the status of a main class method output box.
 * This includes the status message and visual style of it.
 * @param {number} status 
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
 * Removed IDs can either be passed as an argument (removableIds)
 * or not, in which case the default list of all registered IDs 
 * will be used ({@link HTML_IDS}).
 * @example
 * // removes only the requested ID
 * unsetIdValues("id")
 * @example
 * // removes all IDs from HTML_IDS
 * unsetIdValues()
 * @param {string[]} removableIds 
 */
function unsetIdValues(removableIds = null) {
    let ids = removableIds || HTML_IDS

    for (let i = 0; i < ids.length; i++) {
        let element = document.getElementById(ids[i]);
        if (element) {
            element.removeAttribute("id");
        }
    }
}


// CUSTOM HELPER FUNCTIONS

/**
 * Helper function.
 * Appends an element to another parent element through its
 * ID attribute.
 * @param {string} id 
 * @param {HTMLElement} appendableElement 
 */
function _appendThroughId(id, appendableElement) {
    let element = document.getElementById(id);
    element.appendChild(appendableElement);
}


/**
 * Helper function.
 * Appends an element to the currently active main class method 
 * output box.
 * @param {HTMLElement} newContainer 
 */
function _appendToOutputBox(newContainer) {
    let outputBox = document.getElementById("output-box");
    outputBox.insertBefore(newContainer, outputBox.lastElementChild);
}


/**
 * Helper function.
 * Creates a content box element & assigns additional ID and class
 * attributes to it. 
 * Content boxes are div containers that will contain, lets say,
 * printable content for the user, for example, messages, qubit CSV
 * noise data, etc.
 * These content boxes go inside of content containers created by
 * {@link _createContentContainer}.
 * @param {string} id 
 * @param {string[]} classes 
 * @returns {HTMLDivElement}
 */
function _createContentBox(id=null, classes=[]) {
    let contentBox = document.createElement("div");
    contentBox.classList.add("content-boxes");

    if(id) contentBox.id = id;

    for(let className of classes) {
        contentBox.classList.add(className);
    }

    return contentBox;
}


/**
 * Helper function.
 * Creates a content container element for the currently active 
 * main class method output box. These container eventually
 * consist of a content title element from {@link _createContentTitle}
 * and a single or multiple content box elements from 
 * {@link _createContentBox}.
 * @param {string} id 
 * @param {HTMLElement[]} elements - elements to append.
 * @returns 
 */
function _createContentContainer(id=null, elements=[]) {
    let contentContainer = document.createElement("div");
    
    if(id) contentContainer.id = id;
    
    for(let element of elements) {
        contentContainer.appendChild(element);
    }
    
    return contentContainer;
}


/**
 * Helper function.
 * Creates a title element for a content container from 
 * {@link _createContentContainer}.
 * @param {string} titleText 
 * @returns {HTMLParagraphElement}
 */
function _createContentTitle(titleText) {
    let contentTitle = document.createElement("p");
    contentTitle.classList.add("content-headings");
    contentTitle.innerHTML = titleText;
    return contentTitle;
}


/**
 * Helper function.
 * Creates a specific content container element for traceback
 * content - used by {@link addTraceback} function.
 * The created container is automatically appended to the 
 * currently active main class method output box.
 * The returned element is not the container itself, but instead
 * the content box element inside of this container. This is done
 * to simplify traceback content appending for {@link addTraceback}.
 * @returns {HTMLDivElement}
 */
function _createTracebackContainer() {
    let contentTitle = _createContentTitle("Error log:");
    let contentBox = _createContentBox(null, ["traceback-boxes"]);
    let contentContainer = _createContentContainer(
        null, 
        [contentTitle, contentBox]
    );
    _appendToOutputBox(contentContainer);
    return contentBox;
}
