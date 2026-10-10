from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.viva.announcementstate import AnnouncementState
    from office365.sharepoint.viva.dashboard.content import DashboardContent


class EmployeeExperienceController(Entity):
    def dashboard(
        self, form_factor: str, dashboard_id: str, my_site_url: str
    ) -> ClientResult[ClientValueCollection[DashboardContent]]:
        """Dashboard operation.

        Args:
            form_factor (str):
                formFactor parameter
            dashboard_id (str):
                dashboardId parameter
            my_site_url (str):
                mySiteUrl parameter
        """
        from office365.sharepoint.viva.dashboard.content import DashboardContent

        return_type = ClientResult(self.context, ClientValueCollection[DashboardContent]())
        qry = FunctionQuery(self, "Dashboard", [form_factor, dashboard_id, my_site_url], return_type)
        self.context.add_query(qry)
        return return_type

    def get_announcements_state(self, my_site_url: str) -> ClientResult[ClientValueCollection[AnnouncementState]]:
        """GetAnnouncementsState operation.

        Args:
            my_site_url (str):
                mySiteUrl parameter
        """
        from office365.sharepoint.viva.announcementstate import AnnouncementState

        return_type = ClientResult(self.context, ClientValueCollection[AnnouncementState]())
        qry = FunctionQuery(self, "GetAnnouncementsState", [my_site_url], return_type)
        self.context.add_query(qry)
        return return_type

    def save_dashboard(
        self, employee_experience_dashboard_data: DashboardContent, user_cards: str, my_site_url: str
    ) -> Self:
        """SaveDashboard operation.

        Args:
            employee_experience_dashboard_data (DashboardContent):
                employeeExperienceDashboardData parameter
            user_cards (str):
                userCards parameter
            my_site_url (str):
                mySiteUrl parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SaveDashboard",
            None,
            {
                "employeeExperienceDashboardData": employee_experience_dashboard_data,
                "userCards": user_cards,
                "mySiteUrl": my_site_url,
            },
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_announcement_state(
        self, announcement_states: ClientValueCollection[AnnouncementState], my_site_url: str
    ) -> Self:
        """SetAnnouncementState operation.

        Args:
            announcement_states (ClientValueCollection[AnnouncementState]):
                announcementStates parameter
            my_site_url (str):
                mySiteUrl parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetAnnouncementState",
            None,
            {"announcementStates": announcement_states, "mySiteUrl": my_site_url},
            None,
            None,
        )
        self.context.add_query(qry)
        return self
