from office365.runtime.odata.query_options import QueryOptions
from office365.runtime.queries.client_query import ClientQuery


class ReadEntityQuery(ClientQuery):
    def __init__(self, entity, properties_to_include=None):
        """
        Read entity query

        :type properties_to_include: list[str] or None
        :type entity: office365.runtime.client_object.ClientObject
        """
        super(ReadEntityQuery, self).__init__(entity.context, entity, None, None, entity)
        self._properties_to_include = properties_to_include

    @property
    def url(self):
        query_url = super(ReadEntityQuery, self).url
        query_options = QueryOptions.build(self.binding_type, self._properties_to_include)
        return query_url if query_options.is_empty else query_url + "?" + str(query_options)
