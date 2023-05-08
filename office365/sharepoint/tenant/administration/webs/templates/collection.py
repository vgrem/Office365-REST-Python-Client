from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.tenant.administration.webs.templates.template import SPOTenantWebTemplate


class SPOTenantWebTemplateCollection(BaseEntity):

    @property
    def items(self):
        return self.properties.get("Items", ClientValueCollection(SPOTenantWebTemplate))
