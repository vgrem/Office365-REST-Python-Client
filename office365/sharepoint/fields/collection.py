from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, TypeVar, Union, cast

from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.fields.calculated import FieldCalculated
from office365.sharepoint.fields.choice import FieldChoice
from office365.sharepoint.fields.creation_information import FieldCreationInformation
from office365.sharepoint.fields.date_time import FieldDateTime
from office365.sharepoint.fields.field import Field
from office365.sharepoint.fields.geolocation import FieldGeolocation
from office365.sharepoint.fields.multi_choice import FieldMultiChoice
from office365.sharepoint.fields.multi_line_text import FieldMultiLineText
from office365.sharepoint.fields.number import FieldNumber
from office365.sharepoint.fields.text import FieldText
from office365.sharepoint.fields.type import FieldType
from office365.sharepoint.fields.url import FieldUrl
from office365.sharepoint.fields.user import FieldUser
from office365.sharepoint.fields.xmlSchemaFieldCreationInformation import (
    XmlSchemaFieldCreationInformation,
)
from office365.sharepoint.taxonomy.field import TaxonomyField
from office365.sharepoint.taxonomy.sets.set import TermSet

T = TypeVar("T", bound=Field)

_FIELD_TYPE_BY_KIND = {
    "boolean": FieldType.Boolean,
    "datetime": FieldType.DateTime,
    "number": FieldType.Number,
    "text": FieldType.Text,
}


def field_type_from_kind(kind: str) -> FieldType:
    """Map a generic pandas dtype kind (see ``series_kind``) to a SharePoint ``FieldType``.

    Unknown kinds fall back to ``FieldType.Text``. Only the four basic column
    types can be inferred from a pandas dtype; richer SharePoint types (Choice,
    Lookup, User, URL, Currency, MultiLineText, ...) require an explicit
    ``schema`` passed to ``List.from_dataframe``.
    """
    return _FIELD_TYPE_BY_KIND.get(kind, FieldType.Text)


if TYPE_CHECKING:
    from office365.sharepoint.lists.list import List
    from office365.sharepoint.webs.web import Web


class FieldCollection(EntityCollection[Field]):
    """Represents a collection of Field resource."""

    def __init__(self, context, resource_path=None, parent=None):
        super().__init__(context, Field, resource_path, parent)

    def ensure_from_dataframe(self, df, progress=None, *, on_conflict: str = "skip") -> list[Field]:
        """Define a field per DataFrame column, inferring the field type.

        The schema counterpart of ``RecordCollection.from_dataframe`` (which
        imports rows): here each column becomes a field definition. Column names
        are sanitized into field internal names and the ``FieldType`` is inferred
        from the pandas dtype (Boolean/DateTime/Number/Text). Each field is
        ensured idempotently (looked up first, created when missing). Deferred —
        run the lookups/creates with ``execute_query()``.

        A column whose title collides with a built-in field (e.g. ``Name`` ->
        ``FileLeafRef``) is suffixed with ``_`` and a warning is emitted, since
        SharePoint cannot create a second column with that display name.

        Requires ``pip install office365-rest-python-client[pandas]``.

        Args:
            df: A pandas DataFrame whose columns become the field definitions.
            progress: Reserved (kept for signature parity).
            on_conflict: ``"skip"`` (default) or ``"update"``.

        Returns:
            list[Field]: The ensured fields.
        """
        import warnings

        from office365.runtime.converters.dataframe import require_pandas, series_kind
        from office365.sharepoint.fields.name import internal_field_name, is_reserved_field_title

        pd = require_pandas()
        fields: list[Field] = []
        for column in df.columns:
            if is_reserved_field_title(str(column)):
                warnings.warn(
                    f"Column '{column}' collides with a built-in SharePoint field; "
                    f"importing it as '{internal_field_name(str(column))}'.",
                    stacklevel=2,
                )
            field_type = field_type_from_kind(series_kind(pd, df[column]))
            info = FieldCreationInformation(
                Title=internal_field_name(str(column)),
                FieldTypeKind=field_type,
            )
            fields.append(self.ensure(info, on_conflict=on_conflict))
        return fields

    def ensure(self, parameters: FieldCreationInformation, *, on_conflict: str = "skip") -> Field:
        """Ensure the field exists (get-or-create); ``on_conflict="update"`` reconciles it.

        Rich columns are supported: populate ``FieldCreationInformation`` with
        ``Choices`` (Choice/MultiChoice), ``Formula`` (Calculated), ``Required``,
        or ``LookupListId``/``LookupFieldName`` (Lookup). With
        ``on_conflict="update"`` the field kind, description, choices and formula
        are reconciled, and ``Required`` is turned on when requested — a lookup's
        target list is create-only and is never retargeted on a re-run.

        ``Choices``/``Formula`` are reconciled only when set, and ``Required`` is
        only turned on (never off), so a bare ``ensure`` never silently relaxes an
        existing column. Deferred — run with ``execute_query()``.
        """
        from office365.runtime.queries.get_or_create import get_or_create

        return_type = self.get_by_title(parameters.Title)

        def _reconcile(field: Field) -> None:
            changed = False
            if parameters.FieldTypeKind is not None and field.field_type_kind != parameters.FieldTypeKind:
                field.set_property("FieldTypeKind", parameters.FieldTypeKind)
                changed = True
            if parameters.Description is not None and field.properties.get("Description") != parameters.Description:
                field.set_property("Description", parameters.Description)
                changed = True
            if parameters.Choices is not None and list(field.properties.get("Choices") or []) != list(
                parameters.Choices
            ):
                field.set_property("Choices", StringCollection(list(parameters.Choices)))
                changed = True
            if parameters.Formula is not None and field.properties.get("Formula") != parameters.Formula:
                field.set_property("Formula", parameters.Formula)
                changed = True
            if parameters.Required and field.properties.get("Required") is not True:
                field.set_property("Required", True)
                changed = True
            if changed:
                field.update()

        return get_or_create(
            find=return_type.get,
            create_query=lambda: self._build_add_field_query(parameters, return_type),
            return_type=return_type,
            on_conflict=on_conflict,
            reconcile=_reconcile,
        )

    def ensure_xml(self, schema_xml: str, internal_name: str, *, on_conflict: str = "skip") -> Field:
        """Ensure a column defined by raw schema XML exists (idempotent).

        The companion of :meth:`create_field_as_xml` with get-or-create
        semantics: the column is looked up by ``internal_name`` and, when
        missing, created from ``schema_xml``. This preserves a source column's
        exact definition (choices, formula, lookup target, ...) that a
        :class:`FieldCreationInformation` spec cannot always express. Deferred —
        run with ``execute_query()``.

        Args:
            schema_xml (str): The schema that defines the field
                (see :meth:`~office365.sharepoint.fields.field.Field.schema_xml_for_copy`).
            internal_name (str): The internal name used to look the column up.
            on_conflict (str): ``"skip"`` (default, keep an existing column) or
                ``"update"``.
        """
        from office365.runtime.queries.get_or_create import get_or_create

        return_type = self.get_by_internal_name_or_title(internal_name)
        return get_or_create(
            find=return_type.get,
            create_query=lambda: self._build_create_field_as_xml_query(schema_xml, return_type),
            return_type=return_type,
            on_conflict=on_conflict,
        )

    def add_calculated(self, title: str, formula: str, description: Optional[str] = None) -> FieldCalculated:
        """Creates a Calculated field

        Args:
            title (str): Specifies the display name of the field
            formula (str): Specifies the formula for the field
            description (str or None): Specifies the description of the field
        """
        return_type = self.add_field(
            FieldCreationInformation(
                Title=title,
                Formula=formula,
                FieldTypeKind=FieldType.Calculated,
                Description=description,
            ),
            FieldCalculated,
        )
        return return_type

    def add_datetime(self, title: str, description: Optional[str] = None) -> FieldDateTime:
        """Creates DateTime field

        Args:
            title (str): Specifies the display name of the field
            description (str or None): Specifies the description of the field
        """
        return_type = self.add_field(
            FieldCreationInformation(
                Title=title,
                Description=description,
                FieldTypeKind=FieldType.DateTime,
            ),
            FieldDateTime,
        )
        return return_type

    def add_geolocation_field(self, title: str, description: Optional[str] = None) -> FieldGeolocation:
        """Creates Geolocation field

        Args:
            title (str): Specifies the display name of the field
            description (str or None): Specifies the description of the field
        """
        return_type = self.add_field(
            FieldCreationInformation(
                Title=title,
                Description=description,
                FieldTypeKind=FieldType.Geolocation,
            ),
            FieldGeolocation,
        )
        return return_type

    def add_number(self, title: str, description: Optional[str] = None) -> FieldNumber:
        """Creates Number field

        Args:
            title (str): Specifies the display name of the field
            description (str or None): Specifies the description of the field
        """
        return_type = self.add_field(
            FieldCreationInformation(
                Title=title,
                Description=description,
                FieldTypeKind=FieldType.Number,
            ),
            FieldNumber,
        )
        return return_type

    def add_url_field(self, title: str, description: Optional[str] = None) -> FieldUrl:
        """Creates Url field

        Args:
            title (str): Specifies the display name of the field
            description (str or None):
        """
        return self.add_field(
            FieldCreationInformation(Title=title, Description=description, FieldTypeKind=FieldType.URL),
            FieldUrl,
        )

    def add_lookup_field(
        self,
        title: str,
        lookup_list: Union[str, "List"],
        lookup_field_name: str,
        allow_multiple_values: bool = False,
    ):
        """Creates a Lookup field

        Args:
            allow_multiple_values (bool): Flag determines whether to create multi lookup field or not
            lookup_field_name (str): Specifies the name of the field in the other data source when creating a lookup
                field
            lookup_list (str or office365.sharepoint.lists.list.List): Lookup List object or identifier
            title (str): Specifies the display name of the field.
        """
        from office365.sharepoint.fields.lookup import FieldLookup

        return_type = FieldLookup(self.context)

        def _add_lookup_field(lookup_list_id: str) -> None:
            if allow_multiple_values:
                field_schema = """
                        <Field Type="LookupMulti" Mult="TRUE" DisplayName="{title}" Required="FALSE" Hidden="TRUE" \
                        ShowField="{lookup_field_name}" List="{{{lookup_list_id}}}" StaticName="{title}" Name="{title}">
                        </Field>
                        """.format(title=title, lookup_field_name=lookup_field_name, lookup_list_id=lookup_list_id)
                self.create_field_as_xml(field_schema, return_type)
            else:
                self.add_field(
                    FieldCreationInformation(
                        Title=title,
                        LookupListId=lookup_list_id,
                        LookupFieldName=lookup_field_name,
                        FieldTypeKind=FieldType.Lookup,
                    ),
                    return_type,
                )

        from office365.sharepoint.lists.list import List

        if isinstance(lookup_list, List):

            def _lookup_list_loaded():
                lookup_list_id = lookup_list.id
                if lookup_list_id is not None:
                    _add_lookup_field(lookup_list_id)

            lookup_list.ensure_property("Id").after_execute(lambda _: _lookup_list_loaded())
        else:
            _add_lookup_field(lookup_list)
        return return_type

    def add_choice_field(self, title: str, values: list[str], multiple_values: bool = False) -> Field:
        """Creates a Choice field

        Args:
            multiple_values (bool):
            values (list[str]):
            title (str): Specifies the display name of the field.
        """
        fld_type = FieldType.MultiChoice if multiple_values else FieldType.Choice
        field_cls = FieldMultiChoice if multiple_values else FieldChoice
        create_field_info = FieldCreationInformation(Title=title, FieldTypeKind=fld_type, Choices=values)
        return self.add_field(create_field_info, field_cls)

    def add_user_field(
        self,
        title: str,
        description: Optional[str] = None,
        selection_mode=None,
        allow_multiple_values: bool = False,
    ) -> FieldUser:
        """Creates a User field

        Args:
            title (str): Specifies the display name of the field
            description (str or None):
            selection_mode (int or None):
            allow_multiple_values (bool):
        """
        return self._create_field(
            FieldUser,
            FieldTypeKind=FieldType.User.value,
            Title=title,
            Description=description,
            SelectionMode=selection_mode,
            AllowMultipleValues=allow_multiple_values,
        )

    def add_text_field(self, title: str) -> FieldText:
        """Creates a Text field

        Args:
            title (str): specifies the display name of the field
        """
        return self.add_field(FieldCreationInformation(title, FieldType.Text), FieldText)

    def add_note(self, title: str, description: Optional[str] = None) -> FieldMultiLineText:
        """Creates a text field that can contain multiple lines"""
        return self.add_field(FieldCreationInformation(title, FieldType.Note, description), FieldMultiLineText)

    def add_dependent_lookup_field(self, display_name: str, primary_lookup_field_id: str, show_field: bool) -> Field:
        """Adds a secondary lookup field to a field collection (target).
        Args:
            display_name (str): title of the added field in the target FieldCollection.
            primary_lookup_field_id (str): ID of the main lookup-field in the target to
                associate the dependent lookup field with.
            show_field (str): name of the field from the source list to include data from.
        Returns:
            Field: reference to the SP.Field that was added.
        """
        return_type = Field(self.context)
        self.add_child(return_type)
        parameters = {
            "displayName": display_name,
            "primaryLookupFieldId": primary_lookup_field_id,
            "showField": show_field,
        }
        qry = ServiceOperationQuery(self, "AddDependentLookupField", None, parameters, None, return_type)
        self.context.add_query(qry)
        return return_type

    def add(self, field_type_kind: FieldType, **parameters: Any) -> Field:
        """Adds a fields to the fields collection."""
        return self._create_field(
            Field.resolve_field_type(field_type_kind.value),
            FieldTypeKind=field_type_kind.value,
            **parameters,
        )

    def _new_field(self, target: Union[type[T], T]) -> T:
        """Resolve a concrete field class (or reuse the given instance) on this context."""
        return target(self.context) if isinstance(target, type) else target

    def _create_field(self, field_type: Union[type[T], T], **parameters: Any) -> T:
        """Create a field entity of the given type and queue its creation query."""
        return_type = self._new_field(field_type)
        [return_type.set_property(k, v) for k, v in parameters.items() if v is not None]
        self.add_child(return_type)
        qry = CreateEntityQuery(self, return_type, return_type)
        self.context.add_query(qry)
        return return_type

    def _build_add_field_query(
        self,
        parameters: FieldCreationInformation,
        return_type: Field,
    ) -> ServiceOperationQuery:
        """Build (but do not queue) an AddField query for the given parameters."""
        self.add_child(return_type)
        payload = {"parameters": parameters}
        return ServiceOperationQuery(self, "AddField", None, payload, None, return_type)

    def add_field(self, parameters: FieldCreationInformation, return_type: Union[type[T], T] = Field) -> T:
        """Adds a fields to the fields collection.

        Args:
            parameters (FieldCreationInformation):
            return_type (type or Field): The concrete field class to create (e.g.
              ``FieldDateTime``), or a ready field instance to bind the query to
              (used for deferred/async creation).
        """
        field = self._new_field(return_type)
        self.context.add_query(self._build_add_field_query(parameters, field))
        return field

    def create_taxonomy_field(
        self,
        name: str,
        term_set: Union[str, TermSet],
        allow_multiple_values: bool = False,
    ) -> TaxonomyField:
        """Creates a Taxonomy field

        Args:
            name (str): Field name
            term_set (str or TermSet): TermSet identifier or object
            allow_multiple_values (bool): Specifies whether the column will allow more than one value
        """
        tax = self.context.taxonomy

        # resolve the identifiers on the taxonomy service (``_api/v2.1``, OData V4)
        term_store = tax.term_store.get().execute_query()
        if isinstance(term_set, TermSet):
            term_set.ensure_property("id").execute_query()
            term_set_id = term_set.id
        else:
            term_set_id = term_set
        term_store_id = term_store.id
        if not term_store_id or not term_set_id:
            raise ValueError("Unable to resolve the term store or term set identifier")

        # the field creation itself runs on this (OData V3) context
        return_type = TaxonomyField(self.context)
        TaxonomyField.create(
            self,
            name,
            term_set_id,
            term_store_id,
            allow_multiple_values,
            return_type=return_type,
        )
        return return_type

    def _build_create_field_as_xml_query(self, schema_xml: str, return_type: Field) -> ServiceOperationQuery:
        """Build (but do not queue) a ``CreateFieldAsXml`` query for the given schema."""
        self.add_child(return_type)
        payload = {"parameters": XmlSchemaFieldCreationInformation(schema_xml)}
        return ServiceOperationQuery(self, "CreateFieldAsXml", None, payload, None, return_type)

    def create_field_as_xml(self, schema_xml: str, return_type: Union[type[T], T] = Field) -> T:
        """Creates a field based on the values defined in the parameters input parameter.

        Args:
            schema_xml (str): Specifies the schema that defines the field
            return_type (type or Field): The concrete field class to create, or a
              ready field instance to bind the query to (deferred/async creation).
        """
        field = self._new_field(return_type)
        self.context.add_query(self._build_create_field_as_xml_query(schema_xml, field))
        return field

    def get_by_id(self, id_: str, field_type: type[T] = Field) -> T:
        """Gets the fields with the specified ID.

        Args:
            id_ (str): The field identifier.
            field_type (type): The concrete field class the column holds (e.g.
              ``FieldDateTime``); defaults to ``Field``.
        """
        return field_type(self.context, ServiceOperationPath("getById", [id_], self.resource_path))

    def get_by_internal_name_or_title(self, value: str, field_type: type[T] = Field) -> T:
        """Returns the first field in the collection based on the internal name or the title specified
        by the parameter.

        Args:
            value (str): The title or internal name to look up the field (2) by.
            field_type (type): The concrete field class the column holds (e.g.
              ``FieldDateTime``); defaults to ``Field``.
        """
        return field_type(
            self.context,
            ServiceOperationPath("getByInternalNameOrTitle", [value], self.resource_path),
        )

    def get_by_title(self, title: str, field_type: type[T] = Field) -> T:
        """Returns the first fields object in the collection based on the title of the specified fields.

        Args:
            title (str): The title to look up the field by
            field_type (type): The concrete field class the column holds (e.g.
              ``FieldDateTime``); defaults to ``Field``.
        """
        return field_type(
            self.context,
            ServiceOperationPath("getByTitle", [title], self.resource_path),
        )

    @property
    def parent(self) -> Union[Web, List]:
        """Gets the parent object which must be either a Web or List.

        Returns:
            The parent Web or List object

        Raises:
            TypeError: If parent is not set or is of unexpected type
        """
        from office365.sharepoint.lists.list import List
        from office365.sharepoint.webs.web import Web

        if self._parent is None:
            raise RuntimeError(
                "This collection must be associated with either:\n"
                "1. A SharePoint List (for list fields)\n"
                "2. A SharePoint Web (for site fields)\n"
                "Current parent is not initialized."
            )

        if isinstance(self._parent, (Web, List)):
            return cast(Union[Web, List], self._parent)

        raise TypeError(f"Unexpected parent type: {type(self._parent).__name__}")
