from office365.directory.extensions.extension import Extension
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.todo.checklist_item import ChecklistItem
from office365.todo.linked_resource import LinkedResource


class TodoTask(Entity):
    """A todoTask represents a task, such as a piece of work or personal item, that can be tracked and completed."""

    @property
    def extensions(self):
        """The collection of open extensions defined for the task."""
        return self.properties.get('extensions',
                                   EntityCollection(self.context, Extension,
                                                    ResourcePath("extensions", self.resource_path)))

    @property
    def checklist_items(self):
        """A collection of checklistItems linked to a task."""
        return self.properties.get('checklistItems',
                                   EntityCollection(self.context, ChecklistItem,
                                                    ResourcePath("checklistItems", self.resource_path)))

    @property
    def linked_resources(self):
        """A collection of resources linked to the task."""
        return self.properties.get('linkedResources',
                                   EntityCollection(self.context, LinkedResource,
                                                    ResourcePath("linkedResources", self.resource_path)))

    @property
    def entity_type_name(self):
        return None

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "checklistItems": self.checklist_items,
                "linked_resources": self.linked_resources,
            }
            default_value = property_mapping.get(name, None)
        return super(TodoTask, self).get_property(name, default_value)
