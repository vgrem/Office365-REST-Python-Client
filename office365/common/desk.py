from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.booking.mailbox_details import MailboxDetails
    from office365.booking.place_mode import PlaceMode
    from office365.booking.place_service_plan_info import PlaceServicePlanInfo
    from office365.outlook.place_feature_enablement import PlaceFeatureEnablement


class Desk(Entity):
    @property
    def display_device_name(self) -> Optional[str]:
        """Gets the displayDeviceName property"""
        return self.properties.get("displayDeviceName", None)

    @property
    def height_adjustable_state(self) -> PlaceFeatureEnablement:
        """Gets the heightAdjustableState property"""
        from office365.outlook.place_feature_enablement import PlaceFeatureEnablement

        return self.properties.get("heightAdjustableState", PlaceFeatureEnablement.unknown)

    @property
    def mailbox_details(self) -> MailboxDetails:
        """Gets the mailboxDetails property"""
        from office365.booking.mailbox_details import MailboxDetails

        return self.properties.get("mailboxDetails", MailboxDetails())

    @property
    def mode(self) -> PlaceMode:
        """Gets the mode property"""
        from office365.booking.place_mode import PlaceMode

        return self.properties.get("mode", PlaceMode())

    @property
    def service_plans(self) -> ClientValueCollection[PlaceServicePlanInfo]:
        """Gets the servicePlans property"""
        from office365.booking.place_service_plan_info import PlaceServicePlanInfo

        return self.properties.get("servicePlans", ClientValueCollection[PlaceServicePlanInfo](PlaceServicePlanInfo))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Desk"
