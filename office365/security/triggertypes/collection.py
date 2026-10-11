from office365.entity_collection import EntityCollection
from office365.security.triggertypes.event_type import RetentionEventType


class RetentionEventTypeCollection(EntityCollection[RetentionEventType]):
    """"""

    def __init__(self, context, resource_path=None):
        super().__init__(context, RetentionEventType, resource_path)
