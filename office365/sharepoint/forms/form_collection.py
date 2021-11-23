from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.forms.form import Form


class FormCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(FormCollection, self).__init__(context, Form, resource_path)

    def get_by_id(self, _id):
        """Gets the form with the specified ID."""
        return Form(self.context, ServiceOperationPath("GetById", [_id], self.resource_path))

    def get_by_page_type(self, form_type):
        return Form(self.context, ServiceOperationPath("GetByPageType", [form_type], self.resource_path))
