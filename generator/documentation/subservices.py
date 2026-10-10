"""Microsoft Graph service taxonomy from the docs per-service TOCs.

The Graph docs repository generates one TOC per product/service
(``api-reference/<version>/toc/<service>/toc.yml``), each listing its resource
pages. Reading those ~35 small YAML files yields a ``type -> service`` map
(``entra-users``-style product taxonomy) that we cache offline.

The fetch step is explicit (``--fetch-services``); generation only reads the
cache, so placement stays deterministic and offline.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_CACHE_PATH = Path(__file__).resolve().parent.parent / "metadata" / "graph_services.json"
_API = "https://api.github.com/repos/microsoftgraph/microsoft-graph-docs-contrib/contents/api-reference/{version}/toc"
_RAW = "https://raw.githubusercontent.com/microsoftgraph/microsoft-graph-docs-contrib/main/api-reference/{version}/toc/{service}/toc.yml"
_VERSIONS = ("v1.0", "beta")
_RESOURCE_LINK = re.compile(r"\.\./\.\./resources/([a-z0-9_\-]+)\.md")


def cache_path() -> Path:
    """The JSON sidecar holding the fetched ``type -> service`` map."""
    return _CACHE_PATH


def load_service_map() -> dict[str, str]:
    """The cached ``{type_lower: service}`` map, or ``{}`` when not fetched."""
    if not _CACHE_PATH.is_file():
        return {}
    try:
        payload = json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    services = payload.get("services") if isinstance(payload, dict) else None
    return services if isinstance(services, dict) else {}


def _get(url: str) -> Optional[str]:
    try:
        with urllib.request.urlopen(url, timeout=30) as response:  # noqa: S310 - https only
            return response.read().decode("utf-8")
    except (urllib.error.URLError, OSError, UnicodeDecodeError):
        return None


def _service_names(version: str) -> list[str]:
    raw = _get(_API.format(version=version))
    if raw is None:
        return []
    try:
        entries = json.loads(raw)
    except ValueError:
        return []
    return [entry["name"] for entry in entries if isinstance(entry, dict) and entry.get("type") == "dir"]


def fetch_service_map() -> dict[str, str]:
    """Fetch the per-service TOCs and build ``{type_lower: service}`` (network)."""
    services: dict[str, str] = {}
    for version in _VERSIONS:
        for service in _service_names(version):
            text = _get(_RAW.format(version=version, service=service))
            if text is None:
                continue
            for page in _RESOURCE_LINK.findall(text):
                services.setdefault(page, service)
    return services


def write_service_map(services: dict[str, str]) -> Path:
    """Persist the ``type -> service`` map with fetch metadata."""
    payload = {
        "source": "microsoftgraph/microsoft-graph-docs-contrib (api-reference TOC)",
        "fetched": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "count": len(services),
        "services": dict(sorted(services.items())),
    }
    _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CACHE_PATH.write_text(json.dumps(payload, indent=1, sort_keys=True), encoding="utf-8")
    return _CACHE_PATH
