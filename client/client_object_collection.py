from client_object import ClientObject


class ClientObjectCollection(ClientObject):
    """Client object collection"""

    def __init__(self, context, resource_path=None, parent_resource_path=None):
        super(ClientObjectCollection, self).__init__(context, resource_path, parent_resource_path)
        self.__data = []

    def add_child(self, client_object):
        self.__data.append(client_object)

    def __iter__(self):
        return iter(self.__data)
