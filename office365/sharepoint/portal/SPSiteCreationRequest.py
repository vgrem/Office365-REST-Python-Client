from office365.runtime.client_value_object import ClientValueObject


class SPSiteCreationRequest(ClientValueObject):

    def __init__(self, title, url, owner=None):
        self.Title = title
        self.Url = url
        self.WebTemplate = "SITEPAGEPUBLISHING#0"
        self.Owner = owner
        self.Lcid = 1033
        self.ShareByEmailEnabled = False
        self.Classification = ""
        self.Description = ""
        self.SiteDesignId = "00000000-0000-0000-0000-000000000000"
        self.HubSiteId = "00000000-0000-0000-0000-000000000000"
        self.WebTemplateExtensionId = "00000000-0000-0000-0000-000000000000"

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Portal.SPSiteCreationRequest"
