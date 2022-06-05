from office365.runtime.client_value import ClientValue
from office365.runtime.types.collections import StringCollection


class SiteScriptCreationInfo(ClientValue):
    pass


class SiteScriptUpdateInfo(SiteScriptCreationInfo):
    pass


class SiteScriptActionResult(ClientValue):

    def __init__(self, outcome_text=None, target=None):
        """
        :param str outcome_text:
        :param str target:
        """
        self.OutcomeText = outcome_text
        self.Target = target

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Utilities.WebTemplateExtensions.SiteScriptActionResult"


class SiteScriptSerializationResult(ClientValue):

    def __init__(self, json=None, warnings=None):
        """
        :param str json:
        :param list[str] warnings:
        """
        self.JSON = json
        self.Warnings = StringCollection(warnings)


class SiteScriptSerializationInfo(ClientValue):

    def __init__(self, include_branding=None, included_lists=None, include_links_to_exported_items=None,
                 include_regional_settings=None, include_site_external_sharing_capability=None, include_theme=None):
        """
        :param bool include_branding:
        :param list[str] included_lists:
        :param bool include_site_external_sharing_capability:
        :param bool include_theme:
        """
        self.IncludeBranding = include_branding
        self.IncludedLists = StringCollection(included_lists)
        self.IncludeLinksToExportedItems = include_links_to_exported_items
        self.IncludeRegionalSettings = include_regional_settings
        self.IncludeSiteExternalSharingCapability = include_site_external_sharing_capability
        self.IncludeTheme = include_theme

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Utilities.WebTemplateExtensions.SiteScriptSerializationInfo"
