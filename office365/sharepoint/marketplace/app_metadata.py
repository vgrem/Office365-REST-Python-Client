from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity


class CorporateCatalogAppMetadata(BaseEntity):
    """App metadata for apps stored in the corporate catalog."""

    def deploy(self, skip_feature_deployment):
        """This method deploys an app on the app catalog.  It MUST be called in the context of the tenant app
        catalog web or it will fail.

        :param bool skip_feature_deployment: Specifies whether the app can be centrally deployed across the tenant.
        """
        payload = {
            "skipFeatureDeployment": skip_feature_deployment
        }
        qry = ServiceOperationQuery(self, "Deploy", None, payload)
        self.context.add_query(qry)
        return self

    def install(self):
        """This method allows an app which is already deployed to be installed on a web."""
        qry = ServiceOperationQuery(self, "Install")
        self.context.add_query(qry)
        return self

    def uninstall(self):
        """This method uninstalls an app from a web."""
        qry = ServiceOperationQuery(self, "Uninstall")
        self.context.add_query(qry)
        return self

    @property
    def aad_permissions(self):
        """
        :rtype: str
        """
        return self.properties.get("AadPermissions", None)

    @property
    def app_catalog_version(self):
        """The version of the app stored in the corporate catalog.

        :rtype: str
        """
        return self.properties.get("AppCatalogVersion", None)

    @property
    def can_upgrade(self):
        """Whether an existing instance of an app can be upgraded.

        :rtype: bool or None
        """
        return self.properties.get("CanUpgrade", None)

    @property
    def is_client_side_solution(self):
        """Whether the app is a client-side solution.

        :rtype: bool or None
        """
        return self.properties.get("IsClientSideSolution", None)

    @property
    def title(self):
        """The title of the app.

        :rtype: bool or None
        """
        return self.properties.get("Title", None)

    @property
    def id(self):
        """The identifier of the app.

        :rtype: str or None
        """
        return self.properties.get("ID", None)

    @property
    def property_ref_name(self):
        return "AadAppId"

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Marketplace.CorporateCuratedGallery.CorporateCatalogAppMetadata"
