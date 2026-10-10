from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.publishing.amplify.clientamplifyanywhereresults import (
    ClientAmplifyAnywhereResults,
)
from office365.sharepoint.publishing.amplify.clientamplifyresults import (
    ClientAmplifyResults,
)
from office365.sharepoint.publishing.amplify.history import AmplifyPublishingHistory
from office365.sharepoint.publishing.amplify.requestparams import AmplifyRequestParams
from office365.sharepoint.publishing.approval.requestcreationinfo import (
    ApprovalRequestCreationInfo,
)
from office365.sharepoint.publishing.approval.requestresponse import (
    ApprovalRequestResponse,
)
from office365.sharepoint.publishing.boostfieldsdata import BoostFieldsData
from office365.sharepoint.publishing.campaign.loadmaildraftparam import (
    CampaignPublicationLoadMailDraftParam,
)
from office365.sharepoint.publishing.campaign.resetendpointparam import (
    CampaignPublicationResetEndpointParam,
)
from office365.sharepoint.publishing.campaign.savemaildraftparam import (
    CampaignPublicationSaveMailDraftParam,
)
from office365.sharepoint.publishing.highlights_info import HighlightsInfo
from office365.sharepoint.publishing.missingsharepointdestinationwebidrepairitem import (
    MissingSharePointDestinationWebIdRepairItem,
)
from office365.sharepoint.publishing.pages.campaign.maildraftdata import (
    CampaignPublicationMailDraftData,
)
from office365.sharepoint.publishing.pages.coauth_state import SitePageCoAuthState
from office365.sharepoint.publishing.pages.dependency_metadata import (
    SitePageDependencyMetadata,
)
from office365.sharepoint.publishing.pages.page import SitePage
from office365.sharepoint.publishing.pages.schedulepublicationresponse import (
    SchedulePublicationResponse,
)
from office365.sharepoint.publishing.pages.sendtestemailresponse import (
    SendTestEmailResponse,
)
from office365.sharepoint.publishing.pages.sendtestteamsmessageresponse import (
    SendTestTeamsMessageResponse,
)
from office365.sharepoint.publishing.pages.versioninfocollection import (
    SitePageVersionInfoCollection,
)
from office365.sharepoint.publishing.publishpublicationresponse import (
    PublishPublicationResponse,
)
from office365.sharepoint.publishing.sitepageauthoringmetadata import (
    SitePageAuthoringMetadata,
)
from office365.sharepoint.publishing.statusresponse import PublishingStatusResponse
from office365.sharepoint.publishing.validations.response import (
    PrePublishValidationsResponse,
)


class CampaignPublication(SitePage):
    """ """

    def get_highlights_info(self):
        """ """
        return_type = HighlightsInfo(self.context)
        qry = ServiceOperationQuery(self, "GetHighlightsInfo", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def email_endpoint(self) -> Optional[str]:
        """"""
        return self.properties.get("EmailEndpoint", None)

    @property
    def entity_type_name(self):
        return "SP.Publishing.CampaignPublication"

    @property
    def publication_status(self) -> Optional[int]:
        """Gets the PublicationStatus property"""
        return self.properties.get("PublicationStatus", None)

    @property
    def share_point_endpoint(self) -> Optional[str]:
        """Gets the SharePointEndpoint property"""
        return self.properties.get("SharePointEndpoint", None)

    @property
    def teams_endpoint(self) -> Optional[str]:
        """Gets the TeamsEndpoint property"""
        return self.properties.get("TeamsEndpoint", None)

    @property
    def viva_engage_endpoint(self) -> Optional[str]:
        """Gets the VivaEngageEndpoint property"""
        return self.properties.get("VivaEngageEndpoint", None)

    @property
    def yammer_endpoint(self) -> Optional[str]:
        """Gets the YammerEndpoint property"""
        return self.properties.get("YammerEndpoint", None)

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

    def delete(self) -> Self:
        """Delete operation."""
        qry = ServiceOperationQuery(self, "Delete", None, {}, None, None)
        self.context.add_query(qry)
        return self

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

    def amplify_cancel_schedule(self) -> ClientResult[ClientAmplifyResults]:
        """AmplifyCancelSchedule operation."""
        return_type = ClientResult(self.context, ClientAmplifyResults())
        qry = ServiceOperationQuery(self, "AmplifyCancelSchedule", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def amplify_publish(self) -> ClientResult[ClientAmplifyResults]:
        """AmplifyPublish operation."""
        return_type = ClientResult(self.context, ClientAmplifyResults())
        qry = ServiceOperationQuery(self, "AmplifyPublish", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def amplify_schedule(self, publish_start_date: datetime) -> ClientResult[ClientAmplifyResults]:
        """AmplifySchedule operation.

        Args:
            publish_start_date (datetime): publishStartDate parameter
        """
        return_type = ClientResult(self.context, ClientAmplifyResults())
        qry = ServiceOperationQuery(
            self, "AmplifySchedule", None, {"publishStartDate": publish_start_date}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def amplify_validate(self) -> ClientResult[ClientAmplifyResults]:
        """AmplifyValidate operation."""
        return_type = ClientResult(self.context, ClientAmplifyResults())
        qry = ServiceOperationQuery(self, "AmplifyValidate", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def approve_approval_request(self, comment: str) -> ClientResult[ApprovalRequestResponse]:
        """ApproveApprovalRequest operation.

        Args:
            comment (str): comment parameter
        """
        return_type = ClientResult(self.context, ApprovalRequestResponse())
        qry = ServiceOperationQuery(self, "ApproveApprovalRequest", None, {"comment": comment}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def cancel_approval_request(self) -> ClientResult[ApprovalRequestResponse]:
        """CancelApprovalRequest operation."""
        return_type = ClientResult(self.context, ApprovalRequestResponse())
        qry = ServiceOperationQuery(self, "CancelApprovalRequest", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def cancel_schedule_publication(self) -> ClientResult[SchedulePublicationResponse]:
        """CancelSchedulePublication operation."""
        return_type = ClientResult(self.context, SchedulePublicationResponse())
        qry = ServiceOperationQuery(self, "CancelSchedulePublication", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def create_approval_request(
        self, creation_info: ApprovalRequestCreationInfo
    ) -> ClientResult[ApprovalRequestResponse]:
        """CreateApprovalRequest operation.

        Args:
            creation_info (ApprovalRequestCreationInfo): creationInfo parameter
        """
        return_type = ClientResult(self.context, ApprovalRequestResponse())
        qry = ServiceOperationQuery(
            self, "CreateApprovalRequest", None, {"creationInfo": creation_info}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def delete_publication(self) -> ClientResult[UUID]:
        """DeletePublication operation."""
        return_type = ClientResult(self.context, uuid.UUID(int=0))
        qry = ServiceOperationQuery(self, "DeletePublication", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_pre_publish_validation_status(self) -> ClientResult[PrePublishValidationsResponse]:
        """GetPrePublishValidationStatus operation."""
        return_type = ClientResult(self.context, PrePublishValidationsResponse())
        qry = FunctionQuery(self, "GetPrePublishValidationStatus", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_publishing_status(self) -> ClientResult[PublishingStatusResponse]:
        """GetPublishingStatus operation."""
        return_type = ClientResult(self.context, PublishingStatusResponse())
        qry = FunctionQuery(self, "GetPublishingStatus", [], return_type)
        self.context.add_query(qry)
        return return_type

    def load_mail_draft(
        self, request_param: CampaignPublicationLoadMailDraftParam
    ) -> ClientResult[CampaignPublicationMailDraftData]:
        """LoadMailDraft operation.

        Args:
            request_param (CampaignPublicationLoadMailDraftParam): requestParam parameter
        """
        return_type = ClientResult(self.context, CampaignPublicationMailDraftData())
        qry = ServiceOperationQuery(self, "LoadMailDraft", None, {"requestParam": request_param}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def publish_as_bot(
        self, tenant_id: str, channel_ids: list[str], content: str, title: str, headline: str
    ) -> ClientResult[str]:
        """PublishAsBot operation.

        Args:
            tenant_id (str): tenantId parameter
            channel_ids (list[str]): channelIds parameter
            content (str): content parameter
            title (str): title parameter
            headline (str): headline parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self,
            "PublishAsBot",
            None,
            {
                "tenantId": tenant_id,
                "channelIds": StringCollection(channel_ids),
                "content": content,
                "title": title,
                "headline": headline,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def publish_publication(self) -> ClientResult[PublishPublicationResponse]:
        """PublishPublication operation."""
        return_type = ClientResult(self.context, PublishPublicationResponse())
        qry = ServiceOperationQuery(self, "PublishPublication", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def reject_approval_request(self, comment: str) -> ClientResult[ApprovalRequestResponse]:
        """RejectApprovalRequest operation.

        Args:
            comment (str): comment parameter
        """
        return_type = ClientResult(self.context, ApprovalRequestResponse())
        qry = ServiceOperationQuery(self, "RejectApprovalRequest", None, {"comment": comment}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def repair_missing_share_point_destination_web_ids(
        self, repair_items: ClientValueCollection[MissingSharePointDestinationWebIdRepairItem]
    ) -> Self:
        """RepairMissingSharePointDestinationWebIds operation.

        Args:
            repair_items (ClientValueCollection[MissingSharePointDestinationWebIdRepairItem]): repairItems parameter
        """
        qry = ServiceOperationQuery(
            self, "RepairMissingSharePointDestinationWebIds", None, {"repairItems": repair_items}, None, None
        )
        self.context.add_query(qry)
        return self

    def reset_endpoint(self, request_param: CampaignPublicationResetEndpointParam) -> ClientResult[bool]:
        """ResetEndpoint operation.

        Args:
            request_param (CampaignPublicationResetEndpointParam): requestParam parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "ResetEndpoint", None, {"requestParam": request_param}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def save_mail_draft(
        self, request_param: CampaignPublicationSaveMailDraftParam
    ) -> ClientResult[CampaignPublicationMailDraftData]:
        """SaveMailDraft operation.

        Args:
            request_param (CampaignPublicationSaveMailDraftParam): requestParam parameter
        """
        return_type = ClientResult(self.context, CampaignPublicationMailDraftData())
        qry = ServiceOperationQuery(self, "SaveMailDraft", None, {"requestParam": request_param}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def schedule_publication(self, publish_start_date: datetime) -> ClientResult[SchedulePublicationResponse]:
        """SchedulePublication operation.

        Args:
            publish_start_date (datetime): publishStartDate parameter
        """
        return_type = ClientResult(self.context, SchedulePublicationResponse())
        qry = ServiceOperationQuery(
            self, "SchedulePublication", None, {"publishStartDate": publish_start_date}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def sp_site_validator(self, site_url: str) -> ClientResult[ClientValueCollection[int]]:
        """SPSiteValidator operation.

        Args:
            site_url (str): siteUrl parameter
        """
        return_type = ClientResult(self.context, ClientValueCollection(int))
        qry = ServiceOperationQuery(self, "SPSiteValidator", None, {"siteUrl": site_url}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def update_share_point_publishing_status(
        self,
        destination_site_id: str,
        destination_url: str,
        share_point_publishing_status: int,
        share_point_publishing_error_code: int,
    ) -> ClientResult[bool]:
        """UpdateSharePointPublishingStatus operation.

        Args:
            destination_site_id (str): destinationSiteId parameter
            destination_url (str): destinationUrl parameter
            share_point_publishing_status (int): sharePointPublishingStatus parameter
            share_point_publishing_error_code (int): sharePointPublishingErrorCode parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(
            self,
            "UpdateSharePointPublishingStatus",
            None,
            {
                "destinationSiteId": destination_site_id,
                "destinationUrl": destination_url,
                "sharePointPublishingStatus": share_point_publishing_status,
                "sharePointPublishingErrorCode": share_point_publishing_error_code,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    @property
    def sharepoint_endpoint(self) -> Optional[str]:
        """Gets the SharePointEndpoint property"""
        return self.properties.get("SharePointEndpoint", None)

    def repair_missing_sharepoint_destination_web_ids(
        self, repair_items: ClientValueCollection[MissingSharePointDestinationWebIdRepairItem]
    ) -> Self:
        """RepairMissingSharePointDestinationWebIds operation.

        Args:
            repair_items (ClientValueCollection[MissingSharePointDestinationWebIdRepairItem]):
                repairItems parameter
        """
        qry = ServiceOperationQuery(
            self, "RepairMissingSharePointDestinationWebIds", None, {"repairItems": repair_items}, None, None
        )
        self.context.add_query(qry)
        return self

    def update_sharepoint_publishing_status(
        self,
        destination_site_id: str,
        destination_url: str,
        sharepoint_publishing_status: int,
        sharepoint_publishing_error_code: int,
    ) -> ClientResult[bool]:
        """UpdateSharePointPublishingStatus operation.

        Args:
            destination_site_id (str):
                destinationSiteId parameter
            destination_url (str):
                destinationUrl parameter
            sharepoint_publishing_status (int):
                sharePointPublishingStatus parameter
            sharepoint_publishing_error_code (int):
                sharePointPublishingErrorCode parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(
            self,
            "UpdateSharePointPublishingStatus",
            None,
            {
                "destinationSiteId": destination_site_id,
                "destinationUrl": destination_url,
                "sharePointPublishingStatus": sharepoint_publishing_status,
                "sharePointPublishingErrorCode": sharepoint_publishing_error_code,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type
