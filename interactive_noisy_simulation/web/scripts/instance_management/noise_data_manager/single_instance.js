// =====================================================================
// Functions related to page for viewing a specifc noise data instance
// (noise data about for specific qubits)
// =====================================================================

let referenceKey

window.addEventListener('load', function() {
    setTimeout(function() {
        // Loads params from URL
        const urlParams = new URLSearchParams(window.location.search);
        referenceKey = urlParams.get('id');
        // Loads data on page
        setSpecificInstanceName(referenceKey);
        eel.view_qubit_data(referenceKey);
    }, 1);
});


// --------------------------------------------------------------
// Content management
// --------------------------------------------------------------

/**
 * Adds name of the specific instance being viewed to the main
 * content container title.
 * 
 * @param {string} instanceName - name of instance being viewed.
 */
function setSpecificInstanceName(instanceName) {
    let span = document.getElementById("instance-name");
    span.innerText = instanceName;
}


// --------------------------------------------------------------
// Link handling
// --------------------------------------------------------------

/**
 * Returns user to the previous page (which in this case should)
 * only be the page for managing all noise data instances.
 */
function backToInstances() {
    if (window.history.length > 1) {
        window.history.back();
    } else {
        window.location.href = 'index.html';
    }
}
