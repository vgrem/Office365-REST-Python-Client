from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional, Union

from typing_extensions import Self

from office365.directory.permissions.identity_set import IdentitySet
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.onedrive.analytics.item_activity_stat import ItemActivityStat
from office365.onedrive.analytics.item_analytics import ItemAnalytics
from office365.onedrive.base_item import BaseItem
from office365.onedrive.columns.definition_collection import ColumnDefinitionCollection
from office365.onedrive.contenttypes.collection import ContentTypeCollection
from office365.onedrive.drives.drive import Drive
from office365.onedrive.listitems.list_item import ListItem
from office365.onedrive.lists.collection import ListCollection
from office365.onedrive.lists.list import List
from office365.onedrive.operations.rich_long_running import RichLongRunningOperation
from office365.onedrive.permissions.collection import PermissionCollection
from office365.onedrive.permissions.permission import Permission
from office365.onedrive.root import Root
from office365.onedrive.sharepoint.ids import SharePointIds
from office365.onedrive.sitepages.collection import SitePageCollection
from office365.onedrive.sites.collection import SiteCollection
from office365.onedrive.termstore.store import Store
from office365.onenote.onenote import Onenote
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.directory.applications.application import Application
    from office365.directory.serviceprincipals.service_principal import ServicePrincipal
    from office365.runtime.types.public_error import PublicError


def _permission_identity_ids(permission: Permission) -> set[str]:
    """The object IDs of every principal a site permission was granted to."""
    identity_sets: list[IdentitySet] = [permission.granted_to_v2, permission.granted_to]
    identity_sets += list(permission.granted_to_identities_v2)
    identity_sets += list(permission.granted_to_identities)
    ids: set[str] = set()
    for identity_set in identity_sets:
        for _, identity in identity_set:
            principal_id = getattr(identity, "id", None)
            if principal_id:
                ids.add(principal_id)
    return ids


class Site(BaseItem):
    """The site resource provides metadata and relationships for a SharePoint site."""

    def __str__(self):
        return self.display_name or self.name or self.entity_type_name

    def __repr__(self):
        return self.name or self.web_url or self.id or self.entity_type_name

    def get_by_path(self, path: str) -> Site:
        """
        Retrieve properties and relationships for a site resource. A site resource represents a team site in SharePoint.

            In addition to retrieving a site by ID you can retrieve a site based on server-relative URL path.

            Site collection hostname (contoso.sharepoint.com)
            Site path, relative to server hostname.
            There is also a reserved site identifier, root, which always references the root site for a given target,
            as follows:

            /sites/root: The tenant root site.
            /groups/{group-id}/sites/root: The group's team site.
        """
        return_type = Site(self.context)
        qry = ServiceOperationQuery(self, "GetByPath", [path], None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_applicable_content_types_for_list(self, list_or_id: Union[List, str]) -> ContentTypeCollection:
        """Get site contentTypes that can be added to a list.

        Args:
            list_or_id (str|List): GUID of the list for which the applicable content types need to be fetched.
        """
        return_type = ContentTypeCollection(self.context, self.content_types.resource_path)

        def _get_applicable_content_types_for_list(list_id: str | None) -> None:
            if list_id is None:
                return
            params = {"listId": list_id}
            qry = FunctionQuery(self, "getApplicableContentTypesForList", params, return_type)
            self.context.add_query(qry)

        if isinstance(list_or_id, List):
            list_or_id.ensure_property("id").after_execute(
                lambda _: _get_applicable_content_types_for_list(list_or_id.id)
            )
        else:
            _get_applicable_content_types_for_list(list_or_id)
        return return_type

    def get_activities_by_interval(
        self, start_dt: datetime | None = None, end_dt: datetime | None = None, interval: str | None = None
    ) -> EntityCollection[ItemActivityStat]:
        """Get a collection of itemActivityStats resources for the activities that took place on this resource
        within the specified time interval.

        Args:
            start_dt (datetime.datetime): The start time over which to aggregate activities.
            end_dt (datetime.datetime): The end time over which to aggregate activities.
            interval (str): The aggregation interval.
        """
        params = {
            "startDateTime": start_dt.strftime("%m-%d-%Y") if start_dt else None,
            "endDateTime": end_dt.strftime("%m-%d-%Y") if end_dt else None,
            "interval": interval,
        }
        return_type = EntityCollection(self.context, ItemActivityStat)
        qry = FunctionQuery(self, "getActivitiesByInterval", params, return_type)
        self.context.add_query(qry)
        return return_type

    def _app_service_principal(self, app: Application | str) -> ServicePrincipal:
        """Resolve an ``Application`` entity or application (client) ID to its service principal.

        The service principal is returned *deferred*; it is loaded lazily when the
        grant/revoke query runs.
        """
        app_id = app if isinstance(app, str) else app.app_id
        if not app_id:
            raise ValueError("An application (client) ID is required to resolve the service principal.")
        return self.context.service_principals.get_by_app_id(app_id)

    def grant_access(
        self, identity: Union[Entity, str], roles: Union[str, list[str]], identity_type: str | None = None
    ) -> Permission:
        """Grant a principal (user, group, or application) access to this site.

        A thin, discoverable wrapper around
        :meth:`~office365.onedrive.permissions.collection.PermissionCollection.add`,
        so callers can read ``site.grant_access(sp, "write")``. The request is
        queued and sent on ``execute_query``.

        An :class:`~office365.directory.applications.application.Application` is
        resolved to its **service principal** first, because site permissions
        reference the service principal object ID (not the application object ID).
        To pass an application (client) ID as a string, use :meth:`grant_app_access`.

        Args:
            identity: A loaded principal (for example a
                :class:`~office365.directory.serviceprincipals.ServicePrincipal`
                or an :class:`~office365.directory.applications.application.Application`),
                or the **object ID** of the principal.
            roles: A role (``"read"``, ``"write"``, ``"owner"``) or a list of roles.
            identity_type: Required only when ``identity`` is a string object ID
                (for example ``"application"``); inferred from an entity.

        Returns:
            The created :class:`~office365.onedrive.permissions.permission.Permission`.
        """
        from office365.directory.applications.application import Application

        if isinstance(identity, Application):
            identity = self._app_service_principal(identity)
        role_list = [roles] if isinstance(roles, str) else list(roles)
        return self.permissions.add(roles=role_list, identity=identity, identity_type=identity_type)

    def grant_app_access(self, app: Application | str, roles: Union[str, list[str]]) -> Permission:
        """Grant a registered application access to this site.

        Accepts an :class:`~office365.directory.applications.application.Application`
        entity or an application (client) ID string and resolves the matching
        **service principal** internally, so callers do not have to look it up::

            site.grant_app_access(OFFICE365_CLIENT_ID, "write").execute_query()

        Args:
            app: An ``Application`` entity or its application (client) ID.
            roles: A role (``"read"``, ``"write"``, ``"owner"``) or a list of roles.

        Returns:
            The created :class:`~office365.onedrive.permissions.permission.Permission`.
        """
        return self.grant_access(self._app_service_principal(app), roles)

    def revoke_access(self, identity: Union[Entity, str]) -> Self:
        """Revoke the access previously granted to a principal on this site.

        Loads the site permissions and deletes every entry whose grantee matches
        ``identity`` by object ID. The requests are queued and sent on
        ``execute_query``. An entity identity is loaded first, so a deferred
        principal (for example a freshly addressed service principal) works too.

        Args:
            identity: A loaded principal or its object ID.

        Returns:
            Self: The site instance for method chaining.
        """

        def _revoke(permissions: PermissionCollection) -> None:
            identity_id = identity.id if isinstance(identity, Entity) else identity
            for permission in permissions:
                if identity_id in _permission_identity_ids(permission):
                    permission.delete_object()

        def _load_permissions() -> None:
            self.permissions.get().after_execute(_revoke)

        if isinstance(identity, Entity):
            identity.ensure_properties(["id", "displayName"]).after_execute(lambda _: _load_permissions())
        else:
            _load_permissions()
        return self

    def revoke_app_access(self, app: Application | str) -> Self:
        """Revoke the access previously granted to a registered application.

        Accepts an :class:`~office365.directory.applications.application.Application`
        entity or an application (client) ID string and resolves the matching
        service principal internally.

        Args:
            app: An ``Application`` entity or its application (client) ID.

        Returns:
            Self: The site instance for method chaining.
        """
        return self.revoke_access(self._app_service_principal(app))

    @odata(name="siteCollection")
    @property
    def site_collection(self) -> SiteCollection:
        """Provides details about the site's site collection. Available only on the root site."""
        return self.properties.get("siteCollection", SiteCollection())

    @odata(name="sharepointIds")
    @property
    def sharepoint_ids(self) -> SharePointIds:
        """Returns identifiers useful for SharePoint REST compatibility."""
        return self.properties.get("sharepointIds", SharePointIds())

    @property
    def items(self) -> EntityCollection[ListItem]:
        """Used to address any item contained in this site. This collection cannot be enumerated."""
        return self.properties.get(
            "items", EntityCollection(self.context, ListItem, ResourcePath("items", self.resource_path))
        )

    @property
    def columns(self) -> ColumnDefinitionCollection:
        """The collection of columns under this site."""
        return self.properties.get(
            "columns", ColumnDefinitionCollection(self.context, ResourcePath("columns", self.resource_path), self)
        )

    @odata(name="externalColumns")
    @property
    def external_columns(self) -> ColumnDefinitionCollection:
        """The collection of columns under this site."""
        return self.properties.get(
            "externalColumns",
            ColumnDefinitionCollection(self.context, ResourcePath("externalColumns", self.resource_path), self),
        )

    @odata(name="contentTypes")
    @property
    def content_types(self) -> ContentTypeCollection:
        """The collection of content types under this site."""
        return self.properties.get(
            "contentTypes", ContentTypeCollection(self.context, ResourcePath("contentTypes", self.resource_path))
        )

    @property
    def lists(self) -> ListCollection:
        """The collection of lists under this site."""
        return self.properties.get("lists", ListCollection(self.context, ResourcePath("lists", self.resource_path)))

    @property
    def operations(self) -> EntityCollection[RichLongRunningOperation]:
        """The collection of long-running operations on the site."""
        return self.properties.get(
            "operations",
            EntityCollection(self.context, RichLongRunningOperation, ResourcePath("operations", self.resource_path)),
        )

    @property
    def permissions(self) -> PermissionCollection:
        """The permissions associated with the site."""
        return self.properties.get(
            "permissions", PermissionCollection(self.context, ResourcePath("permissions", self.resource_path))
        )

    @property
    def drive(self) -> Drive:
        """The default drive (document library) for this site."""
        return self.properties.get("drive", Drive(self.context, ResourcePath("drive", self.resource_path)))

    @property
    def drives(self) -> EntityCollection[Drive]:
        """The collection of drives under this site."""
        return self.properties.get(
            "drives", EntityCollection(self.context, Drive, ResourcePath("drives", self.resource_path), self)
        )

    @property
    def sites(self) -> EntityCollection[Site]:
        """The collection of sites under this site."""
        return self.properties.get(
            "sites", EntityCollection(self.context, Site, ResourcePath("sites", self.resource_path))
        )

    @property
    def analytics(self) -> ItemAnalytics:
        """Analytics about the view activities that took place on this site."""
        return self.properties.get(
            "analytics", ItemAnalytics(self.context, ResourcePath("analytics", self.resource_path))
        )

    @property
    def onenote(self) -> Onenote:
        """Represents the Onenote services available to a site."""
        return self.properties.get("onenote", Onenote(self.context, ResourcePath("onenote", self.resource_path)))

    @property
    def pages(self) -> SitePageCollection:
        """The collection of site pages under this site."""
        return self.properties.get(
            "pages", SitePageCollection(self.context, ResourcePath("pages", self.resource_path), self.pages_list)
        )

    @property
    def pages_list(self) -> List:
        """The list that contains the site pages."""
        return self.lists.get_by_name("Site Pages")

    @odata(name="termStore")
    @property
    def term_store(self) -> Store:
        """The default termStore under this site."""
        return self.properties.get("termStore", Store(self.context, ResourcePath("termStore", self.resource_path)))

    @odata(name="termStores")
    @property
    def term_stores(self) -> EntityCollection[Store]:
        """The collection of termStores under this site."""
        return self.properties.get(
            "termStores", EntityCollection(self.context, Store, ResourcePath("termStores", self.resource_path))
        )

    @property
    def display_name(self) -> str:
        """Gets the displayName property"""
        return self.properties.get("displayName", "")

    @property
    def is_personal_site(self) -> Optional[bool]:
        """Gets the isPersonalSite property"""
        return self.properties.get("isPersonalSite", None)

    @property
    def root(self) -> Root:
        """Gets the root property"""
        return self.properties.get("root", Root())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Site"

    @property
    def error(self) -> PublicError:
        """Gets the error property"""
        from office365.runtime.types.public_error import PublicError

        return self.properties.get("error", PublicError())
