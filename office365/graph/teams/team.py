from office365.graph.entity import Entity
from office365.graph.teams.channel import Channel
from office365.graph.teams.channelCollection import ChannelCollection
from office365.graph.teams.teamFunSettings import TeamFunSettings
from office365.graph.teams.teamGuestSettings import TeamGuestSettings
from office365.graph.teams.teamMemberSettings import TeamMemberSettings
from office365.graph.teams.teamMessagingSettings import TeamMessagingSettings
from office365.runtime.client_query import UpdateEntityQuery
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath


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
        if self.is_property_available("channels"):
            return self.properties['channels']
        else:
            return ChannelCollection(self.context, ResourcePath("channels", self.resource_path))

    @property
    def primaryChannel(self):
        """The general channel for the team."""
        if self.is_property_available("primaryChannel"):
            return self.properties['primaryChannel']
        else:
            return Channel(self.context, ResourcePath("primaryChannel", self.resource_path))

    def update(self):
        """Updates team."""
        qry = UpdateEntityQuery(self)
        self.context.add_query(qry)

    def archive(self):
        """Archive the specified team. When a team is archived, users can no longer send or like messages on any
        channel in the team, edit the team's name, description, or other settings, or in general make most changes to
        the team. Membership changes to the team continue to be allowed. """
        qry = ServiceOperationQuery(self, "archive")
        self.context.add_query(qry)

    def unarchive(self):
        """Restore an archived team. This restores users' ability to send messages and edit the team, abiding by
        tenant and team settings. """
        qry = ServiceOperationQuery(self, "unarchive")
        self.context.add_query(qry)

    def clone(self):
        """Create a copy of a team. This operation also creates a copy of the corresponding group. """
        qry = ServiceOperationQuery(self, "clone")
        self.context.add_query(qry)
