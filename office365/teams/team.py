from office365.entity import Entity
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
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
from office365.teams.teamsTemplate import TeamsTemplate


class Team(Entity):
    """A team in Microsoft Teams is a collection of channel objects. A channel represents a topic, and therefore a
    logical isolation of discussion, within a team. """

    def __init__(self, context, resource_path=None, properties=None):
        super(Team, self).__init__(context, resource_path, properties)
        self.memberSettings = TeamMemberSettings()
        self.guestSettings = TeamGuestSettings()
        self.messagingSettings = TeamMessagingSettings()
        self.funSettings = TeamFunSettings()

    @property
    def displayName(self):
        """The name of the team."""
        return self.properties.get('displayName', None)

    @property
    def description(self):
        """An optional description for the team."""
        return self.properties.get('description', None)

    @property
    def classification(self):
        """An optional label. Typically describes the data or business sensitivity of the team.
        Must match one of a pre-configured set in the tenant's directory."""
        return self.properties.get('classification', None)

    @property
    def is_archived(self):
        """Whether this team is in read-only mode."""
        return self.properties.get('isArchived', None)

    @property
    def visibility(self):
        """The visibility of the group and team. Defaults to Public."""
        return self.properties.get('visibility', None)

    @property
    def web_url(self):
        """A hyperlink that will go to the team in the Microsoft Teams client. This is the URL that you get when
        you right-click a team in the Microsoft Teams client and select Get link to team. This URL should be treated
        as an opaque blob, and not parsed."""
        return self.properties.get('webUrl', None)

    @property
    def createdDateTime(self):
        """Timestamp at which the team was created."""
        return self.properties.get('createdDateTime', None)

    @property
    def channels(self):
        """The collection of channels & messages associated with the team."""
        return self.properties.get('channels',
                                   ChannelCollection(self.context, ResourcePath("channels", self.resource_path)))

    @property
    def primary_channel(self):
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

    @property
    def template(self):
        """The template this team was created from"""
        return self.properties.get('template',
                                   TeamsTemplate(self.context, ResourcePath("template", self.resource_path)))

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
        super(Team, self).set_property(name, value, persist_changes)
        # fallback: determine whether resource path is resolved
        if name == "id" and self._resource_path.segment == "team":
            self._resource_path = ResourcePath(value, ResourcePath("teams"))
        return self
