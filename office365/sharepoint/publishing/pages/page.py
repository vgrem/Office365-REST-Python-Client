from __future__ import annotations

from typing import Optional
from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.documents.coauthconfiguration import CoAuthConfiguration
from office365.sharepoint.publishing.amplify.clientamplifyanywhereresults import ClientAmplifyAnywhereResults
from office365.sharepoint.publishing.amplify.clientamplifyresults import ClientAmplifyResults
from office365.sharepoint.publishing.amplify.history import AmplifyPublishingHistory
from office365.sharepoint.publishing.amplify.requestparams import AmplifyRequestParams
from office365.sharepoint.publishing.boostfieldsdata import BoostFieldsData
from office365.sharepoint.publishing.pages.boostproperties import SitePageBoostProperties
from office365.sharepoint.publishing.pages.canvas import count_web_parts
from office365.sharepoint.publishing.pages.coauth_state import SitePageCoAuthState
from office365.sharepoint.publishing.pages.collaborator import SitePageCollaborator
from office365.sharepoint.publishing.pages.dependency_metadata import SitePageDependencyMetadata
from office365.sharepoint.publishing.pages.fields_data import SitePageFieldsData
from office365.sharepoint.publishing.pages.metadata import SitePageMetadata
from office365.sharepoint.publishing.pages.sendtestemailresponse import SendTestEmailResponse
from office365.sharepoint.publishing.pages.sendtestteamsmessageresponse import SendTestTeamsMessageResponse
from office365.sharepoint.publishing.pages.sharepagepreviewbyemailfieldsdata import SharePagePreviewByEmailFieldsData
from office365.sharepoint.publishing.pages.versioninfocollection import SitePageVersionInfoCollection
from office365.sharepoint.publishing.sitepageauthoringmetadata import SitePageAuthoringMetadata
from office365.sharepoint.translation.status_collection import TranslationStatusCollection


class SitePage(SitePageMetadata):
    """Represents a Site Page."""

    def checkout_page(self) -> Self:
        """Checks out the current Site Page if it is available to be checked out."""
        qry = ServiceOperationQuery(self, "CheckoutPage", None, None, None, self)
        self.context.add_query(qry)
        return self

    def copy(self) -> Self:
        """Creates a copy of the current Site Page and returns the resulting new SitePage."""
        qry = ServiceOperationQuery(self, "Copy")
        self.context.add_query(qry)
        return self

    def discard_page(self) -> Self:
        """Discards the current checked out version of the Site Page.  Returns the resulting SitePage after discard."""
        qry = ServiceOperationQuery(self, "DiscardPage", return_type=self)
        self.context.add_query(qry)
        return self

    def get_dependency_metadata(self) -> ClientResult[ClientValueCollection[SitePageDependencyMetadata]]:
        """ """
        return_type = ClientResult(self.context, ClientValueCollection(SitePageDependencyMetadata))
        qry = ServiceOperationQuery(self, "GetDependencyMetadata", return_type=return_type)
        self.context.add_query(qry)
        return return_type

    def get_version(self, version_id: str) -> "SitePage":
        """ """
        return_type = SitePage(self.context, self.resource_path)
        qry = ServiceOperationQuery(self, "GetVersion", [version_id], None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def save_page(
        self,
        title: str,
        canvas_content: Optional[str] = None,
        banner_image_url: Optional[str] = None,
        topic_header: Optional[str] = None,
    ):
        """Updates the current Site Page with the provided pageStream content.

        Args:
            title (str): The title of Site Page
            canvas_content (str):
            banner_image_url (str):
            topic_header (str):
        """
        payload = SitePageFieldsData(
            Title=title, CanvasContent1=canvas_content, BannerImageUrl=banner_image_url, TopicHeader=topic_header
        )
        qry = ServiceOperationQuery(self, "SavePage", None, payload, "pageStream")
        self.context.add_query(qry)
        return self

    def save_draft(self, title, canvas_content=None, banner_image_url=None, topic_header=None):
        """Updates the Site Page with the provided sitePage metadata and checks in a minor version if the page library
        has minor versions enabled.

        Args:
            title (str): The title of Site Page
            canvas_content (str):
            banner_image_url (str):
            topic_header (str):
        """
        payload = SitePageFieldsData(
            Title=title, CanvasContent1=canvas_content, BannerImageUrl=banner_image_url, TopicHeader=topic_header
        )
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "SaveDraft", None, payload, "sitePage", return_type)
        self.context.add_query(qry)
        return return_type

    def save_page_as_draft(self, title, canvas_content=None, banner_image_url=None, topic_header=None):
        """Updates the Site Page with the provided pageStream content and checks in a minor version if the page library
        has minor versions enabled.

        Args:
            title (str): The title of Site Page. At least Title property needs to be provided
            canvas_content (str):
            banner_image_url (str):
            topic_header (str):
        """
        payload = SitePageFieldsData(
            Title=title, CanvasContent1=canvas_content, BannerImageUrl=banner_image_url, TopicHeader=topic_header
        )
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "SavePageAsDraft", None, payload, "pageStream", return_type)
        self.context.add_query(qry)
        return return_type

    def save_page_as_template(self) -> "SitePage":
        """ """
        return_type = SitePage(self.context)
        qry = ServiceOperationQuery(self, "SavePageAsTemplate", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def save_page_co_auth(self, page_stream):
        """ """
        return_type = ClientResult(self.context, SitePageCoAuthState())
        payload = {"pageStream": page_stream}
        qry = ServiceOperationQuery(self, "SavePageCoAuth", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def demote_from_news(self):
        """
        Updates the promoted state of the site page to 0. On success MUST return true.
        If the site page already has promoted state as 0, MUST return true. If the site page is not checked out
        to the current user,
        the server MUST throw Microsoft.SharePoint.Client.ClientServiceException with ErrorInformation.HttpStatusCode
        set to 409.
        """
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "DemoteFromNews", None, None, None, result)
        self.context.add_query(qry)
        return result

    def promote_to_news(self):
        """
        Updates the promoted state of the site page to 1 if the site page has not been published yet.
        Updates the promoted state of the site page to 2 if the site page has already been published.
        If the site page already has promoted state set to 1 or 2, MUST return true.
        If the site page is not checked out to the current users,
        the server MUST throw Microsoft.SharePoint.Client.ClientServiceException with ErrorInformation.HttpStatusCode
        set to 409.
        """
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "PromoteToNews", None, None, None, result)
        self.context.add_query(qry)
        return result

    def publish(self) -> ClientResult[bool]:
        """
        Publishes a major version of the current Site Page.  Returns TRUE on success, FALSE otherwise.
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "Publish", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def schedule_publish(self, publish_start_date):
        """Schedules the page publication for a certain date

        Args:
            publish_start_date (datetime.datetime): The pending publication scheduled date
        """
        payload = SitePageFieldsData(PublishStartDate=publish_start_date.isoformat())
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "SchedulePublish", None, payload, "sitePage", result)
        self.context.add_query(qry)
        return result

    def share_page_preview_by_email(self, message: str, recipient_emails: list[str]) -> Self:
        """Args:
        message (str):
        recipient_emails (list[str]):
        """
        payload = SharePagePreviewByEmailFieldsData(message, recipient_emails)
        qry = ServiceOperationQuery(self, "SharePagePreviewByEmail", None, payload)
        self.context.add_query(qry)
        return self

    def start_co_auth(self):
        """"""
        return_type = SitePage(self.context, self.resource_path)
        qry = ServiceOperationQuery(self, "StartCoAuth", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def canvas_content(self) -> Optional[str]:
        """Gets the CanvasContent1 for the current Site Page"""
        return self.properties.get("CanvasContent1", None)

    @property
    def language(self) -> Optional[str]:
        """Gets the Language for the Site Page."""
        return self.properties.get("Language", None)

    @canvas_content.setter
    def canvas_content(self, value: str) -> None:
        """Sets the CanvasContent1 for the current Site Page"""
        self.set_property("CanvasContent1", value)

    @property
    def layout_web_parts_content(self) -> Optional[str]:
        """Gets the LayoutWebPartsContent field for the current Site Page."""
        return self.properties.get("LayoutWebpartsContent", None)

    @layout_web_parts_content.setter
    def layout_web_parts_content(self, value: str) -> None:
        """Sets the LayoutWebPartsContent field for the current Site Page."""
        self.set_property("LayoutWebpartsContent", value)

    @property
    def translations(self) -> TranslationStatusCollection:
        return self.properties.get(
            "Translations", TranslationStatusCollection(self.context, ResourcePath("Translations", self.resource_path))
        )

    AbsoluteUrl: str | None = None
    BannerImageUrl: str | None = None
    BannerThumbnailUrl: str | None = None
    Description: str | None = None
    ID: str | None = None
    Title: str | None = None
    UniqueId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "SP.Publishing.SitePage"

    @property
    def alternative_url_map(self) -> Optional[str]:
        """Gets the AlternativeUrlMap property"""
        return self.properties.get("AlternativeUrlMap", None)

    @property
    def amplify_publishing_history(self) -> AmplifyPublishingHistory:
        """Gets the AmplifyPublishingHistory property"""
        return self.properties.get("AmplifyPublishingHistory", AmplifyPublishingHistory())

    @property
    def authoring_metadata(self) -> SitePageAuthoringMetadata:
        """Gets the AuthoringMetadata property"""
        return self.properties.get("AuthoringMetadata", SitePageAuthoringMetadata())

    @property
    def boost_properties(self) -> SitePageBoostProperties:
        """Gets the BoostProperties property"""
        return self.properties.get("BoostProperties", SitePageBoostProperties())

    @property
    def campaign_metadata(self) -> Optional[str]:
        """Gets the CampaignMetadata property"""
        return self.properties.get("CampaignMetadata", None)

    @property
    def canvas_content1(self) -> Optional[str]:
        """Gets the CanvasContent1 property"""
        return self.properties.get("CanvasContent1", None)

    @property
    def canvas_json1(self) -> Optional[str]:
        """Gets the CanvasJson1 property"""
        return self.properties.get("CanvasJson1", None)

    @property
    def web_part_count(self) -> int:
        """Gets the number of client-side web parts serialized in the page canvas."""
        return count_web_parts(self.canvas_content1)

    @property
    def check_in(self) -> Optional[bool]:
        """Gets the CheckIn property"""
        return self.properties.get("CheckIn", None)

    @property
    def co_auth_state(self) -> SitePageCoAuthState:
        """Gets the CoAuthState property"""
        return self.properties.get("CoAuthState", SitePageCoAuthState())

    @property
    def co_auth_tenant_configuration(self) -> CoAuthConfiguration:
        """Gets the CoAuthTenantConfiguration property"""
        return self.properties.get("CoAuthTenantConfiguration", CoAuthConfiguration())

    @property
    def collaborators(self) -> ClientValueCollection[SitePageCollaborator]:
        """Gets the Collaborators property"""
        return self.properties.get("Collaborators", ClientValueCollection[SitePageCollaborator](SitePageCollaborator))

    @property
    def creation_mode(self) -> Optional[int]:
        """Gets the CreationMode property"""
        return self.properties.get("CreationMode", None)

    @property
    def is_liked_by_current_user(self) -> Optional[bool]:
        """Gets the IsLikedByCurrentUser property"""
        return self.properties.get("IsLikedByCurrentUser", None)

    @property
    def is_template(self) -> Optional[bool]:
        """Gets the IsTemplate property"""
        return self.properties.get("IsTemplate", None)

    @property
    def layout_webparts_content(self) -> Optional[str]:
        """Gets the LayoutWebpartsContent property"""
        return self.properties.get("LayoutWebpartsContent", None)

    @property
    def name(self) -> Optional[str]:
        """Gets the Name property"""
        return self.properties.get("Name", None)

    @property
    def publication_metadata(self) -> Optional[str]:
        """Gets the PublicationMetadata property"""
        return self.properties.get("PublicationMetadata", None)

    @property
    def publication_recipients(self) -> Optional[str]:
        """Gets the PublicationRecipients property"""
        return self.properties.get("PublicationRecipients", None)

    @property
    def site_page_flags(self) -> Optional[str]:
        """Gets the SitePageFlags property"""
        return self.properties.get("SitePageFlags", None)

    @property
    def source_dynamic_section_id(self) -> Optional[str]:
        """Gets the SourceDynamicSectionId property"""
        return self.properties.get("SourceDynamicSectionId", None)

    @property
    def template_scope(self) -> Optional[int]:
        """Gets the TemplateScope property"""
        return self.properties.get("TemplateScope", None)

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
