window.addEventListener('load', function() {
    setTimeout(function() {
        eel.show_log_messages();
    }, 1);
});


eel.expose(loadLogMessage)
function loadLogMessage(id, timestamp, messageText) {
    // Message part with delete action
    let aDelete = document.createElement("a");
    aDelete.innerHTML = "Clear";
    aDelete.role = "button";
    aDelete.onclick = () => eel.clear_message(id)

    let deleteContainer = document.createElement("div");
    deleteContainer.appendChild(aDelete);

    // Message part with timestamp and text
    let pTimestamp = document.createElement("p");
    pTimestamp.innerHTML = timestamp;
    let pMessage = document.createElement("p");
    pMessage.innerHTML = messageText;

    let messageContentContainer = document.createElement("div");
    messageContentContainer.appendChild(pTimestamp);
    messageContentContainer.appendChild(pMessage);

    // Combining both containers into one for the entire message
    // instance
    let messageContainer = document.createElement("div");
    messageContainer.appendChild(deleteContainer);
    messageContainer.appendChild(messageContentContainer);

    _appendThroughId("messages", messageContainer, "before");
}
