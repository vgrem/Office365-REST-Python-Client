"""Generation pipeline: read model, filter types, build, validate and save."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

from generator.builders.render import ruff_binary
from generator.builders.type import TypeBuilder
from generator.checkpoint import Checkpoint, checkpoint_path
from generator.config import GeneratorOptions
from generator.documentation.base import DocumentationProvider
from generator.filters import TypeFilter
from generator.odata.model import ODataModel
from generator.validation import ValidationError, validate_source


def semantic_issues(source: str, filename: str) -> list[str]:
    """Syntax and undefined-name issues in rendered source.

    ``validate_source`` only checks structure (duplicate class/member); this adds
    a compile and a ``ruff`` ``F821``/``F811`` pass so missing imports surface
    during ``--dry-run``, before anything is written.
    """
    try:
        compile(source, filename, "exec")
    except SyntaxError as e:
        return [f"syntax error at line {e.lineno}: {e.msg}"]
    ruff = ruff_binary()
    if ruff is None:
        return []
    try:
        proc = subprocess.run(
            [
                ruff,
                "check",
                "--isolated",
                "--select",
                "F821,F811",
                "--no-cache",
                "--output-format",
                "concise",
                "--stdin-filename",
                filename,
                "-",
            ],
            input=source,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if proc.returncode == 0:
        return []
    return [line.split(": ", 1)[-1] for line in proc.stdout.splitlines() if ": F8" in line]


class GeneratorPipeline:
    """Runs one generation pass over an :class:`ODataModel`."""

    def __init__(
        self,
        model: ODataModel,
        options: GeneratorOptions,
        docs_service: Optional[DocumentationProvider] = None,
        base_dir: Path = Path("."),
        update_only: bool = False,
        only_types: Optional[list[str]] = None,
    ) -> None:
        self._model = model
        self._options = options
        self._docs = docs_service
        self._update_only = update_only
        self._only_types = tuple(only_types or ())
        self._builder_options = options.builder_options()
        self._filter = TypeFilter.from_options(options)
        # Only types this run will actually generate are importable by name.
        self._builder_options["known_types"] = {
            name for name, schema in model.types.items() if self._filter.in_scope(name, schema)
        }
        self._checkpoint = Checkpoint(checkpoint_path(options.metadata_path, base_dir))

    def run(self) -> None:
        """Generate every in-scope type, then drop the checkpoint on success."""
        targeted = bool(self._only_types)
        total = len(self._only_types) if targeted else len(self._model.types)
        if not targeted:
            self._skip_start_at_count()
        else:
            self._warn_unknown_types()
        count = 0 if targeted else len(self._checkpoint.processed)
        skipped_new = 0
        for name in self._model.types:
            schema = self._model.types[name]
            if targeted:
                if name not in self._only_types:
                    continue
            else:
                if self._filter.before_start(name):
                    self._checkpoint.add(name, persist=False)
                    continue
                if self._filter.should_skip(name, schema, self._checkpoint.processed):
                    continue
            builder = TypeBuilder(schema, self._builder_options, self._docs)
            if self._update_only and builder.state != "attached":
                skipped_new += 1
                self._checkpoint.add(name, persist=False)
                continue
            count += 1
            print(f"[{count}/{total}] Processing: {name}")
            self._process(name, builder)
        if skipped_new:
            print(f"  Skipped {skipped_new} new type(s) (update-only)")
        self._checkpoint.clear()

    def _warn_unknown_types(self) -> None:
        missing = [name for name in self._only_types if name not in self._model.types]
        if missing:
            print(f"  Unknown type(s), not in metadata: {', '.join(missing)}")

    def _skip_start_at_count(self) -> None:
        start_at = self._filter.start_at
        if not start_at.isdigit() or int(start_at) <= 0:
            return
        for name in list(self._model.types)[: int(start_at)]:
            self._checkpoint.processed.add(name)
        print(f"  Skipping first {start_at} types (start_at={start_at})")

    def _process(self, name: str, builder: TypeBuilder) -> None:
        """Build, validate (before writing) and checkpoint a single type."""
        try:
            builder.build()
            if builder.status in {"created", "updated"}:
                source = builder.render()
                issues = validate_source(source, builder.file) + semantic_issues(source, builder.file)
                if issues:
                    raise ValidationError(f"{name}: " + "; ".join(issues))
                if self._options.dry_run:
                    print(f"  [dry-run] {builder.status}: {builder.file}")
                else:
                    builder.save()
            self._checkpoint.add(name, persist=not self._options.dry_run)
        except Exception as e:
            print(f"Failed on {name}: {e}")
            print(f"Checkpoint saved. Resume will skip {len(self._checkpoint.processed)} processed types")
            raise
