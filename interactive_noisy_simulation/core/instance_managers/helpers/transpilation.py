# =========================================================================
# This file contains helper functions for the class ExperimentManager.
#
# The following function is used for obtaining a transpiled circuit for
# some experiment job being created.
# =========================================================================

# Third-party imports:
from qiskit import transpile

# Imports only used for type definition:
from qiskit import QuantumCircuit
from qiskit.transpiler import Target


def get_transpiled_circuit(
    circuit: QuantumCircuit,
    optimization_level: int | None,
    transpilation_target: Target
) -> QuantumCircuit:
    """Creates and returns a transpiled circuit that can be run on
    the specific simulator instance.

    Args:
        circuit (QuantumCircuit): Circuit that needs to be transpiled.
        optimization_level (int | None): Optimization level setting for
            the `transpile` function.
        transpilation_target (Target): Custom *Qiskit* `Target` object that 
            is required for successful transpilation without any errors.

    Returns:
        QuantumCircuit: Transpiled circuit that the simulator will be
            running.
    """
    # If there is no noise, optimization level is not allowed
    # to be set, thus, it should be set to 0 (INS default).
    optimization_level = optimization_level or 0

    return transpile(circuits=circuit,
                     target=transpilation_target,
                     optimization_level=optimization_level)
