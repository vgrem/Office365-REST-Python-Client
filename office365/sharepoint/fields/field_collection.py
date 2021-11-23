import uuid

from office365.runtime.queries.create_entity_query import CreateEntityQuery
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.fields.field import Field
from office365.sharepoint.fields.field_creation_information import FieldCreationInformation
from office365.sharepoint.fields.field_type import FieldType
from office365.sharepoint.fields.xmlSchemaFieldCreationInformation import XmlSchemaFieldCreationInformation


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

    def add_user_field(self):
        pass

    def add_dependent_lookup_field(self, displayName, primaryLookupField, lookupField):
        """Adds a secondary lookup field to a field (2) collection.
        A reference (3) to the SP.Field that was added is returned.
        :param str lookupField: Name of the field (2) from the target list (1) to include data from.
        :param Field primaryLookupField: Main lookup field to associate the dependent lookup field with.
            A dependent lookup field will include data from the list item referred to from the instance of the main
            lookup field.
        :param str displayName: Title of the added field
        """
        return_field = Field(self.context)
        self.add_child(return_field)
        parameters = {
            "displayName": displayName,
            "primaryLookupField": primaryLookupField,
            "lookupField": lookupField
        }
        qry = ServiceOperationQuery(self, "AddDependentLookupField", None, parameters, None, return_field)
        self.context.add_query(qry)
        return return_field

    def add(self, field_create_information):
        """Adds a fields to the fields collection.

        :type field_create_information: office365.sharepoint.fields.field_creation_information.FieldCreationInformation
        """
        field = Field.create_field_from_type(self.context, field_create_information)
        self.add_child(field)
        qry = CreateEntityQuery(self, field, field)
        self.context.add_query(qry)
        return field

    def add_field(self, parameters):
        """Adds a fields to the fields collection.

        :type parameters: office365.sharepoint.fields.field_creation_information.FieldCreationInformation
        """
        field = Field(self.context)
        self.add_child(field)
        qry = ServiceOperationQuery(self, "AddField", None, parameters, "parameters", field)
        self.context.add_query(qry)
        return field

    def create_taxonomy_field(self, name, ssp_id, term_set_id, anchor_id="00000000-0000-0000-0000-000000000000",
                              field_id=None, text_field_id=None, web_id=None, list_id=None):

        target_field = Field(self.context)
        field_params = {
            "name": name,
            "ssp_id": ssp_id,
            "term_set_id": term_set_id,
            "anchor_id": anchor_id,
            "field_id": field_id,
            "text_field_id": text_field_id,
            "list_id": list_id,
            "web_id": web_id,
            "target_field": target_field
        }
        if field_id is None:
            field_params["field_id"] = str(uuid.uuid1())

        def _create_taxonomy_field_inner():
            from office365.sharepoint.lists.list import List
            if isinstance(self._parent, List):
                parent_list = self._parent

                def _list_loaded():
                    field_params["web_id"] = parent_list.parent_web.properties["Id"]
                    field_params["list_id"] = parent_list.properties["Id"]
                    self._build_taxonomy_field_query(**field_params)

                self._parent.ensure_properties(["Id", "ParentWeb"], _list_loaded)
            else:

                def _web_loaded():
                    field_params["web_id"] = self.context.web.properties["Id"]
                    self._build_taxonomy_field_query(**field_params)

                self.context.web.ensure_property("Id", _web_loaded)

        if text_field_id is None:
            text_field_name = "{name}".format(name=uuid.uuid4().hex)
            text_field_schema = '''
            <Field Type="Note" DisplayName="{name}_0" Hidden="TRUE" CanBeDeleted="TRUE" ShowInViewForms="FALSE"
                   StaticName="{text_field_name}" Name="{text_field_name}">
            </Field>
            '''.format(name=name, text_field_name=text_field_name)
            text_field = self.create_field_as_xml(text_field_schema)

            def _after_text_field_created(resp):
                field_params["text_field_id"] = text_field.properties["Id"]
                _create_taxonomy_field_inner()

            self.context.after_execute(_after_text_field_created, True)
        else:
            _create_taxonomy_field_inner()

        return target_field

    def _build_taxonomy_field_query(self, name, ssp_id, term_set_id, anchor_id,
                                    field_id=None, text_field_id=None, web_id=None, list_id=None,
                                    target_field=None):
        """

        :param str text_field_id: Text Field Id
        :param str web_id: Web Id
        :param str list_id: List Id
        :param str field_id: Field Id
        :type name: str
        :type ssp_id: str
        :type term_set_id: str
        :type anchor_id: str
        :type target_field: Field
        """

        list_attr = 'List="{{{list_id}}}"'.format(list_id=list_id) if list_id is not None else ""

        schema_xml = '''
<Field Type="TaxonomyFieldType" DisplayName="{name}" {list_attr}
       WebId="{web_id}" Required="FALSE" EnforceUniqueValues="FALSE"
       ID="{{{field_id}}}" StaticName="{name}" Name="{name}">
    <Default/>
    <Customization>
        <ArrayOfProperty>
            <Property>
                <Name>SspId</Name>
                <Value xmlns:q1="http://www.w3.org/2001/XMLSchema" p4:type="q1:string"
                       xmlns:p4="http://www.w3.org/2001/XMLSchema-instance">{ssp_id}
                </Value>
            </Property>
            <Property>
                <Name>GroupId</Name>
            </Property>
            <Property>
                <Name>TermSetId</Name>
                <Value xmlns:q2="http://www.w3.org/2001/XMLSchema" p4:type="q2:string"
                       xmlns:p4="http://www.w3.org/2001/XMLSchema-instance">{term_set_id}
                </Value>
            </Property>
            <Property>
                <Name>AnchorId</Name>
                <Value xmlns:q3="http://www.w3.org/2001/XMLSchema" p4:type="q3:string"
                       xmlns:p4="http://www.w3.org/2001/XMLSchema-instance">{anchor_id}
                </Value>
            </Property>
            <Property>
                <Name>UserCreated</Name>
                <Value xmlns:q4="http://www.w3.org/2001/XMLSchema" p4:type="q4:boolean"
                       xmlns:p4="http://www.w3.org/2001/XMLSchema-instance">false
                </Value>
            </Property>
            <Property>
                <Name>Open</Name>
                <Value xmlns:q5="http://www.w3.org/2001/XMLSchema" p4:type="q5:boolean"
                       xmlns:p4="http://www.w3.org/2001/XMLSchema-instance">true
                </Value>
            </Property>
            <Property>
                <Name>TextField</Name>
                <Value xmlns:q6="http://www.w3.org/2001/XMLSchema" p4:type="q6:string"
                       xmlns:p4="http://www.w3.org/2001/XMLSchema-instance">{{{text_field_id}}}
                </Value>
            </Property>
            <Property>
                <Name>IsPathRendered</Name>
                <Value xmlns:q7="http://www.w3.org/2001/XMLSchema" p4:type="q7:boolean"
                       xmlns:p4="http://www.w3.org/2001/XMLSchema-instance">false
                </Value>
            </Property>
            <Property>
                <Name>IsKeyword</Name>
                <Value xmlns:q8="http://www.w3.org/2001/XMLSchema" p4:type="q8:boolean"
                       xmlns:p4="http://www.w3.org/2001/XMLSchema-instance">false
                </Value>
            </Property>
            <Property>
                <Name>TargetTemplate</Name>
            </Property>
            <Property>
                <Name>CreateValuesInEditForm</Name>
                <Value xmlns:q9="http://www.w3.org/2001/XMLSchema" p4:type="q9:boolean"
                       xmlns:p4="http://www.w3.org/2001/XMLSchema-instance">false
                </Value>
            </Property>
            <Property>
                <Name>FilterAssemblyStrongName</Name>
                <Value xmlns:q10="http://www.w3.org/2001/XMLSchema" p4:type="q10:string"
                       xmlns:p4="http://www.w3.org/2001/XMLSchema-instance">Microsoft.SharePoint.Taxonomy,
                    Version=16.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c
                </Value>
            </Property>
            <Property>
                <Name>FilterClassName</Name>
                <Value xmlns:q11="http://www.w3.org/2001/XMLSchema" p4:type="q11:string"
                       xmlns:p4="http://www.w3.org/2001/XMLSchema-instance">Microsoft.SharePoint.Taxonomy.TaxonomyField
                </Value>
            </Property>
            <Property>
                <Name>FilterMethodName</Name>
                <Value xmlns:q12="http://www.w3.org/2001/XMLSchema" p4:type="q12:string"
                       xmlns:p4="http://www.w3.org/2001/XMLSchema-instance">GetFilteringHtml
                </Value>
            </Property>
            <Property>
                <Name>FilterJavascriptProperty</Name>
                <Value xmlns:q13="http://www.w3.org/2001/XMLSchema" p4:type="q13:string"
                       xmlns:p4="http://www.w3.org/2001/XMLSchema-instance">FilteringJavascript
                </Value>
            </Property>
        </ArrayOfProperty>
    </Customization>
</Field>
'''.format(list_id=list_id, name=name, list_attr=list_attr, web_id=web_id, field_id=field_id, ssp_id=ssp_id,
           term_set_id=term_set_id, anchor_id=anchor_id, text_field_id=text_field_id)

        field_schema = XmlSchemaFieldCreationInformation(schema_xml)
        self._create_field_as_xml_query(field_schema, target_field)

    def create_field_as_xml(self, schema_xml):
        """
        :type schema_xml: str
        """
        field = Field(self.context)
        field_schema = XmlSchemaFieldCreationInformation(schema_xml)
        self._create_field_as_xml_query(field_schema, field)
        return field

    def _create_field_as_xml_query(self, schema_xml, field):
        """
        :type field: Field
        :type schema_xml: XmlSchemaFieldCreationInformation
        """
        self.add_child(field)
        qry = ServiceOperationQuery(self, "CreateFieldAsXml", None, schema_xml, "parameters", field)
        self.context.add_query(qry)
        return field

    def get_by_id(self, _id):
        """Gets the fields with the specified ID."""
        return Field(self.context, ServiceOperationPath("getById", [_id], self.resource_path))

    def get_by_internal_name_or_title(self, name_title):
        """Returns the first field (2) in the collection based on the internal name or the title specified
        by the parameter.

        :param str name_title:  The title or internal name to look up the field (2) by.
        """
        return Field(self.context,
                     ServiceOperationPath("getByInternalNameOrTitle", [name_title], self.resource_path))

    def get_by_title(self, title):
        """Returns the first fields object in the collection based on the title of the specified fields.

        :type title: str
        """
        return Field(self.context,
                     ServiceOperationPath("getByTitle", [title], self.resource_path))
