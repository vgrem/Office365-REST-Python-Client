from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath


class Trending(Entity):
    """
    Rich relationship connecting a user to documents that are trending around the user (are relevant to the user).
    OneDrive files, and files stored on SharePoint team sites can trend around the user.
    """

    @property
    def resource(self):
        """Used for navigating to the trending document."""
        return self.properties.get('resource',
                                   Entity(self.context, ResourcePath("resource", self.resource_path)))

