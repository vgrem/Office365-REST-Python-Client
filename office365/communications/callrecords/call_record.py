from office365.directory.identities.identity_set import IdentitySet
from office365.entity import Entity


class CallRecord(Entity):
    """Represents a single peer-to-peer call or a group call between multiple participants,
    sometimes referred to as an online meeting."""

    @property
    def join_web_url(self):
        """Meeting URL associated to the call. May not be available for a peerToPeer call record type."""
        return self.properties.get("joinWebUrl", None)

    @property
    def organizer(self):
        """The organizing party's identity.."""
        return self.properties.get("organizer", IdentitySet())
