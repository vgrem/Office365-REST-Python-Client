from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.forms.form import Form


class FormCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(FormCollection, self).__init__(context, Form, resource_path)

    def get_by_page_type(self):
        pass
