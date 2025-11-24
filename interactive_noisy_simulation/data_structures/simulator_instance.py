# Standard library imports:
from dataclasses import dataclass

# Imports only used for type definition:
from qiskit_aer import AerSimulator

@dataclass
class SimulatorInstance:
    """Class for storing a simulator instance.
    
    Attributes:
        noise_model_source (str): Reference key for NoiseModelInstance 
            object that was the source for creating the AerSimulator
            object.
        simulator (AerSimulator): AerSimulator class object that represents
            the simulator.
    """
    noise_model_source: str
    simulator: AerSimulator


    def get_qubit_count(self) -> int:
        """Returns simulator qubit count as `int` value.

        This number is based on the selected simulation method, which
        also takes into consideration available RAM of device that is
        running this code.
        
        Returns:
            int: number of qubits the simulator backend supports.
        """
        return self.simulator.num_qubits


    def has_noise(self) -> str:
        """Checks if `AerSimulator` object has noise or is it noiseless.

        Returns:
            str: 
                - "Yes" if it has noise.
                - "No" if it is noiseless.
        """
        noise_model = self.simulator.options.noise_model
        if noise_model.is_ideal():
            return "No"
        else:
            return "Yes"