// =================================================================
// Functionality related to message and error log
// =================================================================

// Loading existing message and error entries into log
window.addEventListener('load', function() {
    setTimeout(function() {
        eel.show_log_messages();
        eel.show_log_errors();
    }, 1);
});


// --------------------------------------------------------------
// Showing / hiding log sidebar
// --------------------------------------------------------------

/**
 * Makes log sidebar / side panel visible.
 */
function showLogSidebar() {
    let sidebar = document.getElementById("log-sidebar");
    // Prevent scrolling in body of currently open page
    document.body.classList.add("no-scroll");
    sidebar.classList.remove('hidden-element');
}


/**
 * Makes log sidebar / side panel hidden.
 */
function hideLogSidebar() {
    let sidebar = document.getElementById("log-sidebar");
    sidebar.classList.add('hidden-element');
    // Allow scrolling in body of currently open page
    document.body.classList.remove("no-scroll");
}


// --------------------------------------------------------------
// Loading and rendering current messages and errors into log
// --------------------------------------------------------------
/**
 * @typedef {Object} LogEntry
 * @property {string} text - log entry text.
 * @property {string[]} highlightables - log entry text fragments
 * that need to be highlighted.
 * @property {string} timestamp - time at which the log entry was 
 * generated.
 */

eel.expose(loadLogEntry)
/**
 * Loads log entry into specific log section.
 * 
 * @param {string} entryId - id of the log entry (used for specific log
 * instance clearing functionality).
 * @param {LogEntry} logEntry - object of log entry that needs to be
 * displayed.
 * @param {LogEntry} entryType - type of log entry being loaded. 
 * (e.g. `message` or `error`).
 */
function loadLogEntry(entryId, logEntry, entryType) {
    addHighlights(logEntry);
    
    // Log entry part with delete action
    let aDelete = document.createElement("a");
    aDelete.innerHTML = "Clear";
    aDelete.role = "button";
    aDelete.classList.add("clickable", "action", ACTION_STYLES.delete);

    let deleteContainer = document.createElement("div");
    deleteContainer.classList.add("log-entry-action-box");
    deleteContainer.appendChild(aDelete);

    // Log entry part with timestamp and text
    let pTimestamp = document.createElement("p");
    pTimestamp.classList.add("log-timestamp");
    pTimestamp.innerHTML = logEntry.timestamp;
    let pText = document.createElement("p");
    pText.innerHTML = logEntry.text;

    let logEntryContentContainer = document.createElement("div");
    logEntryContentContainer.classList.add("log-entry-content-box");
    logEntryContentContainer.appendChild(pTimestamp);
    logEntryContentContainer.appendChild(pText);

    // Combining both containers into one for the entire log entry
    let logEntryContainer = document.createElement("div");
    logEntryContainer.classList.add("log-entry");
    logEntryContainer.appendChild(deleteContainer);
    logEntryContainer.appendChild(logEntryContentContainer);

    // Append everything to the log entry content box
    switch (entryType) {
        case "message":
            aDelete.onclick = () => eel.clear_message(entryId);
            _appendThroughId("messages", logEntryContainer, "before");
            break;
        case "error":
            aDelete.onclick = () => eel.clear_error(entryId);
            _appendThroughId("errors", logEntryContainer, "before");
            break;
    }
}


/**
 * Adds highlighting style to defined log entry text fragments, based
 * on `logEntry.highlightables` array.
 * 
 * @param {LogEntry} logEntry - Object of log entry that needs its text 
 * fragments to be highlighted.
 */
function addHighlights(logEntry) {
    const escaped = logEntry.highlightables
        // longest first (avoids issue with highlighting substrings)
        .sort((a, b) => b.length - a.length)
        .map(h => h.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));

    const pattern = escaped.join('|');

    const regex = new RegExp(
        `(^|\\s)(${pattern})(?=$|[\\s!?,.:])`,
        'g'
    );

    logEntry.text = logEntry.text.replace(regex, (match, before, word) => {
        return `${before}<span class="highlight">${word}</span>`;
    });
}
