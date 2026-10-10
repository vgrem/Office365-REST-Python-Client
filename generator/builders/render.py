"""Post-processing of generated source.

``ast.unparse`` emits ``'single'`` string literals, while the codebase (and
``ruff format``) uses ``"double"`` and only falls back to single quotes when the
value itself contains a double quote. Re-quoting here keeps regenerated files
stable against the committed style instead of churning every string literal.
"""

from __future__ import annotations

import ast
import io
import json
import shutil
import subprocess
import sys
import tokenize
from functools import lru_cache
from pathlib import Path
from typing import Optional

_TRIPLE_QUOTES = ('"""', "'''")


def normalize_quotes(source: str) -> str:
    """Rewrite simple string literals to the project's quote style.

    Docstrings, bytes literals, raw strings and f-strings are left untouched.
    """
    tokens = []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        emitted = token
        if token.type == tokenize.STRING:
            requoted = _requote(token.string)
            if requoted != token.string:
                emitted = tokenize.TokenInfo(token.type, requoted, token.start, token.end, token.line)
        tokens.append(emitted)
    return tokenize.untokenize(tokens)


def _requote(literal: str) -> str:
    prefix, body = _split_prefix(literal)
    if body.startswith(_TRIPLE_QUOTES) or prefix.lower() == "r":
        return literal
    try:
        value = ast.literal_eval(literal)
    except (SyntaxError, ValueError):
        return literal
    if not isinstance(value, str):
        return literal
    return prefix + _quote(value)


def _quote(value: str) -> str:
    """Double-quoted literal, but single quotes when the value contains ``"``."""
    if '"' in value and "'" not in value:
        return repr(value)
    return json.dumps(value, ensure_ascii=False)


def _split_prefix(literal: str) -> tuple[str, str]:
    index = 0
    while index < len(literal) and literal[index].isalpha():
        index += 1
    return literal[:index], literal[index:]


@lru_cache(maxsize=1)
def ruff_binary() -> Optional[str]:
    """Locate ``ruff`` (on PATH or beside the running interpreter)."""
    found = shutil.which("ruff")
    if found:
        return found
    sibling = Path(sys.executable).with_name("ruff")
    return str(sibling) if sibling.exists() else None


def _ruff_stdin(ruff: str, args: list[str], source: str, filename: str) -> Optional[str]:
    try:
        proc = subprocess.run(
            [ruff, *args, "--stdin-filename", filename, "-"],
            input=source,
            capture_output=True,
            text=True,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout or None


def ruff_normalize(source: str, filename: str) -> str:
    """Sort imports and format the source with ruff (repo style); best effort."""
    ruff = ruff_binary()
    if ruff is None:
        return source
    fixed = _ruff_stdin(ruff, ["check", "--isolated", "--select", "I001", "--fix"], source, filename)
    if fixed:
        source = fixed
    formatted = _ruff_stdin(ruff, ["format"], source, filename)
    return formatted or source
