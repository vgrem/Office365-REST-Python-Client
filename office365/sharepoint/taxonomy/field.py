import uuid

from office365.sharepoint.fields.lookup import FieldLookup


class TaxonomyField(FieldLookup):
    """Represents a taxonomy field."""

    @staticmethod
    def create(context, name, ssp_id, term_set_id):
        """
        :type context: office365.sharepoint.client_context.ClientContext
        :param str name:
        :param str ssp_id:
        :param str term_set_id:
        """
        pass

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
