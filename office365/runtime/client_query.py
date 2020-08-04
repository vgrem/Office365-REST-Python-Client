from office365.runtime.client_object import ClientObject


class ClientQuery(object):
    """Client query"""

    def __init__(self, binding_type, parameter_type=None, parameter_name=None, return_type=None):
        """
        Base query

        :type binding_type: office365.runtime.client_object.ClientObject
        :type parameter_type:  ClientObject or ClientValue or dict or bytes or None
        :type parameter_name:  str or None
        :type return_type:  ClientObject or ClientResult or ClientValueObject or None
        """
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
        """
        Create entity query

        :type entity_to_create: office365.runtime.client_object.ClientObject
        :type create_info: ClientObject or ClientValue or dict
        :type parent_entity: ClientObject
        """
        super(CreateEntityQuery, self).__init__(parent_entity, create_info, None, entity_to_create)


class ReadEntityQuery(ClientQuery):
    def __init__(self, entity_to_read, properties_to_include=None):
        """
        Read entity query

        :type properties_to_include: list[str] or None
        :type entity_to_read: office365.runtime.client_object.ClientObject
        """
        binding_type = entity_to_read.clone_object()

        super(ReadEntityQuery, self).__init__(binding_type, None, None, entity_to_read)
        if properties_to_include:
            self._include_properties(properties_to_include)

    def _include_properties(self, properties_to_include):
        for n in properties_to_include:
            prop_val = self._binding_type.get_property(n)
            if isinstance(prop_val, ClientObject):
                self._binding_type.query_options.expand.append(n)
            self._binding_type.query_options.select.append(n)


class UpdateEntityQuery(ClientQuery):
    def __init__(self, entity_to_update):
        """
        Update entity query

        :type entity_to_update: office365.runtime.client_object.ClientObject
        """
        super(UpdateEntityQuery, self).__init__(entity_to_update, entity_to_update, None, None)


class DeleteEntityQuery(ClientQuery):
    def __init__(self, entity_to_delete):
        """
        Delete entity query

        :type entity_to_delete: office365.runtime.client_object.ClientObject
        """
        super(DeleteEntityQuery, self).__init__(entity_to_delete, None, None, None)
