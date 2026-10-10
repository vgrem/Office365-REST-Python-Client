from __future__ import annotations

from typing import Optional

from office365.sharepoint.entity import Entity


class ApprovalRequest(Entity):
    @property
    def actions(self) -> Optional[str]:
        """Gets the Actions property"""
        return self.properties.get("Actions", None)

    @property
    def allow_cancel(self) -> Optional[bool]:
        """Gets the AllowCancel property"""
        return self.properties.get("AllowCancel", None)

    @property
    def allow_respond(self) -> Optional[bool]:
        """Gets the AllowRespond property"""
        return self.properties.get("AllowRespond", None)

    @property
    def allow_resubmit(self) -> Optional[bool]:
        """Gets the AllowResubmit property"""
        return self.properties.get("AllowResubmit", None)

    @property
    def approvers(self) -> Optional[str]:
        """Gets the Approvers property"""
        return self.properties.get("Approvers", None)

    @property
    def await_all(self) -> Optional[bool]:
        """Gets the AwaitAll property"""
        return self.properties.get("AwaitAll", None)

    @property
    def current_step_number(self) -> Optional[int]:
        """Gets the CurrentStepNumber property"""
        return self.properties.get("CurrentStepNumber", None)

    @property
    def details(self) -> Optional[str]:
        """Gets the Details property"""
        return self.properties.get("Details", None)

    @property
    def partner_metadata(self) -> Optional[str]:
        """Gets the PartnerMetadata property"""
        return self.properties.get("PartnerMetadata", None)

    @property
    def priority(self) -> Optional[int]:
        """Gets the Priority property"""
        return self.properties.get("Priority", None)

    @property
    def request_type(self) -> Optional[str]:
        """Gets the RequestType property"""
        return self.properties.get("RequestType", None)

    @property
    def responses(self) -> Optional[str]:
        """Gets the Responses property"""
        return self.properties.get("Responses", None)

    @property
    def status(self) -> Optional[int]:
        """Gets the Status property"""
        return self.properties.get("Status", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the Title property"""
        return self.properties.get("Title", None)

    @property
    def id(self) -> Optional[str]:
        """Gets the Id property"""
        return self.properties.get("Id", None)
