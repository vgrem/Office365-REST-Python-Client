from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import GuidCollection
from office365.sharepoint.entity import Entity
from office365.sharepoint.sites.home.spreference import SPHSiteReference

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext
    from office365.sharepoint.portal.orgnews.sitereference import (
        PortalAndOrgNewsSiteReference,
    )
    from office365.sharepoint.sites.home.details import HomeSitesDetails
    from office365.sharepoint.sites.home.reference import HomeSiteReference
    from office365.sharepoint.viva.targetedsitedetails import TargetedSiteDetails


class SPHSite(Entity):
    def __init__(self, context, resource_path=None):
        """
        A home site represents a SharePoint communication site.
        It brings together news, events, embedded video and conversations, and other resources to deliver an engaging
        experience that reflects your organization's voice, priorities, and brand.
        It also allows your users to search for content (such as sites, news, and files) across your organization
        """
        if resource_path is None:
            resource_path = ResourcePath("SP.SPHSite")
        super().__init__(context, resource_path)

    def details(self) -> ClientResult[SPHSiteReference]:
        return_type = ClientResult(self.context, SPHSiteReference())
        qry = ServiceOperationQuery(self, "Details", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    @staticmethod
    def is_comm_site(context, site_url, return_value=None):
        """Determines whether a site is a communication site

        Args:
            context (office365.sharepoint.client_context.ClientContext):
            site_url (str): URL of the site to return status for
            return_value (ClientResult):
        """
        if return_value is None:
            return_value = ClientResult(context)
        params = {"siteUrl": site_url}
        qry = ServiceOperationQuery(SPHSite(context), "IsCommSite", params, None, None, return_value, True)
        context.add_query(qry)
        return return_value

    @staticmethod
    def is_modern_site_with_horizontal_nav(context, site_url, return_type=None):
        """Determines whether a site is a modern site with horizontal navigation

        Args:
            context (office365.sharepoint.client_context.ClientContext):
            site_url (str): URL of the site to return status for
            return_type (ClientResult): Return value
        """
        if return_type is None:
            return_type = ClientResult(context)
        params = {"siteUrl": site_url}
        qry = ServiceOperationQuery(
            SPHSite(context),
            "IsModernSiteWithHorizontalNav",
            params,
            None,
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def is_valid_home_site(context, site_url, return_value=None):
        """Determines whether a site is landing site for your intranet.

        Args:
            context (office365.sharepoint.client_context.ClientContext):
            site_url (str): URL of the site to return status for
            return_value (ClientResult):
        """

        if return_value is None:
            return_value = ClientResult(context)
        sph = SPHSite(context)
        params = {"siteUrl": site_url}
        qry = ServiceOperationQuery(sph, "IsValidHomeSite", params, None, None, return_value)
        qry.static = True
        context.add_query(qry)
        return return_value

    @staticmethod
    def validate_home_site(context, site_url, validation_action_type):
        """Args:
        context (office365.sharepoint.client_context.ClientContext):
        site_url (str): URL of the site to return status for
        validation_action_type (int):
        """
        sph = SPHSite(context)
        params = {"siteUrl": site_url, "validationActionType": validation_action_type}
        qry = ServiceOperationQuery(sph, "ValidateHomeSite", params, None, None, None, True)
        context.add_query(qry)
        return sph

    @staticmethod
    def set_as_home_site(
        context, site_url, viva_connections_default_start=None, return_value: ClientResult[str] | None = None
    ):
        """Sets a site as a landing site for your intranet.

        Args:
            return_value (ClientResult):
            context (office365.sharepoint.client_context.ClientContext):
            site_url (str):
            viva_connections_default_start (bool):
        """

        if return_value is None:
            return_value = ClientResult[str](context)
        sph = SPHSite(context)
        params = {
            "siteUrl": site_url,
            "vivaConnectionsDefaultStart": viva_connections_default_start,
        }
        qry = ServiceOperationQuery(sph, "SetSPHSite", None, params, None, return_value)
        context.add_query(qry)
        return return_value

    def add_home_site(
        self,
        site_url: str,
        order: int,
        audiences: list[UUID],
        viva_connections_default_start: bool,
        is_in_draft_mode: bool,
    ) -> ClientResult[TargetedSiteDetails]:
        """AddHomeSite operation.

        Args:
            site_url (str):
                siteUrl parameter
            order (int):
                order parameter
            audiences (list[UUID]):
                audiences parameter
            viva_connections_default_start (bool):
                vivaConnectionsDefaultStart parameter
            is_in_draft_mode (bool):
                isInDraftMode parameter
        """
        from office365.sharepoint.viva.targetedsitedetails import TargetedSiteDetails

        return_type = ClientResult(self.context, TargetedSiteDetails())
        qry = ServiceOperationQuery(
            self,
            "AddHomeSite",
            None,
            {
                "siteUrl": site_url,
                "order": order,
                "audiences": GuidCollection(audiences),
                "vivaConnectionsDefaultStart": viva_connections_default_start,
                "isInDraftMode": is_in_draft_mode,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    @staticmethod
    def add_org_news_site(context: ClientContext, site_url: str) -> ClientResult[UUID]:
        """AddOrgNewsSite operation.

        Args:
            site_url (str):
                siteUrl parameter
        """
        from office365.sharepoint.sites.home.site import SPHSite

        return_type = ClientResult(context, UUID(int=0))
        qry = ServiceOperationQuery(
            SPHSite(context), "AddOrgNewsSite", None, {"siteUrl": site_url}, None, return_type, True
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def add_sp_home_nav_node(context: ClientContext, site_id: UUID) -> ClientResult[bool]:
        """AddSPHomeNavNode operation.

        Args:
            site_id (UUID):
                siteId parameter
        """
        from office365.sharepoint.sites.home.site import SPHSite

        return_type = ClientResult(context, bool())
        qry = ServiceOperationQuery(
            SPHSite(context), "AddSPHomeNavNode", None, {"siteId": site_id}, None, return_type, True
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def assert_site_in_subscription(context: ClientContext, url: str, context_subscription_id: UUID) -> None:
        """AssertSiteInSubscription operation.

        Args:
            url (str):
                url parameter
            context_subscription_id (UUID):
                contextSubscriptionId parameter
        """
        from office365.sharepoint.sites.home.site import SPHSite

        qry = ServiceOperationQuery(
            SPHSite(context),
            "AssertSiteInSubscription",
            None,
            {"url": url, "contextSubscriptionId": context_subscription_id},
            None,
            None,
            True,
        )
        context.add_query(qry)

    @staticmethod
    def get_site_reference_xgeo(context: ClientContext, site_url: str) -> ClientResult[PortalAndOrgNewsSiteReference]:
        """GetSiteReferenceXgeo operation.

        Args:
            site_url (str):
                siteUrl parameter
        """
        from office365.sharepoint.portal.orgnews.sitereference import (
            PortalAndOrgNewsSiteReference,
        )
        from office365.sharepoint.sites.home.site import SPHSite

        return_type = ClientResult(context, PortalAndOrgNewsSiteReference())
        qry = ServiceOperationQuery(
            SPHSite(context), "GetSiteReferenceXgeo", None, {"siteUrl": site_url}, None, return_type, True
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_site_title_xgeo(context: ClientContext, site_url: str) -> ClientResult[str]:
        """GetSiteTitleXgeo operation.

        Args:
            site_url (str):
                siteUrl parameter
        """
        from office365.sharepoint.sites.home.site import SPHSite

        return_type = ClientResult(context, str())
        qry = ServiceOperationQuery(
            SPHSite(context), "GetSiteTitleXgeo", None, {"siteUrl": site_url}, None, return_type, True
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_sph_site_x_geo(context: ClientContext) -> ClientResult[SPHSiteReference]:
        """GetSPHSiteXGeo operation."""
        from office365.sharepoint.sites.home.site import SPHSite
        from office365.sharepoint.sites.home.spreference import SPHSiteReference

        return_type = ClientResult(context, SPHSiteReference())
        qry = ServiceOperationQuery(SPHSite(context), "GetSPHSiteXGeo", None, {}, None, return_type, True)
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_targeted_sites_details_current_user_can_edit_x_geo(
        context: ClientContext, site_ids: list[UUID], stop_redirect: bool
    ) -> ClientResult[ClientValueCollection[TargetedSiteDetails]]:
        """GetTargetedSitesDetailsCurrentUserCanEditXGeo operation.

        Args:
            site_ids (list[UUID]):
                siteIds parameter
            stop_redirect (bool):
                stopRedirect parameter
        """
        from office365.sharepoint.sites.home.site import SPHSite
        from office365.sharepoint.viva.targetedsitedetails import TargetedSiteDetails

        return_type = ClientResult(context, ClientValueCollection[TargetedSiteDetails]())
        qry = ServiceOperationQuery(
            SPHSite(context),
            "GetTargetedSitesDetailsCurrentUserCanEditXGeo",
            None,
            {"siteIds": GuidCollection(site_ids), "stopRedirect": stop_redirect},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_xgeo_home_site_detail(
        context: ClientContext, site_id: UUID, site_url: str
    ) -> ClientResult[HomeSitesDetails]:
        """GetXgeoHomeSiteDetail operation.

        Args:
            site_id (UUID):
                siteId parameter
            site_url (str):
                siteUrl parameter
        """
        from office365.sharepoint.sites.home.details import HomeSitesDetails
        from office365.sharepoint.sites.home.site import SPHSite

        return_type = ClientResult(context, HomeSitesDetails())
        qry = ServiceOperationQuery(
            SPHSite(context),
            "GetXgeoHomeSiteDetail",
            None,
            {"siteId": site_id, "siteUrl": site_url},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def remove_dashboard_feature(context: ClientContext, site_url: str) -> None:
        """RemoveDashboardFeature operation.

        Args:
            site_url (str):
                siteUrl parameter
        """
        from office365.sharepoint.sites.home.site import SPHSite

        qry = ServiceOperationQuery(
            SPHSite(context), "RemoveDashboardFeature", None, {"siteUrl": site_url}, None, None, True
        )
        context.add_query(qry)

    def set_sph_site(
        self, site_url: str, viva_connections_default_start: bool, is_in_draft_mode: bool
    ) -> ClientResult[UUID]:
        """SetSPHSite operation.

        Args:
            site_url (str):
                siteUrl parameter
            viva_connections_default_start (bool):
                vivaConnectionsDefaultStart parameter
            is_in_draft_mode (bool):
                isInDraftMode parameter
        """
        return_type = ClientResult(self.context, UUID(int=0))
        qry = ServiceOperationQuery(
            self,
            "SetSPHSite",
            None,
            {
                "siteUrl": site_url,
                "vivaConnectionsDefaultStart": viva_connections_default_start,
                "isInDraftMode": is_in_draft_mode,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    @staticmethod
    def validate_home_site_candidate(context: ClientContext, site_url: str) -> ClientResult[HomeSiteReference]:
        """ValidateHomeSiteCandidate operation.

        Args:
            site_url (str):
                siteUrl parameter
        """
        from office365.sharepoint.sites.home.reference import HomeSiteReference
        from office365.sharepoint.sites.home.site import SPHSite

        return_type = ClientResult(context, HomeSiteReference())
        qry = ServiceOperationQuery(
            SPHSite(context), "ValidateHomeSiteCandidate", None, {"siteUrl": site_url}, None, return_type, True
        )
        context.add_query(qry)
        return return_type
