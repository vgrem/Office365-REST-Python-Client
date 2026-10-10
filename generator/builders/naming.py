from __future__ import annotations

import builtins
import keyword
import re

#: Product/compound names kept as one word when snake-cased (``SharePoint`` -> ``sharepoint``).
_COMPOUND_WORDS = ("SharePoint", "OneDrive", "OneNote", "DateTime")


def _protect_compounds(name: str) -> str:
    """Collapse multi-word product names so the camel split keeps them whole."""
    for word in _COMPOUND_WORDS:
        name = re.sub(word, word.lower().capitalize(), name, flags=re.IGNORECASE)
    return name


def to_snake_case(name: str, avoid_keywords: bool = True, avoid_builtins: bool = False) -> str:
    """Converts a PascalCase/camelCase identifier to snake_case.

    Handles acronyms and plural acronyms:

    * ``emailIDs`` -> ``email_ids``, ``APIs`` -> ``apis``, ``URLs`` -> ``urls``
    * ``HTTPServer`` -> ``http_server``, ``UTCToLocalTime`` -> ``utc_to_local_time``

    Args:
        name: Identifier to convert.
        avoid_keywords: When true, append ``_`` to Python keywords so the result is
            a valid name (``Class`` -> ``class_``).
        avoid_builtins: When true, also avoid Python builtins (``ID`` -> ``id_``).
            Off by default: builtins are valid member names and the codebase uses
            them (``id``, ``type``, ``list``); on for method arguments to satisfy
            ``flake8-builtins`` (A002).
    """
    # lower -> upper boundary (emailIDs -> email_IDs)
    s1 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", _protect_compounds(name))
    # single capital followed by a word (ASite -> A_Site, IFollowed -> I_Followed)
    s2 = re.sub(r"([A-Z])([A-Z][a-z]{2,})", r"\1_\2", s1)
    # acronym followed by a short word (UTCTo -> UTC_To); 's' is excluded so that
    # plural acronyms (IDs, URLs, APIs) are not split
    s3 = re.sub(r"([A-Z]{2,})([A-Z][a-rt-z])", r"\1_\2", s2)
    # merge a leading single lowercase word (iCalUId -> ical_uid) before lowercasing
    snake_case = re.sub(r"^([a-z])_", r"\1", s3).lower()
    if avoid_keywords and keyword.iskeyword(snake_case):
        return snake_case + "_"
    if avoid_builtins and hasattr(builtins, snake_case):
        return snake_case + "_"
    return snake_case
