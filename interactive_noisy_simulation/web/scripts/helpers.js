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


/**
 * Removes classes from a specific element based on the specified prefix.
 * 
 * This is useful in cases, where multiple different class names start
 * with the same prefixes, and that specific class has to be removed,
 * no matter what the full name of the class is.
 * 
 * E.g.: variant-green, variant-red, variant-disabled.
 * 
 * @param {HTMLElement} element  - Element with removable CSS classes.
 * @param {string} prefix - Removable CSS class name prefix.
 */
function removeClassesByPrefix(element, prefix) {
    element.classList.forEach(cls => {
        if (cls.startsWith(prefix)) {
            element.classList.remove(cls);
        }
    });
}
