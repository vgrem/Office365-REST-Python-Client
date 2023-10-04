from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity


class AnnouncementsController(BaseEntity):
    def __init__(self, context, path=None):
        if path is None:
            path = ResourcePath("SP.Publishing.AnnouncementsController")
        super(AnnouncementsController, self).__init__(context, path)

    @property
    def entity_type_name(self):
        return "SP.Publishing.AnnouncementsController"
