from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.contentsolution.add_template_fields_request import (
        AddTemplateFieldsRequest,
    )
    from office365.sharepoint.contentsolution.content_control_std_content import (
        ContentControlStdContent,
    )
    from office365.sharepoint.contentsolution.create_template_request import (
        CreateTemplateRequest,
    )
    from office365.sharepoint.contentsolution.document_field import DocumentField
    from office365.sharepoint.contentsolution.field_input import FieldInput
    from office365.sharepoint.contentsolution.template import Template
    from office365.sharepoint.contentsolution.update_template_field_request import (
        UpdateTemplateFieldRequest,
    )


class TemplateAPI(Entity):
    @property
    def entity_type_name(self) -> str:
        return "Microsoft.SharePoint.ContentSolution.API.TemplateAPI"

    def add_fields(self, request: AddTemplateFieldsRequest) -> ClientResult[ClientValueCollection[DocumentField]]:
        """addFields operation.

        Args:
            request (AddTemplateFieldsRequest):
                request parameter
        """
        from office365.sharepoint.contentsolution.document_field import DocumentField

        return_type = ClientResult(self.context, ClientValueCollection[DocumentField]())
        qry = ServiceOperationQuery(self, "addFields", None, {"request": request}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def create_document(self) -> Self:
        """createDocument operation."""
        qry = ServiceOperationQuery(self, "createDocument", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def create_template(self, request: CreateTemplateRequest) -> ClientResult[Template]:
        """createTemplate operation.

        Args:
            request (CreateTemplateRequest):
                request parameter
        """
        from office365.sharepoint.contentsolution.template import Template

        return_type = ClientResult(self.context, Template())
        qry = ServiceOperationQuery(self, "createTemplate", None, {"request": request}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def create_template_using_stream(
        self,
        document_folder_id: int,
        document_library_id: UUID,
        document_site_id: UUID,
        document_web_id: UUID,
        fields: ClientValueCollection[FieldInput],
        form_id: str,
        template_name: str,
        content_stream: bytes,
    ) -> ClientResult[Template]:
        """CreateTemplateUsingStream operation.

        Args:
            document_folder_id (int):
                DocumentFolderId parameter
            document_library_id (UUID):
                DocumentLibraryId parameter
            document_site_id (UUID):
                DocumentSiteId parameter
            document_web_id (UUID):
                DocumentWebId parameter
            fields (ClientValueCollection[FieldInput]):
                Fields parameter
            form_id (str):
                FormId parameter
            template_name (str):
                TemplateName parameter
            content_stream (bytes):
                contentStream parameter
        """
        from office365.sharepoint.contentsolution.template import Template

        return_type = ClientResult(self.context, Template())
        qry = ServiceOperationQuery(
            self,
            "CreateTemplateUsingStream",
            None,
            {
                "DocumentFolderId": document_folder_id,
                "DocumentLibraryId": document_library_id,
                "DocumentSiteId": document_site_id,
                "DocumentWebId": document_web_id,
                "Fields": fields,
                "FormId": form_id,
                "TemplateName": template_name,
                "contentStream": content_stream,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_content_control_standard_content(
        self, template_id: UUID, fetch_conditionals_only: bool
    ) -> ClientResult[ClientValueCollection[ContentControlStdContent]]:
        """getContentControlStandardContent operation.

        Args:
            template_id (UUID):
                templateId parameter
            fetch_conditionals_only (bool):
                fetchConditionalsOnly parameter
        """
        from office365.sharepoint.contentsolution.content_control_std_content import (
            ContentControlStdContent,
        )

        return_type = ClientResult(self.context, ClientValueCollection[ContentControlStdContent]())
        qry = FunctionQuery(
            self, "getContentControlStandardContent", [template_id, fetch_conditionals_only], return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_fields(self, template_id: UUID, version_type: int) -> ClientResult[ClientValueCollection[DocumentField]]:
        """getFields operation.

        Args:
            template_id (UUID):
                templateId parameter
            version_type (int):
                versionType parameter
        """
        from office365.sharepoint.contentsolution.document_field import DocumentField

        return_type = ClientResult(self.context, ClientValueCollection[DocumentField]())
        qry = FunctionQuery(self, "getFields", [template_id, version_type], return_type)
        self.context.add_query(qry)
        return return_type

    def get_template(self, template_id: UUID) -> ClientResult[Template]:
        """getTemplate operation.

        Args:
            template_id (UUID):
                templateId parameter
        """
        from office365.sharepoint.contentsolution.template import Template

        return_type = ClientResult(self.context, Template())
        qry = FunctionQuery(self, "getTemplate", [template_id], return_type)
        self.context.add_query(qry)
        return return_type

    def publish_template(self) -> Self:
        """publishTemplate operation."""
        qry = ServiceOperationQuery(self, "publishTemplate", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def update_field(self, request: UpdateTemplateFieldRequest) -> ClientResult[DocumentField]:
        """updateField operation.

        Args:
            request (UpdateTemplateFieldRequest):
                request parameter
        """
        from office365.sharepoint.contentsolution.document_field import DocumentField

        return_type = ClientResult(self.context, DocumentField())
        qry = ServiceOperationQuery(self, "updateField", None, {"request": request}, None, return_type)
        self.context.add_query(qry)
        return return_type
