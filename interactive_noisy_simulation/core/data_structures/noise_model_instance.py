# Standard library imports:
from dataclasses import dataclass

# Imports only used for type definition:
from qiskit.transpiler import CouplingMap
from qiskit_aer.noise import NoiseModel

@dataclass
class NoiseModelInstance:
    """Dataclass for storing a noise model instance.
    
    Attributes:
        data_source (str): Reference key for NoiseDataInstance object that
            was the source for creating the NoiseModel and CouplingMap
            objects.
        noise_model (NoiseModel): NoiseModel class object that represents
            the noise model.
        coupling_map (CouplingMap): Coupling map that is associated
            with the current noise model.
    """
    data_source: str
    noise_model: NoiseModel
    coupling_map: CouplingMap


    def get_basis_gates_str(self) -> str:
        """Returns noise model basis gates as `str` value.
        
        Returns:
            str: All gates are joined from list with the separator 
                symbol `;`.
        """
        return "; ".join(self.noise_model.basis_gates)
    
    
    def get_qubit_count(self) -> int:
        """Returns noise model qubit count as `int` value.
        
        Returns:
            int: number of available qubits in noise model.
        """
        return self.coupling_map.size() 
    

    def has_noise(self) -> str:
        """Checks if `NoiseModel` object has noise or is it noiseless.

        Returns:
            str: 
                - "Yes" if it has noise.
                - "No" if it is noiseless.
        """
        if self.noise_model.is_ideal():
            return "No"
        else:
            return "Yes"
