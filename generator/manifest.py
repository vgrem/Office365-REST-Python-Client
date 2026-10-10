"""Run manifest: the last synced metadata snapshot, for deletion tracking.

Each successful run records the metadata fingerprint and, per type, the member
names the metadata declared. The next run diffs against it to report members or
types that **disappeared from the metadata** — without ever mistaking a
hand-written member for a deletion (the comparison is metadata vs metadata, not
metadata vs code).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from generator.odata.model import ODataModel


def manifest_path(metadata_path: str, base_dir: Path) -> Path:
    """The manifest file for a metadata source (``.state/<name>.json``)."""
    return base_dir / ".state" / f"{Path(metadata_path).stem}.json"


def metadata_fingerprint(metadata_path: str) -> str:
    """A content hash of the metadata file (used for the no-op fast path)."""
    return hashlib.sha1(Path(metadata_path).read_bytes()).hexdigest()


def schema_members(model: ODataModel) -> dict[str, list[str]]:
    """Every metadata member name, per type (properties + methods + enum members)."""
    return {
        name: sorted(set(schema.Properties) | set(schema.Methods) | set(schema.Members))
        for name, schema in model.types.items()
    }


@dataclass
class MetadataChanges:
    """What the metadata lost since the last recorded run."""

    removed_types: list[str]
    removed_members: dict[str, list[str]]

    @property
    def is_empty(self) -> bool:
        return not self.removed_types and not self.removed_members


def diff_members(previous: dict[str, list[str]], current: dict[str, list[str]]) -> MetadataChanges:
    """Types/members present in ``previous`` but gone from ``current``."""
    removed_types = sorted(name for name in previous if name not in current)
    removed_members = {
        name: sorted(set(members) - set(current.get(name, [])))
        for name, members in previous.items()
        if name in current and set(members) - set(current.get(name, []))
    }
    return MetadataChanges(removed_types, removed_members)


@dataclass
class Manifest:
    """The persisted snapshot of the last successful run."""

    path: Path
    fingerprint: str
    members: dict[str, list[str]]

    @classmethod
    def load(cls, metadata_path: str, base_dir: Path) -> Optional["Manifest"]:
        path = manifest_path(metadata_path, base_dir)
        if not path.is_file():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        if not isinstance(data, dict):
            return None
        return cls(path, str(data.get("fingerprint", "")), data.get("members", {}))

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"fingerprint": self.fingerprint, "members": self.members}
        self.path.write_text(json.dumps(payload, indent=1, sort_keys=True), encoding="utf-8")
