from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.navigation.configured_metadata_items import ConfiguredMetadataNavigationItemCollection


class MetadataNavigationSettings(BaseEntity):


    @staticmethod
    def get_configured_settings(context, url):
        """
        Retrieves the configured metadata navigation settings for the list with the specified url.


        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        :param str url: Specifies list url
        """

        return_type = ClientResult(context, ConfiguredMetadataNavigationItemCollection())
        payload = {
            "DecodedUrl": url
        }
        qry = ServiceOperationQuery(MetadataNavigationSettings(context), "GetConfiguredSettings", None, payload,
                                    None, return_type, True)
        context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self):
        return "SP.MetadataNavigation.MetadataNavigationSettings"
