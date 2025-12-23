// =====================================================================
// Functions related to page for viewing a specifc noise data instance
// (noise data about for specific qubits)
// =====================================================================

let referenceKey

window.onload = function() {
    setTimeout(function() {
        const urlParams = new URLSearchParams(window.location.search);
        referenceKey = urlParams.get('id');
        eel.view_qubit_data(referenceKey);
    }, 1);
};

function backToInstances() {
    window.location.href = `index.html`;
}
