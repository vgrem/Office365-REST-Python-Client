from office365.runtime.queries.client_query import ClientQuery


class DeleteEntityQuery(ClientQuery):
    def __init__(self, delete_type):
        """
        Delete entity query

        :type delete_type: office365.runtime.client_object.ClientObject
        """
        super(DeleteEntityQuery, self).__init__(delete_type.context, delete_type)
