from office365.delta_collection import DeltaCollection
from office365.directory.groups.group import Group
from office365.directory.groups.profile import GroupProfile
from office365.runtime.queries.create_entity import CreateEntityQuery


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

    def create_with_team(self, group_name):
        """Provision a new group along with a team.

        :param str group_name:
        """
        grp_properties = GroupProfile(group_name)
        grp_properties.securityEnabled = False
        grp_properties.mailEnabled = True
        grp_properties.groupTypes = ["Unified"]
        return_type = self.context.groups.add(grp_properties)

        def _group_created(resp):
            """
            :type resp: requests.Response
            """
            new_team = return_type.add_team()
            return_type.set_property("team", new_team, False)

        self.context.after_execute(_group_created)
        return return_type
