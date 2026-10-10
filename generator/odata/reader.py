from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Optional
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element

from office365.runtime.odata.type import ODataType

from generator.odata.member import MemberInformation
from generator.odata.method import MethodInformation
from generator.odata.model import ODataModel
from generator.odata.property import PropertyInformation
from generator.odata.type_information import TypeInformation

_BASE_TYPES = ("ComplexType", "EntityType", "EnumType")


class ODataReader(ABC):
    """Parses OData CSDL metadata into an :class:`ODataModel`."""

    def __init__(self, metadata_path: str):
        self._metadata_path = metadata_path
        self._root: Optional[Element] = None

    @property
    @abstractmethod
    def xml_namespaces(self) -> Dict[str, str]:
        """XML namespaces for the specific OData version"""

    def read(self) -> ODataModel:
        """Parses the metadata file and returns the populated model."""
        model = ODataModel()
        self._root = ET.parse(self._metadata_path).getroot()
        self._aliases = self._load_aliases()
        self._parse_types(model)
        self.process_operations(model)
        return model

    def _load_aliases(self) -> Dict[str, str]:
        """The ``Alias -> Namespace`` map declared by the schemas (e.g. ``graph``)."""
        assert self._root is not None
        aliases: Dict[str, str] = {}
        for schema_node in self._root.findall("edmx:DataServices/xmlns:Schema", self.xml_namespaces):
            namespace = schema_node.get("Namespace")
            alias = schema_node.get("Alias")
            if namespace and alias:
                aliases[alias] = namespace
        return aliases

    def _qualified_type_name(self, type_name: Optional[str]) -> Optional[str]:
        """Expand a schema alias to its namespace and normalize the class name.

        Graph metadata refers to types with aliases (``graph.user``,
        ``self.alertEvidence``); normalizing here keeps every ``TypeName``
        fully-qualified, so resolution and routing are unambiguous.
        """
        if not type_name:
            return type_name
        if ODataType.is_collection_name(type_name):
            return f"Collection({self._qualified_type_name(ODataType.strip_collection(type_name))})"
        namespace, sep, class_name = type_name.rpartition(".")
        if not sep or namespace == "Edm":
            return type_name
        namespace = self._aliases.get(namespace, namespace)
        return f"{namespace}.{ODataType.normalize_class_name(class_name)}"

    def _parse_types(self, model: ODataModel) -> None:
        assert self._root is not None
        schema_nodes = self._root.findall("edmx:DataServices/xmlns:Schema", self.xml_namespaces)
        for base_type in _BASE_TYPES:
            for schema_node in schema_nodes:
                for type_node in schema_node.findall(f"xmlns:{base_type}", self.xml_namespaces):
                    model.add_type(self.process_type_node(type_node, schema_node, base_type))

    @abstractmethod
    def process_operations(self, model: ODataModel) -> None:
        """Parses operations (functions/actions) and attaches them to their binding types."""

    def _attach_method(self, model: ODataModel, binding_type: str | None, method: MethodInformation) -> None:
        """Attaches an operation to its binding type, when that type is known."""
        if not binding_type:
            return
        type_schema = model.find_type(binding_type)
        if type_schema is not None:
            type_schema.add_method(method)

    @staticmethod
    def _entity_binding_type(parameter: dict) -> Optional[str]:
        """Resolves the entity type an operation is bound to.

        Operations bound to a collection (``Collection(X)``) apply to the ``XCollection``
        class in the Python model, which is hand-written, so they are not attached to the
        item entity and ``None`` is returned.
        """
        raw_type = parameter.get("Type")
        if raw_type is None or ODataType.is_collection_name(raw_type):
            return None
        return ODataType.normalize_type_name(raw_type)

    @staticmethod
    def _new_navigation(node: Element) -> PropertyInformation:
        """Creates the common part of a navigation property schema."""
        schema = PropertyInformation()
        schema.Name = node.get("Name") or ""
        schema.IsNavigation = True
        return schema

    def parse_parameters(self, node: Element) -> list:
        """Extracts ``<Parameter>`` children into plain dicts (types qualified)."""
        return [
            {
                "Name": param.get("Name"),
                "Type": self._qualified_type_name(param.get("Type")),
                "Nullable": param.get("Nullable") != "false",
            }
            for param in node.findall("xmlns:Parameter", self.xml_namespaces)
        ]

    def process_type_node(self, type_node: Element, schema_node: Element, base_type: str) -> TypeInformation:
        type_schema = TypeInformation()
        type_name = type_node.get("Name")
        if type_name is None:
            raise ValueError("Type node missing 'Name' attribute")
        type_schema.FullName = f"{schema_node.attrib['Namespace']}.{ODataType.normalize_class_name(type_name)}"
        type_schema.BaseTypeFullName = base_type
        type_schema.IsValueObject = base_type == "EntityType"

        if base_type == "EnumType":
            for member_node in type_node.findall("xmlns:Member", self.xml_namespaces):
                type_schema.add_member(self.process_member_node(member_node))
        else:
            for prop_node in type_node.findall("xmlns:Property", self.xml_namespaces):
                type_schema.add_property(self.process_property_node(prop_node))

            for prop_node in type_node.findall("xmlns:NavigationProperty", self.xml_namespaces):
                schema = self.process_navigation_property_node(prop_node)
                if schema:
                    type_schema.add_property(schema)

        return type_schema

    @abstractmethod
    def process_navigation_property_node(self, node: Element) -> Optional[PropertyInformation]:
        pass

    def process_property_node(self, node: Element) -> PropertyInformation:
        schema = PropertyInformation()
        schema.Name = node.get("Name") or ""
        schema.TypeName = self._qualified_type_name(node.get("Type"))
        return schema

    def process_member_node(self, node: Element) -> MemberInformation:
        schema = MemberInformation()
        schema.Name = node.get("Name") or ""
        schema.Value = node.get("Value")
        return schema
