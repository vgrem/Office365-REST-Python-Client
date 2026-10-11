from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.teams.administration.assignment_category import AssignmentCategory

if TYPE_CHECKING:
    from office365.teams.administration.activation_state import ActivationState
    from office365.teams.administration.assignment_status import AssignmentStatus
    from office365.teams.administration.customer_action import CustomerAction
    from office365.teams.administration.number_capability import NumberCapability
    from office365.teams.administration.number_source import NumberSource
    from office365.teams.administration.number_type import NumberType
    from office365.teams.administration.port_in_status import PortInStatus
    from office365.teams.administration.reverse_number_lookup_option import (
        ReverseNumberLookupOption,
    )


class NumberAssignment(Entity):
    @property
    def assignment_category(self) -> AssignmentCategory:
        """Gets the assignmentCategory property"""
        return self.properties.get("assignmentCategory", AssignmentCategory())

    @property
    def assignment_target_id(self) -> Optional[str]:
        """Gets the assignmentTargetId property"""
        return self.properties.get("assignmentTargetId", None)

    @property
    def city(self) -> Optional[str]:
        """Gets the city property"""
        return self.properties.get("city", None)

    @property
    def civic_address_id(self) -> Optional[str]:
        """Gets the civicAddressId property"""
        return self.properties.get("civicAddressId", None)

    @property
    def iso_country_code(self) -> Optional[str]:
        """Gets the isoCountryCode property"""
        return self.properties.get("isoCountryCode", None)

    @property
    def location_id(self) -> Optional[str]:
        """Gets the locationId property"""
        return self.properties.get("locationId", None)

    @property
    def network_site_id(self) -> Optional[str]:
        """Gets the networkSiteId property"""
        return self.properties.get("networkSiteId", None)

    @property
    def operator_id(self) -> Optional[str]:
        """Gets the operatorId property"""
        return self.properties.get("operatorId", None)

    @property
    def telephone_number(self) -> Optional[str]:
        """Gets the telephoneNumber property"""
        return self.properties.get("telephoneNumber", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.teamsAdministration.NumberAssignment"

    @property
    def activation_state(self) -> ActivationState:
        """Gets the activationState property"""
        from office365.teams.administration.activation_state import ActivationState

        return self.properties.get("activationState", ActivationState.activated)

    @property
    def assignment_status(self) -> AssignmentStatus:
        """Gets the assignmentStatus property"""
        from office365.teams.administration.assignment_status import AssignmentStatus

        return self.properties.get("assignmentStatus", AssignmentStatus.unassigned)

    @property
    def capabilities(self) -> ClientValueCollection[NumberCapability]:
        """Gets the capabilities property"""
        from office365.teams.administration.number_capability import NumberCapability

        return self.properties.get("capabilities", ClientValueCollection[NumberCapability](NumberCapability))

    @property
    def number_source(self) -> NumberSource:
        """Gets the numberSource property"""
        from office365.teams.administration.number_source import NumberSource

        return self.properties.get("numberSource", NumberSource.online)

    @property
    def number_type(self) -> NumberType:
        """Gets the numberType property"""
        from office365.teams.administration.number_type import NumberType

        return self.properties.get("numberType", NumberType.internalError)

    @property
    def port_in_status(self) -> PortInStatus:
        """Gets the portInStatus property"""
        from office365.teams.administration.port_in_status import PortInStatus

        return self.properties.get("portInStatus", PortInStatus.completed)

    @property
    def reverse_number_lookup_options(self) -> ClientValueCollection[ReverseNumberLookupOption]:
        """Gets the reverseNumberLookupOptions property"""
        from office365.teams.administration.reverse_number_lookup_option import (
            ReverseNumberLookupOption,
        )

        return self.properties.get(
            "reverseNumberLookupOptions", ClientValueCollection[ReverseNumberLookupOption](ReverseNumberLookupOption)
        )

    @property
    def supported_customer_actions(self) -> ClientValueCollection[CustomerAction]:
        """Gets the supportedCustomerActions property"""
        from office365.teams.administration.customer_action import CustomerAction

        return self.properties.get("supportedCustomerActions", ClientValueCollection[CustomerAction](CustomerAction))
