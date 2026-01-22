// =========================================================
// Functionality related to message and error log
// =========================================================

// Loading existing messages into log content box
window.addEventListener('load', function() {
    setTimeout(function() {
        eel.show_log_messages();
    }, 1);
});


// Showing / hiding log sidebar
function showLogSidebar() {
    let sidebar = document.getElementById("log-sidebar");
    sidebar.classList.remove('hidden-log');
    sidebar.classList.add('visible-log');
}


function hideLogSidebar() {
    let sidebar = document.getElementById("log-sidebar");
    sidebar.classList.remove('visible-log');
    sidebar.classList.add('hidden-log');
}


eel.expose(loadLogMessage)
function loadLogMessage(id, timestamp, messageText) {
    // Message part with delete action
    let aDelete = document.createElement("a");
    aDelete.innerHTML = "Clear";
    aDelete.role = "button";
    aDelete.classList.add("log-clear-action");
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

    _appendThroughId("messages", messageContainer, "before");
}
