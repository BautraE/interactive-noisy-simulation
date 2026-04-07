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
