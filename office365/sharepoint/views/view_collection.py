from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.views.view import View


class ViewCollection(BaseEntityCollection):
    """Represents a collection of View resources."""

    def __init__(self, context, resource_path=None, parent_list=None):
        """

        :type parent_list: office365.sharepoint.list.List or None
        """
        super(ViewCollection, self).__init__(context, View, resource_path, parent_list)

    def add(self, view_creation_information):
        """

        :type view_creation_information: office365.sharepoint.view_create_information.ViewCreationInformation
        """
        view = View(self.context, None, self._parent)
        self.add_child(view)
        qry = ServiceOperationQuery(self, "Add", None, view_creation_information, "parameters", view)
        self.context.add_query(qry)
        return view

    def get_by_title(self, view_title):
        """Gets the list view with the specified title.

        :type view_title: str
        """
        return View(self.context,
                    ServiceOperationPath("GetByTitle", [view_title], self.resource_path), self._parent)

    def get_by_id(self, view_id):
        """Gets the list view with the specified ID.

        :type view_id: str
        """
        return View(self.context,
                    ServiceOperationPath("GetById", [view_id], self.resource_path), self._parent)

    @property
    def parent_list(self):
        return self._parent
