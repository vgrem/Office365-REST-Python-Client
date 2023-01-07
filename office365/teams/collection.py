from office365.directory.groups.group import Group
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.teams.team import Team


class TeamCollection(EntityCollection):
    """Team's collection"""

    def __init__(self, context, resource_path=None):
        super(TeamCollection, self).__init__(context, Team, resource_path)

    def get_all(self, page_size=None, page_loaded=None):
        """List all teams in Microsoft Teams for an organization

        :param int page_size: Page size
        :param (ClientObjectCollection) -> None page_loaded: Page loaded event
        """
        def _init_teams(groups):
            """
            :type groups: GroupCollection
            """
            for grp in groups:  # type: Group
                if "Team" in grp.properties["resourceProvisioningOptions"]:
                    team = Team(self.context, ResourcePath(grp.id, self.resource_path))
                    for k, v in grp.properties.items():
                        team.set_property(k, v)
                    self.add_child(team)

        self.context.groups.get_all(page_size, page_loaded=_init_teams)
        return self

    def create(self, display_name, description=None):
        """Create a new team.

        :param str display_name: The name of the team.
        :param str or None description: 	An optional description for the team. Maximum length: 1024 characters.

        :rtype: Team
        """
        payload = {
            "displayName": display_name,
            "description": description,
            "template@odata.bind": "https://graph.microsoft.com/v1.0/teamsTemplates('standard')",
        }

        return_type = self.add(**payload)

        def _process_response(resp):
            """
            :type resp: requests.Response
            """
            content_loc = resp.headers.get('Content-Location', None)
            team_id = content_loc[content_loc.find("(") + 2:content_loc.find(")") - 1]
            return_type.set_property("id", team_id)
        self.context.after_execute(_process_response)
        return return_type
