import uuid

from office365.sharepoint.fields.lookup import FieldLookup
from office365.sharepoint.taxonomy.create_xml_parameters import TaxonomyFieldCreateXmlParameters


class TaxonomyField(FieldLookup):
    """Represents a taxonomy field."""

    @staticmethod
    def create(fields, name, term_set_id, term_store_id=None, allow_multiple_values=False, return_type=None):
        """
        :type fields: office365.sharepoint.fields.collection.FieldCollection
        :param str name: Field name
        :param str term_set_id: Term set identifier
        :param str term_store_id: Term store identifier
        :param bool allow_multiple_values: Specifies whether the column will allow more than one value
        :param TaxonomyField return_type: Return type
        """
        if return_type is None:
            return_type = TaxonomyField(fields.context)
        fields.add_child(return_type)
        params = TaxonomyFieldCreateXmlParameters(name, term_set_id, term_store_id=term_store_id,
                                                  allow_multiple_values=allow_multiple_values)

        def _create_taxonomy_field_inner():
            from office365.sharepoint.lists.list import List
            if isinstance(fields.parent, List):
                parent_list = fields.parent

                def _list_loaded():
                    params.web_id = parent_list.parent_web.id
                    params.list_id = parent_list.id
                    fields.create_field_as_xml(params.schema_xml, return_type)
                fields.parent.ensure_properties(["Id", "ParentWeb"], _list_loaded)
            else:
                def _web_loaded():
                    params.web_id = fields.context.web.id
                    fields.create_field_as_xml(params.schema_xml, return_type)
                fields.context.web.ensure_property("Id", _web_loaded)

        def _after_text_field_created(text_field):
            params.text_field_id = text_field.id
            _create_taxonomy_field_inner()

        return_type._create_text_field(name).after_execute(_after_text_field_created)
        return return_type

    def _create_text_field(self, name):
        """Creates hidden text field"""
        text_field_name = "{name}".format(name=uuid.uuid4().hex)
        text_field_schema = '''
                    <Field Type="Note" DisplayName="{name}_0" Hidden="TRUE" CanBeDeleted="TRUE" ShowInViewForms="FALSE"
                           CanToggleHidden="TRUE" StaticName="{text_field_name}" Name="{text_field_name}">
                    </Field>
                '''.format(name=name, text_field_name=text_field_name)
        return self.parent_collection.create_field_as_xml(text_field_schema)

    @property
    def anchor_id(self):
        """Gets or sets the GUID of the anchor Term object for a TaxonomyField object."""
        return self.properties.get('AnchorId', None)

    @property
    def is_anchor_valid(self):
        """Gets a Boolean value that specifies whether the Term object identified by the AnchorId property is valid."""
        return self.properties.get('IsAnchorValid', None)

    @property
    def text_field_id(self):
        """Gets the GUID that identifies the hidden text field in an item."""
        return self.properties.get('TextField', None)

    @property
    def text_field(self):
        """Gets the hidden text field in an item.

        :rtype: office365.sharepoint.fields.multi_line_text.FieldMultiLineText
        """
        return self.parent_collection.parent.fields.get_by_id(self.text_field_id)

    @property
    def entity_type_name(self):
        return "SP.Taxonomy.TaxonomyField"
