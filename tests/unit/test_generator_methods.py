"""Offline tests for generated OData operation methods (functions/actions)."""

from __future__ import annotations

import ast
import textwrap
from pathlib import Path

from generator.builders.method import MethodBuilder
from generator.builders.type import TypeBuilder
from generator.builders.type_registry import TypeRegistry
from generator.odata.method import MethodInformation
from generator.odata.property import PropertyInformation
from generator.odata.type_information import TypeInformation
from generator.odata.v3.metadata_reader import ODataV3Reader
from generator.odata.v4.metadata_reader import ODataV4Reader

_TEMPLATES = Path(__file__).resolve().parents[2] / "generator" / "templates" / "sharepoint"

_V3_METADATA = """<?xml version="1.0" encoding="utf-8"?>
<edmx:Edmx xmlns:edmx="http://schemas.microsoft.com/ado/2007/06/edmx">
  <edmx:DataServices>
    <Schema Namespace="SP" xmlns="http://schemas.microsoft.com/ado/2009/11/edm">
      <EntityType Name="ObjectSharingInformation">
        <Key><PropertyRef Name="AnonymousEditLink"/></Key>
        <Property Name="AnonymousEditLink" Type="Edm.String" Nullable="false"/>
      </EntityType>
      <EntityContainer Name="ApiData">
        <FunctionImport Name="SP_ObjectSharingInformation_CanCurrentUserShareRemote" ReturnType="Edm.Int32">
          <Parameter Name="docId" Type="Edm.String"/>
        </FunctionImport>
        <FunctionImport Name="MoveToSecondStage" IsBindable="true">
          <Parameter Name="this" Type="SP.ObjectSharingInformation"/>
        </FunctionImport>
        <FunctionImport Name="RemoveByLoginName" IsBindable="true">
          <Parameter Name="this" Type="Collection(SP.ObjectSharingInformation)"/>
          <Parameter Name="loginName" Type="Edm.String"/>
        </FunctionImport>
        <FunctionImport
          Name="ObjectSharingInformationSet"
          ReturnType="Collection(SP.ObjectSharingInformation)"
          EntitySet="ObjectSharingInformations"/>
      </EntityContainer>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>
"""

_V4_METADATA = """<?xml version="1.0" encoding="utf-8"?>
<edmx:Edmx xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx">
  <edmx:DataServices>
    <Schema Namespace="microsoft.graph.identityGovernance" xmlns="http://docs.oasis-open.org/odata/ns/edm">
      <EntityType Name="workflow">
        <Key><PropertyRef Name="id"/></Key>
        <Property Name="id" Type="Edm.String" Nullable="false"/>
      </EntityType>
      <Action Name="activate" IsBound="true">
        <Parameter Name="bindingParameter" Type="microsoft.graph.identityGovernance.workflow"/>
      </Action>
      <Action Name="clearQuarantine" IsBound="true">
        <Parameter Name="bindingParameter" Type="microsoft.graph.identityGovernance.workflow"/>
        <ReturnType Type="microsoft.graph.identityGovernance.workflow"/>
      </Action>
      <Function Name="summary" IsBound="true">
        <Parameter Name="bindingParameter" Type="Collection(microsoft.graph.identityGovernance.workflow)"/>
        <Parameter Name="startDateTime" Type="Edm.DateTimeOffset" Nullable="false"/>
        <ReturnType Type="microsoft.graph.identityGovernance.workflow"/>
      </Function>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>
"""


def _write(tmp_path: Path, name: str, content: str) -> str:
    path = tmp_path / name
    path.write_text(textwrap.dedent(content), encoding="utf8")
    return str(path)


def test_v3_parses_bound_and_static_function_imports(tmp_path: Path):
    model = ODataV3Reader(_write(tmp_path, "sp.xml", _V3_METADATA)).read()
    schema = model.types["SP.ObjectSharingInformation"]

    static = schema.Methods["CanCurrentUserShareRemote"]
    assert static.IsStatic is True
    assert static.Kind == "action"
    assert static.ReturnTypeFullName == "Edm.Int32"
    assert [p["Name"] for p in static.Parameters] == ["docId"]

    bound = schema.Methods["MoveToSecondStage"]
    assert bound.IsStatic is False
    assert bound.IsBound is True
    assert bound.Kind == "action"
    assert bound.Parameters == []

    # entity-set accessors are skipped
    assert "ObjectSharingInformationSet" not in schema.Methods

    # collection-bound operations belong to the hand-written <Item>Collection class and are skipped
    assert "RemoveByLoginName" not in schema.Methods


def test_v4_parses_bound_actions_and_functions(tmp_path: Path):
    model = ODataV4Reader(_write(tmp_path, "graph.xml", _V4_METADATA)).read()
    schema = model.types["microsoft.graph.identityGovernance.Workflow"]

    activate = schema.Methods["activate"]
    assert activate.Kind == "action"
    assert activate.IsBound is True
    assert activate.ReturnTypeFullName is None

    quarantine = schema.Methods["clearQuarantine"]
    assert quarantine.ReturnTypeFullName == "microsoft.graph.identityGovernance.Workflow"

    # collection-bound functions belong to the hand-written <Item>Collection class and are skipped
    assert "summary" not in schema.Methods


_ALIASED_METADATA = """<?xml version="1.0" encoding="utf-8"?>
<edmx:Edmx xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx">
  <edmx:DataServices>
    <Schema Namespace="microsoft.graph" Alias="graph" xmlns="http://docs.oasis-open.org/odata/ns/edm">
      <ComplexType Name="emailAddress">
        <Property Name="address" Type="Edm.String"/>
      </ComplexType>
    </Schema>
    <Schema Namespace="microsoft.graph.security" Alias="self" xmlns="http://docs.oasis-open.org/odata/ns/edm">
      <ComplexType Name="alertEvidence">
        <Property Name="email" Type="graph.emailAddress"/>
      </ComplexType>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>
"""


def test_v4_expands_schema_aliases(tmp_path: Path):
    """A ``graph.emailAddress`` reference resolves to ``microsoft.graph.EmailAddress``."""
    model = ODataV4Reader(_write(tmp_path, "aliased.xml", _ALIASED_METADATA)).read()
    evidence = model.types["microsoft.graph.security.AlertEvidence"]
    assert evidence.Properties["email"].TypeName == "microsoft.graph.EmailAddress"


def _build_static_method_type(tmp_path: Path, generate_methods: str) -> str:
    schema = TypeInformation(BaseTypeFullName="ComplexType", FullName="SP.TestThing", IsValueObject=True)
    schema.add_property(PropertyInformation(Name="Title", TypeName="Edm.String"))
    schema.add_method(
        MethodInformation(
            Name="SP_TestThing_DoIt",
            ReturnTypeFullName="Edm.Int32",
            Parameters=[{"Name": "value", "Type": "Edm.String"}],
            IsBound=False,
            IsStatic=True,
            Kind="action",
        )
    )
    options = {
        "template_path": str(_TEMPLATES),
        "output_path": str(tmp_path),
        "modules": "office365.sharepoint",
        "context_type": "ClientContext",
        "generate_methods": generate_methods,
    }
    builder = TypeBuilder(schema, options)
    builder.build()
    builder.save()
    return Path(builder.file).read_text(encoding="utf8")


def test_generate_methods_disabled_skips_methods_and_imports(tmp_path: Path):
    source = _build_static_method_type(tmp_path, "false")
    assert "def sp_test_thing_do_it" not in source
    assert "ServiceOperationQuery" not in source
    assert "ClientContext" not in source
    _compile(source)


def test_generate_methods_enabled_emits_method_and_imports(tmp_path: Path):
    source = _build_static_method_type(tmp_path, "true")
    assert "def sp_test_thing_do_it(context: ClientContext, value: str)" in source
    assert "from office365.runtime.queries.service_operation import ServiceOperationQuery" in source
    assert "from office365.sharepoint.client_context import ClientContext" in source
    _compile(source)


def test_generate_methods_flag_is_case_insensitive(tmp_path: Path):
    source = _build_static_method_type(tmp_path, "True")
    assert "def sp_test_thing_do_it(context: ClientContext, value: str)" in source
    _compile(source)


def _compile(source: str) -> ast.Module:
    return ast.parse(source)


def test_method_builder_static_function():
    schema = MethodInformation(
        Name="CanCurrentUserShareRemote",
        Parameters=[{"Name": "docId", "Type": "Edm.String", "Nullable": True}],
        ReturnTypeFullName="Edm.Int32",
        BindingTypeFullName="SP.ObjectSharingInformation",
        IsBound=False,
        IsStatic=True,
        Kind="action",
    )
    source = MethodBuilder(schema).build_source()

    assert "@staticmethod" in source
    assert "def can_current_user_share_remote(context: ClientContext, doc_id: str) -> ClientResult[int]:" in source
    assert "ServiceOperationQuery(" in source
    assert "None, return_type, True" in source  # is_static
    _compile(source)


def test_method_builder_instance_void_and_primitive():
    void = MethodInformation(
        Name="MoveToSecondStage",
        BindingTypeFullName="SP.ObjectSharingInformation",
        IsBound=True,
        IsStatic=False,
        Kind="action",
    )
    source = MethodBuilder(void).build_source()
    assert "def move_to_second_stage(self) -> Self:" in source
    assert "return self" in source
    _compile(source)

    primitive = MethodInformation(
        Name="CanCurrentUserShare",
        Parameters=[{"Name": "docId", "Type": "Edm.String", "Nullable": True}],
        ReturnTypeFullName="Edm.Int32",
        BindingTypeFullName="SP.ObjectSharingInformation",
        IsBound=True,
        IsStatic=False,
        Kind="function",
    )
    source = MethodBuilder(primitive).build_source()
    assert "-> ClientResult[int]:" in source
    assert "FunctionQuery(self" in source
    _compile(source)


def test_method_builder_void_action_keeps_payload():
    schema = MethodInformation(
        Name="AddModelDependency",
        Parameters=[
            {"Name": "modelId", "Type": "Edm.String", "Nullable": True},
            {"Name": "updateExisting", "Type": "Edm.Boolean", "Nullable": True},
        ],
        BindingTypeFullName="SP.ContentCenter.SPMachineLearningModel",
        IsBound=True,
        IsStatic=False,
        Kind="action",
    )
    source = MethodBuilder(schema).build_source()
    assert "def add_model_dependency(self, model_id: str, update_existing: bool) -> Self:" in source
    assert '{"modelId": model_id, "updateExisting": update_existing}' in source
    assert "return self" in source
    _compile(source)


def test_method_builder_stream_function_uses_raw_content():
    function = MethodInformation(
        Name="DownloadStream",
        ReturnTypeFullName="Edm.Stream",
        BindingTypeFullName="SP.ContentCenter.SPMachineLearningModel",
        IsBound=True,
        IsStatic=False,
        Kind="function",
    )
    source = MethodBuilder(function).build_source()
    assert 'FunctionQuery(self, "DownloadStream", [], return_type, return_raw_content=True)' in source
    _compile(source)

    action = MethodInformation(
        Name="InvokeConnectorQuery",
        ReturnTypeFullName="Edm.Stream",
        BindingTypeFullName="SP.ContentCenter.SPMachineLearningModel",
        IsBound=True,
        IsStatic=False,
        Kind="action",
    )
    source = MethodBuilder(action).build_source()
    assert "return_raw_content" not in source
    _compile(source)


def test_method_builder_key_value_collection():
    schema = MethodInformation(
        Name="GetProperties",
        ReturnTypeFullName="Collection(SP.KeyValue)",
        BindingTypeFullName="SP.ContentCenter.SPMachineLearningHub",
        IsBound=True,
        IsStatic=False,
        Kind="function",
    )
    source = MethodBuilder(schema, resolver=_resolver()).build_source()
    assert "-> ClientResult[dict]:" in source
    assert "return_type = ClientResult(self.context, dict())" in source
    _compile(source)


def _resolver() -> TypeRegistry:
    return TypeRegistry(["office365.sharepoint"])


def test_method_builder_primitive_collection_param_is_list():
    schema = MethodInformation(
        Name="CreatePersonalSiteEnqueueBulk",
        Parameters=[{"Name": "emailIDs", "Type": "Collection(Edm.String)", "Nullable": True}],
        ReturnTypeFullName="Collection(Edm.String)",
        BindingTypeFullName="SP.UserProfiles.ProfileLoader",
        IsBound=True,
        IsStatic=False,
        Kind="action",
    )
    source = MethodBuilder(schema).build_source()
    assert "email_ids: list[str]" in source
    assert '{"emailIDs": StringCollection(email_ids)}' in source
    _compile(source)


def test_method_builder_primitive_collection_param_wrappers():
    schema = MethodInformation(
        Name="SetIds",
        Parameters=[
            {"Name": "intIds", "Type": "Collection(Edm.Int32)", "Nullable": True},
            {"Name": "guidIds", "Type": "Collection(Edm.Guid)", "Nullable": True},
        ],
        BindingTypeFullName="SP.Web",
        IsBound=True,
        IsStatic=False,
        Kind="action",
    )
    source = MethodBuilder(schema).build_source()
    assert "int_ids: list[int]" in source
    assert "guid_ids: list[UUID]" in source
    assert '"intIds": ClientValueCollection(int, int_ids)' in source
    assert '"guidIds": GuidCollection(guid_ids)' in source
    _compile(source)


def test_method_builder_stream_maps_to_bytes():
    schema = MethodInformation(
        Name="InvokeConnectorQuery",
        ReturnTypeFullName="Edm.Stream",
        BindingTypeFullName="SP.ContentCenter.SPMachineLearningModel",
        IsBound=True,
        IsStatic=False,
        Kind="action",
    )
    source = MethodBuilder(schema, resolver=_resolver()).build_source()
    assert "def invoke_connector_query(self) -> ClientResult[bytes]:" in source
    assert "return_type = ClientResult(self.context, bytes())" in source
    _compile(source)


def test_method_builder_complex_return_is_wrapped_in_client_result():
    schema = MethodInformation(
        Name="GetColumnLLMInfo",
        ReturnTypeFullName="SP.Utilities.LLMColumnInfo",
        BindingTypeFullName="SP.ContentCenter.SPMachineLearningHub",
        IsBound=True,
        IsStatic=False,
        Kind="function",
    )
    source = MethodBuilder(schema, resolver=_resolver()).build_source()
    assert "def get_column_llm_info(self) -> ClientResult[LLMColumnInfo]:" in source
    assert "return_type = ClientResult(self.context, LLMColumnInfo())" in source
    _compile(source)


def test_method_builder_entity_return_is_direct():
    schema = MethodInformation(
        Name="GetByContentTypeId",
        ReturnTypeFullName="SP.Web",
        BindingTypeFullName="SP.ContentCenter.SPMachineLearningHub",
        IsBound=True,
        IsStatic=False,
        Kind="function",
    )
    source = MethodBuilder(schema, resolver=_resolver()).build_source()
    assert "def get_by_content_type_id(self) -> Web:" in source
    assert "return_type = Web(self.context)" in source
    _compile(source)


def test_method_builder_entity_collection_is_direct():
    schema = MethodInformation(
        Name="GetWebs",
        ReturnTypeFullName="Collection(SP.Web)",
        BindingTypeFullName="SP.ContentCenter.SPMachineLearningHub",
        IsBound=True,
        IsStatic=False,
        Kind="function",
    )
    source = MethodBuilder(schema, resolver=_resolver()).build_source()
    assert "-> EntityCollection[Web]:" in source
    assert "return_type = EntityCollection(self.context, Web)" in source
    _compile(source)


def test_method_builder_complex_collection_is_wrapped():
    schema = MethodInformation(
        Name="GetRetentionLabels",
        ReturnTypeFullName="Collection(SP.Compliance.Tags.ComplianceTag)",
        BindingTypeFullName="SP.ContentCenter.SPMachineLearningHub",
        IsBound=True,
        IsStatic=False,
        Kind="function",
    )
    source = MethodBuilder(schema, resolver=_resolver()).build_source()
    assert "-> ClientResult[ClientValueCollection[ComplianceTag]]:" in source
    assert "return_type = ClientResult(self.context, ClientValueCollection[ComplianceTag]())" in source
    _compile(source)
