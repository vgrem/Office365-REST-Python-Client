from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.forms.form import Form


class FormCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(FormCollection, self).__init__(context, Form, resource_path)

    def get_by_page_type(self):
        pass
