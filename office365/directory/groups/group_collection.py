from office365.directory.groups.group import Group
from office365.entity_collection import DeltaCollection
from office365.runtime.queries.create_entity_query import CreateEntityQuery


class GroupCollection(DeltaCollection):
    """Group's collection"""

    def __init__(self, context, resource_path=None):
        super(GroupCollection, self).__init__(context, Group, resource_path)

    def add(self, group_properties):
        """Create a Group resource.  You can create the following types of groups:
        Office 365 group (unified group)
        Security group

        :type group_properties: GroupProfile"""
        return_type = Group(self.context)
        self.add_child(return_type)
        qry = CreateEntityQuery(self, group_properties, return_type)
        self.context.add_query(qry)
        return return_type
