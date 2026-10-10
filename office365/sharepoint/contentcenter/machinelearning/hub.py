from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata
from office365.sharepoint.compliance.tags.tag import ComplianceTag
from office365.sharepoint.contentcenter.defaultcontentcentersiteinfo import (
    DefaultContentCenterSiteInfo,
)
from office365.sharepoint.contentcenter.machinelearning.enabled import (
    SPMachineLearningEnabled,
)
from office365.sharepoint.contentcenter.machinelearning.models.collection import (
    SPMachineLearningModelCollection,
)
from office365.sharepoint.contentcenter.machinelearning.publications.publication import (
    SPMachineLearningPublication,
)
from office365.sharepoint.contentcenter.machinelearning.samples.collection import (
    SPMachineLearningSampleCollection,
)
from office365.sharepoint.contentcenter.machinelearning.workitems.item import (
    SPMachineLearningWorkItem,
)
from office365.sharepoint.contentcenter.syntex_models_landing_info import (
    SyntexModelsLandingInfo,
)
from office365.sharepoint.entity import Entity
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.utilities.autofillcolumninfo import AutofillColumnInfo
from office365.sharepoint.viva.syntexcontext import SyntexContext

if TYPE_CHECKING:
    from office365.sharepoint.utilities.llmcolumninfo import LLMColumnInfo


class SPMachineLearningHub(Entity):
    """ """

    def get_by_content_type_id(self, content_type_id: str) -> SyntexModelsLandingInfo:
        """Args:
        content_type_id (str):
        """
        return_type = SyntexModelsLandingInfo(self.context)
        payload = {"contentTypeId": content_type_id}
        qry = ServiceOperationQuery(self, "GetByContentTypeId", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_models(
        self, list_id=None, model_types=None, publication_types=None, include_management_not_allowed_models=None
    ):
        """Args:
        list_id (str):
        model_types (int):
        publication_types (int):
        include_management_not_allowed_models (bool):
        """
        return_type = SPMachineLearningModelCollection(self.context)
        payload = {
            "listId": list_id,
            "modelTypes": model_types,
            "publicationTypes": publication_types,
            "includeManagementNotAllowedModels": include_management_not_allowed_models,
        }
        qry = ServiceOperationQuery(self, "GetModels", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_retention_labels(self):
        """ """
        return_type = ClientResult(self.context, ClientValueCollection(ComplianceTag))
        qry = ServiceOperationQuery(self, "GetRetentionLabels", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def is_default_content_center(self) -> Optional[bool]:
        """ """
        return self.properties.get("IsDefaultContentCenter", None)

    @property
    def machine_learning_capture_enabled(self) -> Optional[bool]:
        """ """
        return self.properties.get("MachineLearningCaptureEnabled", None)

    @odata(name="MachineLearningEnabled")
    @property
    def machine_learning_enabled(self) -> SPMachineLearningEnabled:
        """ """
        return self.properties.get(
            "MachineLearningEnabled",
            SPMachineLearningEnabled(self.context, ResourcePath("MachineLearningEnabled", self.resource_path)),
        )

    @property
    def models(self) -> SPMachineLearningModelCollection:
        """ """
        return self.properties.get(
            "Models", SPMachineLearningModelCollection(self.context, ResourcePath("Models", self.resource_path))
        )

    @property
    def samples(self) -> SPMachineLearningSampleCollection:
        """ """
        return self.properties.get(
            "Samples", SPMachineLearningSampleCollection(self.context, ResourcePath("Samples", self.resource_path))
        )

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.ContentCenter.SPMachineLearningHub"

    @property
    def agreement_work_items(self) -> EntityCollection[SPMachineLearningWorkItem]:
        """Gets the AgreementWorkItems property"""
        return self.properties.get(
            "AgreementWorkItems",
            EntityCollection[SPMachineLearningWorkItem](
                self.context, SPMachineLearningWorkItem, ResourcePath("AgreementWorkItems", self.resource_path)
            ),
        )

    @property
    def default_content_center(self) -> DefaultContentCenterSiteInfo:
        """Gets the DefaultContentCenter property"""
        return self.properties.get(
            "DefaultContentCenter",
            DefaultContentCenterSiteInfo(self.context, ResourcePath("DefaultContentCenter", self.resource_path)),
        )

    @property
    def publications(self) -> EntityCollection[SPMachineLearningPublication]:
        """Gets the Publications property"""
        return self.properties.get(
            "Publications",
            EntityCollection[SPMachineLearningPublication](
                self.context, SPMachineLearningPublication, ResourcePath("Publications", self.resource_path)
            ),
        )

    @property
    def syntex_context(self) -> SyntexContext:
        """Gets the SyntexContext property"""
        return self.properties.get(
            "SyntexContext", SyntexContext(self.context, ResourcePath("SyntexContext", self.resource_path))
        )

    @property
    def work_items(self) -> EntityCollection[SPMachineLearningWorkItem]:
        """Gets the WorkItems property"""
        return self.properties.get(
            "WorkItems",
            EntityCollection[SPMachineLearningWorkItem](
                self.context, SPMachineLearningWorkItem, ResourcePath("WorkItems", self.resource_path)
            ),
        )

    def get_autofill_column_settings(self, doc_lib_id: UUID) -> ClientResult[str]:
        """GetAutofillColumnSettings operation.

        Args:
            doc_lib_id (UUID): docLibId parameter
        """
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "GetAutofillColumnSettings", [doc_lib_id], return_type)
        self.context.add_query(qry)
        return return_type

    def get_library_llm_info(self, doc_lib_id: UUID) -> ClientResult[ClientValueCollection[AutofillColumnInfo]]:
        """GetLibraryLLMInfo operation.

        Args:
            doc_lib_id (UUID): docLibId parameter
        """
        return_type = ClientResult(self.context, ClientValueCollection[AutofillColumnInfo]())
        qry = FunctionQuery(self, "GetLibraryLLMInfo", [doc_lib_id], return_type)
        self.context.add_query(qry)
        return return_type

    def get_machine_learning_flags(self, doc_lib_id: UUID) -> ClientResult[int]:
        """GetMachineLearningFlags operation.

        Args:
            doc_lib_id (UUID): docLibId parameter
        """
        return_type = ClientResult(self.context, int())
        qry = FunctionQuery(self, "GetMachineLearningFlags", [doc_lib_id], return_type)
        self.context.add_query(qry)
        return return_type

    def get_model_id_for_content_type(self, content_type_name: str) -> ClientResult[str]:
        """GetModelIdForContentType operation.

        Args:
            content_type_name (str): contentTypeName parameter
        """
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "GetModelIdForContentType", [content_type_name], return_type)
        self.context.add_query(qry)
        return return_type

    def get_syntex_powered_column_prompts(self, doc_lib_id: UUID) -> ClientResult[str]:
        """GetSyntexPoweredColumnPrompts operation.

        Args:
            doc_lib_id (UUID): docLibId parameter
        """
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "GetSyntexPoweredColumnPrompts", [doc_lib_id], return_type)
        self.context.add_query(qry)
        return return_type

    def set_autofill_column_settings(self, doc_lib_id: UUID, autofill_column_settings: str) -> Self:
        """SetAutofillColumnSettings operation.

        Args:
            doc_lib_id (UUID): docLibId parameter
            autofill_column_settings (str): autofillColumnSettings parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetAutofillColumnSettings",
            None,
            {"docLibId": doc_lib_id, "autofillColumnSettings": autofill_column_settings},
            None,
        )
        self.context.add_query(qry)
        return self

    def set_column_llm_info(
        self,
        doc_lib_id: UUID,
        column_id: UUID,
        autofill_prompt: str,
        is_enabled: bool,
        autofill_column_type: str,
        overwrite_mode: int,
        processing_pass: int,
    ) -> Self:
        """SetColumnLLMInfo operation.

        Args:
            doc_lib_id (UUID): docLibId parameter
            column_id (UUID): columnId parameter
            autofill_prompt (str): autofillPrompt parameter
            is_enabled (bool): isEnabled parameter
            autofill_column_type (str): autofillColumnType parameter
            overwrite_mode (int): overwriteMode parameter
            processing_pass (int): processingPass parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetColumnLLMInfo",
            None,
            {
                "docLibId": doc_lib_id,
                "columnId": column_id,
                "autofillPrompt": autofill_prompt,
                "isEnabled": is_enabled,
                "autofillColumnType": autofill_column_type,
                "overwriteMode": overwrite_mode,
                "processingPass": processing_pass,
            },
            None,
        )
        self.context.add_query(qry)
        return self

    def set_machine_learning_flags(self, doc_lib_id: UUID, machine_learning_flags: int) -> Self:
        """SetMachineLearningFlags operation.

        Args:
            doc_lib_id (UUID): docLibId parameter
            machine_learning_flags (int): machineLearningFlags parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetMachineLearningFlags",
            None,
            {"docLibId": doc_lib_id, "machineLearningFlags": machine_learning_flags},
            None,
        )
        self.context.add_query(qry)
        return self

    def set_syntex_powered_column_prompts(self, doc_lib_id: UUID, syntex_powered_column_prompts: str) -> Self:
        """SetSyntexPoweredColumnPrompts operation.

        Args:
            doc_lib_id (UUID): docLibId parameter
            syntex_powered_column_prompts (str): syntexPoweredColumnPrompts parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetSyntexPoweredColumnPrompts",
            None,
            {"docLibId": doc_lib_id, "syntexPoweredColumnPrompts": syntex_powered_column_prompts},
            None,
        )
        self.context.add_query(qry)
        return self

    def verify_model_urls(self, urls: StringCollection) -> Self:
        """VerifyModelUrls operation.

        Args:
            urls (StringCollection): urls parameter
        """
        qry = ServiceOperationQuery(self, "VerifyModelUrls", None, {"urls": urls}, None)
        self.context.add_query(qry)
        return self

    def verify_model_urls_and_grant_pac(self, urls: StringCollection) -> ClientResult[str]:
        """VerifyModelUrlsAndGrantPAC operation.

        Args:
            urls (StringCollection): urls parameter
        """
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "VerifyModelUrlsAndGrantPAC", [urls], return_type)
        self.context.add_query(qry)
        return return_type

    def get_column_llm_info(self, doc_lib_id: UUID, column_id: UUID) -> ClientResult[LLMColumnInfo]:
        """GetColumnLLMInfo operation.

        Args:
            doc_lib_id (UUID):
                docLibId parameter
            column_id (UUID):
                columnId parameter
        """
        from office365.sharepoint.utilities.llmcolumninfo import LLMColumnInfo

        return_type = ClientResult(self.context, LLMColumnInfo())
        qry = FunctionQuery(self, "GetColumnLLMInfo", [doc_lib_id, column_id], return_type)
        self.context.add_query(qry)
        return return_type

    def get_retention_label(self, retention_label_id: UUID) -> ClientResult[ComplianceTag]:
        """GetRetentionLabel operation.

        Args:
            retention_label_id (UUID):
                retentionLabelId parameter
        """
        from office365.sharepoint.compliance.tags.tag import ComplianceTag

        return_type = ClientResult(self.context, ComplianceTag())
        qry = FunctionQuery(self, "GetRetentionLabel", [retention_label_id], return_type)
        self.context.add_query(qry)
        return return_type
