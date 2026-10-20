from office365.entity import Entity
from office365.outlook.categories.collection import OutlookCategoryCollection
from office365.outlook.locale_info import LocaleInfo
from office365.outlook.timezones.information import TimeZoneInformation
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.types.odata_property import odata


class OutlookUser(Entity):
    """Represents the Outlook services available to a user."""

    @odata(name="supportedLanguages")
    def supported_languages(self) -> ClientResult[ClientValueCollection[LocaleInfo]]:
        """
        Get the list of locales and languages that are supported for the user, as configured on the user's
        mailbox server. When setting up an Outlook client, the user selects the preferred language from this supported
        list. You can subsequently get the preferred language by getting the user's mailbox settings.
        """
        return_type = ClientResult(self.context, ClientValueCollection(LocaleInfo))
        qry = FunctionQuery(self, "supportedLanguages", None, return_type)
        self.context.add_query(qry)
        return return_type

    @odata(name="supportedTimeZones")
    def supported_time_zones(self) -> ClientResult[ClientValueCollection[TimeZoneInformation]]:
        """
        Get the list of time zones that are supported for the user, as configured on the user's mailbox server.
        You can explicitly specify to have time zones returned in the Windows time zone format or
        Internet Assigned Numbers Authority (IANA) time zone (also known as Olson time zone) format.
        The Windows format is the default.
        When setting up an Outlook client, the user selects the preferred time zone from this supported list.
        You can subsequently get the preferred time zone by getting the user's mailbox settings.
        """
        return_type = ClientResult(self.context, ClientValueCollection(TimeZoneInformation))
        qry = FunctionQuery(self, "supportedTimeZones", None, return_type)
        self.context.add_query(qry)
        return return_type

    @odata(name="masterCategories", navigation=True)
    @property
    def master_categories(self) -> OutlookCategoryCollection:
        """A list of categories defined for the user."""
        return self.properties.get(
            "masterCategories",
            OutlookCategoryCollection(self.context, ResourcePath("masterCategories", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OutlookUser"
