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
from typing import TYPE_CHECKING, Optional

from generator.odata.model import ODataModel

if TYPE_CHECKING:
    from generator.config import GeneratorOptions


def manifest_path(metadata_path: str, base_dir: Path) -> Path:
    """The manifest file for a metadata source (``.state/<name>.json``)."""
    return base_dir / ".state" / f"{Path(metadata_path).stem}.json"


def metadata_fingerprint(metadata_path: str) -> str:
    """A content hash of the metadata file (used for the no-op fast path)."""
    return hashlib.sha1(Path(metadata_path).read_bytes()).hexdigest()


def _hash_files(digest: "hashlib._Hash", root: Path) -> None:
    """Fold every ``*.py`` file under ``root`` (path + content) into ``digest``."""
    if not root.is_dir():
        return
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())


def run_signature(options: "GeneratorOptions", source_root: Optional[Path] = None) -> str:
    """A hash of everything that changes generated output.

    Covers the metadata, the effective options/flags, the template sources **and
    the generator's own source**, so an unchanged signature means a run would be a
    no-op (see the fast path) and a generator upgrade always invalidates it.
    """
    digest = hashlib.sha1()
    digest.update(metadata_fingerprint(options.metadata_path).encode())
    payload = {
        "output_path": options.output_path,
        "template_path": options.template_path,
        "context_type": options.context_type,
        "generate_methods": options.generate_methods,
        "modules": options.modules,
        "namespace": options.namespace,
        "ignored_types": options.ignored_types,
        "ignored_properties": options.ignored_properties,
        "ignored_methods": options.ignored_methods,
        "include_base_types": options.include_base_types,
        "start_at": options.start_at,
        "routing": sorted(options.routing.items()),
        "type_routing": sorted(options.type_routing.items()),
    }
    digest.update(json.dumps(payload, sort_keys=True).encode())
    _hash_files(digest, Path(options.template_path))
    _hash_files(digest, source_root or Path(__file__).parent)
    return digest.hexdigest()


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
    signature: str = ""

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
        return cls(
            path,
            str(data.get("fingerprint", "")),
            data.get("members", {}),
            str(data.get("signature", "")),
        )

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"fingerprint": self.fingerprint, "signature": self.signature, "members": self.members}
        self.path.write_text(json.dumps(payload, indent=1, sort_keys=True), encoding="utf-8")
