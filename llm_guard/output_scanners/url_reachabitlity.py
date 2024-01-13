from typing import List

import requests

from llm_guard.util import extract_urls, logger

from .base import Scanner


class URLReachability(Scanner):
    """
    This scanner checks URLs for their reachability.
    """

    def __init__(self, *, success_status_codes: List[int] = None, timeout: int = 5):
        """
        Parameters:
            success_status_codes: A list of status codes that are considered as successful.
            timeout: The timeout in seconds for the HTTP requests.
        """
        if success_status_codes is None:
            success_status_codes = [
                requests.codes.ok,
                requests.codes.created,
                requests.codes.accepted,
            ]

        self._success_status_codes = success_status_codes
        self._timeout = timeout

    def is_reachable(self, url: str) -> bool:
        """
        Check if the URL is reachable.
        """
        try:
            response = requests.get(url, timeout=self._timeout)
            return response.status_code in self._success_status_codes
        except requests.RequestException:
            return False

    def scan(self, prompt: str, output: str) -> (str, bool, float):
        urls = extract_urls(output)
        if not urls:
            return output, True, 0.0

        logger.debug(f"Found {len(urls)} URLs in the output")

        unreachable_urls = [url for url in urls if not self.is_reachable(url)]

        if unreachable_urls:
            logger.warning(f"Unreachable URLs detected: {unreachable_urls}")
            return output, False, 1.0

        logger.debug("All URLs are reachable.")
        return output, True, 0.0
