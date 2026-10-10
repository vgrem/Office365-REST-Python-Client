"""Type filtering: which OData types a run should generate."""

from __future__ import annotations

from dataclasses import dataclass, field

from generator.config import GeneratorOptions, split_ignored
from generator.odata.type_information import TypeInformation


@dataclass
class TypeFilter:
    """Decides whether a metadata type is skipped."""

    exact_ignored: list[str] = field(default_factory=list)
    prefix_ignored: list[str] = field(default_factory=list)
    include_base_types: set[str] = field(default_factory=set)
    start_at: str = ""

    @classmethod
    def from_options(cls, options: GeneratorOptions) -> "TypeFilter":
        exact, prefix = split_ignored(options.ignored_types)
        return cls(
            exact_ignored=exact,
            prefix_ignored=prefix,
            include_base_types=set(options.include_base_types),
            start_at=options.start_at.strip(),
        )

    def should_skip(self, name: str, schema: TypeInformation, processed: set[str]) -> bool:
        """Whether ``name`` is out of scope (already processed / filtered / wrong base type)."""
        if name in processed:
            return True
        if self.include_base_types and schema.BaseTypeFullName not in self.include_base_types:
            processed.add(name)
            print(f"  Skipping {name} (BaseType={schema.BaseTypeFullName})")
            return True
        if name in self.exact_ignored or any(name.startswith(prefix) for prefix in self.prefix_ignored):
            return True
        return False

    def in_scope(self, name: str, schema: TypeInformation) -> bool:
        """Whether ``name`` will be generated (no side effects; used for import planning)."""
        if self.include_base_types and schema.BaseTypeFullName not in self.include_base_types:
            return False
        return not (name in self.exact_ignored or any(name.startswith(p) for p in self.prefix_ignored))

    def before_start(self, name: str) -> bool:
        """Name-based ``start_at``: skip every type until ``name`` matches the marker."""
        if not self.start_at or self.start_at.isdigit():
            return False
        if name.startswith(self.start_at):
            self.start_at = ""
            return False
        print(f"  Skipping {name} (start_at={self.start_at})")
        return True
