from __future__ import annotations

from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.publishing.amplify.clientamplifyanywhereresults import ClientAmplifyAnywhereResults
from office365.sharepoint.publishing.amplify.clientamplifyresults import ClientAmplifyResults
from office365.sharepoint.publishing.amplify.history import AmplifyPublishingHistory
from office365.sharepoint.publishing.amplify.requestparams import AmplifyRequestParams
from office365.sharepoint.publishing.boostfieldsdata import BoostFieldsData
from office365.sharepoint.publishing.pages.coauth_state import SitePageCoAuthState
from office365.sharepoint.publishing.pages.dependency_metadata import SitePageDependencyMetadata
from office365.sharepoint.publishing.pages.page import SitePage
from office365.sharepoint.publishing.pages.sendtestemailresponse import SendTestEmailResponse
from office365.sharepoint.publishing.pages.sendtestteamsmessageresponse import SendTestTeamsMessageResponse
from office365.sharepoint.publishing.pages.versioninfocollection import SitePageVersionInfoCollection
from office365.sharepoint.publishing.sitepageauthoringmetadata import SitePageAuthoringMetadata


class SitePage3D(SitePage):
    @property
    def space_content(self):
        return self.properties.get("SpaceContent", None)

    @property
    def entity_type_name(self):
        return "SP.Publishing.SitePage3D"

    def amplify(self, request: AmplifyRequestParams) -> ClientResult[ClientAmplifyAnywhereResults]:
        """Amplify operation.

        Args:
            request (AmplifyRequestParams): request parameter
        """
        return_type = ClientResult(self.context, ClientAmplifyAnywhereResults())
        qry = ServiceOperationQuery(self, "Amplify", None, {"request": request}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def amplify_history(self) -> ClientResult[AmplifyPublishingHistory]:
        """AmplifyHistory operation."""
        return_type = ClientResult(self.context, AmplifyPublishingHistory())
        qry = ServiceOperationQuery(self, "AmplifyHistory", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def amplify_send_test_email_message(self, content_stream: bytes) -> ClientResult[ClientAmplifyResults]:
        """AmplifySendTestEmailMessage operation.

        Args:
            content_stream (bytes): contentStream parameter
        """
        return_type = ClientResult(self.context, ClientAmplifyResults())
        qry = ServiceOperationQuery(
            self, "AmplifySendTestEmailMessage", None, {"contentStream": content_stream}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def amplify_send_test_teams_message(
        self, audience_id: str, group_id: UUID, transpile_content: str, channel_name: str, team_name: str
    ) -> ClientResult[ClientAmplifyResults]:
        """AmplifySendTestTeamsMessage operation.

        Args:
            audience_id (str): audienceId parameter
            group_id (UUID): groupId parameter
            transpile_content (str): transpileContent parameter
            channel_name (str): channelName parameter
            team_name (str): teamName parameter
        """
        return_type = ClientResult(self.context, ClientAmplifyResults())
        qry = ServiceOperationQuery(
            self,
            "AmplifySendTestTeamsMessage",
            None,
            {
                "audienceId": audience_id,
                "groupId": group_id,
                "transpileContent": transpile_content,
                "channelName": channel_name,
                "teamName": team_name,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def boost_news(self, site_page_boost: BoostFieldsData) -> Self:
        """BoostNews operation.

        Args:
            site_page_boost (BoostFieldsData): SitePageBoost parameter
        """
        qry = ServiceOperationQuery(self, "BoostNews", None, {"SitePageBoost": site_page_boost}, None, None)
        self.context.add_query(qry)
        return self

    def check_out(self) -> ClientResult[bool]:
        """CheckOut operation."""
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "CheckOut", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def demote_from_news(self) -> ClientResult[bool]:
        """DemoteFromNews operation."""
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "DemoteFromNews", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def extend_session_co_auth(
        self, authoring_metadata: SitePageAuthoringMetadata, connectivity_update_reason: int
    ) -> ClientResult[SitePageCoAuthState]:
        """ExtendSessionCoAuth operation.

        Args:
            authoring_metadata (SitePageAuthoringMetadata): authoringMetadata parameter
            connectivity_update_reason (int): connectivityUpdateReason parameter
        """
        return_type = ClientResult(self.context, SitePageCoAuthState())
        qry = ServiceOperationQuery(
            self,
            "ExtendSessionCoAuth",
            None,
            {"authoringMetadata": authoring_metadata, "connectivityUpdateReason": connectivity_update_reason},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_dependency_metadata(self) -> ClientResult[ClientValueCollection[SitePageDependencyMetadata]]:
        """GetDependencyMetadata operation."""
        return_type = ClientResult(self.context, ClientValueCollection[SitePageDependencyMetadata]())
        qry = FunctionQuery(self, "GetDependencyMetadata", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_latest_versions_in_descending_order(
        self, num_versions: int
    ) -> ClientResult[ClientValueCollection[SitePageVersionInfoCollection]]:
        """GetLatestVersionsInDescendingOrder operation.

        Args:
            num_versions (int): numVersions parameter
        """
        return_type = ClientResult(self.context, ClientValueCollection[SitePageVersionInfoCollection]())
        qry = FunctionQuery(self, "GetLatestVersionsInDescendingOrder", [num_versions], return_type)
        self.context.add_query(qry)
        return return_type

    def promote_to_news(self) -> ClientResult[bool]:
        """PromoteToNews operation."""
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "PromoteToNews", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def publish(self) -> ClientResult[bool]:
        """Publish operation."""
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "Publish", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def publish_co_auth(self, page_stream: bytes) -> ClientResult[SitePageCoAuthState]:
        """PublishCoAuth operation.

        Args:
            page_stream (bytes): pageStream parameter
        """
        return_type = ClientResult(self.context, SitePageCoAuthState())
        qry = ServiceOperationQuery(self, "PublishCoAuth", None, {"pageStream": page_stream}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def restore_by_label(self, versionlabel: str) -> Self:
        """RestoreByLabel operation.

        Args:
            versionlabel (str): versionlabel parameter
        """
        qry = ServiceOperationQuery(self, "RestoreByLabel", None, {"versionlabel": versionlabel}, None, None)
        self.context.add_query(qry)
        return self

    def save_page_co_auth(self, page_stream: bytes) -> ClientResult[SitePageCoAuthState]:
        """SavePageCoAuth operation.

        Args:
            page_stream (bytes): pageStream parameter
        """
        return_type = ClientResult(self.context, SitePageCoAuthState())
        qry = ServiceOperationQuery(self, "SavePageCoAuth", None, {"pageStream": page_stream}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def save_streams(self, content_stream: bytes, shared_lock_id: str, scenario: int) -> Self:
        """SaveStreams operation.

        Args:
            content_stream (bytes): contentStream parameter
            shared_lock_id (str): sharedLockId parameter
            scenario (int): scenario parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SaveStreams",
            None,
            {"contentStream": content_stream, "sharedLockId": shared_lock_id, "scenario": scenario},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def send_test_email(
        self, transpile_content: str, subject: str, sensitivity_label_id: str
    ) -> ClientResult[SendTestEmailResponse]:
        """SendTestEmail operation.

        Args:
            transpile_content (str): transpileContent parameter
            subject (str): subject parameter
            sensitivity_label_id (str): sensitivityLabelId parameter
        """
        return_type = ClientResult(self.context, SendTestEmailResponse())
        qry = ServiceOperationQuery(
            self,
            "SendTestEmail",
            None,
            {"transpileContent": transpile_content, "subject": subject, "sensitivityLabelId": sensitivity_label_id},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def send_test_email_stream(self, content_stream: bytes) -> ClientResult[SendTestEmailResponse]:
        """SendTestEmailStream operation.

        Args:
            content_stream (bytes): contentStream parameter
        """
        return_type = ClientResult(self.context, SendTestEmailResponse())
        qry = ServiceOperationQuery(
            self, "SendTestEmailStream", None, {"contentStream": content_stream}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def send_test_teams_message(
        self, audience_id: str, transpile_content: str
    ) -> ClientResult[SendTestTeamsMessageResponse]:
        """SendTestTeamsMessage operation.

        Args:
            audience_id (str): audienceId parameter
            transpile_content (str): transpileContent parameter
        """
        return_type = ClientResult(self.context, SendTestTeamsMessageResponse())
        qry = ServiceOperationQuery(
            self,
            "SendTestTeamsMessage",
            None,
            {"audienceId": audience_id, "transpileContent": transpile_content},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def share_page_preview_by_email(self, message: str, recipient_emails: list[str]) -> Self:
        """SharePagePreviewByEmail operation.

        Args:
            message (str): message parameter
            recipient_emails (list[str]): recipientEmails parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SharePagePreviewByEmail",
            None,
            {"message": message, "recipientEmails": StringCollection(recipient_emails)},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def start_exclusive_authoring(self) -> ClientResult[bool]:
        """StartExclusiveAuthoring operation."""
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "StartExclusiveAuthoring", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def try_process_source_page_after_page_move_publish(self) -> ClientResult[bool]:
        """TryProcessSourcePageAfterPageMovePublish operation."""
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "TryProcessSourcePageAfterPageMovePublish", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def try_process_source_page_before_page_move_publish(self) -> ClientResult[bool]:
        """TryProcessSourcePageBeforePageMovePublish operation."""
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "TryProcessSourcePageBeforePageMovePublish", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type
