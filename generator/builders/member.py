from __future__ import annotations

import ast
import keyword
from typing import TYPE_CHECKING

from generator.odata.member import MemberInformation

if TYPE_CHECKING:
    from generator.builders.template_context import TemplateContext

#: Names that are valid identifiers but trigger lint (``E741``) or are confusing.
_AMBIGUOUS_NAMES = {"l", "I", "O"}


def sanitize_member_name(name: str) -> str:
    """A safe Python member name (keywords and ambiguous single letters get ``_``)."""
    if keyword.iskeyword(name) or name in _AMBIGUOUS_NAMES:
        return f"{name}_"
    return name


class MemberBuilder:
    def __init__(self, schema: MemberInformation, status="detached"):
        self.schema = schema
        self.status = status
        self.docstring = None

    def build(self, template: TemplateContext) -> list:
        """Build AST nodes for this member"""
        if self.status == "attached":
            return []

        member_node = template.build_member(self)

        # Add docstring if available
        if self.docstring:
            # Create a docstring node before the assignment
            docstring_node = ast.Expr(value=ast.Constant(value=self.docstring))
            return [docstring_node, member_node]

        return [member_node]

    @property
    def name(self):
        return sanitize_member_name(self.schema.Name)

    @property
    def value(self):
        return self.schema.Value
