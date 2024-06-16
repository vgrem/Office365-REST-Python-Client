from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.entity import Entity
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.multigeo.unified_group import UnifiedGroup


class MultiGeoServices(Entity):
    """
    Multi-Geo capabilities in OneDrive and SharePoint enable control of shared resources like SharePoint team sites
    and Microsoft 365 Group mailboxes stored at rest in a specified geo location.

    Each user, Group mailbox, and SharePoint site have a Preferred Data Location (PDL) which denotes the geo location
    where related data is to be stored. Users' personal data (Exchange mailbox and OneDrive) along with any
    Microsoft 365 Groups or SharePoint sites that they create can be stored in the specified geo location to meet
    data residency requirements.
    """

    @property
    def unified_groups(self):
        # type: () -> EntityCollection[UnifiedGroup]
        """ """
        return self.properties.get(
            "UnifiedGroups",
            EntityCollection(
                self.context,
                UnifiedGroup,
                ResourcePath("UnifiedGroups", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.MultiGeo.Service.MultiGeoServicesBeta"

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {"UnifiedGroups": self.unified_groups}
            default_value = property_mapping.get(name, None)
        return super(MultiGeoServices, self).get_property(name, default_value)
