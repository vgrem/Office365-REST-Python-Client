from office365.entity import Entity
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.queries.update_entity_query import UpdateEntityQuery
from office365.runtime.resource_path import ResourcePath
from office365.teams.channel import Channel
from office365.teams.channelCollection import ChannelCollection
from office365.teams.schedule import Schedule
from office365.teams.teamFunSettings import TeamFunSettings
from office365.teams.teamGuestSettings import TeamGuestSettings
from office365.teams.teamMemberSettings import TeamMemberSettings
from office365.teams.teamMessagingSettings import TeamMessagingSettings
from office365.teams.teamsAppInstallationCollection import TeamsAppInstallationCollection
from office365.teams.teamsAsyncOperationCollection import TeamsAsyncOperationCollection


class Team(Entity):
    """A team in Microsoft Teams is a collection of channel objects. A channel represents a topic, and therefore a
    logical isolation of discussion, within a team. """

    def __init__(self, context, resource_path=None):
        super().__init__(context, resource_path)
        self.memberSettings = TeamMemberSettings()
        self.guestSettings = TeamGuestSettings()
        self.messagingSettings = TeamMessagingSettings()
        self.funSettings = TeamFunSettings()

    @property
    def channels(self):
        """The collection of channels & messages associated with the team."""
        return self.properties.get('channels',
                                   ChannelCollection(self.context, ResourcePath("channels", self.resource_path)))

    @property
    def primaryChannel(self):
        """The general channel for the team."""
        return self.properties.get('primaryChannel',
                                   Channel(self.context, ResourcePath("primaryChannel", self.resource_path)))

    @property
    def schedule(self):
        """The schedule of shifts for this team."""
        return self.properties.get('schedule',
                                   Schedule(self.context, ResourcePath("schedule", self.resource_path)))

    @property
    def installedApps(self):
        """The apps installed in this team."""
        return self.properties.get('installedApps',
                                   TeamsAppInstallationCollection(self.context,
                                                                  ResourcePath("installedApps", self.resource_path)))

    @property
    def operations(self):
        """The async operations that ran or are running on this team."""
        return self.properties.get('operations',
                                   TeamsAsyncOperationCollection(self.context,
                                                                 ResourcePath("installedApps", self.resource_path)))

    def update(self):
        """Updates a Team."""
        qry = UpdateEntityQuery(self)
        self.context.add_query(qry)
        return self

    def archive(self):
        """Archive the specified team. When a team is archived, users can no longer send or like messages on any
        channel in the team, edit the team's name, description, or other settings, or in general make most changes to
        the team. Membership changes to the team continue to be allowed. """
        qry = ServiceOperationQuery(self, "archive")
        self.context.add_query(qry)
        return self

    def unarchive(self):
        """Restore an archived team. This restores users' ability to send messages and edit the team, abiding by
        tenant and team settings. """
        qry = ServiceOperationQuery(self, "unarchive")
        self.context.add_query(qry)
        return self

    def clone(self):
        """Create a copy of a team. This operation also creates a copy of the corresponding group. """
        qry = ServiceOperationQuery(self, "clone")
        self.context.add_query(qry)
        return self

    def set_property(self, name, value, persist_changes=True):
        super().set_property(name, value, persist_changes)
        # fallback: fix resource path
        if name == "id" and self._resource_path.segment == "team":
            self._resource_path = ResourcePath(value, ResourcePath("teams"))
        return self
