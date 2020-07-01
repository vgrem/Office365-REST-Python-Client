from office365.sharepoint.base_entity import BaseEntity


class Utility(BaseEntity):

    def __init__(self, context, resource_path):
        super().__init__(context, resource_path, "SP.Utilities")
