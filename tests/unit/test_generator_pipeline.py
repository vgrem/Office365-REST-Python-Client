"""Offline tests for the generation pipeline (update-only filtering)."""

from __future__ import annotations

from pathlib import Path

import pytest
from generator import pipeline as pipeline_module
from generator.config import GeneratorOptions
from generator.manifest import Manifest, manifest_path, run_signature
from generator.odata.model import ODataModel
from generator.odata.type_information import TypeInformation
from generator.pipeline import GeneratorPipeline
from generator.validation import ValidationError


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

    @property
    def skip_reason(self) -> str:
        return ""

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


def _real_options(tmp_path: Path) -> GeneratorOptions:
    metadata = tmp_path / "meta.xml"
    metadata.write_text("<a/>", encoding="utf-8")
    return GeneratorOptions(
        metadata_path=str(metadata),
        output_path=str(tmp_path / "office365"),
        template_path=str(tmp_path),
    )


def test_module_name_derives_a_dotted_path(tmp_path: Path) -> None:
    pipeline = GeneratorPipeline(_model(), _real_options(tmp_path), base_dir=tmp_path)
    assert pipeline._module_name(str(tmp_path / "office365" / "a" / "b.py")) == "office365.a.b"
    assert pipeline._module_name(str(tmp_path / "elsewhere" / "b.py")) is None


def test_smoke_import_raises_on_import_failure(tmp_path: Path, monkeypatch) -> None:
    pipeline = GeneratorPipeline(_model(), _real_options(tmp_path), base_dir=tmp_path)

    class _Builder:
        file = str(tmp_path / "office365" / "thing.py")

    def _boom(module: str):
        raise ImportError("boom")

    monkeypatch.setattr(pipeline_module.importlib, "import_module", _boom)
    with pytest.raises(ValidationError, match="failed to import"):
        pipeline._smoke_import([("x", _Builder())])


def test_can_skip_only_when_the_recorded_signature_matches(tmp_path: Path) -> None:
    options = _real_options(tmp_path)
    Manifest(manifest_path(options.metadata_path, tmp_path), "fp", {}, run_signature(options)).save()

    assert GeneratorPipeline(_model(), options, base_dir=tmp_path)._can_skip() is True
    assert GeneratorPipeline(_model(), options, base_dir=tmp_path, force=True)._can_skip() is False
    assert GeneratorPipeline(_model(), options, base_dir=tmp_path, only_types=["SP.X"])._can_skip() is False


def test_cli_up_to_date_fast_path(tmp_path: Path, monkeypatch) -> None:
    from generator import cli

    monkeypatch.setattr(cli, "GENERATOR_DIR", tmp_path)
    options = _real_options(tmp_path)
    assert cli._up_to_date(options, force=False, only_types=None, report_path=None) is False

    Manifest(manifest_path(options.metadata_path, tmp_path), "fp", {}, run_signature(options)).save()
    assert cli._up_to_date(options, force=False, only_types=None, report_path=None) is True
    assert cli._up_to_date(options, force=True, only_types=None, report_path=None) is False
    assert cli._up_to_date(options, force=False, only_types=["SP.X"], report_path=None) is False
    assert cli._up_to_date(options, force=False, only_types=None, report_path="r.json") is False
