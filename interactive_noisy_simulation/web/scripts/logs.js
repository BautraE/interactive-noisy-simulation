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

eel.expose(loadLogMessage)
/**
 * Loads message into log.
 * 
 * @param {string} id - id of the message (used for specific log
 * instance clearing functionality).
 * @param {string} timestamp - time at which the message was generated.
 * @param {string} messageText - log message text.
 */
function loadLogMessage(id, timestamp, messageText) {
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
    pTimestamp.innerHTML = timestamp;
    let pMessage = document.createElement("p");
    pMessage.innerHTML = messageText;

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
