import uuid

from office365.sharepoint.fields.field import Field
from office365.sharepoint.fields.fieldText import FieldText
from office365.sharepoint.fields.fieldType import FieldType
from office365.sharepoint.fields.field_creation_information import FieldCreationInformation
from tests.sharepoint.sharepoint_case import SPTestCase


class TestField(SPTestCase):
    target_field = None   # type: Field
    target_field_name = "Title"

    def test_1_get_site_fields(self):
        site_fields = self.client.site.rootWeb.fields
        self.client.load(site_fields)
        self.client.execute_query()
        self.assertGreater(len(site_fields), 0)

    def test_2_get_field(self):
        title_field = self.client.site.rootWeb.fields.get_by_internal_name_or_title(self.target_field_name)
        self.client.load(title_field)
        self.client.execute_query()
        self.assertIsNotNone(title_field.properties['InternalName'])
        self.assertEqual(title_field.properties['InternalName'], self.target_field_name)
        self.assertIsInstance(title_field, FieldText)
        self.assertIsNotNone(title_field.max_length)

    def test_3_get_field_by_title(self):
        title_field = self.client.site.rootWeb.fields.get_by_title(self.target_field_name)
        self.client.load(title_field)
        self.client.execute_query()
        self.assertIsNotNone(title_field.properties['InternalName'])
        self.assertEqual(title_field.properties['InternalName'], self.target_field_name)

    def test_4_create_site_field(self):
        field_name = "Title_" + uuid.uuid4().hex
        create_field_info = FieldCreationInformation(field_name, FieldType.Text)
        created_field = self.client.site.rootWeb.fields.add(create_field_info)
        self.client.execute_query()
        self.assertEqual(created_field.properties["Title"], field_name)
        self.__class__.target_field = created_field

    def test_5_update_site_field(self):
        field_to_update = self.__class__.target_field
        updated_field_name = "Title_" + uuid.uuid4().hex
        field_to_update.set_property('Title', updated_field_name)
        field_to_update.update()
        self.client.execute_query()

        updated_field = self.client.site.rootWeb.fields.get_by_title(updated_field_name)
        self.client.load(updated_field)
        self.client.execute_query()
        self.assertIsNotNone(updated_field.properties['Id'])
        self.assertEqual(updated_field.properties['Title'], updated_field_name)

    def test_6_delete_site_field(self):
        field_to_delete = self.__class__.target_field
        field_to_delete.delete_object()
        self.client.execute_query()
