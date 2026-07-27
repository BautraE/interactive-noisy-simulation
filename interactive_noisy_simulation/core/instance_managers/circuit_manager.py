# Third-party imports:
from qiskit import qpy

# Project-related imports:
from ..data_structures.circuit_instance import CircuitInstance
from ..data_structures.file import File
from ..data_structures.instance_data import InstanceData


class CircuitManager:
    # =========================================================================
    # Table of Contents for CircuitManager
    # =========================================================================
    # 1. Initialization (constructor method).
    # 2. Class properties.
    # 3. Circuit instance management - creating new instances, viewing and
    #       deleting existing ones.
    # =========================================================================

    # =========================================================================
    # 1. Initialization (constructor method).
    # =========================================================================

    def __init__(self) -> None:
        """Constructor method."""
        self._circuits: dict[str, CircuitInstance] = {}

    # =========================================================================
    # 2. Class properties.
    # =========================================================================

    @property
    def circuits(self) -> dict[str, CircuitInstance]:
        """Returns a reference to data structure containing quantum circuit 
        instances.
        
        Returns:
            dict[str, CircuitInstance] - dictionary with reference keys and 
                instances as its data.
        """
        return self._circuits
    

    # =========================================================================
    # 3. Circuit instance management
    # =========================================================================
    
    def create_instance(
        self, 
        reference_key: str,
        source_file: File,
    ) -> None:
        """Creates new circuit instance from imported files containing
        a quantum circuit.

        **Note:**
        Even though `qpy` allows users to store multiple circuits in a single
        file, the current functionality only supports importing them one
        at a time. This means that only the first circuit from the entire list
        will be imported.

        This method currently only fully works with the following files:
        - QPY (`.qpy`) - a binary serialization format used for storing
            `QuantumCircuit` objects.

        Args:
            reference_key (str): Reference key that will be set for the newly
                created instance.
            source_file (File): Imported file containing quantum circuit.
        """
        # Processing imported .qpy file:
        with open(source_file.path, 'rb') as data:
            circuit = qpy.load(data)[0]

        # Creating new instance:
        new_instance = CircuitInstance(
            reference_key=reference_key,
            source_file=source_file,
            circuit=circuit)
        self._circuits[reference_key] = new_instance


    def get_instance_data(self) -> InstanceData | None:
        """Returns data about currently created circuit instances.

        Returned information includes:
        - Reference key for the current instance;
        - Number of qubits in the circuit;
        - Amount of memory (RAM) that is required to simulate the specific
            qubit count of the circuit (calculated for the `statevector` and
            `density_matrix`simulation methods);
        - Name of the QPY file;
        - Full path of QPY file on user's device.

        Returns:
            InstanceData: Dataclasss for displayable instance data.
                If there is no data to be displayed, the function returns
                nothing (`None`).
        """
        if self._circuits:
            columns = [
                "Reference key", "Number of qubits", 
                "Memory (RAM) requirements",
                "Source file", 
                "Source file path on device"
            ]
            rows = [
                [instance.reference_key, instance.num_qubits,
                 instance.memory_requirements,
                 instance.source_file.name, 
                 instance.source_file.full_path]
                for instance in self._circuits.values()
            ]
            actions = ["delete"]
        
            return InstanceData(columns=columns,
                                rows=rows,
                                actions=actions)


    def remove_instance(
                self, 
                reference_key: str
        ) -> None:
            """Removes existing circuit instance based on its reference key.

            Args:
                reference_key (str): Reference key of existing deletable 
                    circuit instance.
            """
            del self._circuits[reference_key]
