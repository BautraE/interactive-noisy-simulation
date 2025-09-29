HTML_IDS = [
    "output-box", "output-heading", "messages", "status", "tracebacks", "qubit-noise-data",
    "qubit-noise-data-table", "message-box-heading"
];


function addMessage(message) {
    let textElement = document.createElement('p');
    textElement.classList.add("messages-text");
    textElement.innerHTML = message;

    __appendThroughId("messages", textElement);
}


function addTraceback(tracebackCss, tracebackHtml) {
    let tracebackContentBox = __createTracebackContainer();
    
    // Dynamically add Python pygments generated CSS for tracebacks
    let style = document.createElement("style");
    style.id = "traceback-style";
    style.innerHTML = tracebackCss;
    document.head.appendChild(style);

    // Append traceback HTML
    tracebackContentBox.insertAdjacentHTML("beforeend", tracebackHtml);
}


function addQubitNoiseDataContainer() {
    let contentTitle = __createContentTitle("Retrieved qubits:")
    let contentContainer = __createContentContainer("qubit-noise-data",
                                                    [contentTitle]);
    __appendToOutputBox(contentContainer);
}


function addQubitNoiseDataContentBox() {
    unsetIdValues(["qubit-noise-data-table"]);
    
    let table = document.createElement("table");
    table.classList.add("qubit-noise-data-tables");
    table.id = "qubit-noise-data-table";
    
    let contentBox = __createContentBox();
    contentBox.appendChild(table)

    __appendThroughId("qubit-noise-data", contentBox);
}


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

    __appendThroughId("qubit-noise-data-table", row);
}


function genericContentContainer(headingText) {
    let contentTitle = document.getElementById("message-box-heading");
    contentTitle.innerHTML = headingText;
}


function setOutputHeading(headingText) {
    let outputHeading = document.getElementById("output-heading");
    outputHeading.innerHTML = headingText;
}


function setStatus(status) {
    let statusMessage = document.getElementById("status");
    statusMessage.classList.remove('status-in-progress');
    if (status == 1) {
        statusMessage.classList.add("status-completed");
        statusMessage.innerHTML = "completed";
    } 
    else {
        statusMessage.classList.add("status-failed");
        statusMessage.innerHTML = "failed";
    }
}


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

function __appendThroughId(id, appendableElement) {
    element = document.getElementById(id);
    element.appendChild(appendableElement);
}


function __appendToOutputBox(newContainer) {
    let outputBox = document.getElementById("output-box");
    outputBox.insertBefore(newContainer, outputBox.lastElementChild);
}


function __createContentBox(id=null, classes=[]) {
    let contentBox = document.createElement("div");
    contentBox.classList.add("content-boxes");

    if(id) contentBox.id = id;

    for(let className of classes) {
        contentBox.classList.add(className);
    }

    return contentBox;
}


function __createContentContainer(id=null, elements=[]) {
    let contentContainer = document.createElement("div");
    
    if(id) contentContainer.id = id;
    
    for(let element of elements) {
        contentContainer.appendChild(element);
    }
    
    return contentContainer;
}


function __createContentTitle(titleText) {
    let contentTitle = document.createElement("p")
    contentTitle.classList.add("content-headings");
    contentTitle.innerHTML = titleText;
    return contentTitle;
}


function __createTracebackContainer() {
    let contentTitle = __createContentTitle("Error log:");
    let contentBox = __createContentBox(null, ["traceback-boxes"]);
    let contentContainer = __createContentContainer(null, [contentTitle, contentBox]);
    __appendToOutputBox(contentContainer);
    return contentBox;
}
