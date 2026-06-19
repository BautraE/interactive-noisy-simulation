// =====================================================================
// Functions related to page for viewing a specifc experiment instance
// (experiment job management)
// =====================================================================
// File contents list:
// 1. Page-specific variables
// 2. Initial page-specific actions that are performed upon
//    loading in this page.
// 3. Content management
// 4. Link handling
// 5. Action handling
// 6. New job creation for experiment instance
// -----------------------------------------------------------------

// --------------------------------------------------------------
// 1. Page-specific variables
// --------------------------------------------------------------

// Reference key of currently opened experiment instance
let experimentReferenceKey;
// Form step titles for job instance creation
const jobFormSteps = {
    1: "Job instance creation",
    2: "Noise settings",
    3: "Simulator settings"
};
// Assignment of specific functions that shoul be executed upon loading
// tables and rows for displaying existing instance data.
instanceDataModifications = {
    row: modifyDataRow,
    table: addEventListenerToTable
}


// --------------------------------------------------------------
// 2. Initial page-specific actions that are performed upon
//    loading in this page.
// --------------------------------------------------------------

window.addEventListener('load', function() {
    setTimeout(function() {
        // Loads params from URL
        const urlParams = new URLSearchParams(window.location.search);
        experimentReferenceKey = urlParams.get('id');
        // Loads data on page
        setSpecificInstanceName(experimentReferenceKey);
        eel.view_experiment_jobs(experimentReferenceKey);
    }, 1);
});


// --------------------------------------------------------------
// 3. Content management
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


/**
 * Calls sub-functions that are responsible for making required changes
 * related to the specific table row.
 * 
 * @param {HTMLElement} rowElement - HTML row element that will
 * be modified.
 * @param {Array} rowContent - Array of row content (as strings) that
 * are displayed within the row. Primarily used for obtaining something
 * that will be used during element modification.
 */
function modifyDataRow(rowElement, rowContent) {
    addAttributesToRow(rowElement, rowContent);
    colorStatusCell(rowElement, rowContent);
}


/**
 * Adds additional attribues to created instance table row elements.
 * 
 * All data row elements will have the class "clickable"
 * added to them.
 * 
 * All data row elements will have a dataset added to them
 * dynamically, which will contain the IDs of a specific instance.
 * 
 * @param {HTMLElement} rowElement - HTML row element that will
 * be modified.
 * @param {Array} rowContent - Array of row content (as strings) that
 * are displayed within the row. Primarily used for obtaining something
 * that will be used during element modification.
 */
function addAttributesToRow(rowElement, rowContent) {
    rowElement.classList.add("clickable");
    rowElement.dataset.jobId = rowContent[0];
}


/**
 * Adds specific CSS styles for the status collumn (accomplished through 
 * table rows).
 * 
 * @param {HTMLElement} rowElement - HTML row element that will
 * be modified.
 * @param {Array} rowContent - Array of row content (as strings) that
 * are displayed within the row. Primarily used for obtaining something
 * that will be used during element modification.
 */
function colorStatusCell(rowElement, rowContent) {
    const statusMessageStyles = {
        completed: "variant-green",
        partial: "variant-yellow",
        pending: "variant-grey"
    }

    // Job completion status is located in the 2nd column
    let statusCell = rowElement.children[1];
    let statusStyle = statusMessageStyles[rowContent[1]];
    if(statusStyle) {
        statusCell.classList.add("status-text", statusStyle);
    }
}


/**
 * Adds event listener to displayable instance table element.
 * 
 * The added event listener is responsible for switching between
 * displaying detailed view of specific job instances.
 * 
 * @param {HTMLElement} tableElement - HTML table element that will
 * have the event listener added to it.
 */
function addEventListenerToTable(tableElement) {
    tableElement.addEventListener("click", (e) => {
        const row = e.target.closest("tr.clickable");
        if (row) {
            eel.view_experiment_job_detailed(
                experimentReferenceKey,
                row.dataset.jobId
            );
        }
    });
}


eel.expose(viewJobDetailedData);
/**
 * Calls other specific functions for the following goals:
 * - to render detailed experiment job data for the user;
 * - to change the CSS style of job instance talbe rows based on the currently
 *   selected experiment job instance.
 * 
 * @param {object} detailedData - Dictionary containing detailed data
 * about the selected experiment job instance.
 * 
 * @param {string} detailedData.reference_key - reference key of job instance.
 */
function viewJobDetailedData(detailedData) {
    selectJobRow(detailedData.reference_key);
    renderDetailedJobView(detailedData);
}


/**
 * Switches active experiment job instance row in table (CSS-related
 * changes).
 * 
 * @param {HTMLElement} rowElement - HTML row element of selected
 * experiment job instance.
 */
function selectJobRow(jobId) {
    document.querySelectorAll("#job-instances-table tr.active")
        .forEach(row => row.classList.remove("active"));
    const rowElement = document.querySelector(`[data-job-id="${jobId}"]`);
    rowElement.classList.add("active");
}


/**
 * Displays required HTML code with detailed data about the selected
 * experiment job instance.
 * 
 * @param {object} detailedData - Dictionary containing detailed data
 * about the selected experiment job instance.
 * 
 * @param {string} detailedData.reference_key - reference key of job instance.
 * @param {string} detailedData.circuit - reference key of selected circuit
 * instance for this job.
 * @param {string} detailedData.shot_count - number of times the circuit will
 * be executed as part of this job.
 * @param {string} detailedData.hardware - selected hardware that the simulator
 * will run on (e.g. "CPU" or "GPU").
 * @param {string} detailedData.simulation_method - selected simulation method
 * that the simulator will use.
 * @param {string} detailedData.noise_model - reference key of selected noise
 * model instance for this job.
 * @param {string} detailedData.optimization_level - circuit optimization level
 * that will be used during circuit transpilation.
 */
function renderDetailedJobView(detailedData) {
    const viewContainer = document.getElementById("detailed-job-view");
    viewContainer.innerHTML = `
        <div class="details">
            <div>
                <span class="label">Job reference key:</span>  
                <span>${detailedData.reference_key}</span>
            </div>
            <div>
                <span class="label">Circuit:</span>  
                <span>${detailedData.circuit}</span>
            </div>
            <div>
                <span class="label">Settings:</span>  
                <ul>
                    <li>
                        <span class="label">Shot count:</span>  
                        <span>${detailedData.shot_count}</span>
                    </li>
                    <li>
                        <span class="label">Hardware:</span>  
                        <span>${detailedData.hardware}</span>
                    </li>
                    <li>
                        <span class="label">Simulation method:</span>  
                        <span>${detailedData.simulation_method}</span>
                    </li>
                    <li>
                        <span class="label">Noise model:</span>  
                        <span>${detailedData.noise_model}</span>
                    </li>
                    <li>
                        <span class="label">Circuit optimization level:</span>  
                        <span>${detailedData.optimization_level}</span>
                    </li>
                </ul>
            </div>
            <div>
                <span class="label">Job progress:</span>
                <ul>
                    <li>
                        <span class="label">Completed shots:</span>  
                        <span>${detailedData.completed_shots}</span>
                    </li>
                    <li>
                        <span class="label">Remaining shots:</span>  
                        <span>${detailedData.remaining_shots}</span>
                    </li>
                </ul>
            </div>
            <div>
                <span class="label">Current result counts:</span>
                ${
                    typeof detailedData.current_result_counts === "string"
                        ? `<span>${detailedData.current_result_counts}</span>`
                        : `<pre>${JSON.stringify(detailedData.current_result_counts, null, 4)}</pre>`
                }
            </div>
        </div>
        <div class="actions">
            <div role="button"
                 class="clickable button-regular variant-red"
                 onclick="handleAction('delete', '${detailedData.reference_key}')">Delete</div>
        </div>
    `;
}


// --------------------------------------------------------------
// 4. Link handling
// --------------------------------------------------------------

/**
 * Returns user to the previous page (which in this case should)
 * only be the page for managing all experiment instances.
 */
function backToInstances() {
    if (window.history.length > 1) {
        window.history.back();
    } else {
        window.location.href = 'index.html';
    }
}


// --------------------------------------------------------------
// 5. Action handling
// --------------------------------------------------------------

/**
 * Redirects action to specific function based on given
 * action type.
 * 
 * @param {string} actionType - type of action expressed as a
 * string ("delete", "view", etc.).
 * @param {string} referenceKey - reference key of the current 
 * experiment job instance for which the action must be performed.
 */
function handleAction(actionType, rowId) {
    switch (actionType) {
        case "delete":
            eel.remove_job_from_experiment(experimentReferenceKey, rowId);
            break;
    }
}


// --------------------------------------------------------------
// 6. New job creation for experiment instance
// --------------------------------------------------------------

// --------------------------------------------------------------
// Initializer function

/**
 * Runs additional functionality-related initialization steps for the 
 * experiment job instance creation form.
 */
async function initNewInstanceForm() {
    // -------------------------------------------------------------------------------
    // Adding missing dynamic values for radio input fields

    // Step 1: Job instance creation:
    await loadRadioInputOptions({
        containerId: "circuit-instance-container",
        inputId: "circuit-instance",
        dataRetrievalFunction: eel.get_circuit_references
    });
    // Step 2: Noise settings:
    await loadRadioInputOptions({
        containerId: "noise-model-container",
        inputId: "noise-model-instance",
        dataRetrievalFunction: eel.get_noise_model_references
    });
    await loadRadioInputOptions({
        containerId: "opt-level-container",
        inputId: "opt-level-option",
        dataRetrievalFunction: eel.get_available_optimization_options
    });
    // Step 3: Simulator settings:
    await loadRadioInputOptions({
        containerId: "sim-method-options-container",
        inputId: "sim-method",
        dataRetrievalFunction: eel.get_available_sim_methods
    });
    await loadRadioInputOptions({
        containerId: "hardware-options-container",
        inputId: "hardware-option",
        dataRetrievalFunction: eel.get_available_hardware_options
    });


    // -------------------------------------------------------------------------------
    // Adding max length number for form input fields

    const maxLengthSpan = document.getElementById("reference-key-input-max-length");
    maxLengthSpan.textContent = MAX_REFERENCE_KEY_LENGTH;


    // -------------------------------------------------------------------------------
    // Adjusting height of current form window for height change animation

    activePopupElement = document.querySelector('.pop-up');
    adjustHeightOfParent(activePopupElement);
    
    // -------------------------------------------------------------------------------
    // Adding required event listeners to form:

    // Adding required event listeners for switching between form steps
    const popupContainer = document.querySelector(".form-step-select");
    popupContainer.addEventListener("click", (event) => {
        const step = event.target.closest('.step-bar-block');
        if (step) {
            let activeStepNr = switchActiveStep(step);
            updateActiveStepTitle(activeStepNr);
            updateActiveStepInputs(step.dataset.stepName);
        }
    });


    // Adding required event listeners for reference key input field
    const referenceInput = document.getElementById("reference-key");
    referenceInput.addEventListener('change', () =>
        removeInputErrorStyles({
            outlinedElementId: "reference-key", 
            messageElementId: "reference-key-input-message"
        })
    );
    referenceInput.addEventListener('input', () =>
        referenceInput.value = adjustReferenceKey(referenceInput.value)
    );
    referenceInput.addEventListener('input', () =>
        updateTextContentLength({
            textContent: referenceInput.value,
            maxLength: MAX_REFERENCE_KEY_LENGTH,
            lengthDisplayElementId: "reference-key-input-length",
        })
    );


    // Adding required event listeners for circuit input field
    const circuitInput = document.getElementById("circuit-instance-container");
    circuitInput.addEventListener("change", (event) => {
        if (event.target.name === "circuit-instance") {
            removeInputErrorStyles({
                outlinedElementId: "circuit-instance-container",
                messageElementId: "circuit-instance-input-message"
            });
        }
    });


    // Adding required event noisy / noiseless simulation toggle checkbox
    const noiselessSimulationCheckbox = document.getElementById("noiseless-simulation");
    noiselessSimulationCheckbox.addEventListener('change', () => {
        removeInputErrorStyles({
            outlinedElementId: "noise-model-container", 
            messageElementId: "noise-model-input-message"
        });
        removeInputErrorStyles({
            outlinedElementId: "opt-level-container",
            messageElementId: "opt-level-input-message"
        });

        const isChecked = noiselessSimulationCheckbox.checked;
        if (isChecked) {
            disableForm("noise-model-container");
            disableForm("opt-level-container");
        } else {
            enableForm("noise-model-container");
            enableForm("opt-level-container");
        }
    });


    // Adding required event listeners for noise model input field
    const noiseModelInput = document.getElementById("noise-model-container");
    noiseModelInput.addEventListener("change", (event) => {
        if (event.target.name === "noise-model-instance") {
            removeInputErrorStyles({
                outlinedElementId: "noise-model-container",
                messageElementId: "noise-model-input-message"
            });
        }
    });


    // Adding required event listeners for optimization level input field
    const optimizationLevelInput = document.getElementById("opt-level-container");
    optimizationLevelInput.addEventListener("change", (event) => {
        if (event.target.name === "opt-level-option") {
            removeInputErrorStyles({
                outlinedElementId: "opt-level-container",
                messageElementId: "opt-level-input-message"
            });
        }
    });


    // Adding required event listeners for shot count input field
    const shotCountInput = document.getElementById("shot-count");
    shotCountInput.addEventListener('change', () =>
        removeInputErrorStyles({
            outlinedElementId: "shot-count", 
            messageElementId: "shot-count-input-message"
        })
    );
    

    // Adding required event listeners for hardware input field
    const hardwareInput = document.getElementById("hardware-options-container");
    hardwareInput.addEventListener("change", (event) => {
        if (event.target.name === "hardware-option") {
            removeInputErrorStyles({
                outlinedElementId: "hardware-options-container",
                messageElementId: "hardware-options-input-message"
            });
        }
    });


    // Adding required event listeners for simulation method input field
    const simulationMethodInput = document.getElementById("sim-method-options-container");
    simulationMethodInput.addEventListener("change", (event) => {
        if (event.target.name === "sim-method") {
            removeInputErrorStyles({
                outlinedElementId: "sim-method-options-container",
                messageElementId: "sim-method-options-input-message"
            });
        }
    });
}


/**
 * Switches active step - adjusts the style of the currently selected 
 * step in the step navigation bar.
 * 
 * @param {HTMLElement} step - HTML container element for specific step
 * in the step navigation bar.
 * 
 * @returns {nubmer} Order number of the new active step. To be primarily
 * used for switching active step heading.
 */
function switchActiveStep(step) {
    allSteps = document.querySelectorAll('.step-bar-block');
    allSteps.forEach(block => block.classList.remove('active-step'));
    
    step.classList.add('active-step');
    // Returns number of active step
    return Array.from(allSteps).indexOf(step) + 1;
}


/**
 * Updates active step title by adding the correct step order number and
 * changing to the new title text.
 * 
 * @param {number} activeStepNr - Order number of the currently active step.
 */
function updateActiveStepTitle(activeStepNr) {
    const stepNumber = document.getElementById("form-current-step-number");
    stepNumber.innerText = activeStepNr;
    const heading = document.getElementById("form-current-step-heading-text");
    heading.innerText = jobFormSteps[activeStepNr];
}


/**
 * Switches form input fields based on currently active step.
 * 
 * @param {string} activeStepName - Name of currently active step that
 * is written in the dataset step-name for specific elements. This is
 * used to determine which element belongs to which step.
 */
function updateActiveStepInputs(activeStepName) {
    const formInputs = document
        .querySelectorAll('.form-input-group[data-step-name]');

    formInputs.forEach(formInput => {
        const shouldShow = formInput.dataset.stepName === activeStepName;
        formInput.classList.toggle('hidden-element', !shouldShow);
    });

    adjustHeightOfParent(activePopupElement);
}


// --------------------------------------------------------------
// Regular functionality

/**
 * Takes input field values and attempts to create a new job
 * instance for the current experiment.
 */
async function createInstance() {
    // Obtaining values from input fields:
    // Step 1: Job instance creation
    const referenceKey = document.getElementById("reference-key").value;
    const circuitReferenceKey = document.querySelector(
        'input[name="circuit-instance"]:checked'
    );
    // Step 2: Noise settings
    const noiselessSimulation = document.getElementById("noiseless-simulation").checked;
    const noiseModelReferenceKey = document.querySelector(
        'input[name="noise-model-instance"]:checked'
    );
    const optimizationLevel = document.querySelector(
        'input[name="opt-level-option"]:checked'
    );
    // Step 3: Simulator settings
    const shotCount = document.getElementById("shot-count").value.trim();
    const hardware = document.querySelector(
        'input[name="hardware-option"]:checked'
    );
    const simulationMethod = document.querySelector(
        'input[name="sim-method"]:checked'
    );

    // Validation definitions
    let validations = [
        {value: referenceKey, validator: validateReferenceKey},
        {value: circuitReferenceKey?.value, validator: validateCircuit},
        {value: shotCount, validator: validateShotCount},
        {value: hardware?.value, validator: validateHardware},
        {value: simulationMethod?.value, validator: validateSimulationMethod}
    ]
    if (!noiselessSimulation) {
        validations.push(
            {value: noiseModelReferenceKey?.value, validator: validateNoiseModel},
            {value: optimizationLevel?.value, validator: validateOptimizationLevel}
        );
    }
    // Validation process
    const isValid = await validateForm(validations);

    // New instance creation if all input fields are valid
    if (isValid) {
        eel.create_job_for_experiment(
            experimentReferenceKey,
            referenceKey,
            circuitReferenceKey.value,
            noiselessSimulation ? null : noiseModelReferenceKey.value,
            shotCount,
            hardware.value,
            simulationMethod.value,
            noiselessSimulation ? null : optimizationLevel.value,
        );
        hidePopUpWindow();
    }
}


// --------------------------------------------------------------
// Input validation

/**
 * Reference key input value validation function.
 * 
 * The function uses the provided reference key value and goes through
 * all required validation steps for it.
 * 
 * @param {string} referenceKey - Reference key value that will be
 * validated.
 * 
 * @returns {boolean} Whether or not the input field is valid (valid = true,
 * invalid = false)
 */
async function validateReferenceKey(referenceKey) {
    const outlinedElementId = "reference-key";
    const messageElementId = "reference-key-input-message";

    // If reference key field is empty
    if (!referenceKey) {
        addInputErrorStyles({
            outlinedElementId: outlinedElementId,
            messageElementId: messageElementId,
            errorMessageText: "Reference key is mandatory!"
        });
        return false;
    }
    // If reference key exceeds maximum length
    if (referenceKey.length > MAX_REFERENCE_KEY_LENGTH) {
        addInputErrorStyles({
            outlinedElementId: outlinedElementId,
            messageElementId: messageElementId,
            errorMessageText: `The reference key is too long! Max length is 
            ${MAX_REFERENCE_KEY_LENGTH} characters!`
        });
        return false;
    }
    // If reference key is already used by same type of instance
    const isUnique = await eel.is_job_key_unique(experimentReferenceKey, referenceKey)();
    if (!isUnique) {
        addInputErrorStyles({
            outlinedElementId: outlinedElementId,
            messageElementId: messageElementId,
            errorMessageText: "This reference key is already used by another job within this experiment instance!"
        });
        return false;
    }

    // Input field is valid
    return true;
}


/**
 * Circuit input value validation function.
 * 
 * The function uses the selected circuit reference and goes through
 * all required validation steps for it.
 * 
 * @param {string} circuit - Reference key for the circuit that
 * needs to be validated.
 * 
 * @returns {boolean} Whether or not the input field is valid (valid = true,
 * invalid = false)
 */
function validateCircuit(circuit) {
    const outlinedElementId = "circuit-instance-container";
    const messageElementId = "circuit-instance-input-message";

    // If source data is not selected
    if (!circuit) {
        addInputErrorStyles({
            outlinedElementId: outlinedElementId,
            messageElementId: messageElementId,
            errorMessageText: "A circuit instance must be selected!"
        });
        return false;
    }

    // Input field is valid
    return true;
}


/**
 * Noise model input value validation function.
 * 
 * The function uses the selected noise model reference and goes through
 * all required validation steps for it.
 * 
 * @param {string} circuit - Reference key for the noise model that
 * needs to be validated.
 * 
 * @returns {boolean} Whether or not the input field is valid (valid = true,
 * invalid = false)
 */
function validateNoiseModel(circuit) {
    const outlinedElementId = "noise-model-container";
    const messageElementId = "noise-model-input-message";

    // If source data is not selected
    if (!circuit) {
        addInputErrorStyles({
            outlinedElementId: outlinedElementId,
            messageElementId: messageElementId,
            errorMessageText: "Unless a noiseless simulation is intended, a noise model instance must be selected!"
        });
        return false;
    }

    // Input field is valid
    return true;
}


/**
 * Optimization level input value validation function.
 * 
 * The function uses the selected optimization level and goes through
 * all required validation steps for it.
 * 
 * @param {string} optimizationLevel - Selected optimization level.
 * 
 * @returns {boolean} Whether or not the input field is valid (valid = true,
 * invalid = false)
 */
function validateOptimizationLevel(optimizationLevel) {
    const outlinedElementId = "opt-level-container";
    const messageElementId = "opt-level-input-message";

    // If an optimization level is not selected
    if (!optimizationLevel) {
        addInputErrorStyles({
            outlinedElementId: outlinedElementId,
            messageElementId: messageElementId,
            errorMessageText: "An optimization level must be selected!"
        });
        return false;
    }

    // Input field is valid
    return true;
}


/**
 * Shot count input value validation function.
 * 
 * The function uses the provided reference key value and goes through
 * all required validation steps for it.
 * 
 * @param {string} shotCount - Shot count value that will be
 * validated.
 * 
 * @returns {boolean} Whether or not the input field is valid (valid = true,
 * invalid = false)
 */
function validateShotCount(shotCount) {
    const outlinedElementId = "shot-count";
    const messageElementId = "shot-count-input-message";

    // If no shot count has been written
    if (!shotCount) {
        addInputErrorStyles({
            outlinedElementId: outlinedElementId,
            messageElementId: messageElementId,
            errorMessageText: "Shot count is mandatory!"
        });
        return false;
    }
    // If entered value is not a positive number, starting from 1
    if (!/^[1-9]\d*$/.test(shotCount)) {
        addInputErrorStyles({
            outlinedElementId: outlinedElementId,
            messageElementId: messageElementId,
            errorMessageText: "Shot count must be a positive integer value, starting from '1'!"
        });
        return false;
    }

    // Input field is valid
    return true;
}


/**
 * Hardware input value validation function.
 * 
 * The function uses the selected hardware and goes through
 * all required validation steps for it.
 * 
 * @param {string} hardware - Selected hardware option.
 * 
 * @returns {boolean} Whether or not the input field is valid (valid = true,
 * invalid = false)
 */
function validateHardware(hardware) {
    const outlinedElementId = "hardware-options-container";
    const messageElementId = "hardware-options-input-message";

    // If hardware is not selected
    if (!hardware) {
        addInputErrorStyles({
            outlinedElementId: outlinedElementId,
            messageElementId: messageElementId,
            errorMessageText: "Hardware must be selected for use during simulation!"
        });
        return false;
    }

    // Input field is valid
    return true;
}


/**
 * Simulation method input value validation function.
 * 
 * The function uses the selected simulation method and goes through
 * all required validation steps for it.
 * 
 * @param {string} simulationMethod - Selected simulation method option.
 * 
 * @returns {boolean} Whether or not the input field is valid (valid = true,
 * invalid = false)
 */
function validateSimulationMethod(simulationMethod) {
    const outlinedElementId = "sim-method-options-container";
    const messageElementId = "sim-method-options-input-message";

    // If simulation method is not selected
    if (!simulationMethod) {
        addInputErrorStyles({
            outlinedElementId: outlinedElementId,
            messageElementId: messageElementId,
            errorMessageText: "A simulation method must be selected!"
        });
        return false;
    }

    // Input field is valid
    return true;
}
