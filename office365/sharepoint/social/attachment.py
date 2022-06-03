from office365.sharepoint.base_entity import BaseEntity


class SocialAttachment(BaseEntity):
    """The SocialAttachment class represents an image, document preview, or video preview attachment."""

    @property
    def entity_type_name(self):
        return "SP.Social.SocialAttachment"
