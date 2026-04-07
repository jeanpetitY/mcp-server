from __future__ import annotations

import time
from typing import Any

import requests

DEFAULT_TIMEOUT_SECONDS = 20
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_USER_AGENT = (
    "tib-mcp/0.1.0 (+https://gitlab.com/TIBHannover/orkg/tib-aissistant/tib-mcp)"
)
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def clamp_limit(limit: int, *, minimum: int = 1, maximum: int = 25) -> int:
    """Keep user-provided limits within a predictable and MCP-friendly range."""
    if limit < minimum:
        raise ValueError(f"limit must be greater than or equal to {minimum}.")
    return min(limit, maximum)


def build_headers(extra: dict[str, str] | None = None) -> dict[str, str]:
    """Build standard JSON headers and merge optional provider-specific values."""
    headers = {
        "Accept": "application/json",
        "User-Agent": DEFAULT_USER_AGENT,
    }
    if extra:
        headers.update({key: value for key, value in extra.items() if value})
    return headers


def request_json(
    url: str,
    *,
    method: str = "GET",
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | list[Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    retry_attempts: int = DEFAULT_RETRY_ATTEMPTS,
) -> Any:
    """Send an HTTP request and raise readable errors for MCP clients."""
    for attempt in range(retry_attempts):
        try:
            response = requests.request(
                method,
                url,
                params=params,
                json=json_body,
                headers=headers,
                timeout=timeout,
            )
        except requests.RequestException as exc:
            if attempt + 1 >= retry_attempts:
                raise RuntimeError(f"Request to {url} failed: {exc}") from exc

            time.sleep(_retry_delay_seconds(attempt))
            continue

        if response.ok:
            break

        if (
            response.status_code not in RETRYABLE_STATUS_CODES
            or attempt + 1 >= retry_attempts
        ):
            detail = _extract_error_detail(response)
            raise RuntimeError(
                f"Request to {url} failed with status {response.status_code}: {detail}"
            )

        time.sleep(_retry_delay_seconds(attempt))
    else:
        raise RuntimeError(f"Request to {url} failed after {retry_attempts} attempts.")

    try:
        return response.json()
    except ValueError as exc:
        raise RuntimeError(f"Request to {url} returned invalid JSON.") from exc


def _extract_error_detail(response: requests.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text or response.reason or "Unknown error"

    if isinstance(payload, dict):
        for key in ("message", "error", "detail"):
            value = payload.get(key)
            if value:
                return str(value)

    return response.text or response.reason or "Unknown error"


def _retry_delay_seconds(attempt: int) -> float:
    return 0.5 * (2**attempt)
