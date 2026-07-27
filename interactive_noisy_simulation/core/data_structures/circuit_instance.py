# Standard library imports:
from dataclasses import dataclass

# Imports only used for type definition:
from qiskit import QuantumCircuit
from .file import File


@dataclass
class CircuitInstance:
    """Class for storing a quantum circuit instance.
    
    Attributes:
        reference_key (str): Key by which the specific object is accessed 
            in other places of the INS app.
        source_file (File): Imported circuit .qpy file.
        circuit (QuantumCircuit): Circuit representation as a `Qiskit` 
            `QuantumCircuit` object.
    """
    reference_key: str
    source_file: File
    circuit: QuantumCircuit


    @property
    def num_qubits(self) -> int:
        """Returns number of qubits in the circuit.
        
        Returns:
            int: Number of qubits in the circuit.
        """
        return self.circuit.num_qubits


    @property
    def memory_requirements(self) -> dict[str, int | None]:
        """Returns dictionary containing information on all memory requirements
        for each simulation method.
        
        'each method' refers to all methods with constant memory reuirement 
        calculations that can be simply predicted. `matrix_product_state` 
        and `tensor_network` are more complicated and there is no simple way
        to calculate memory requirements, because it strictly depends on the
        circuit.

        Returns:
            dict[str, int]: Memory requirements for calculable simulation
                methods in bytes.
        """
        return {
            # 16 × 2ⁿ - statevector memory calculation
            "statevector": 16 << self.num_qubits 
                if self.num_qubits <= 1000
                else None,
            # 16 × 4ⁿ - density_matrix memory calculation
            "density_matrix": 16 << (2 * self.num_qubits)
                if (2 * self.num_qubits) <= 1000
                else None,
        }
