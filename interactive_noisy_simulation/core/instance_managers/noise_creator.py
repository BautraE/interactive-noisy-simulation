#Third party imports:
from qiskit_aer.noise import NoiseModel

# Project-related imports:
from ..data_structures.instance_data import InstanceData
from ..data_structures.noise_model_instance import NoiseModelInstance
from .helpers.noise_model_creation import (
    get_basis_gates, get_coupling_map,
    add_depolarizing_error, add_readout_error, add_thermal_error
)

# Imports only used for type definition:
from ..data_structures.noise_data_instance import NoiseDataInstance
from typing import Callable


class NoiseCreator:

    # =========================================================================
    # Table of Contents for NoiseCreator
    # =========================================================================
    # 1. Initialization (constructor method).
    # 2. Class properties.
    # 3. Noise model instance management - creating new instances, viewing and
    #       deleting existing ones.
    # =========================================================================

    # =========================================================================
    # 1. Initialization (constructor method).
    # =========================================================================

    def __init__(self) -> None:
        """Constructor method."""
        self.__noise_models: dict[str, NoiseModelInstance] = {}


    # =========================================================================
    # 2. Class properties.
    # =========================================================================

    @property
    def noise_models(self) -> dict[str, NoiseModelInstance]:
        """Returns a reference to data structure containing noise model 
        instances.
        
        Returns:
            dict[str, NoiseModelInstance] - dictionary with reference key and 
                instance.
        """
        return self.__noise_models


    # =========================================================================
    # 3. Noise model instance management - creating new instances, viewing and
    #       deleting existing ones.
    # =========================================================================
    
    def create_noise_model(
            self,
            reference_key: str, 
            noise_data: NoiseDataInstance,
            progress_callback: Callable[[float], None] | None = None
    ) -> None:
        """Creates a new NoiseModelInstance object.
        
        All errors along with the coupling map and list of basis gates
        is based on the provided NoiseDataInstance.

        Args:
            reference_key (str): Reference key for the newly created
                instance.
            noise_data (NoiseDataInstance): Noise data source for the new 
                NoiseModelInstance object.
            progress_callback (Callable[[float], None] | None): Reference to 
                callback function that gets called for displayable progress 
                tracking.
        """
        noise_dataframe = noise_data.dataframe

        # Creating qiskit_aer.noise NoiseModel object:
        noise_model = NoiseModel(get_basis_gates(noise_dataframe))
        if progress_callback: progress_callback(5.0)

        for qubit_nr, columns in noise_dataframe.iterrows():
            add_readout_error(qubit_nr, columns, noise_model)
            add_depolarizing_error(qubit_nr, columns, noise_model)
            add_thermal_error(qubit_nr, columns, 
                                noise_model, noise_dataframe)
            if progress_callback:
                total_iterations = noise_data.get_qubit_count()
                loop_decimal = (qubit_nr + 1) / total_iterations
                percentage = 5.0 + (loop_decimal * 90)
                progress_callback(round(percentage, 2))

        coupling_map = get_coupling_map(noise_dataframe)
        if progress_callback: progress_callback(100.0)       

        # Defining new noise model instance
        new_instance = NoiseModelInstance(
            reference_key=reference_key,
            data_source=noise_data.reference_key,
            noise_model=noise_model,
            coupling_map=coupling_map)
        self.__noise_models[reference_key] = new_instance

    
    def get_instance_data(self) -> InstanceData | None:
        """Returns data about currently created noise model instances.

        Returned information includes:
        - Reference key for the current instance;
        - Noise model qubit count; 
        - List of basis gates;
        - Whether or not the noise model has noise;
        - Reference key for the source noise data instance that was
          used in the making of the current instance.

        Returns:
            InstanceData: Dataclasss for displayable instance data.
                If there is no data to be displayed, the function returns
                nothing (`None`).
        """
        if self.__noise_models:
            columns = ["Reference key", "Qubit count", 
                       "Basis gates", "Has noise", 
                       "Noise data source"]
            rows = [[key, str(instance.get_qubit_count()),
                     instance.get_basis_gates_str(), instance.has_noise(),
                     instance.data_source,] 
                    for key, instance in self.__noise_models.items()]
            actions = ["delete"]
        
            return InstanceData(columns=columns,
                                rows=rows,
                                actions=actions)


    def remove_noise_model_instance(
            self, 
            reference_key: str
    ) -> None:
        """Removes existing noise model instance by reference key.
        
        Args:
            reference_key (str): Key of the removable noise model
                instance.
        """
        del self.__noise_models[reference_key]
