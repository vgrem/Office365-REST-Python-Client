from __future__ import annotations

import builtins
import keyword
import re

from generator.odata.type_system import is_collection_name, primitive_type_for, strip_collection

#: Product/compound names kept as one word when snake-cased (``SharePoint`` -> ``sharepoint``).
#: ``DateTime`` is *not* here: the library convention is ``created_date_time``.
_COMPOUND_WORDS = ("SharePoint", "OneDrive", "OneNote")


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


def normalize_member_key(name: str) -> str:
    """A separator-insensitive key for member de-duplication.

    ``created_date_time`` and ``created_datetime`` share a key, while the leading
    and trailing underscores of names like ``__class__`` are preserved.
    """
    return re.sub(r"(?<=\w)_(?=\w)", "", name)


def python_name(type_name: str | None, is_object_type: bool = False) -> str:
    """Format an OData type name as the Python annotation name.

    ``Edm.Int32`` -> ``int``; ``Collection(Edm.String)`` ->
    ``ClientValueCollection[str]``; ``SP.Web`` -> ``Web``;
    ``Collection(SP.Web)`` -> ``EntityCollection[Web]`` when ``is_object_type``.
    """
    if type_name is None:
        return ""
    primitive = primitive_type_for(type_name)
    if primitive is not None:
        return primitive.__name__
    if is_collection_name(type_name):
        child = item_name(strip_collection(type_name), is_object_type)
        return f"EntityCollection[{child}]" if is_object_type else f"ClientValueCollection[{child}]"
    if type_name.startswith("Edm."):
        raise ValueError(f"Unmapped OData primitive '{type_name}'; add it to PRIMITIVE_PY_TYPES.")
    cls_name = type_name.split(".")[-1]
    if cls_name and cls_name[0].islower():
        cls_name = cls_name[0].upper() + cls_name[1:]
    return cls_name


def item_name(type_name: str | None, is_object_type: bool = False) -> str:
    """Format the item type of a collection (or the type itself) as a Python name."""
    return python_name(strip_collection(type_name), is_object_type)
