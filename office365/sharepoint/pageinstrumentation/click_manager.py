from office365.sharepoint.base_entity import BaseEntity


class ClickManager(BaseEntity):

    @property
    def entity_type_name(self):
        return "SP.PageInstrumentation.ClickManager"

