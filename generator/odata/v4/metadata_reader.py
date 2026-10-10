from typing import Dict, Optional
from xml.etree.ElementTree import Element

from generator.odata.method import MethodInformation
from generator.odata.model import ODataModel
from generator.odata.property import PropertyInformation
from generator.odata.reader import ODataReader


class ODataV4Reader(ODataReader):
    """OData v4 reader"""

    def process_navigation_property_node(self, node: Element) -> Optional[PropertyInformation]:
        schema = self._new_navigation(node)
        schema.TypeName = self._qualified_type_name(node.get("Type"))
        schema.IsBeta = False
        return schema

    def process_operations(self, model: ODataModel) -> None:
        assert self._root is not None
        nodes = self._root.findall(".//xmlns:Action", self.xml_namespaces)
        nodes += self._root.findall(".//xmlns:Function", self.xml_namespaces)
        for node in nodes:
            name = node.get("Name")
            params = self.parse_parameters(node)
            if not name or node.get("IsBound") != "true" or not params:
                continue  # unbound operations can't be attached to a generated type
            binding_param = params[0]
            if binding_param.get("Type") is None:
                continue
            binding_type = self._entity_binding_type(binding_param)
            if binding_type is None:
                continue  # collection-bound -> hand-written on the <Item>Collection class
            return_node = node.find("xmlns:ReturnType", self.xml_namespaces)
            kind = "action" if node.tag.endswith("Action") else "function"
            self._attach_method(
                model,
                binding_type,
                MethodInformation(
                    Name=name,
                    Parameters=params[1:],
                    ReturnTypeFullName=self._qualified_type_name(return_node.get("Type"))
                    if return_node is not None
                    else None,
                    BindingTypeFullName=binding_type,
                    IsBound=True,
                    IsStatic=False,
                    Kind=kind,
                    IsSideEffecting=kind == "action",
                ),
            )

    @property
    def xml_namespaces(self) -> Dict[str, str]:
        return {
            "xmlns": "http://docs.oasis-open.org/odata/ns/edm",
            "edmx": "http://docs.oasis-open.org/odata/ns/edmx",
        }
