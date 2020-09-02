from office365.runtime.queries.client_query import ClientQuery


class UpdateEntityQuery(ClientQuery):
    def __init__(self, entity_to_update):
        """
        Update entity query

        :type entity_to_update: office365.runtime.client_object.ClientObject
        """
        super(UpdateEntityQuery, self).__init__(entity_to_update.context,
                                                entity_to_update,
                                                entity_to_update,
                                                None,
                                                None)
