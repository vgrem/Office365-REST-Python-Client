from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.approvals.mediaserviceupdateparameters import (
        MediaServiceUpdateParameters,
    )
    from office365.sharepoint.listitems.delete_parameters import (
        ListItemDeleteParameters,
    )
    from office365.sharepoint.listitems.form_update_value import ListItemFormUpdateValue
    from office365.sharepoint.listitems.update_parameters import (
        ListItemUpdateParameters,
    )
    from office365.sharepoint.listitems.updateresults import ListItemUpdateResults
    from office365.sharepoint.permissions.base_permissions import BasePermissions
    from office365.sharepoint.webs.spimageitem import SPImageItem
    from office365.sharepoint.workflow.labelaccesscontroldata import (
        LabelAccessControlData,
    )


class SPWorkflowTask(Entity):
    @property
    def entity_type_name(self) -> str:
        return "SP.Workflow.SPWorkflowTask"

    def break_role_inheritance(self, copy_role_assignments: bool, clear_subscopes: bool) -> Self:
        """BreakRoleInheritance operation.

        Args:
            copy_role_assignments (bool):
                copyRoleAssignments parameter
            clear_subscopes (bool):
                clearSubscopes parameter
        """
        qry = ServiceOperationQuery(
            self,
            "BreakRoleInheritance",
            None,
            {"copyRoleAssignments": copy_role_assignments, "clearSubscopes": clear_subscopes},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def reset_role_inheritance(self) -> Self:
        """ResetRoleInheritance operation."""
        qry = ServiceOperationQuery(self, "ResetRoleInheritance", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def add_thumbnail_field_data(
        self, image_stream: bytes, image_name: str, field_internal_name: str, lock_id: str
    ) -> ClientResult[SPImageItem]:
        """AddThumbnailFieldData operation.

        Args:
            image_stream (bytes):
                imageStream parameter
            image_name (str):
                imageName parameter
            field_internal_name (str):
                fieldInternalName parameter
            lock_id (str):
                lockId parameter
        """
        from office365.sharepoint.webs.spimageitem import SPImageItem

        return_type = ClientResult(self.context, SPImageItem())
        qry = ServiceOperationQuery(
            self,
            "AddThumbnailFieldData",
            None,
            {
                "imageStream": image_stream,
                "imageName": image_name,
                "fieldInternalName": field_internal_name,
                "lockId": lock_id,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def archive(self) -> ClientResult[str]:
        """Archive operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "Archive", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def delete_with_parameters(self, parameters: ListItemDeleteParameters) -> Self:
        """DeleteWithParameters operation.

        Args:
            parameters (ListItemDeleteParameters):
                parameters parameter
        """
        qry = ServiceOperationQuery(self, "DeleteWithParameters", None, {"parameters": parameters}, None, None)
        self.context.add_query(qry)
        return self

    def do_entities_have_access_to_label(
        self, people_picker_input: str
    ) -> ClientResult[ClientValueCollection[LabelAccessControlData]]:
        """DoEntitiesHaveAccessToLabel operation.

        Args:
            people_picker_input (str):
                peoplePickerInput parameter
        """
        from office365.sharepoint.workflow.labelaccesscontroldata import (
            LabelAccessControlData,
        )

        return_type = ClientResult(self.context, ClientValueCollection[LabelAccessControlData]())
        qry = ServiceOperationQuery(
            self, "DoEntitiesHaveAccessToLabel", None, {"peoplePickerInput": people_picker_input}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def folder_archive_progress(self) -> ClientResult[str]:
        """FolderArchiveProgress operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "FolderArchiveProgress", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def folder_unarchive_progress(self) -> ClientResult[str]:
        """FolderUnarchiveProgress operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "FolderUnarchiveProgress", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_user_effective_permissions(self, user_name: str) -> ClientResult[BasePermissions]:
        """GetUserEffectivePermissions operation.

        Args:
            user_name (str):
                userName parameter
        """
        from office365.sharepoint.permissions.base_permissions import BasePermissions

        return_type = ClientResult(self.context, BasePermissions())
        qry = FunctionQuery(self, "GetUserEffectivePermissions", [user_name], return_type)
        self.context.add_query(qry)
        return return_type

    def get_wopi_frame_url(self, action: int) -> ClientResult[str]:
        """GetWOPIFrameUrl operation.

        Args:
            action (int):
                action parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetWOPIFrameUrl", None, {"action": action}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def media_service_update(self, parameters: MediaServiceUpdateParameters) -> Self:
        """MediaServiceUpdate operation.

        Args:
            parameters (MediaServiceUpdateParameters):
                parameters parameter
        """
        qry = ServiceOperationQuery(self, "MediaServiceUpdate", None, {"parameters": parameters}, None, None)
        self.context.add_query(qry)
        return self

    def media_service_update_v2(self, parameters: MediaServiceUpdateParameters, event_firing_enabled: bool) -> Self:
        """MediaServiceUpdateV2 operation.

        Args:
            parameters (MediaServiceUpdateParameters):
                parameters parameter
            event_firing_enabled (bool):
                eventFiringEnabled parameter
        """
        qry = ServiceOperationQuery(
            self,
            "MediaServiceUpdateV2",
            None,
            {"parameters": parameters, "eventFiringEnabled": event_firing_enabled},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def override_policy_tip(self, user_action: int, justification: str) -> ClientResult[int]:
        """OverridePolicyTip operation.

        Args:
            user_action (int):
                userAction parameter
            justification (str):
                justification parameter
        """
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(
            self,
            "OverridePolicyTip",
            None,
            {"userAction": user_action, "justification": justification},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def parse_and_set_field_value(self, field_name: str, value: str) -> Self:
        """ParseAndSetFieldValue operation.

        Args:
            field_name (str):
                fieldName parameter
            value (str):
                value parameter
        """
        qry = ServiceOperationQuery(
            self, "ParseAndSetFieldValue", None, {"fieldName": field_name, "value": value}, None, None
        )
        self.context.add_query(qry)
        return self

    def recycle(self) -> ClientResult[UUID]:
        """Recycle operation."""
        return_type = ClientResult(self.context, UUID(int=0))
        qry = ServiceOperationQuery(self, "Recycle", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def recycle_with_parameters(self, parameters: ListItemDeleteParameters) -> ClientResult[UUID]:
        """RecycleWithParameters operation.

        Args:
            parameters (ListItemDeleteParameters):
                parameters parameter
        """
        return_type = ClientResult(self.context, UUID(int=0))
        qry = ServiceOperationQuery(self, "RecycleWithParameters", None, {"parameters": parameters}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def render_list_item_data_as_stream(self, options: int) -> ClientResult[bytes]:
        """RenderListItemDataAsStream operation.

        Args:
            options (int):
                options parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = FunctionQuery(self, "RenderListItemDataAsStream", [options], return_type, return_raw_content=True)
        self.context.add_query(qry)
        return return_type

    def set_comments_disabled(self, value: bool) -> Self:
        """SetCommentsDisabled operation.

        Args:
            value (bool):
                value parameter
        """
        qry = ServiceOperationQuery(self, "SetCommentsDisabled", None, {"value": value}, None, None)
        self.context.add_query(qry)
        return self

    def set_compliance_tag(
        self,
        compliance_tag: str,
        is_tag_policy_hold: bool,
        is_tag_policy_record: bool,
        is_event_based_tag: bool,
        is_tag_super_lock: bool,
        is_unlocked_as_default: bool,
    ) -> Self:
        """SetComplianceTag operation.

        Args:
            compliance_tag (str):
                complianceTag parameter
            is_tag_policy_hold (bool):
                isTagPolicyHold parameter
            is_tag_policy_record (bool):
                isTagPolicyRecord parameter
            is_event_based_tag (bool):
                isEventBasedTag parameter
            is_tag_super_lock (bool):
                isTagSuperLock parameter
            is_unlocked_as_default (bool):
                isUnlockedAsDefault parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetComplianceTag",
            None,
            {
                "complianceTag": compliance_tag,
                "isTagPolicyHold": is_tag_policy_hold,
                "isTagPolicyRecord": is_tag_policy_record,
                "isEventBasedTag": is_event_based_tag,
                "isTagSuperLock": is_tag_super_lock,
                "isUnlockedAsDefault": is_unlocked_as_default,
            },
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_compliance_tag_with_explicit_metas_update(
        self, compliance_tag: str, compliance_flags: int, compliance_tag_written_time: datetime, user_email_address: str
    ) -> Self:
        """SetComplianceTagWithExplicitMetasUpdate operation.

        Args:
            compliance_tag (str):
                complianceTag parameter
            compliance_flags (int):
                complianceFlags parameter
            compliance_tag_written_time (datetime):
                complianceTagWrittenTime parameter
            user_email_address (str):
                userEmailAddress parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetComplianceTagWithExplicitMetasUpdate",
            None,
            {
                "complianceTag": compliance_tag,
                "complianceFlags": compliance_flags,
                "complianceTagWrittenTime": compliance_tag_written_time,
                "userEmailAddress": user_email_address,
            },
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_compliance_tag_with_hold(self, compliance_tag: str) -> Self:
        """SetComplianceTagWithHold operation.

        Args:
            compliance_tag (str):
                complianceTag parameter
        """
        qry = ServiceOperationQuery(
            self, "SetComplianceTagWithHold", None, {"complianceTag": compliance_tag}, None, None
        )
        self.context.add_query(qry)
        return self

    def set_compliance_tag_with_meta_info(
        self,
        compliance_tag: str,
        block_delete: bool,
        block_edit: bool,
        compliance_tag_written_time: datetime,
        user_email_address: str,
        is_tag_super_lock: bool,
        is_record_unlocked_as_default: bool,
    ) -> Self:
        """SetComplianceTagWithMetaInfo operation.

        Args:
            compliance_tag (str):
                complianceTag parameter
            block_delete (bool):
                blockDelete parameter
            block_edit (bool):
                blockEdit parameter
            compliance_tag_written_time (datetime):
                complianceTagWrittenTime parameter
            user_email_address (str):
                userEmailAddress parameter
            is_tag_super_lock (bool):
                isTagSuperLock parameter
            is_record_unlocked_as_default (bool):
                isRecordUnlockedAsDefault parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetComplianceTagWithMetaInfo",
            None,
            {
                "complianceTag": compliance_tag,
                "blockDelete": block_delete,
                "blockEdit": block_edit,
                "complianceTagWrittenTime": compliance_tag_written_time,
                "userEmailAddress": user_email_address,
                "isTagSuperLock": is_tag_super_lock,
                "isRecordUnlockedAsDefault": is_record_unlocked_as_default,
            },
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_compliance_tag_with_no_hold(self, compliance_tag: str) -> Self:
        """SetComplianceTagWithNoHold operation.

        Args:
            compliance_tag (str):
                complianceTag parameter
        """
        qry = ServiceOperationQuery(
            self, "SetComplianceTagWithNoHold", None, {"complianceTag": compliance_tag}, None, None
        )
        self.context.add_query(qry)
        return self

    def set_compliance_tag_with_record(self, compliance_tag: str) -> Self:
        """SetComplianceTagWithRecord operation.

        Args:
            compliance_tag (str):
                complianceTag parameter
        """
        qry = ServiceOperationQuery(
            self, "SetComplianceTagWithRecord", None, {"complianceTag": compliance_tag}, None, None
        )
        self.context.add_query(qry)
        return self

    def system_update(self) -> Self:
        """SystemUpdate operation."""
        qry = ServiceOperationQuery(self, "SystemUpdate", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def unarchive(self) -> ClientResult[str]:
        """Unarchive operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "Unarchive", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def update_ex(self, parameters: ListItemUpdateParameters) -> Self:
        """UpdateEx operation.

        Args:
            parameters (ListItemUpdateParameters):
                parameters parameter
        """
        qry = ServiceOperationQuery(self, "UpdateEx", None, {"parameters": parameters}, None, None)
        self.context.add_query(qry)
        return self

    def update_overwrite_version(self) -> Self:
        """UpdateOverwriteVersion operation."""
        qry = ServiceOperationQuery(self, "UpdateOverwriteVersion", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def validate_update_fetch_list_item(
        self,
        form_values: ClientValueCollection[ListItemFormUpdateValue],
        bnew_document_update: bool,
        check_in_comment: str,
        dates_in_utc: bool,
        number_in_invariant_culture: bool,
        view: str,
        root_folder: str,
    ) -> ClientResult[ListItemUpdateResults]:
        """ValidateUpdateFetchListItem operation.

        Args:
            form_values (ClientValueCollection[ListItemFormUpdateValue]):
                formValues parameter
            bnew_document_update (bool):
                bNewDocumentUpdate parameter
            check_in_comment (str):
                checkInComment parameter
            dates_in_utc (bool):
                datesInUTC parameter
            number_in_invariant_culture (bool):
                numberInInvariantCulture parameter
            view (str):
                View parameter
            root_folder (str):
                RootFolder parameter
        """
        from office365.sharepoint.listitems.updateresults import ListItemUpdateResults

        return_type = ClientResult(self.context, ListItemUpdateResults())
        qry = ServiceOperationQuery(
            self,
            "ValidateUpdateFetchListItem",
            None,
            {
                "formValues": form_values,
                "bNewDocumentUpdate": bnew_document_update,
                "checkInComment": check_in_comment,
                "datesInUTC": dates_in_utc,
                "numberInInvariantCulture": number_in_invariant_culture,
                "View": view,
                "RootFolder": root_folder,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def validate_update_fetch_list_item_in_folder(
        self,
        form_values: ClientValueCollection[ListItemFormUpdateValue],
        bnew_document_update: bool,
        check_in_comment: str,
        dates_in_utc: bool,
        number_in_invariant_culture: bool,
        root_folder: str,
    ) -> ClientResult[ListItemUpdateResults]:
        """ValidateUpdateFetchListItemInFolder operation.

        Args:
            form_values (ClientValueCollection[ListItemFormUpdateValue]):
                formValues parameter
            bnew_document_update (bool):
                bNewDocumentUpdate parameter
            check_in_comment (str):
                checkInComment parameter
            dates_in_utc (bool):
                datesInUTC parameter
            number_in_invariant_culture (bool):
                numberInInvariantCulture parameter
            root_folder (str):
                rootFolder parameter
        """
        from office365.sharepoint.listitems.updateresults import ListItemUpdateResults

        return_type = ClientResult(self.context, ListItemUpdateResults())
        qry = ServiceOperationQuery(
            self,
            "ValidateUpdateFetchListItemInFolder",
            None,
            {
                "formValues": form_values,
                "bNewDocumentUpdate": bnew_document_update,
                "checkInComment": check_in_comment,
                "datesInUTC": dates_in_utc,
                "numberInInvariantCulture": number_in_invariant_culture,
                "rootFolder": root_folder,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def validate_update_list_item(
        self,
        form_values: ClientValueCollection[ListItemFormUpdateValue],
        bnew_document_update: bool,
        check_in_comment: str,
        dates_in_utc: bool,
        number_in_invariant_culture: bool,
        shared_lock_id: str,
    ) -> ClientResult[ClientValueCollection[ListItemFormUpdateValue]]:
        """ValidateUpdateListItem operation.

        Args:
            form_values (ClientValueCollection[ListItemFormUpdateValue]):
                formValues parameter
            bnew_document_update (bool):
                bNewDocumentUpdate parameter
            check_in_comment (str):
                checkInComment parameter
            dates_in_utc (bool):
                datesInUTC parameter
            number_in_invariant_culture (bool):
                numberInInvariantCulture parameter
            shared_lock_id (str):
                sharedLockId parameter
        """
        from office365.sharepoint.listitems.form_update_value import (
            ListItemFormUpdateValue,
        )

        return_type = ClientResult(self.context, ClientValueCollection[ListItemFormUpdateValue]())
        qry = ServiceOperationQuery(
            self,
            "ValidateUpdateListItem",
            None,
            {
                "formValues": form_values,
                "bNewDocumentUpdate": bnew_document_update,
                "checkInComment": check_in_comment,
                "datesInUTC": dates_in_utc,
                "numberInInvariantCulture": number_in_invariant_culture,
                "sharedLockId": shared_lock_id,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type
