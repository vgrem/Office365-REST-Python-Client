from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity


class PointPublishingSiteManager(BaseEntity):
    """"""

    def __init__(self, context):
        super(PointPublishingSiteManager, self).__init__(
            context, ResourcePath("SP.Publishing.PointPublishingSiteManager")
        )
