// =================================================================
// Minor miscellaneous functions that are common across almost all
// pages.
// =================================================================

// --------------------------------------------------------------
// Pop-up functionality
// --------------------------------------------------------------

/**
 * Hides pop-up / dialog window and removes it from currently active
 * HTML.
 */
function hidePopUpWindow() {
    let popupContainer = document.getElementById("pop-up-container");
    popupContainer.classList.add("hidden-element");
    popupContainer.replaceChildren();
}


/**
 * Loads retrieved HTML code for relevant pop-up / dialog window and
 * makes it visible on the page.
 * 
 * @param {string} popupName - name of pop-up, based on which the
 * HTML code will be retrieved (matches HTML popup code fie name
 * without the exension).
 */
async function showPopUpWindow(popupName) {
    let popupContainer = document.getElementById("pop-up-container");
    let popupCode = await eel.get_popup(popupName)();
    popupContainer.innerHTML = popupCode;
    popupContainer.classList.remove("hidden-element");
}


// --------------------------------------------------------------
// General content-related functions
// --------------------------------------------------------------
eel.expose(addNoInstanceMessage);
/**
 * Adds specific message that notifies about there not being any
 * instances or messages to display.
 * 
 * @param {string} messageText - text of the message that will
 * be shown.
 * @param {string} parentElementId - id of the element where the
 * message will be added to.
 */
function addNoInstanceMessage(messageText, parentElementId) {
    let messageElement = document.createElement("p");
    messageElement.classList.add("no-instances-text");
    messageElement.innerHTML = messageText;

    _appendThroughId(parentElementId, messageElement);
}
