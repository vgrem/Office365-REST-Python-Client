from office365.graph.directory.groupProfile import GroupProfile
from office365.graph.teams.team import Team
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_result import ClientResult
from office365.runtime.resource_path import ResourcePath


class TeamCollection(ClientObjectCollection):
    """Team's collection"""

    def __init__(self, context, resource_path=None):
        super(TeamCollection, self).__init__(context, Team, resource_path)

    def __getitem__(self, key):
        if type(key) == int:
            return self._data[key]
        return Team(self.context, ResourcePath(key, self.resource_path))

    def create(self, group_name):
        """Provision a new team along with a group.

        :type group_name: str
        :rtype: ClientResult
        """

        grp_properties = GroupProfile(group_name)
        grp_properties.securityEnabled = False
        grp_properties.mailEnabled = True
        grp_properties.groupTypes = ["Unified"]
        target_group = self.context.groups.add(grp_properties)
        result = ClientResult(Team(self.context))

        def _group_created(resp):
            result.value = target_group.add_team()
        self.context.after_execute(_group_created)
        return result
