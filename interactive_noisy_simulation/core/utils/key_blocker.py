# Local project imports:
from ..exceptions import BlockedKeyError
from ...data._data import (
    ERRORS
)

class KeyBlocker:

    def __init__(self) -> None:
        """Constructor method."""
        # Currently unavailable keys for new instances
        # Each enyty of "blocked_keys" will contain the blocked key
        # along with a key of the blocker.
        self.key_availability = {
            "noise_data": {
                "blocked_keys": {},
                "blocker_type": "noise model",
                "self_type": "noise data"
            },
            "noise_models": {
                "blocked_keys": {},
                "blocker_type": "simulator",
                "self_type": "noise model"
            }
        }


    def block_key(
            self,
            key: str, 
            instance_type: str, 
            blocker_key: str
    ) -> None:
        """Blocks current instance key from being used for new instances

        Blocking is done because some instances hold references of other
        instances that were used in the creation process of them:
        - noise model instance references noise data instance;
        - simulator instance references noise model instance.

        Args:
            key (str): Referemce key that needs to be blocked because of a
                reference from a different instance.
            instance_type (str): Type of instance that blockable reference
                key allows to access:
                - 'noise_data' - noise data instances.
                - 'noise_models' - noise model instances.
            blocker_key (str): Key of instance that is causing the blocking
                of the current key.
        """
        blocked_keys = self.key_availability[instance_type]["blocked_keys"]
        blocked_keys[key] = blocker_key


    def unblock_key(
            self, 
            key: str, 
            instance_type: str
    ) -> None:
        """Unblocks current instance key for it to become usable

        Instance that holds reference to a certain key has been deleted,
        thus the unblocked key cam be used again to create new instances:
        - deleting noise model instance unblocks reference key for new 
        noise data instances;
        - deleting simulator instance unblocks reference key for new noise
        model instance.

        Args:
            key (str): Referemce key that needs to be unblocked.
            instance_type (str): Type of instance that blocked reference
                key allows to access:
                - 'noise_data' - noise data instances.
                - 'noise_models' - noise model instances.
        """
        blocked_keys = self.key_availability[instance_type]["blocked_keys"]
        del blocked_keys[key]


    def check_blocked_key(
            self,
            key: str, 
            instance_type: str
    ) -> None:
        """Checks if an instance key is being currently blocked

        Args:
            key (str): Reference key that will be checked.
            instance_type (str): Type of instance that the reference
                key allows to access:
                - 'noise_data' - noise data instances.
                - 'noise_models' - noise model instances.

        Raises:
            BlockedKeyError: If current key is blocked and is unable to be
                used for a new instance.
        """
        instance_info = self.key_availability[instance_type]
        blocked_keys = self.key_availability[instance_type]["blocked_keys"]

        if key in blocked_keys:
            raise BlockedKeyError(
                ERRORS["blocked_reference_key"].format(
                    reference_key=key,
                    instance_type=instance_info["self_type"],
                    blocker_instance_type=instance_info["blocker_type"],
                    blocker=blocked_keys[key]))
