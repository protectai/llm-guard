from typing import List, Optional, Tuple


class Vault:
    """
    This class serves as a vault to store tuples. These tuples are typically placeholder values
    used for anonymization that need to be retained for later decoding.

    The vault provides methods to append single tuples, extend with a list of tuples, remove a tuple,
    and get the list of all stored tuples.
    """

    def __init__(self, tuples: Optional[List[Tuple]] = None):
        if tuples is None:
            tuples = []

        self._tuples = tuples

    def append(self, new_tuple: Tuple):
        self._tuples.append(new_tuple)

    def extend(self, new_tuples: List[Tuple]):
        self._tuples.extend(new_tuples)

    def remove(self, tuple_to_remove: Tuple):
        self._tuples.remove(tuple_to_remove)

    def get(self) -> List[Tuple]:
        return self._tuples

    def placeholder_exists(self, placeholder: str) -> bool:
        for entity_placeholder, _ in self._tuples:
            if placeholder == entity_placeholder:
                return True
        return False
