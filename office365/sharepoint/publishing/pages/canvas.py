"""Parse a modern SharePoint page canvas (``CanvasContent1``).

A modern page serializes its content as HTML in which every client-side control
carries its settings in a ``data-sp-controldata`` attribute holding an
(HTML-escaped) JSON blob. A ``controlType`` of ``4`` marks a web part; the rest
are the layout skeleton (sections, columns, text) and text/web-part content.

Parsing is a pure function over data a caller already read, so these helpers
never talk to the server: ``SitePage.web_part_count`` applies them to
``CanvasContent1``, and the same functions serve any inventory that reads the
column directly (e.g. a list item).

Example:
    >>> from office365.sharepoint.publishing.pages.canvas import count_web_parts
    >>> count_web_parts(page.canvas_content1)
    3
"""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

__all__ = ["WEB_PART_CONTROL_TYPE", "CanvasControl", "count_web_parts", "parse_canvas_controls"]

WEB_PART_CONTROL_TYPE = 4
"""``controlType`` of a client-side (SPFx or built-in) web part."""

#: The canvas attribute holding one control's JSON settings.
_CONTROL_DATA_RE = re.compile(r'data-sp-controldata="([^"]*)"')


@dataclass
class CanvasControl:
    """One control serialized in a page canvas."""

    control_type: Optional[int] = None
    """The control's ``controlType``; ``None`` when the blob did not declare one."""

    data: Dict[str, Any] = field(default_factory=dict)
    """The decoded control data, as serialized (version, id, position, ...)."""

    @property
    def is_web_part(self) -> bool:
        """Whether this control is a client-side web part (not layout or text)."""
        return self.control_type == WEB_PART_CONTROL_TYPE


def parse_canvas_controls(canvas: Optional[str]) -> List[CanvasControl]:
    """Decode every control serialized in ``canvas``, skipping malformed blobs.

    Args:
        canvas: A page's ``CanvasContent1`` (``None``/empty for a classic page).

    Returns:
        The controls in canvas order; empty when the page carries no canvas.
    """
    controls: List[CanvasControl] = []
    if not canvas:
        return controls
    for match in _CONTROL_DATA_RE.finditer(canvas):
        try:
            data = json.loads(html.unescape(match.group(1)))
        except ValueError:
            continue
        if not isinstance(data, dict):
            continue
        controls.append(CanvasControl(control_type=data.get("controlType"), data=data))
    return controls


def count_web_parts(canvas: Optional[str]) -> int:
    """How many client-side web parts ``canvas`` serializes.

    Args:
        canvas: A page's ``CanvasContent1`` (``None``/empty for a classic page).
    """
    return sum(1 for control in parse_canvas_controls(canvas) if control.is_web_part)
