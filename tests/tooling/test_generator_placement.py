"""Offline tests for hierarchical (subsystem) placement of new types."""

from __future__ import annotations

from pathlib import Path

from generator.routing import descend_module


def test_descend_into_matching_subsystem_and_strip_prefix(tmp_path: Path):
    package = tmp_path / "directory" / "identitygovernance" / "accessreview"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")

    module, stem = descend_module(
        "office365.directory.identitygovernance",
        "AccessReviewContextDataBase",
        str(tmp_path),
    )

    assert module == "office365.directory.identitygovernance.accessreview"
    assert stem == "context_data_base"


def test_no_descent_without_a_matching_package(tmp_path: Path):
    module, stem = descend_module("office365.directory", "AccessReviewError", str(tmp_path))

    assert module == "office365.directory"
    assert stem == "access_review_error"


def test_longest_matching_package_wins(tmp_path: Path):
    for name in ("access", "accessreview"):
        package = tmp_path / "directory" / name
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("", encoding="utf-8")

    module, stem = descend_module("office365.directory", "AccessReviewInstance", str(tmp_path))

    assert module == "office365.directory.accessreview"
    assert stem == "instance"


def test_descend_matches_a_plural_subpackage(tmp_path: Path):
    package = tmp_path / "communications" / "calls"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")

    module, stem = descend_module("office365.communications", "CallMediaState", str(tmp_path))

    assert module == "office365.communications.calls"
    assert stem == "media_state"


def test_descend_keeps_the_full_name_on_a_collision(tmp_path: Path):
    package = tmp_path / "communications" / "calls"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "participant_info.py").write_text("class ParticipantInfo:\n    pass\n", encoding="utf-8")

    module, stem = descend_module("office365.communications", "CallParticipantInfo", str(tmp_path))

    assert module == "office365.communications.calls"
    assert stem == "call_participant_info"


def test_descend_strips_a_redundant_module_name(tmp_path: Path):
    package = tmp_path / "communications"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")

    module, stem = descend_module("office365.communications", "CommunicationsApplicationIdentity", str(tmp_path))

    assert module == "office365.communications"
    assert stem == "application_identity"


def test_descend_strips_a_module_path_prefix(tmp_path: Path):
    package = tmp_path / "onedrive" / "workbooks" / "charts"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")

    for module_path in ("office365.onedrive.workbooks.charts", "office365.onedrive.workbooks"):
        module, stem = descend_module(module_path, "WorkbookChartAxisFormat", str(tmp_path))
        # the leaf package is the module, whether the path already names it or descends into it
        assert module == "office365.onedrive.workbooks.charts"
        assert stem == "axis_format"


def test_descend_strips_path_segments_in_any_order(tmp_path: Path):
    package = tmp_path / "directory" / "certificates" / "x509"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")

    module, stem = descend_module(
        "office365.directory.certificates.x509",
        "X509CertificateAuthenticationMethodConfiguration",
        str(tmp_path),
    )

    assert module == "office365.directory.certificates.x509"
    assert stem == "authentication_method_configuration"
