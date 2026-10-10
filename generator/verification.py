"""Source validation and post-commit checks for generated files.

``semantic_issues`` runs before anything is written (undefined names surface
during ``--dry-run``); :class:`PostCommitVerifier` imports the written modules
and optionally runs ruff/pyright over them.
"""

from __future__ import annotations

import importlib
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Sequence

from generator.builders.render import ruff_binary
from generator.validation import ValidationError

if TYPE_CHECKING:
    from generator.builders.type import TypeBuilder

Planned = Sequence[tuple[str, "TypeBuilder"]]


def semantic_issues(source: str, filename: str) -> list[str]:
    """Syntax and undefined-name issues in rendered source.

    :func:`~generator.validation.validate_source` only checks structure
    (duplicate class/member); this adds a compile and a ``ruff``
    ``F821``/``F811`` pass so missing imports surface before anything is written.
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


@dataclass
class PostCommitVerifier:
    """Checks the written output: import smoke, and optional ruff + pyright."""

    output_root: Path
    smoke: bool = True
    check: bool = False

    def verify(self, planned: Planned) -> None:
        """Run the enabled checks; raise :class:`ValidationError` on failure."""
        if self.smoke:
            self._smoke_import(planned)
        if self.check:
            self._run_checks(planned)

    def _module_name(self, file: str) -> Optional[str]:
        """The importable module name for a generated file, or ``None``."""
        try:
            relative = Path(file).resolve().relative_to(self.output_root)
        except ValueError:
            return None
        parts = [self.output_root.name, *relative.with_suffix("").parts]
        if not all(part.isidentifier() for part in parts):
            return None
        return ".".join(parts)

    def _smoke_import(self, planned: Planned) -> None:
        """Import every written module to catch runtime import errors."""
        failures: list[str] = []
        for _name, builder in planned:
            module = self._module_name(builder.file)
            if module is None:
                continue
            try:
                importlib.import_module(module)
            except Exception as e:  # noqa: BLE001 - report any import failure
                failures.append(f"{module}: {type(e).__name__}: {e}")
        if failures:
            for failure in failures:
                print(f"  import failed: {failure}")
            raise ValidationError(f"{len(failures)} generated module(s) failed to import")

    def _run_checks(self, planned: Planned) -> None:
        """Run ``ruff`` and ``pyright`` on the written output (opt-in, slow)."""
        files = [builder.file for _name, builder in planned if Path(builder.file).exists()]
        if not files:
            return
        ruff = ruff_binary()
        if ruff is not None:
            proc = subprocess.run([ruff, "check", *files], capture_output=True, text=True, check=False)
            if proc.returncode != 0:
                print(proc.stdout.strip()[:4000])
                raise ValidationError("ruff check failed on generated files")
        self._run_pyright()

    @staticmethod
    def _run_pyright() -> None:
        """Type-check the output using the repository's pyright configuration."""
        if shutil.which("pyright"):
            command = ["pyright"]
        elif shutil.which("uv"):
            command = ["uv", "run", "pyright"]
        else:
            return
        proc = subprocess.run(command, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            print((proc.stdout or proc.stderr).strip()[-4000:])
            raise ValidationError("pyright reported errors in the generated output")
