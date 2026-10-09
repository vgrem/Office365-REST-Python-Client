"""Generation pipeline: read model, filter types, build, validate and save."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from generator.builders.type import TypeBuilder
from generator.checkpoint import Checkpoint, checkpoint_path
from generator.config import GeneratorOptions
from generator.documentation.base import DocumentationProvider
from generator.filters import TypeFilter
from generator.odata.model import ODataModel
from generator.validation import ValidationError, validate_source


class GeneratorPipeline:
    """Runs one generation pass over an :class:`ODataModel`."""

    def __init__(
        self,
        model: ODataModel,
        options: GeneratorOptions,
        docs_service: Optional[DocumentationProvider] = None,
        base_dir: Path = Path("."),
        update_only: bool = False,
    ) -> None:
        self._model = model
        self._options = options
        self._docs = docs_service
        self._update_only = update_only
        self._builder_options = options.builder_options()
        self._filter = TypeFilter.from_options(options)
        self._checkpoint = Checkpoint(checkpoint_path(options.metadata_path, base_dir))

    def run(self) -> None:
        """Generate every in-scope type, then drop the checkpoint on success."""
        total = len(self._model.types)
        self._skip_start_at_count()
        count = len(self._checkpoint.processed)
        skipped_new = 0
        for name in self._model.types:
            schema = self._model.types[name]
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
                issues = validate_source(builder.render(), builder.file)
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
