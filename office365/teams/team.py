from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import UpdateEntityQuery
from office365.runtime.resourcePath import ResourcePath
from office365.runtime.serviceOperationQuery import ServiceOperationQuery
from office365.teams.channel import Channel
from office365.teams.channelCollection import ChannelCollection
from office365.teams.teamFunSettings import TeamFunSettings
from office365.teams.teamGuestSettings import TeamGuestSettings
from office365.teams.teamMemberSettings import TeamMemberSettings
from office365.teams.teamMessagingSettings import TeamMessagingSettings


class Team(ClientObject):
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
        return ChannelCollection(self, ResourcePath("channels"))

    @property
    def primaryChannel(self):
        """The general channel for the team."""
        return Channel(self, ResourcePath("primaryChannel"))

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
