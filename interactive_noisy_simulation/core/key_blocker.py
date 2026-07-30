class KeyBlocker:

    def __init__(self) -> None:
        """Constructor method."""
        # Currently unavailable keys for new instances in the form of:
        # blocked_key: [blocker_keys]
        self.key_availability = {
            "noise_data": {}
        }


    def block_key(
            self,
            key: str, 
            instance_type: str, 
            blocker_key: str
    ) -> None:
        """Blocks current instance key from being used for new instances.

        Blocking is done because some instances hold references of other
        instances that were used in the creation process of them:
        - noise model instance references noise data instance.

        Args:
            key (str): Referemce key that needs to be blocked.
            instance_type (str): Type of instance that blockable reference
                key allows to access:
                - 'noise_data' - noise data instances.
            blocker_key (str): Key of instance that is causing the blocking
                of the current key.
        """
        blocked_keys = self.key_availability[instance_type]
        if key not in blocked_keys:
            blocked_keys[key] = [blocker_key]
        else:
            blocked_keys[key].append(blocker_key)


    def unblock_key(
            self, 
            key: str, 
            instance_type: str,
            blocker_key: str
    ) -> None:
        """Unblocks current instance key for it to become usable again.

        Instance that holds reference to a certain key has been deleted,
        thus, the unblocked key cam be used again to create a new instance:
        - deleting noise model instance unblocks reference key for new 
        noise data instances.

        **Note:**
        If multiple instances reference a single instance, all of their
        keys act as blockers. To unblock the single referenced instance,
        all blocker instances must be deleted.

        Args:
            key (str): Referemce key that needs to be unblocked.
            instance_type (str): Type of instance that blocked reference
                key allows to access:
                - 'noise_data' - noise data instances.
            blocker_key (str): Reference key for blocker instance that is
                being removed.
        """
        blocked_keys = self.key_availability[instance_type]
        if len(blocked_keys[key]) == 1:
            del blocked_keys[key]
        else:
            blocked_keys[key].remove(blocker_key)


    def check_key_block(
            self,
            key: str, 
            instance_type: str
    ) -> list[str] | None:
        """Checks if an instance key is being currently blocked.

        Args:
            key (str): Reference key that will be checked.
            instance_type (str): Type of instance that the reference
                key allows to access:
                - 'noise_data' - noise data instances.

        Returns:
            list[str]: Reference keys of blocker instances. If key is not 
                blocked, nothing (None) is returned.
        """
        blocked_keys = self.key_availability[instance_type]

        if key in blocked_keys.keys():
            return blocked_keys[key]
