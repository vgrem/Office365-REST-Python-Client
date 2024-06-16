from typing import Dict

from office365.runtime.client_object import ClientObject
from office365.runtime.client_value import ClientValue
from office365.runtime.queries.client_query import ClientQuery


class CreateEntityQuery(ClientQuery):
    def __init__(self, parent_entity, parameters, return_type=None):
        # type: (ClientObject, ClientObject|ClientValue|Dict, ClientObject) -> None
        """Create entity query"""
        super(CreateEntityQuery, self).__init__(
            parent_entity.context, parent_entity, parameters, None, return_type
        )
