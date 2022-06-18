from office365.communications.calls.invitation_participant_info import InvitationParticipantInfo
from office365.communications.calls.participant_info import ParticipantInfo
from office365.communications.operations.invite_participants import InviteParticipantsOperation
from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery


class Participant(Entity):
    """Represents a participant in a call."""

    def invite(self, participants, client_context):
        """Invite participants to the active call.

        :param list[InvitationParticipantInfo] participants: Unique Client Context string. Max limit is 256 chars.
        :param str client_context: Unique Client Context string. Max limit is 256 chars.
        """
        return_type = InviteParticipantsOperation(self.context)
        payload = {
            "participants": ClientValueCollection(InvitationParticipantInfo, participants),
            "clientContext": client_context
        }
        qry = ServiceOperationQuery(self, "invite", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def info(self):
        """Information about the participant."""
        return self.properties.get("info", ParticipantInfo())
