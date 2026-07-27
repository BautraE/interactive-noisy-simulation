# Interactive Noisy Simulation Module

The module **Interactive Noisy Simulation** (further on referred to as **INS**) provides a more intuitive and interactive way of creating noise models and simulators, as well as executing circuits with the created simulators.

The module consists of custom classes and methods that provide the additional functionality, and it is currently usable in ***Python Notebook*** files (***.ipynb***).

## 1. Functionality overview

*INS* currently provides the ability to:
- Import CSV calibration data files obtained from any of the available IBM Quantum Platform QPUs;
- Look up noise data for a certain qubit;
- Use the imported data to create a noise models and coupling maps;
- Create a simulator instances with the custom noise models and coupling maps;
- Run a user-provided citruit with the created simulator.

Other than this, there are also informative methods:
- `help_csv_columns()` from `NoiseDataManager` will print out all relevant CSV columns (the ones that are used in the creation of noise models) along with explanations for them.

## 2. Setup guide

### 2.1. Versions & dependencies

In order to install *INS*, the environment has to have the following Python version:
- `Python >= 3.13`

The module currently requires the following dependencies of third party packages / libraries:
- `pandas >= 2.3.1`
- `qiskit >= 2.1.1`
- `qiskit-aer >= 0.17.1`
- `requests >= 2.32.5`
- `rich >= 14.2.0`
- `rich-argparse >= 1.7.2`

If any of these dependencies are not set up prior to installing *INS*, they will be automatically downloaded and installed to the current environment.

**Additional notes regarding *Python* and dependencies:** 
- Some packages like Qiskit have not been tested with older versions than the ones mentioned in the dependencies. Therefore, even if they could work, the minimum version has been set to the one that was used during development. The same goes for *Python*.
- There might be potential errors because of specific updates to the packages *INS* depends on. As well as issues might be caused by these packages not yet being adapted to a new *Python* version. In these cases, the exact versions mentioned in the list above should be installed. The project was developed with them, which means that everything should work.

### 2.2. Module setup

1. There are currently no plans of publishing *INS* to *PyPI*, which means that it is required to do either of the following:
    - Get package link of latest release.
    - Download a stable version from the releases.

2. Based on the choice at step 1., use `pip` to install the package with one of the following ways:
    ```
    pip install relevant_version_link
    pip install ./path/to/downloaded/file
    ```
3. After successfully installing *INS*, you can import the module as follows:
    ```python
    # For importing everything
    from interactive_noisy_simulation import *
    # For importing separate classes
    from interactive_noisy_simulation import NoiseDataManager, NoiseCreator, SimulatorManager
    ```

## 3. Package updating & terminal commands

#### IMPORTANT: Installed *INS* version must be at least 1.2.2 for this to be available.

The package also includes functionality for a few terminal commands:
- `interactive_noisy_simulation -h | --help`: The usual `help` command behavior.
- `interactive_noisy_simulation -v | --version`: Retrieves the current version of INS.
- `interactive_noisy_simulation -u | --update`: If a newer version exists, automatically updates the package to it.

## 4. Use case example

The following code example shows basic steps to complete a single cycle of all available functionality:

```python
# New classes:
noise_data_manager = NoiseDataManager()
noise_creator = NoiseCreator()
simulator_manager = SimulatorManager()

# NoiseDataManager functionality:
noise_data_manager.import_csv_data(
    reference_key="noise_data",
    file_path="path/to/file.csv")
# Looking up a single qubit - qubit with index 5
noise_data_manager.get_qubit_noise_information(
    reference_key="noise_data",
    qubits=5)
# Looking up multiple qubits - qubits with indexes 1, 10, and 20
noise_data_manager.get_qubit_noise_information(
    reference_key="noise_data",
    qubits=[1, 10, 20])

noise_data_manager.help_csv_columns()

# NoiseCreator functionality:
# Linking is required to access data from other class objects
noise_creator.link_noise_data_manager(noise_data_manager)

noise_creator.create_noise_model(
    noise_model_reference_key="noise_model",
    data_reference_key="noise_data",
    has_noise=True ) # Default value is True. Use False for noiseless.

# SimulatorManager functionality:
simulator_manager.link_noise_creator(noise_creator)

simulator_manager.create_simulator(
    simulator_reference_key="simulator", 
    noise_model_reference_key="noise_model")

result_job = simulator_manager.run_simulator(
    simulator_reference_key="simulator",
    circuit=ciircuit, 
    optimization=0, 
    shots=1000)
```

There are also additional methods for managing created noise data, noise model and simulator instances:

```python
# View all created instances:
noise_data_manager.view_noise_data_instances()
noise_creator.view_noise_models()
simulator_manager.view_simulators()

# Remove created instance:
noise_data_manager.remove_noise_data_instance(
   reference_key="noise_data")
noise_creator.remove_noise_model_instance(
   reference_key="noise_model")
simulator_manager.remove_simulator_instance(
   reference_key="simulator")
```

## 5. Things to note & future plans

While the functionality is currently working, it is highly dependent on [IBM Qiskit](https://github.com/Qiskit/qiskit) and other related things like the [IBM Quantum Platform](https://quantum.cloud.ibm.com/). Any significant changes to their code might break the current functionality of *INS*. 

*(This is for other potential people joining in on the project)* To overcome this issue easier some actions have been / will be taken:
- The code will be made in a way that is simpler to modify if any changes might occur (in the realms of possibility ofcourse), for example, by implementing a `config.json` file;
- Some versions of *INS* might require certain versions of other libraries / modules (for example, *Qiskit*) if new updates significantly impact the current functionality of them. Though not all issues can be overcome by this, such as the format of the downloadable calibration data CSV files, which is not tied to any library / module version.

The following points describe some additional functionality features that can be implemented over time in no specific order:
- Add the **possibility to select certain noisy qubits**, while leaving others noiseless, when creating a noise model. This would provide the ability of creating a wider range of different noise models that can be experimented with;
- Add the **possibility to modify imported data from CSV files manually**, as well as to create an empty data table and fill it with custom values. Again, this feature would provide even more flexibility to the user in terms of creating noise models;
- Add **extra informative helper methods to each class** that show and explain all available methods to the user. Even though `help()` already exists in Python, the custom methods would have an improved visual output style that is easier to read for the user. 

**Note:** This list of additional features is not final and new things may be added to it down the road.

# NEW NOTES (SLOWLY ADDING INFORMATION HERE FOR THE FINAL VERSION OF THE README.MD FILE)

## Things to note

### Importing circuits from older versions of *Qiskit*
While developing *INS*, the following error has been encountered: 
```
The QPY format version being read, {version_number}, isn't supported by this Qiskit version. Please upgrade your version of Qiskit to load this qpy payload
```
This means that there is no issue with importing circuits from older versions, however, it will raise this error if a circuit `.qpy` file was created through an environment with a newer *Qiskit* version than the one being used by *INS*.

This isn't something that can be fixed on the side of *INS*, which means the user should resolve issues related to this, if they appear. This information is mentioned here as an explanation of the situation.

### Automatically-updating radio input fields
When creating a job for an experiment, additional validation happens, affecting what kind of radio input options will appear. These things are currently not explained anywhere through the UI of INS, thus they will be mentioned here:
- **Selecting a circuit instance will check which noise model instances support it**. If a quantum circuit has more qubits than the noise model, it will not be shown as an option.
- **Selecting a circuit instance will check which simulation methods are capable of running it**. Quantum computer simulation is expensive, especially with bigger qubit counts, as it requires a lot of memory (RAM), thus *INS* calculates the required memory for those methods, where it is straightforward to do so (`statevector` and `density_matrix`);
- **Selecting a simulation method will check what kind of hardware options are available for it** (not all simulation methods support all available hardware options).

In cases, where an option was previously selected before any validation took place, one of the following scenarios will play out:
- If the previously selected option is still available, it will remain selected in that specific input field;
- If the previously selected option is no longer available, no option will be selected in that specific input field.

### Different simulation method speeds
Since this is not currently mentioned anywhere in the UI of *INS*, it will be mentioned here.

From what has been tested, each of the supported simulation methods has a different execution speed:
- `density_matrix` - completes jobs the fastest, but requires the most memory;
- `statevector` - is noticeably slower than `density_matrix`, but also requires quite a bit less memory (can simulate 2x the amount of qubits);
- `matrix_product_state` - the slowest one (especially with noise). Though the benefit of it is the fact that it can simulate way more qubits than the `statevector` method.

### Non-calculable memory (RAM) requirements and potential errors
Even though it is possible to precisely calculate how much RAM is required to run a circuit with the `statevector` and `density_matrix` simulation methods, there are other situations, where something like this may not be possible (or at the very least, not accomplishable without a complicated solution that might take lots of time to create and implement).
- **`matrix_product_state`** - The memory requirements of this method are dynamically altered not just by the number of qubits in the circuit, but also the overall entanglement and depth (at least from what I have understood up until the point of writing this). I am also not sure if *Qiskit* functionality will stop this circuit from running successfully if the memory requirements suddenly exceed the available memory (even though this was not tested, the next point might imply that this would happen). In any case, an additional argument / setting is also given to each created simulator instance through INS - `max_memory_mb` (calculated based on available RAM of the used device);
- Large circuit transpilation has caused an error to be raised in regards to some sort of memory-related issue (`MemoryError`). This was encountered while doing some tests with the `matrix_product_state` method. Similarly as with the previous point, I do not currently know of any optimal way to prevent this from happening, other than limiting, let's say, the number of qubits or depth of the circuit. But as it stands, no restrictions for this have been set by *INS*.

