# Interactive Noisy Simulation Module

The module **Interactive Noisy Simulation** (further on referred to as **INS**) provides a more intuitive and interactive way of creating noise models and simulators, as well as executing circuits with the created simulators.

The module consists of custom classes and methods that provide the additional functionality, and it is currently usable in ***Python Notebook*** files (***.ipynb***).

## 1. Functionality overview

*INS* currently provides the ability to:
- Import CSV calibration data files obtained from any of the available IBM Quantum Platform QPUs;
- Look up noise data for a certain qubit;
- Use the imported data to create a noise model and coupling map;
- Create a simulator instance with the custom noise model and coupling map;
- Run a provided citruit with the created simulator.

Other than this, there are also informative methods:
- `help_csv_columns()` from `NoiseDataManager` will print out all relevant CSV columns (the ones that are used in the creation of noise models) along with explanations for them.

## 2. Use case example

The following code example shows basic steps to complete a single cycle of all available functionality:

```python
# New classes:
noise_data_manager = NoiseDataManager()
noise_creator = NoiseCreator()
simulator_manager = SimulatorManager()

# NoiseDataManager functionality:
noise_data_manager.import_csv_data("path/to/file.csv")
# Looking up a single qubit - qubit with index 5
noise_data_manager.get_qubit_noise_information(5)
# Looking up multiple qubits - qubits with indexes 1, 10, and 20
noise_data_manager.get_qubit_noise_information([1, 10, 20])
noise_data_manager.help_csv_columns()

# NoiseCreator functionality:
# Linking is required to access data from other class objects
noise_creator.link_noise_data_manager(noise_data_manager)
noise_creator.create_noise_model()

# NoiseCreator functionality:
simulator_manager.link_noise_creator(noise_creator)
simulator_manager.create_simulator()
result_job = simulator_manager.run_simulator(circuit, optimization, shots)
```

## 3. Setup guide

### 3.1. Versions & dependencies

In order to install *INS*, the environment has to have the following Python version:
- `Python >= 3.13`

The module currently requires the following dependencies of third party packages / libraries:
- `pandas >= 2.3.1`
- `qiskit >= 2.1.1`
- `qiskit-aer >= 0.17.1`

If any of these dependencies are not set up prior to installing *INS*, they will be automatically downloaded and installed to the current environment.

**Additional note regarding Python and dependencies:** Some packages like Qiskit have not been tested with older versions than the ones mentioned in the dependencies. Therefore, even if they could work, the minimum version has been set to the one that was used during development. The same goes for Python.

### 3.2. Module setup

1. There are currently no plans of publishing *INS* to *PyPI*, which means that downloading a stable version from the releases is required.

2. After downloading *INS* and unzipping the files, use Pip to install the package:
    ```
    pip install ./path/to/module_directory
    ```
3. After successfully installing *INS*, you can import the module as follows:
    ```python
    # For importing everything
    from interactive_noisy_simulation import *
    # For importing separate classes
    from interactive_noisy_simulation import NoiseDataManager, NoiseCreator, SimulatorManager
    ```

## 4. Things to note & future plans

While the functionality is currently working, it is highly dependent on [IBM Qiskit](https://github.com/Qiskit/qiskit) and other related things like the [IBM Quantum Platform](https://quantum.cloud.ibm.com/). Any significant changes to their code might break the current functionality of *INS*. 

*(This is for other potential people joining in on the project)* To overcome this issue easier some actions have been / will be taken:
- The code will be made in a way that is simpler to modify if any changes might occur (in the realms of possibility ofcourse), for example, by implementing a `config.json` file;
- Some versions of *INS* might require certain versions of other libraries / modules (for example, *Qiskit*) if new updates significantly impact the current functionality of them. Though not all issues can be overcome by this, such as the format of the downloadable calibration data CSV files, which is not tied to any library / module version.

The following points describe some additional functionality features that can be implemented over time in no specific order:
- Add the **possibility of managing multiple noise data, noise model and simulator objects simultaneously** instead of the current limitations of one at a time. This would just give the user way more freedom in terms of creating multiple objects;
- Add the **possibility to select certain noisy qubits**, while leaving others noiseless, when creating a noise model. This would provide the ability of creating a wider range of different noise models that can be experimented with;
- Add the **possibility to modify imported data from CSV files manually**, as well as to create an empty data table and fill it with custom values. Again, this feature would provide even more flexibility to the user in terms of creating noise models;
- Add **extra informative helper methods to each class** that show and explain all available methods to the user. Even though `help()` already exists in Python, the custom methods would have an improved visual output style that is easier to read for the user. 

**Note:** This list of additional features is not final and new things may be added to it down the road.