# INS AF2 (Additional Feature 2) - Expanded managingement capabilities

This feature aims to expand the possibilities of users by simplifying the management of multiple simultaneous experiments.

Instead of being limited to a single object (noise data instance, noise model, simulator) for each manager class object, there is an option to store multiple of them at once. Now the user can simply pick which one is required for what task, for example, create noise model *x* with noise data *y*.

## 1. Feature functionality overview

Main changes:
- ...

Additional changes:
- ...

## 2. Additional things to note

...

### 2.1. Limitations regarding interactive data input

There was an initial idea of simply having a single function, for example, `add_noise_data()`, which would create an output box with form-related *HTML* elements and buttons. This would make this project way more interactive and intuitive. However, there is an issue.

Since the current design solution uses *HTML + JavaScript*, the data will be initially passed to the *JavaScript* functions. This means that the same data should then be passed to *Python* for use - this is the part that isn’t as simple.

Even though there could be a way to get this to work, it would be quite overkill for this kind of project, especially if it is currently meant for Python Notebook files and is run with the help of separate classes. This, along with the fact of there being differences between the environments of *Jupyter Notebook* and *Visual Studio Code*, led to the decision of going for a simpler approach - passing all input data during main class method calls.
