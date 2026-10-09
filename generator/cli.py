"""Command line entry point for the model generator."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional, Sequence

from generator.config import GeneratorOptions
from generator.odata.reader import ODataReader
from generator.pipeline import GeneratorPipeline
from generator.services import get_service, service_names

#: Config/paths are resolved relative to this directory, not the CWD.
GENERATOR_DIR = Path(__file__).parent


def generate(service: str, *, dry_run: bool = False, update_only: bool = False) -> None:
    """Read the service metadata and generate/update the corresponding model files."""
    definition = get_service(service)
    options = GeneratorOptions.load(service, GENERATOR_DIR, dry_run=dry_run)
    reader: ODataReader = definition.reader(options.metadata_path)
    documentation = definition.documentation() if definition.documentation else None
    GeneratorPipeline(reader.read(), options, documentation, base_dir=GENERATOR_DIR, update_only=update_only).run()


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
    args = parser.parse_args(argv)
    generate(args.service, dry_run=args.dry_run, update_only=args.update_only)
    return 0
