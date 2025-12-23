// =====================================================================
// NoiseDataManager exposed method usage
// =====================================================================

window.onload = function() {
    setTimeout(function() {
        eel.view_noise_data_instances();
    }, 1);
};


function importCSVCalibrationData() {
    var reference_key = document.getElementById("key_input").value;
    var file_path = document.getElementById("path_input").value;

    eel.import_csv_calibration_data(reference_key, file_path);
}


function removeNoiseDataInstance(referenceKey) {
    eel.remove_noise_data_instance(referenceKey);
}


function viewSpecificNoiseData(referenceKey) {
    window.location.href = `noise_data_instance.html?id=${referenceKey}`;
}


function handleAction(actionType, rowId) {
    switch (actionType) {
        case "delete":
            removeNoiseDataInstance(rowId);
            break;
        case "view":
            viewSpecificNoiseData(rowId);
            break;
    }
}
