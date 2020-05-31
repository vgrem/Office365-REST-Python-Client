class ClientQuery(object):
    """Client query"""

    def __init__(self, binding_type, parameter_type=None, parameter_name=None, return_type=None):
        self._binding_type = binding_type
        self._parameter_type = parameter_type
        self._parameter_name = parameter_name
        self._return_type = return_type

    @property
    def id(self):
        return id(self)

    @property
    def binding_type(self):
        return self._binding_type

    @property
    def parameter_name(self):
        return self._parameter_name

    @property
    def parameter_type(self):
        return self._parameter_type

    @property
    def return_type(self):
        return self._return_type


class CreateEntityQuery(ClientQuery):
    def __init__(self, parent_entity, create_info, entity_to_create):
        super(CreateEntityQuery, self).__init__(parent_entity, create_info, None, entity_to_create)


class ReadEntityQuery(ClientQuery):
    def __init__(self, entity_to_read, properties_to_include=None):
        super(ReadEntityQuery, self).__init__(entity_to_read, None, None, entity_to_read)
        if properties_to_include:
            entity_to_read.query_options.expand = properties_to_include


class UpdateEntityQuery(ClientQuery):
    def __init__(self, entity_to_update):
        super(UpdateEntityQuery, self).__init__(entity_to_update, entity_to_update, None, None)


class DeleteEntityQuery(ClientQuery):
    def __init__(self, entity_to_delete):
        super(DeleteEntityQuery, self).__init__(entity_to_delete, None, None, None)
