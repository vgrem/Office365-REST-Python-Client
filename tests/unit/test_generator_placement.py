"""Offline tests for hierarchical (subsystem) placement of new types."""

from __future__ import annotations

from pathlib import Path

from generator.builders.type import TypeBuilder
from generator.odata.type_information import TypeInformation


class _StubResolver:
    def resolve(self, type_name):
        return None

    def strict_module_for(self, type_name):
        return None

    def module_for(self, type_name):
        return None

    def members_of(self, type_name):
        return set()


def _options(tmp_path: Path, routing: dict[str, str]) -> dict:
    options = {
        "template_path": str(tmp_path),
        "output_path": str(tmp_path),
        "modules": "office365",
        "namespace": "microsoft.graph",
    }
    for prefix, module in routing.items():
        options[f"routing_{prefix}"] = module
    return options


def test_descend_into_matching_subsystem_and_strip_prefix(tmp_path: Path):
    package = tmp_path / "directory" / "identitygovernance" / "accessreview"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")

    schema = TypeInformation(BaseTypeFullName="ComplexType", FullName="microsoft.graph.X", IsValueObject=True)
    builder = TypeBuilder(
        schema,
        _options(tmp_path, {"microsoft.graph.identityGovernance": "office365.directory.identitygovernance"}),
        resolver=_StubResolver(),
    )
    module, stem = builder._descend_submodule(
        "office365.directory.identitygovernance",
        str(tmp_path),
        "access_review_context_data_base",
    )

    assert module == "office365.directory.identitygovernance.accessreview"
    assert stem == "context_data_base"


def test_no_descent_without_a_matching_package(tmp_path: Path):
    schema = TypeInformation(BaseTypeFullName="ComplexType", FullName="microsoft.graph.X", IsValueObject=True)
    builder = TypeBuilder(schema, _options(tmp_path, {}), resolver=_StubResolver())

    module, stem = builder._descend_submodule("office365.directory", str(tmp_path), "access_review_error")

    assert module == "office365.directory"
    assert stem == "access_review_error"
