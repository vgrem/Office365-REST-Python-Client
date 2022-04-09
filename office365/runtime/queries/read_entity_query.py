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
        value = super(ReadEntityQuery, self).url
        if self._properties_to_include is not None:
            value += "?" + QueryOptions.build(self.binding_type, self._properties_to_include).to_url()
        elif not self.binding_type.query_options.is_empty:
            value += "?" + self.binding_type.query_options.to_url()
        return value
