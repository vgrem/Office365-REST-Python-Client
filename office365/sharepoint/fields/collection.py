from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.fields.field import Field
from office365.sharepoint.fields.creation_information import FieldCreationInformation
from office365.sharepoint.fields.type import FieldType
from office365.sharepoint.fields.xmlSchemaFieldCreationInformation import XmlSchemaFieldCreationInformation
from office365.sharepoint.taxonomy.field import TaxonomyField
from office365.sharepoint.taxonomy.sets.set import TermSet


class FieldCollection(BaseEntityCollection):
    """Represents a collection of Field resource."""

    def __init__(self, context, resource_path=None, parent=None):
        super(FieldCollection, self).__init__(context, Field, resource_path, parent)

    def add_geolocation_field(self, title, description=None):
        """
        Creates Geolocation field

        :param str title: Specifies the display name of the field
        :param str or None description: Specifies the description of the field
        """
        return self.add(FieldCreationInformation(title=title,
                                                 description=description,
                                                 field_type_kind=FieldType.Geolocation))

    def add_url_field(self, title, description=None):
        """
        Creates Url field

        :param str title:
        :param str or None description:
        """
        return self.add(FieldCreationInformation(title=title,
                                                 description=description,
                                                 field_type_kind=FieldType.URL))

    def add_lookup_field(self, title, lookup_list_id, lookup_field_name, allow_multiple_values=False):
        """
        Creates a Lookup field

        :param bool allow_multiple_values:
        :param str lookup_field_name:
        :param str lookup_list_id:
        :param str title:
        """
        if allow_multiple_values:
            field_schema = '''
                        <Field Type="LookupMulti" Mult="TRUE" DisplayName="{title}" Required="FALSE" Hidden="TRUE" \
                        ShowField="{lookup_field_name}" List="{{{lookup_list_id}}}" StaticName="{title}" Name="{title}">
                        </Field>
                        '''.format(title=title, lookup_field_name=lookup_field_name, lookup_list_id=lookup_list_id)
            return self.create_field_as_xml(field_schema)
        else:
            return self.add_field(FieldCreationInformation(title=title,
                                                           lookup_list_id=lookup_list_id,
                                                           lookup_field_name=lookup_field_name,
                                                           field_type_kind=FieldType.Lookup))

    def add_choice_field(self, title, values, multiple_values=False):
        """
        Created Choice field

        :param bool multiple_values:
        :param list[str] values:
        :param str title:
        """
        fld_type = FieldType.MultiChoice if multiple_values else FieldType.Choice
        create_field_info = FieldCreationInformation(title, fld_type)
        [create_field_info.Choices.add(choice) for choice in values]
        return self.add_field(create_field_info)

    def add_user_field(self, title):
        """
        Creates a User field

        :param str title: specifies the display name of the field
        """
        return self.add_field(FieldCreationInformation(title, FieldType.User))

    def add_text_field(self, title):
        """
        Creates a Text field

        :param str title: specifies the display name of the field
        :rtype: office365.sharepoint.fields.text.FieldText
        """
        return self.add_field(FieldCreationInformation(title, FieldType.Text))

    def add_dependent_lookup_field(self, display_name, primary_lookup_field, lookup_field):
        """Adds a secondary lookup field to a field (2) collection.
        A reference (3) to the SP.Field that was added is returned.
        :param str lookup_field: Name of the field (2) from the target list (1) to include data from.
        :param Field primary_lookup_field: Main lookup field to associate the dependent lookup field with.
            A dependent lookup field will include data from the list item referred to from the instance of the main
            lookup field.
        :param str display_name: Title of the added field
        """
        return_type = Field(self.context)
        self.add_child(return_type)
        parameters = {
            "displayName": display_name,
            "primaryLookupField": primary_lookup_field,
            "lookupField": lookup_field
        }
        qry = ServiceOperationQuery(self, "AddDependentLookupField", None, parameters, None, return_type)
        self.context.add_query(qry)
        return return_type

    def add_taxonomy_field(self, title, description=None):
        """
        Adds a taxonomy field
        """
        pass

    def add(self, field_create_information):
        """Adds a fields to the fields collection.

        :type field_create_information: office365.sharepoint.fields.creation_information.FieldCreationInformation
        """
        return_type = Field.create_field_from_type(self.context, field_create_information)
        self.add_child(return_type)
        qry = CreateEntityQuery(self, return_type, return_type)
        self.context.add_query(qry)
        return return_type

    def add_field(self, parameters):
        """Adds a fields to the fields collection.

        :type parameters: office365.sharepoint.fields.creation_information.FieldCreationInformation
        """
        return_type = Field(self.context)
        self.add_child(return_type)
        payload = {"parameters": parameters}
        qry = ServiceOperationQuery(self, "AddField", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def create_taxonomy_field(self, name, term_set, allow_multiple_values=False):
        """
        Creates a Taxonomy field

        :param str name: Field name
        :param str or TermSet term_set: TermSet identifier or object
        :param bool allow_multiple_values: Specifies whether the column will allow more than one value
        """
        return_type = TaxonomyField(self.context)

        if isinstance(term_set, TermSet):
            def _term_set_loaded():
                TaxonomyField.create(self, name, term_set.id, None, allow_multiple_values, return_type=return_type)
            term_set.ensure_property("id", _term_set_loaded)
            return return_type
        else:

            def _term_store_loaded(term_store):
                TaxonomyField.create(self, name, term_set, term_store.id, allow_multiple_values,
                                     return_type=return_type)
            self.context.load(self.context.taxonomy.term_store, after_loaded=_term_store_loaded)
        return return_type

    def create_field_as_xml(self, schema_xml, return_type=None):
        """
        Creates a field based on the values defined in the parameters input parameter.

        :param str schema_xml: Specifies the schema that defines the field
        :type return_type: Field
        """
        if return_type is None:
            return_type = Field(self.context)
        self.add_child(return_type)
        payload = {"parameters": XmlSchemaFieldCreationInformation(schema_xml)}
        qry = ServiceOperationQuery(self, "CreateFieldAsXml", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_by_id(self, _id):
        """
        Gets the fields with the specified ID.

        :param str _id: The field identifier.
        """
        return Field(self.context, ServiceOperationPath("getById", [_id], self.resource_path))

    def get_by_internal_name_or_title(self, value):
        """Returns the first field (2) in the collection based on the internal name or the title specified
        by the parameter.

        :param str value:  The title or internal name to look up the field (2) by.
        """
        return Field(self.context,
                     ServiceOperationPath("getByInternalNameOrTitle", [value], self.resource_path))

    def get_by_title(self, title):
        """
        Returns the first fields object in the collection based on the title of the specified fields.

        :param str title: The title to look up the field by
        """
        return Field(self.context, ServiceOperationPath("getByTitle", [title], self.resource_path))
