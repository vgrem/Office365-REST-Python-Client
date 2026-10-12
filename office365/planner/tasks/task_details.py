from typing import Iterable, Optional, Union

from typing_extensions import Self

from office365.planner.entity import PlannerEntity
from office365.planner.external_references import PlannerExternalReferences
from office365.planner.tasks.check_list_item import PlannerChecklistItem
from office365.planner.tasks.check_list_items import PlannerChecklistItems
from office365.runtime.types.odata_property import odata


class PlannerTaskDetails(PlannerEntity):
    """
    The plannerTaskDetails resource represents the additional information about a task.
    Each task object has a details object.
    """

    @odata(name="checklist", persist=True)
    @property
    def checklist(self) -> PlannerChecklistItems:
        """
        The collection of checklist items on the task, keyed by item id.

        The returned map is mutable: changes are sent with :meth:`update`
        without re-assigning the property.
        """
        return self.properties.setdefault("checklist", PlannerChecklistItems())

    def add_checklist_item(self, title: str, *, is_checked: bool = False, order_hint: str = " !") -> Self:
        """Adds a checklist item.

        Args:
            title: The item text.
            is_checked: Whether the item is already checked.
            order_hint: Planner ordering hint; ``" !"`` appends.
        """
        self.checklist.add(title, is_checked=is_checked, order_hint=order_hint)
        return self

    def set_checklist(self, items: Iterable[Union[str, PlannerChecklistItem]]) -> Self:
        """Replaces the task checklist with ``items``.

        Items already loaded on this object are removed first, so the resulting
        checklist matches ``items`` exactly. Strings create unchecked items;
        :class:`PlannerChecklistItem` values keep their ``is_checked`` flag.
        """
        checklist = self.checklist
        for item_id in list(vars(checklist)):
            checklist.set_property(item_id, None)
        for item in items:
            if isinstance(item, str):
                checklist.add(item)
            else:
                checklist.add(
                    item.title or "",
                    is_checked=bool(item.isChecked),
                    order_hint=item.orderHint or " !",
                )
        self.set_property("checklist", checklist)
        return self

    @property
    def description(self) -> Optional[str]:
        """Description of the task."""
        return self.properties.get("description", None)

    @description.setter
    def description(self, value: str) -> None:
        self.set_property("description", value)

    @property
    def preview_type(self) -> Optional[str]:
        """This sets the type of preview that shows up on the task.
        The possible values are: automatic, noPreview, checklist, description, reference.
        When set to automatic the displayed preview is chosen by the app viewing the task.
        """
        return self.properties.get("previewType", None)

    @preview_type.setter
    def preview_type(self, value: str) -> None:
        self.set_property("previewType", value)

    @property
    def references(self) -> PlannerExternalReferences:
        """
        The collection of references on the task.
        """
        return self.properties.get("references", PlannerExternalReferences())
