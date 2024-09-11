from office365.sharepoint.authpolicy.events.event import SPAuthEvent
from office365.sharepoint.entity_collection import EntityCollection


class SPAuthEventCollection(EntityCollection[SPAuthEvent]):
    """Represents a collection of Field resource."""

    def __init__(self, context, resource_path=None, parent=None):
        super(SPAuthEventCollection, self).__init__(
            context, SPAuthEvent, resource_path, parent
        )
