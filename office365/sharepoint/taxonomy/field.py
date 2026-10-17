from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional, cast

from office365.runtime.types.odata_property import odata
from office365.sharepoint.fields.lookup import FieldLookup
from office365.sharepoint.fields.multi_line_text import FieldMultiLineText
from office365.sharepoint.taxonomy.create_xml_parameters import (
    TaxonomyFieldCreateXmlParameters,
)

if TYPE_CHECKING:
    from office365.sharepoint.fields.collection import FieldCollection


class TaxonomyField(FieldLookup):
    """Represents a taxonomy field."""

    def set_field_value_by_value(self, item, tax_value):
        """
        Sets the value of the corresponding field in the list item to the value of the specified TaxonomyFieldValue

        Args:
            item: The ListItem object whose field is to be updated.
            tax_value: The TaxonomyFieldValue object whose value is to be used to update this field.
        """

        def _set_field_value_by_value():
            item.set_property(self.internal_name, tax_value)

        self.ensure_property("InternalName").after_execute(lambda _: _set_field_value_by_value())
        return self

    @staticmethod
    def create(
        fields: FieldCollection,
        name: str,
        term_set_id: str,
        term_store_id: str | None = None,
        allow_multiple_values: bool = False,
        return_type: TaxonomyField | None = None,
    ):
        """
        Args:
            name: Field name
            term_set_id: Term set identifier
            term_store_id: Term store identifier
            allow_multiple_values: Specifies whether the column will allow more than one value
            return_type: Return type
        """
        if return_type is None:
            return_type = TaxonomyField(fields.context)
        fields.add_child(return_type)
        params = TaxonomyFieldCreateXmlParameters(
            Name=name,
            TermSetId=term_set_id,
            SspId=term_store_id,
            FieldId=str(uuid.uuid4()),
            AllowMultipleValues=allow_multiple_values,
        )

        def _create_taxonomy_field_inner():
            # A taxonomy column's ``List`` attribute names the web's hidden
            # TaxonomyHiddenList -- *not* the list the column is added to. Emitting
            # the containing list's id here makes SharePoint set the column's
            # ``LookupList`` to that list, after which every value read fails with
            # ``SPFieldValidationException`` ("the given guid does not exist in the
            # term store"). Creating the column without a ``List`` attribute lets
            # SharePoint bind it to the taxonomy hidden list automatically.
            def _web_loaded():
                params.WebId = fields.context.web.id
                fields.create_field_as_xml(params.schema_xml, return_type)

            fields.context.web.ensure_property("Id").after_execute(lambda _: _web_loaded())

        def _text_field_created(text_field: FieldMultiLineText) -> None:
            params.TextFieldId = text_field.id
            _create_taxonomy_field_inner()

        return_type._create_text_field(name).after_execute(_text_field_created)
        return return_type

    def _create_text_field(self, name: str):
        """Creates hidden text field"""
        text_field_name = f"{uuid.uuid4().hex}"
        text_field_schema = """
                    <Field Type="Note" DisplayName="{name}_0" Hidden="TRUE" CanBeDeleted="TRUE" ShowInViewForms="FALSE"
                           CanToggleHidden="TRUE" StaticName="{text_field_name}" Name="{text_field_name}">
                    </Field>
                """.format(name=name, text_field_name=text_field_name)
        return self.parent_collection.create_field_as_xml(text_field_schema)

    @property
    def anchor_id(self) -> str | None:
        """Gets or sets the GUID of the anchor Term object for a TaxonomyField object."""
        return self.properties.get("AnchorId", None)

    @property
    def create_values_in_edit_form(self) -> bool | None:
        """
        Specifies a Boolean value that specifies whether the new Term  objects can be added to the
        TermSet while typing in the TaxonomyField editor control.
        """
        return self.properties.get("CreateValuesInEditForm", None)

    @property
    def is_anchor_valid(self) -> bool | None:
        """Gets a Boolean value that specifies whether the Term object identified by the AnchorId property is valid."""
        return self.properties.get("IsAnchorValid", None)

    @property
    def is_doc_tags_enabled(self) -> bool | None:
        """ """
        return self.properties.get("IsDocTagsEnabled", None)

    @property
    def is_keyword(self) -> bool | None:
        """
        Specifies a Boolean value that indicates whether the TaxonomyField value points to the
        keywords term set  object.
        """
        return self.properties.get("IsKeyword", None)

    @property
    def is_path_rendered(self) -> bool | None:
        """
        Specifies a Boolean value that specifies whether the default Label objects of all the parent
        Term objects of a Term in the TaxonomyField object will be rendered in
        addition to the default label of that Term.
        """
        return self.properties.get("IsPathRendered", None)

    @property
    def is_term_set_valid(self) -> bool | None:
        """
        Gets a Boolean value that specifies whether the TermSet object identified by the TermSetId
        property exists and is available for tagging.
        """
        return self.properties.get("IsTermSetValid", None)

    @property
    def open(self) -> bool | None:
        """
        Specifies a Boolean value that specifies whether the TaxonomyField object is linked to an
        open TermSet (section 3.1.5.20) object or a closed TermSet.
        """
        return self.properties.get("Open", None)

    @property
    def ssp_id(self) -> str | None:
        """
        Specifies the GUID that identifies the TermStore object, which contains the Enterprise
        keywords for the site that the current TaxonomyField belongs to.
        """
        return self.properties.get("SspId", None)

    @property
    def target_template(self) -> str | None:
        """
        Specifies the Web-relative Uniform Resource Locator (URL) of the target page that is used to construct the
        hyperlink on each Term object when the TaxonomyField (section 3.1.5.27) object is rendered.
        """
        return self.properties.get("TargetTemplate", None)

    @property
    def term_set_id(self) -> str | None:
        """
        Specifies the GUID of the TermSet object that contains the Term
        objects used by the current TaxonomyField () object.
        """
        return self.properties.get("TermSetId", None)

    @odata(name="TextField")
    @property
    def text_field_id(self) -> str | None:
        """Gets the GUID that identifies the hidden text field in an item."""
        return self.properties.get("TextField", None)

    @property
    def text_field(self) -> FieldMultiLineText:
        """Gets the hidden text field in an item."""
        text_field_id = self.text_field_id
        assert text_field_id is not None
        return cast(FieldMultiLineText, self.parent_collection.parent.fields.get_by_id(text_field_id))

    @property
    def user_created(self) -> bool | None:
        """
        Specifies a Boolean value that specifies whether the TaxonomyField object is linked to a
        customized TermSet object.
        """
        return self.properties.get("UserCreated", None)

    @property
    def parent_collection(self) -> FieldCollection:
        from office365.sharepoint.fields.collection import FieldCollection

        return cast(FieldCollection, self._parent_collection)

    @property
    def entity_type_name(self) -> str:
        return "SP.Taxonomy.TaxonomyField"

    @property
    def is_enhanced_image_tagging_enabled(self) -> Optional[bool]:
        """Gets the IsEnhancedImageTaggingEnabled property"""
        return self.properties.get("IsEnhancedImageTaggingEnabled", None)
