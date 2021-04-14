from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.lists.list_template import ListTemplate


class ListTemplateCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(ListTemplateCollection, self).__init__(context, ListTemplate, resource_path)

    def get_by_name(self, name):
        """

        :param str name:
        :return:
        """
        return ListTemplate(self.context,
                            ResourcePathServiceOperation("getByName", [name], self.resource_path))
