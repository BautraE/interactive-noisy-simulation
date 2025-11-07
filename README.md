# General Improvements Branch

This branch is used for **improvements** to the package that are **not related to** any specific **new feature**. It covers existing functionality with the goal of **implementing better solutions** or **cleaning up some mess** that hase been left from other updates.

The rest of this `README.md` file will consist of changes and comments related to a specific version, which will get updated over time.

## v1.2.2

### Changes:

#### For end user:
- It is now possible to check the currently installed version with the help of the following command:
    - `interactive_noisy_simulation [-v | --version]`
- It is now possible to update the current version of INS automatically, if there is a newer version available. It can be done with the help of the following command:
    - `interactive_noisy_simulation [-u | --update]`

#### For developers:
- All new terminal command outputs have slight styling adjustments with [*Python Rich*](https://github.com/Textualize/rich). Though there is one exception - the *help* command, as it requires another package called *[rich-argparse](https://github.com/hamdanal/rich-argparse)*.

### Additional Comments:

#### Automatic package updating with `interactive_noisy_simulation [-u | --update]`

The **ability to check for new updates** to INS is added successfully, however, a **slight workaround** had to be implemented. Since there is no executable file currently, there is no way of safely deleting current files and replacing them with newer versions, because the old files are still being used as part of the current python executable instance.

To overcome this, a new **separate process** begins after the original one closes - this 'unlocks' the current files and allows them to be removed. This causes the terminal to print out some unnecessary spaces, as well as the current path (again), but other than this, there is nothing wrong with it.

Example of the output:

```console
(py_environment) C:\some\path>interactive_noisy_simulation -u
The current version is outdated.
Updating from v1.2.0 to v1.2.1.

(py_environment) C:\some\path>
Interactive Noisy Simulation has been updated successfully!
Press ENTER to continue.

```

Since the package is not published anywhere, for example, on [PyPI](https://pypi.org/), **automatic version checking** has been implemented with the help of **manually created functions** that look through the *GitHub* repository for this project. No major issues have been encountered with this feature yet.
