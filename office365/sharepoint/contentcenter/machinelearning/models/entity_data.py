from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import GuidCollection
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.contentcenter.machinelearning.models.columndef import (
        ColumnDef,
    )


class SPMachineLearningModelEntityData(Entity):
    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.ContentCenter.SPMachineLearningModelEntityData"

    @property
    def accuracy(self) -> Optional[float]:
        """Gets the Accuracy property"""
        return self.properties.get("Accuracy", None)

    @property
    def ai_builder_hybrid_model_environment(self) -> Optional[str]:
        """Gets the AIBuilderHybridModelEnvironment property"""
        return self.properties.get("AIBuilderHybridModelEnvironment", None)

    @property
    def ai_builder_hybrid_model_host_name(self) -> Optional[str]:
        """Gets the AIBuilderHybridModelHostName property"""
        return self.properties.get("AIBuilderHybridModelHostName", None)

    @property
    def ai_builder_hybrid_model_in_test_environment(self) -> Optional[bool]:
        """Gets the AIBuilderHybridModelInTestEnvironment property"""
        return self.properties.get("AIBuilderHybridModelInTestEnvironment", None)

    @property
    def azure_cognitive_prebuilt_model_name(self) -> Optional[str]:
        """Gets the AzureCognitivePrebuiltModelName property"""
        return self.properties.get("AzureCognitivePrebuiltModelName", None)

    @property
    def base_content_type_name(self) -> Optional[str]:
        """Gets the BaseContentTypeName property"""
        return self.properties.get("BaseContentTypeName", None)

    @property
    def ai_builder_hybrid_model_type(self) -> Optional[str]:
        """Gets the AIBuilderHybridModelType property"""
        return self.properties.get("AIBuilderHybridModelType", None)

    @property
    def column_id(self) -> Optional[str]:
        """Gets the ColumnId property"""
        return self.properties.get("ColumnId", None)

    @property
    def column_name(self) -> Optional[str]:
        """Gets the ColumnName property"""
        return self.properties.get("ColumnName", None)

    @property
    def columns(self) -> ClientValueCollection[ColumnDef]:
        """Gets the Columns property"""
        from office365.sharepoint.contentcenter.machinelearning.models.columndef import (
            ColumnDef,
        )

        return self.properties.get("Columns", ClientValueCollection[ColumnDef](ColumnDef))

    @property
    def column_type(self) -> Optional[str]:
        """Gets the ColumnType property"""
        return self.properties.get("ColumnType", None)

    @property
    def content_type_group(self) -> Optional[str]:
        """Gets the ContentTypeGroup property"""
        return self.properties.get("ContentTypeGroup", None)

    @property
    def content_type_id(self) -> Optional[str]:
        """Gets the ContentTypeId property"""
        return self.properties.get("ContentTypeId", None)

    @property
    def content_type_name(self) -> Optional[str]:
        """Gets the ContentTypeName property"""
        return self.properties.get("ContentTypeName", None)

    @property
    def explanations(self) -> Optional[str]:
        """Gets the Explanations property"""
        return self.properties.get("Explanations", None)

    @property
    def last_trained(self) -> Optional[datetime]:
        """Gets the LastTrained property"""
        return self.properties.get("LastTrained", datetime.min)

    @property
    def locale(self) -> Optional[str]:
        """Gets the Locale property"""
        return self.properties.get("Locale", None)

    @property
    def model_name(self) -> Optional[str]:
        """Gets the ModelName property"""
        return self.properties.get("ModelName", None)

    @property
    def model_settings(self) -> Optional[str]:
        """Gets the ModelSettings property"""
        return self.properties.get("ModelSettings", None)

    @property
    def model_type(self) -> Optional[str]:
        """Gets the ModelType property"""
        return self.properties.get("ModelType", None)

    @property
    def sample_file_unique_ids(self) -> GuidCollection:
        """Gets the SampleFileUniqueIds property"""
        return self.properties.get("SampleFileUniqueIds", GuidCollection())

    @property
    def schemas(self) -> Optional[str]:
        """Gets the Schemas property"""
        return self.properties.get("Schemas", None)

    @property
    def table_link_columns(self) -> ClientValueCollection[ColumnDef]:
        """Gets the TableLinkColumns property"""
        from office365.sharepoint.contentcenter.machinelearning.models.columndef import (
            ColumnDef,
        )

        return self.properties.get("TableLinkColumns", ClientValueCollection[ColumnDef](ColumnDef))
