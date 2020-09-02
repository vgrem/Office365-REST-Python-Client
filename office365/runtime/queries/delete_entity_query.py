from office365.runtime.queries.client_query import ClientQuery


class DeleteEntityQuery(ClientQuery):
    def __init__(self, entity_to_delete):
        """
        Delete entity query

        :type entity_to_delete: office365.runtime.client_object.ClientObject
        """
        super(DeleteEntityQuery, self).__init__(entity_to_delete.context, entity_to_delete)
