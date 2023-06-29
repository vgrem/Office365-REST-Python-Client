from office365.runtime.odata.query_options import QueryOptions
from office365.runtime.queries.client_query import ClientQuery


class ReadEntityQuery(ClientQuery):
    def __init__(self, return_type, properties_to_include=None):
        """
        Read client object query

        :type properties_to_include: list[str] or None
        :type return_type: office365.runtime.client_object.ClientObject
        """
        super(ReadEntityQuery, self).__init__(return_type.context, return_type, None, None, return_type)
        self._properties_to_include = properties_to_include
        self._query_options = QueryOptions.build(return_type, properties_to_include)

    @property
    def url(self):
        print(self._query_options)
        orig_url = super(ReadEntityQuery, self).url
        return orig_url if self._query_options.is_empty else orig_url + "?" + str(self._query_options)
