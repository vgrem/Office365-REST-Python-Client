from office365.runtime.queries.client_query import ClientQuery


class UpdateEntityQuery(ClientQuery):
    def __init__(self, update_type):
        """
        Update client object query

        :type update_type: office365.runtime.client_object.ClientObject
        """
        super(UpdateEntityQuery, self).__init__(update_type.context, update_type, update_type)
