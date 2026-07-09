from __future__ import annotations

import requests

from llm_guard.util import extract_urls, get_logger

from .base import Scanner

LOGGER = get_logger()


class URLReachability(Scanner):
    """
    This scanner checks URLs for their reachability.
    """

    def __init__(self, *, success_status_codes: list[int] | None = None, timeout: int = 5) -> None:
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

    @staticmethod
    def _validate_url(url: str) -> tuple[str, str, str, str] | None:
        """Validate and resolve a URL, returning (scheme, resolved_ip, path) or None if unsafe."""
        import ipaddress
        import socket
        from urllib.parse import urlparse

        parsed_url = urlparse(url)
        if parsed_url.scheme not in ("http", "https"):
            return None

        hostname = parsed_url.hostname
        if not hostname:
            return None

        try:
            ip = socket.gethostbyname(hostname)
        except socket.gaierror:
            return None

        try:
            ip_obj = ipaddress.ip_address(ip)
        except ValueError:
            return None

        if ip_obj.is_loopback or ip_obj.is_private or ip_obj.is_link_local or not ip_obj.is_global:
            return None

        path = parsed_url.path or "/"
        if parsed_url.query:
            path = f"{path}?{parsed_url.query}"

        return parsed_url.scheme, ip, path, hostname

    def is_reachable(self, url: str) -> bool:
        """
        Check if the URL is reachable.
        """
        result = self._validate_url(url)
        if result is None:
            LOGGER.warning("URL validation failed or blocked", url=url)
            return False

        scheme, ip, path, hostname = result
        # SECURITY: URL is validated above — hostname resolved to a public IP,
        # scheme restricted to http/https, and private/loopback IPs are rejected.
        sanitized_url = f"{scheme}://{ip}{path}"

        try:
            response = requests.get(  # nosec B113 - SSRF mitigated by IP validation above
                sanitized_url, timeout=self._timeout, headers={"Host": hostname}
            )
            return response.status_code in self._success_status_codes
        except requests.RequestException:
            return False

    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
        urls = extract_urls(output)
        if not urls:
            return output, True, -1.0

        LOGGER.debug("Found URLs in the output", len=len(urls))

        unreachable_urls = [url for url in urls if not self.is_reachable(url)]

        if unreachable_urls:
            LOGGER.warning("Unreachable URLs detected", urls=unreachable_urls)
            return output, False, 1.0

        LOGGER.debug("All URLs are reachable.")
        return output, True, -1.0
