from office365.sharepoint.activities.action_facet import ActionFacet
from office365.sharepoint.base_entity import BaseEntity


class SPActivityEntity(BaseEntity):

    @property
    def action(self):
        return self.properties.get("action", ActionFacet())

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Activities.SPActivityEntity"
