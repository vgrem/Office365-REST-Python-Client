from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.fields.field import Field
from office365.sharepoint.fields.creation_information import FieldCreationInformation
from office365.sharepoint.fields.type import FieldType
from office365.sharepoint.fields.xmlSchemaFieldCreationInformation import XmlSchemaFieldCreationInformation
from office365.sharepoint.taxonomy.field import TaxonomyField


class FieldCollection(BaseEntityCollection):
    """Represents a collection of Field resource."""

    def __init__(self, context, resource_path=None, parent=None):
        super(FieldCollection, self).__init__(context, Field, resource_path, parent)

    def add_url_field(self, title, description=None):
        """
        Adds Url field

        :param str title:
        :param str or None description:
        :return:
        """
        create_field_info = FieldCreationInformation(title=title,
                                                     description=description,
                                                     field_type_kind=FieldType.URL)
        return self.add(create_field_info)

    def add_lookup_field(self, title, lookup_list_id, lookup_field_name, allow_multiple_values=False):
        """
        Adds Lookup field

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
            target_field = self.create_field_as_xml(field_schema)
        else:
            create_field_info = FieldCreationInformation(title=title,
                                                         lookup_list_id=lookup_list_id,
                                                         lookup_field_name=lookup_field_name,
                                                         field_type_kind=FieldType.Lookup)
            target_field = self.add_field(create_field_info)
        return target_field

    def add_choice_field(self, title, values, multiple_values=False):
        """
        Adds Choice field

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
        Adds a user field

        :param str title: specifies the display name of the field
        """
        create_field_info = FieldCreationInformation(title, FieldType.User)
        return self.add_field(create_field_info)

    def add_dependent_lookup_field(self, display_name, primary_lookup_field, lookup_field):
        """Adds a secondary lookup field to a field (2) collection.
        A reference (3) to the SP.Field that was added is returned.
        :param str lookup_field: Name of the field (2) from the target list (1) to include data from.
        :param Field primary_lookup_field: Main lookup field to associate the dependent lookup field with.
            A dependent lookup field will include data from the list item referred to from the instance of the main
            lookup field.
        :param str display_name: Title of the added field
        """
        return_field = Field(self.context)
        self.add_child(return_field)
        parameters = {
            "displayName": display_name,
            "primaryLookupField": primary_lookup_field,
            "lookupField": lookup_field
        }
        qry = ServiceOperationQuery(self, "AddDependentLookupField", None, parameters, None, return_field)
        self.context.add_query(qry)
        return return_field

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
        qry = ServiceOperationQuery(self, "AddField", None, parameters, "parameters", return_type)
        self.context.add_query(qry)
        return return_type

    def create_taxonomy_field(self, name, term_set_id):
        """
        Creates a taxonomy field

        :param str name: Field name
        :param str term_set_id: TermSet Id
        """
        return TaxonomyField.create(self, name, term_set_id)

    def create_field_as_xml(self, schema_xml, return_type=None):
        """
        Creates a field based on the values defined in the parameters input parameter.

        :param str schema_xml:
        :type return_type: Field
        """
        if return_type is None:
            return_type = Field(self.context)
        self.add_child(return_type)
        field_schema = XmlSchemaFieldCreationInformation(schema_xml)
        qry = ServiceOperationQuery(self, "CreateFieldAsXml", None, field_schema, "parameters", return_type)
        self.context.add_query(qry)
        return return_type

    def get_by_id(self, _id):
        """
        Gets the fields with the specified ID.

        :type _id: str
        """
        return Field(self.context, ServiceOperationPath("getById", [_id], self.resource_path))

    def get_by_internal_name_or_title(self, name_title):
        """Returns the first field (2) in the collection based on the internal name or the title specified
        by the parameter.

        :param str name_title:  The title or internal name to look up the field (2) by.
        """
        return Field(self.context,
                     ServiceOperationPath("getByInternalNameOrTitle", [name_title], self.resource_path))

    def get_by_title(self, title):
        """
        Returns the first fields object in the collection based on the title of the specified fields.

        :type title: str
        """
        return Field(self.context, ServiceOperationPath("getByTitle", [title], self.resource_path))
