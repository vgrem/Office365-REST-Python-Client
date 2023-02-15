from office365.sharepoint.base_entity import BaseEntity


class Link(BaseEntity):

    @property
    def entity_type_name(self):
        return "SP.Directory.Link"
