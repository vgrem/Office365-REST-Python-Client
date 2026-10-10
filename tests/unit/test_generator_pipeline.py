"""Offline tests for the generation pipeline (update-only filtering)."""

from __future__ import annotations

from pathlib import Path

from generator import pipeline as pipeline_module
from generator.config import GeneratorOptions
from generator.odata.model import ODataModel
from generator.odata.type_information import TypeInformation
from generator.pipeline import GeneratorPipeline


class _FakeBuilder:
    """Stands in for ``TypeBuilder``: attached iff the type is named ``SP.Existing*``."""

    built: list[str] = []

    def __init__(self, schema, options, docs=None, resolver=None):
        self._schema = schema

    @property
    def state(self) -> str:
        return "attached" if self._schema.FullName.startswith("SP.Existing") else "detached"

    @property
    def routed(self) -> bool:
        return True

    def build(self) -> None:
        type(self).built.append(self._schema.FullName)

    def render(self) -> str:
        return "class Placeholder:\n    pass\n"

    @property
    def status(self) -> str:
        return "updated"

    @property
    def file(self) -> str:
        return f"{self._schema.FullName}.py"


def _model(*names: str) -> ODataModel:
    model = ODataModel()
    for name in names:
        model.add_type(TypeInformation(BaseTypeFullName="EntityType", FullName=name, IsValueObject=False))
    return model


def _options(tmp_path: Path) -> GeneratorOptions:
    return GeneratorOptions(
        metadata_path=str(tmp_path / "meta.xml"),
        output_path=str(tmp_path),
        template_path=str(tmp_path),
        dry_run=True,
    )


def test_update_only_skips_new_types(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(pipeline_module, "TypeBuilder", _FakeBuilder)
    _FakeBuilder.built = []
    GeneratorPipeline(_model("SP.ExistingThing", "SP.NewThing"), _options(tmp_path), update_only=True).run()
    assert _FakeBuilder.built == ["SP.ExistingThing"]


def test_default_processes_new_and_existing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(pipeline_module, "TypeBuilder", _FakeBuilder)
    _FakeBuilder.built = []
    GeneratorPipeline(_model("SP.ExistingThing", "SP.NewThing"), _options(tmp_path)).run()
    assert _FakeBuilder.built == ["SP.ExistingThing", "SP.NewThing"]
