from office365.communications.calls.participant_info import ParticipantInfo
from office365.entity import Entity


class Participant(Entity):
    """Represents a participant in a call."""

    @property
    def info(self):
        """Information about the participant."""
        return self.properties.get("info", ParticipantInfo())
