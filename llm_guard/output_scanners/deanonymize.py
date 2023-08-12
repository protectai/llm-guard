import logging

from llm_guard.vault import Vault

from .base import Scanner

log = logging.getLogger(__name__)


class Deanonymize(Scanner):
    """
    A class for replacing placeholders in the model output with real values from a vault.

    This class uses the Vault class to access stored values and replaces any placeholders
    in the model's output with their corresponding values from the vault.
    """

    def __init__(self, vault: Vault):
        """
        Initializes an instance of the Deanonymize class.

        Parameters:
            vault (Vault): An instance of the Vault class which stores the real values.
        """
        self._vault = vault

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        vault_items = self._vault.get()
        if len(vault_items) == 0:
            log.warning("No items found in the Vault")

        for vault_item in vault_items:
            log.debug(f"Replaced placeholder ${vault_item[0]} with real value")
            output = output.replace(vault_item[0], vault_item[1])

        return output, True, 0.0
