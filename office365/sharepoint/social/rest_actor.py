from office365.sharepoint.base_entity import BaseEntity


class SocialRestActor(BaseEntity):
    """The SocialRestActor type contains information about an actor retrieved from server. An actor is a user, document,
     site, or tag. The SocialRestActor type is available when the protocol client sends an OData request to a protocol
     server using [MS-CSOMREST]. It is not available using [MS-CSOM]."""

    @property
    def entity_type_name(self):
        return "SP.Social.SocialRestActor"
