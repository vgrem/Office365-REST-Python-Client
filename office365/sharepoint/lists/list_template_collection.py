from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.lists.list_template import ListTemplate


class ListTemplateCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(ListTemplateCollection, self).__init__(context, ListTemplate, resource_path)

    def get_by_name(self, name):
        """

        :param str name:
        :return:
        """
        return ListTemplate(self.context,
                            ServiceOperationPath("getByName", [name], self.resource_path))
