// =================================================================
// Functionality related to message and error log
// =================================================================

// Loading existing messages and errors into log content box
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
 * @typedef {Object} Message
 * @property {string} message_text - log message text.
 * @property {string[]} highlightables - message text fragments
 * that need to be highlighted.
 * @property {string} timestamp - time at which the message was 
 * generated.
 */

eel.expose(loadLogMessage)
/**
 * Loads message into log.
 * 
 * @param {string} id - id of the message (used for specific log
 * instance clearing functionality).
 * @param {Message} message - object of message that needs to be
 * displayed.
 */
function loadLogMessage(id, message) {
    addHighlights(message);
    
    // Message part with delete action
    let aDelete = document.createElement("a");
    aDelete.innerHTML = "Clear";
    aDelete.role = "button";
    aDelete.classList.add("clickable", "action", "delete-action");
    aDelete.onclick = () => eel.clear_message(id);

    let deleteContainer = document.createElement("div");
    deleteContainer.classList.add("log-instance-action-box");
    deleteContainer.appendChild(aDelete);

    // Message part with timestamp and text
    let pTimestamp = document.createElement("p");
    pTimestamp.classList.add("log-timestamp");
    pTimestamp.innerHTML = message.timestamp;
    let pMessage = document.createElement("p");
    pMessage.innerHTML = message.message_text;

    let messageContentContainer = document.createElement("div");
    messageContentContainer.classList.add("log-instance-content-box");
    messageContentContainer.appendChild(pTimestamp);
    messageContentContainer.appendChild(pMessage);

    // Combining both containers into one for the entire message
    // instance
    let messageContainer = document.createElement("div");
    messageContainer.classList.add("log-instance");
    messageContainer.appendChild(deleteContainer);
    messageContainer.appendChild(messageContentContainer);

    // Append everything to the log message content box
    _appendThroughId("messages", messageContainer, "before");
}


/**
 * Adds highlighting style to defined message fragments, based
 * on `message.highlightables` array.
 * 
 * @param {Message} message - Object of message that needs its fragments
 * to be highlighted.
 */
function addHighlights(message) {
    const escaped = message.highlightables
        // longest first (avoids issue with highlighting substrings)
        .sort((a, b) => b.length - a.length)
        .map(h => h.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));

    const pattern = escaped.join('|');

    const regex = new RegExp(
        `(^|\\s)(${pattern})(?=$|[\\s!?,.:])`,
        'g'
    );

    message.message_text = message.message_text.replace(regex, (match, before, word) => {
        return `${before}<span class="highlight">${word}</span>`;
    });
}
