from office365.runtime.queries.client_query import ClientQuery


class CreateEntityQuery(ClientQuery):
    def __init__(self, parent_entity, parameters, return_type=None):
        """
        Create entity query

        :type return_type: office365.runtime.client_object.ClientObject
        :type parameters: office365.runtime.client_object.ClientObject or office365.runtime.client_value.ClientValue
            or dict
        :type parent_entity: office365.runtime.client_object.ClientObject
        """
        super(CreateEntityQuery, self).__init__(parent_entity.context,
                                                parent_entity,
                                                parameters,
                                                None,
                                                return_type)
