from office365.runtime.odata.odata_path_parser import ODataPathParser
from office365.runtime.utilities.http_method import HttpMethod


class ClientQuery(object):
    """Client query"""

    def __init__(self, url, method=HttpMethod.Get, payload=None):
        self.__url = url
        self.__method = method
        self.__payload = payload

    @property
    def url(self):
        return self.__url

    @property
    def method(self):
        return self.__method

    @property
    def payload(self):
        return self.__payload

    @property
    def id(self):
        return id(self)

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        return self.url == other.url


class CreateEntityQuery(ClientQuery):
    def __init__(self, parent_resource, parameters):
        super(CreateEntityQuery, self).__init__(parent_resource.resource_url, HttpMethod.Post, parameters)


class ReadEntityQuery(ClientQuery):
    def __init__(self, resource):
        super(ReadEntityQuery, self).__init__(resource.resource_url, HttpMethod.Get)


class UpdateEntityQuery(ClientQuery):
    def __init__(self, resource):
        super(UpdateEntityQuery, self).__init__(resource.resource_url, HttpMethod.Post, resource)


class DeleteEntityQuery(ClientQuery):
    def __init__(self, resource):
        super(DeleteEntityQuery, self).__init__(resource.resource_url, HttpMethod.Post)


class ServiceOperationQuery(ClientQuery):
    def __init__(self, resource, method, method_name, method_params=None, payload=None):
        url = resource.resource_url + "/" + ODataPathParser.from_method(method_name, method_params)
        super(ServiceOperationQuery, self).__init__(url, method, payload)
