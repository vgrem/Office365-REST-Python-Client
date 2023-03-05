from office365.sharepoint.base_entity import BaseEntity


class ComponentContextInfo(BaseEntity):
    """This class functions as a wrapper of the ContextInfo object. Reserved for internal use only."""

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Internal.ClientSideComponent.ComponentContextInfo"
