// =================================================================
// Functionality related to a specific page - viewing and managing
// all noise model instances.
// =================================================================
// File contents list:
// 1. Action handling
// 2. New NoiseModelInstance creation form functionality
// -----------------------------------------------------------------

// Loading existing noise data instances
window.addEventListener('load', function() {
    setTimeout(function() {
        eel.view_noise_model_instances();
    }, 1);
});


// --------------------------------------------------------------
// 1. Action handling
// --------------------------------------------------------------

/**
 * Redirects action to specific function based on given
 * action type.
 * 
 * @param {string} actionType - type of action expressed as a
 * string ("delete" or "view").
 * @param {string} referenceKey - reference key of the current 
 * noise data instance for which the action must be performed.
 */
function handleAction(actionType, rowId) {
    switch (actionType) {
        case "delete":
            eel.remove_noise_model_instance(rowId);
            break;
    }
}


// --------------------------------------------------------------
// 2. New NoiseModelInstance creation form functionality
// --------------------------------------------------------------

/**
 * Creates radio input fields for each existing noise data instance.
 * 
 * Used in the pop-up form for creating new noise model instances.
 */
async function loadAvailableNoiseData() {
    let reference_keys = await eel.get_noise_data_references()();

    const container = document.getElementById("noise-source-container");

    for(let key of reference_keys) {
        //  Clicking anywhere on label element ensures input activation.
        const label = document.createElement("label");
        label.classList.add("radio-option");

        label.innerHTML = `
            <input type="radio"
                   name="noise-data-source"
                   id="noise-data-source"
                   value="${key}">
            <span class="custom-radio"></span>
            <span class="radio-text">${key}</span>
        `;

        container.appendChild(label);
    }
}


/**
 * Takes input field values and attempts to create a new noise model
 * instance.
 * 
 * Right before creation process begins, action buttons are replaced
 * by a progress bar.
 */
async function createNoiseModelInstance() {
    // Hides actions and shows progress bar
    const actions = document.getElementById("action-buttons");
    const progressBar = document.getElementById("progress-bar");
    progressBar.classList.remove("hidden-element");
    actions.classList.add("hidden-element");
    // Retrieves form input data
    const referenceKey = document.getElementById("reference-key");
    const noiseDataSource = document.querySelector(
        'input[name="noise-data-source"]:checked'
    );
        
    disableForm("pop-up-form");
    await eel.create_noise_model_instance(referenceKey.value, noiseDataSource.value)();
    hidePopUpWindow();
}


eel.expose(updateInstanceProgress);
/**
 * Updates current progress percentage values for progress bar showing
 * creation of a new NoiseModelInstance object.
 * 
 * @param {number} percentage - New progress percentage value.
 */
function updateInstanceProgress(percentage) {
    const progressBar = document.getElementById("current-progress");
    progressBar.style.width = `${percentage}%`;
    progressBar.innerText = `${percentage}%`;
}
