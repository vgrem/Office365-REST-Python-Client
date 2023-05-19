from office365.entity_collection import EntityCollection
from office365.onedrive.termstore.groups.group import Group


class GroupCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(GroupCollection, self).__init__(context, Group, resource_path)

    def add(self, display_name):
        """
        Create a new group object in a term store.

        :param str display_name: Name of the group to be created.
        :rtype: Group
        """
        props = {"displayName": display_name}
        return super(GroupCollection, self).add(**props)

    def get_by_name(self, name):
        """Returns the group with the specified name.

        :param str name: Group name
        """
        return_type = Group(self.context)
        self.add_child(return_type)

        def _after_get_by_name(col):
            """
            :type col: GroupCollection
            """
            if len(col) == 0:
                message = "Group not found for name: {0}".format(name)
                raise ValueError(message)
            elif len(col) != 1:
                message = "Ambiguous match found for name: {0}".format(name)
                raise ValueError(message)
            return_type.set_property("id", col[0].get_property("id"))

        self.filter("displayName eq '{0}'".format(name))
        self.context.load(self, after_loaded=_after_get_by_name)
        return return_type

