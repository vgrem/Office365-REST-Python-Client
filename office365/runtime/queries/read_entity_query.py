from office365.runtime.client_object import ClientObject
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
    def query_options(self):
        if self._properties_to_include is not None:
            return self._build_query_options()
        else:
            return self._binding_type.query_options

    def _build_query_options(self):
        query = QueryOptions()
        for n in self._properties_to_include:
            prop_val = self._binding_type.get_property(n)
            if isinstance(prop_val, ClientObject) or n == "Properties":
                query.expand.append(n)
            query.select.append(n)
        return query
