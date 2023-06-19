from office365.runtime.client_result import ClientResult
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.files.file import File
from office365.sharepoint.marketplace.app_metadata import CorporateCatalogAppMetadata
from office365.sharepoint.marketplace.app_metadata_collection import CorporateCatalogAppMetadataCollection
from office365.sharepoint.marketplace.corporatecuratedgallery.app_upgrade_availability import AppUpgradeAvailability
from office365.sharepoint.marketplace.corporatecuratedgallery.teams_package_download import TeamsPackageDownload
from office365.sharepoint.marketplace.sitecollection.appcatalog.allowed_items import \
    SiteCollectionAppCatalogAllowedItems


class TenantCorporateCatalogAccessor(BaseEntity):
    """Accessor for the tenant corporate catalog."""

    def add(self, content, overwrite, url):
        """
        Adds a file to the corporate catalog.

        :param str or bytes content: Specifies the binary content of the file to be added.
        :param bool overwrite: Specifies whether to overwrite an existing file with the same name and in the same
            location as the one being added.
        :param str url: Specifies the URL of the file to be added.
        """
        return_type = File(self.context)
        payload = {
            "Content": content,
            "Overwrite": overwrite,
            "Url": url
        }
        qry = ServiceOperationQuery(self, "Add", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def download_teams_solution(self, _id):
        """
        :param int _id:
        """
        return_type = TeamsPackageDownload(self.context)
        payload = {
            "id": _id
        }
        qry = ServiceOperationQuery(self, "DownloadTeamsSolution", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_app_by_id(self, item_unique_id):
        """
        :param str item_unique_id:
        """
        params = {"itemUniqueId": item_unique_id}
        return CorporateCatalogAppMetadata(self.context,
                                           ServiceOperationPath("GetAppById", params, self.resource_path))

    def is_app_upgrade_available(self, _id):
        """
        :param int _id:
        """
        return_type = ClientResult(self.context, AppUpgradeAvailability())
        payload = {
            "id": _id
        }
        qry = ServiceOperationQuery(self, "IsAppUpgradeAvailable", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def send_app_request_status_notification_email(self, request_guid):
        """
        :param str request_guid:
        """
        qry = ServiceOperationQuery(self, "SendAppRequestStatusNotificationEmail", [request_guid])
        self.context.add_query(qry)
        return self

    @property
    def available_apps(self):
        """Returns the apps available in this corporate catalog."""
        return self.properties.get('AvailableApps',
                                   CorporateCatalogAppMetadataCollection(self.context,
                                                                         ResourcePath("AvailableApps",
                                                                                      self.resource_path)))

    @property
    def site_collection_app_catalogs_sites(self):
        """Returns an accessor to the allow list of site collections allowed to have site collection corporate
        catalogs."""
        return self.properties.get('SiteCollectionAppCatalogsSites',
                                   SiteCollectionAppCatalogAllowedItems(self.context,
                                                                        ResourcePath("SiteCollectionAppCatalogsSites",
                                                                                     self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "AvailableApps": self.available_apps,
                "SiteCollectionAppCatalogsSites": self.site_collection_app_catalogs_sites
            }
            default_value = property_mapping.get(name, None)
        return super(TenantCorporateCatalogAccessor, self).get_property(name, default_value)
