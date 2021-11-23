from office365.directory.groups.group import Group
from office365.directory.groups.group_profile import GroupProfile
from office365.entity_collection import EntityCollection
from office365.runtime.client_result import ClientResult
from office365.runtime.paths.resource_path import ResourcePath
from office365.teams.team import Team


class TeamCollection(EntityCollection):
    """Team's collection"""

    def __init__(self, context, resource_path=None):
        super(TeamCollection, self).__init__(context, Team, resource_path)

    def __getitem__(self, key):
        """
        :rtype: Team
        """
        return Team(self.context, ResourcePath(key, self.resource_path))

    def get(self):
        """
        :rtype: TeamCollection
        """
        return super(TeamCollection, self).get()

    def get_all(self, include_properties=None):
        """List all teams in Microsoft Teams for an organization"""
        if include_properties is None:
            include_properties = []
        include_properties = include_properties + ["id", "resourceProvisioningOptions"]
        groups = self.context.groups.select(include_properties).get()

        def _process_response(resp):
            for grp in groups:  # type: Group
                if "Team" in grp.properties["resourceProvisioningOptions"]:
                    new_team = Team(self.context, ResourcePath(grp.id, self.resource_path))
                    for k, v in grp.properties.items():
                        new_team.set_property(k, v)
                    self.add_child(new_team)

        self.context.after_execute(_process_response)
        return self

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
        result = ClientResult(self.context, Team(self.context))

        def _group_created(resp):
            """
            :type resp: requests.Response
            """
            result.value = target_group.add_team()

        self.context.after_execute(_group_created)
        return result
