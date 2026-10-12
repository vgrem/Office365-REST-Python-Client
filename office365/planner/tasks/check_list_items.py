from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from typing_extensions import Self

from office365.planner.tasks.check_list_item import PlannerChecklistItem
from office365.runtime.client_value import ClientValue
from office365.runtime.converters.value import deserialize_value, serialize_value
from office365.runtime.odata.json_format import ODataJsonFormat


class PlannerChecklistItems(ClientValue):
    """The checklist of a task.

    An Open Type serialized as a JSON object keyed by checklist item id, where
    each value is a :class:`PlannerChecklistItem`. Item ids are client-generated
    (Graph echoes them back).
    """

    _item_type = PlannerChecklistItem

    def set_property(self, k: str | int, v: Any, persist_changes: bool = True) -> Self:
        # Map raw JSON objects onto the typed item so reads stay strongly typed.
        if isinstance(v, dict):
            v = deserialize_value(self._item_type, v, None, persist_changes)
        return super().set_property(k, v, persist_changes)

    def add(self, title: str, *, is_checked: bool = False, order_hint: str = " !") -> str:
        """Adds a checklist item and returns its generated id.

        Args:
            title: The item text.
            is_checked: Whether the item is already checked.
            order_hint: Planner ordering hint; ``" !"`` appends.
        """
        item_id = str(uuid.uuid4())
        self.set_property(item_id, PlannerChecklistItem(title=title, isChecked=is_checked, orderHint=order_hint))
        return item_id

    def remove(self, item_id: str) -> Self:
        """Removes a checklist item.

        Graph drops the entry when its value is ``null``.
        """
        self.set_property(item_id, None)
        return self

    def to_json(self, json_format: Optional[ODataJsonFormat] = None) -> Dict[str, Any]:
        """Serializes the checklist, preserving ``null`` entries used to remove items."""
        return {k: (None if v is None else serialize_value(v, json_format)) for k, v in self}
