from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.listitems.form_update_value import ListItemFormUpdateValue


class ListFormsAPI(Entity):
    def get_form_schema(self, container_guid: str, form_id: str, sharing_url: str) -> ClientResult[str]:
        """GetFormSchema operation.

        Args:
            container_guid (str):
                containerGuid parameter
            form_id (str):
                formId parameter
            sharing_url (str):
                sharingUrl parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self,
            "GetFormSchema",
            None,
            {"containerGuid": container_guid, "formId": form_id, "sharingUrl": sharing_url},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_form_schema_from_sharing_url(self, sharing_url: str) -> ClientResult[str]:
        """GetFormSchemaFromSharingUrl operation.

        Args:
            sharing_url (str):
                sharingUrl parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "GetFormSchemaFromSharingUrl", None, {"sharingUrl": sharing_url}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def submit_list_form(
        self,
        container_guid: str,
        form_id: str,
        form_values: ClientValueCollection[ListItemFormUpdateValue],
        sharing_url: str,
    ) -> ClientResult[ClientValueCollection[ListItemFormUpdateValue]]:
        """SubmitListForm operation.

        Args:
            container_guid (str):
                containerGuid parameter
            form_id (str):
                formId parameter
            form_values (ClientValueCollection[ListItemFormUpdateValue]):
                formValues parameter
            sharing_url (str):
                sharingUrl parameter
        """
        from office365.sharepoint.listitems.form_update_value import (
            ListItemFormUpdateValue,
        )

        return_type = ClientResult(self.context, ClientValueCollection[ListItemFormUpdateValue]())
        qry = ServiceOperationQuery(
            self,
            "SubmitListForm",
            None,
            {"containerGuid": container_guid, "formId": form_id, "formValues": form_values, "sharingUrl": sharing_url},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def submit_list_form_from_sharing_url(
        self, sharing_url: str, form_values: ClientValueCollection[ListItemFormUpdateValue]
    ) -> ClientResult[ClientValueCollection[ListItemFormUpdateValue]]:
        """SubmitListFormFromSharingUrl operation.

        Args:
            sharing_url (str):
                sharingUrl parameter
            form_values (ClientValueCollection[ListItemFormUpdateValue]):
                formValues parameter
        """
        from office365.sharepoint.listitems.form_update_value import (
            ListItemFormUpdateValue,
        )

        return_type = ClientResult(self.context, ClientValueCollection[ListItemFormUpdateValue]())
        qry = ServiceOperationQuery(
            self,
            "SubmitListFormFromSharingUrl",
            None,
            {"sharingUrl": sharing_url, "formValues": form_values},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type
