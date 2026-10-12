from __future__ import annotations

from typing import Any, Dict, Optional

from typing_extensions import Self

from office365.planner.assignment import PlannerAssignment
from office365.runtime.client_value import ClientValue
from office365.runtime.converters.value import deserialize_value, serialize_value
from office365.runtime.odata.json_format import ODataJsonFormat


class PlannerAssignments(ClientValue):
    """The set of users assigned to a task.

    An Open Type serialized as a JSON object keyed by user id, where each value
    is a :class:`PlannerAssignment`.
    """

    _item_type = PlannerAssignment

    def set_property(self, k: str | int, v: Any, persist_changes: bool = True) -> Self:
        # Map raw JSON objects onto the typed assignment so reads stay strongly typed.
        if isinstance(v, dict):
            v = deserialize_value(self._item_type, v, None, persist_changes)
        return super().set_property(k, v, persist_changes)

    def add(self, user_id: str, *, order_hint: str = " !") -> str:
        """Assigns a user and returns their id.

        Args:
            user_id: The id of the user to assign.
            order_hint: Planner ordering hint; ``" !"`` appends.
        """
        user_id = str(user_id)
        self.set_property(user_id, PlannerAssignment(orderHint=order_hint))
        return user_id

    def remove(self, user_id: str) -> Self:
        """Unassigns a user.

        Graph drops the entry when its value is ``null``.
        """
        self.set_property(str(user_id), None)
        return self

    def to_json(self, json_format: Optional[ODataJsonFormat] = None) -> Dict[str, Any]:
        """Serializes the assignments, preserving ``null`` entries used to unassign users."""
        return {k: (None if v is None else serialize_value(v, json_format)) for k, v in self}
