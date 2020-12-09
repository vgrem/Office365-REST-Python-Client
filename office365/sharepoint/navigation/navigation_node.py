from office365.runtime.queries.delete_entity_query import DeleteEntityQuery
from office365.runtime.resource_path import ResourcePath
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.base_entity import BaseEntity


class NavigationNode(BaseEntity):
    """
    Represents the URL to a specific navigation node and provides access to properties and methods for
    manipulating the ordering of the navigation node in a navigation node collection.
    """

    def delete_object(self):
        """Deletes the navigation node."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()
        return self

    @property
    def children(self):
        """Gets the collection of child nodes of the navigation node."""
        from office365.sharepoint.navigation.navigation_node_collection import NavigationNodeCollection
        return self.properties.get('Children',
                                   NavigationNodeCollection(self.context, ResourcePath("Children", self.resource_path)))

    @property
    def title(self):
        """Gets a value that specifies the anchor text for the navigation node link."""
        return self.properties.get('Title', None)

    @title.setter
    def title(self, value):
        """Sets a value that specifies the anchor text for the navigation node link."""
        self.set_property('Title', value)

    @property
    def url(self):
        """Gets a value that specifies the URL stored with the navigation node."""
        return self.properties.get('Url', None)

    @url.setter
    def url(self, value):
        """Sets a value that specifies the URL stored with the navigation node."""
        self.set_property('Url', value)

    @property
    def is_visible(self):
        """Gets a value that specifies the anchor text for the navigation node link."""
        return self.properties.get('Title', None)

    def set_property(self, name, value, persist_changes=True):
        super(NavigationNode, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "Id":
                self._resource_path = ResourcePathServiceOperation("GetById",
                                                                   [value],
                                                                   self._parent_collection.resource_path)
        return self
