// =====================================================================
// Helper functions only used by other project-related JS functions.
// =====================================================================

/**
 * Appends an element to another parent element through its ID attribute.
 * 
 * Helper function to simplify code and eliminate unnecessary code
 * duplication.
 * 
 * @param {string} id - ID of parent element.
 * @param {HTMLElement} appendableElement  - appendable element.
 * @param {string} placement - determines where inside of the parent should
 * the element be appended - before all other elements (`"before"`) or 
 * at the end of the parent element (`"after"`). 
 * [`Default = "after"`]
 */
function _appendThroughId(id, appendableElement, placement="after") {
    let element = document.getElementById(id);
    if (placement === "before") element.prepend(appendableElement);
    else element.appendChild(appendableElement);
}
