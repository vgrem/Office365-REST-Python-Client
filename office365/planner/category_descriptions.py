from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class PlannerCategoryDescriptions(ClientValue):
    """Represents the descriptive labels for the categories that have been defined for a plan.
    It belongs to the plan details object. There can be up to 25 categories defined."""

    category1: str | None = None

    category10: str | None = None

    category11: str | None = None

    category12: str | None = None

    category13: str | None = None

    category14: str | None = None

    category15: str | None = None

    category16: str | None = None

    category17: str | None = None

    category18: str | None = None

    category19: str | None = None

    category2: str | None = None

    category20: str | None = None

    category21: str | None = None

    category22: str | None = None

    category23: str | None = None

    category24: str | None = None

    category25: str | None = None

    category3: str | None = None

    category4: str | None = None

    category5: str | None = None

    category6: str | None = None

    category7: str | None = None

    category8: str | None = None

    category9: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PlannerCategoryDescriptions"
