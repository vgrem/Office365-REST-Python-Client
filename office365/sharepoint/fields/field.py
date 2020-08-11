from office365.runtime.client_query import DeleteEntityQuery
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.fields.field_type import FieldType


class Field(BaseEntity):
    """A container for metadata within a SharePoint list and associated list items."""

    def __init__(self, context, resource_path=None):
        super().__init__(context, resource_path)

    @staticmethod
    def resolve_field_type(type_id):
        from office365.sharepoint.fields.field_calculated import FieldCalculated
        from office365.sharepoint.fields.field_choice import FieldChoice
        from office365.sharepoint.fields.field_computed import FieldComputed
        from office365.sharepoint.fields.field_currency import FieldCurrency
        from office365.sharepoint.fields.field_guid import FieldGuid
        from office365.sharepoint.fields.field_lookup import FieldLookup
        from office365.sharepoint.fields.fieldMultiChoice import FieldMultiChoice
        from office365.sharepoint.fields.fieldMultiLineText import FieldMultiLineText
        from office365.sharepoint.fields.field_text import FieldText
        from office365.sharepoint.fields.field_url import FieldUrl
        from office365.sharepoint.fields.field_user import FieldUser
        field_types = {
            FieldType.Text: FieldText,
            FieldType.Calculated: FieldCalculated,
            FieldType.Choice: FieldChoice,
            FieldType.MultiChoice: FieldMultiChoice,
            FieldType.Lookup: FieldLookup,
            FieldType.User: FieldUser,
            FieldType.Computed: FieldComputed,
            FieldType.URL: FieldUrl,
            FieldType.Guid: FieldGuid,
            FieldType.Currency: FieldCurrency,
            FieldType.Note: FieldMultiLineText
        }
        return field_types.get(type_id, Field)

    @staticmethod
    def create_field_from_type(context, field_type):
        field_type = Field.resolve_field_type(field_type)
        return field_type(context)

    def set_show_in_display_form(self, flag):
        """Sets the value of the ShowInDisplayForm property for this fields.

        :type flag: bool
        """
        qry = ServiceOperationQuery(self, "setShowInDisplayForm", [flag])
        self.context.add_query(qry)

    def set_show_in_edit_form(self, flag):
        """Sets the value of the ShowInEditForm property for this fields.
        :type flag: bool
        """
        qry = ServiceOperationQuery(self, "setShowInEditForm", [flag])
        self.context.add_query(qry)

    def set_show_in_new_form(self, flag):
        """Sets the value of the ShowInNewForm property for this fields."""
        qry = ServiceOperationQuery(self, "setShowInNewForm", [flag])
        self.context.add_query(qry)

    def delete_object(self):
        """Deletes the fields."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()

    @property
    def internal_name(self):
        """Gets a value that specifies the field internal name.

        :rtype: str or None
        """
        return self.properties.get('InternalName', None)

    def set_property(self, name, value, persist_changes=True):
        super(Field, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if name == "Id" and self._resource_path is None:
            self._resource_path = ResourcePathServiceOperation(
                "getById", [value], self._parent_collection.resource_path)
        if name == "FieldTypeKind":
            self.__class__ = self.resolve_field_type(value)
