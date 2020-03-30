from office365.directory.group import Group
from office365.directory.directoryObjectCollection import DirectoryObjectCollection
from office365.runtime.client_query import CreateEntityQuery


class GroupCollection(DirectoryObjectCollection):
    """User's collection"""

    def __init__(self, context, resource_path=None):
        super(GroupCollection, self).__init__(context, Group, resource_path)

    def add(self, group_properties):
        """Create a Group resource.  You can create the following types of groups:
        Office 365 group (unified group)
        Security group"""
        grp = Group(self.context)
        self.add_child(grp)
        qry = CreateEntityQuery(self, group_properties, grp)
        self.context.add_query(qry)
        return grp
