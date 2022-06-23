from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.outlook.locale_info import LocaleInfo
from office365.outlook.category import OutlookCategory
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery


class OutlookUser(Entity):
    """Represents the Outlook services available to a user."""

    def supported_languages(self):
        """
        Get the list of locales and languages that are supported for the user, as configured on the user's
        mailbox server. When setting up an Outlook client, the user selects the preferred language from this supported
        list. You can subsequently get the preferred language by getting the user's mailbox settings.
        """
        return_type = ClientResult(self.context, ClientValueCollection(LocaleInfo))
        qry = ServiceOperationQuery(self, "supportedLanguages", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def master_categories(self):
        """A list of categories defined for the user."""
        return self.properties.get('masterCategories',
                                   EntityCollection(self.context, OutlookCategory,
                                                    ResourcePath("masterCategories", self.resource_path)))
