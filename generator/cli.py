"""Command line entry point for the model generator."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional, Sequence

from generator.builders.resolution import TypeRegistry
from generator.checkpoint import checkpoint_path
from generator.config import ConfigError, GeneratorOptions
from generator.filters import TypeFilter
from generator.manifest import Manifest, run_signature
from generator.odata.reader import ODataReader
from generator.pipeline import GeneratorPipeline
from generator.routing import Router, render_suggestions
from generator.services import get_service, service_names
from generator.validation import ValidationError

#: Config/paths are resolved relative to this directory, not the CWD.
GENERATOR_DIR = Path(__file__).parent


def _up_to_date(
    options: GeneratorOptions, *, force: bool, only_types: Optional[Sequence[str]], report_path: Optional[str]
) -> bool:
    """True when the last successful run already covered this exact input."""
    if force or only_types or report_path or options.dry_run:
        return False
    if checkpoint_path(options.metadata_path, GENERATOR_DIR).exists():
        return False  # an interrupted run must be resumed
    previous = Manifest.load(options.metadata_path, GENERATOR_DIR)
    return bool(previous and previous.signature and previous.signature == run_signature(options))


def generate(
    service: str,
    *,
    dry_run: bool = False,
    update_only: bool = False,
    only_types: Optional[Sequence[str]] = None,
    report_path: Optional[str] = None,
    force: bool = False,
    smoke: bool = True,
    check: bool = False,
) -> None:
    """Read the service metadata and generate/update the corresponding model files."""
    definition = get_service(service)
    options = GeneratorOptions.load(service, GENERATOR_DIR, dry_run=dry_run)
    if _up_to_date(options, force=force, only_types=only_types, report_path=report_path):
        print("Model is up to date (metadata, config and templates unchanged); nothing to do.")
        return
    reader: ODataReader = definition.reader(options.metadata_path)
    documentation = definition.documentation() if definition.documentation else None
    GeneratorPipeline(
        reader.read(),
        options,
        documentation,
        base_dir=GENERATOR_DIR,
        update_only=update_only,
        only_types=list(only_types) if only_types else None,
        report_path=report_path,
        force=force,
        smoke=smoke,
        check=check,
    ).run()


def suggest_routing(service: str) -> None:
    """Print a proposed ``routing``/``type_routing`` YAML block for unrouted types."""
    definition = get_service(service)
    options = GeneratorOptions.load(service, GENERATOR_DIR)
    model = definition.reader(options.metadata_path).read()
    registry = TypeRegistry(options.modules.split(","), namespace=options.namespace)
    router = Router.from_options(options.builder_context())
    print(render_suggestions(model, TypeFilter.from_options(options), registry, router))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate entity model files from OData metadata")
    parser.add_argument(
        "service",
        nargs="?",
        default="sharepoint",
        choices=service_names(),
        help="which model to generate (default: sharepoint)",
    )
    parser.add_argument("--dry-run", action="store_true", help="validate and report without writing files")
    parser.add_argument(
        "--update-only",
        action="store_true",
        help="only update types that already exist in the model; never create new files",
    )
    parser.add_argument(
        "--type",
        dest="types",
        action="append",
        default=[],
        metavar="ODATA_TYPE",
        help="only process this OData type (e.g. SP.File); repeatable",
    )
    parser.add_argument("--report", dest="report_path", help="write a JSON run report to this path")
    parser.add_argument(
        "--force",
        action="store_true",
        help="ignore the up-to-date fast path and regenerate from scratch",
    )
    parser.add_argument(
        "--no-smoke",
        dest="smoke",
        action="store_false",
        help="skip importing the written modules after a successful run",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="run ruff and pyright on the output after writing (slow)",
    )
    parser.add_argument(
        "--suggest-routing",
        action="store_true",
        help="print a proposed routing block for unrouted types and exit",
    )
    args = parser.parse_args(argv)
    if args.suggest_routing:
        suggest_routing(args.service)
        return 0
    try:
        generate(
            args.service,
            dry_run=args.dry_run,
            update_only=args.update_only,
            only_types=args.types,
            report_path=args.report_path,
            force=args.force,
            smoke=args.smoke,
            check=args.check,
        )
    except ValidationError as e:
        print(f"error: {e}")
        return 1
    except ConfigError as e:
        print(f"config error: {e}")
        return 1
    return 0
