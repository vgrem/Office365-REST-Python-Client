from typing import Dict, Optional
from xml.etree.ElementTree import Element

from generator.odata.method import MethodInformation
from generator.odata.model import ODataModel
from generator.odata.property import PropertyInformation
from generator.odata.reader import ODataReader

_MIN_TYPE_ENCODED_PARTS = 3


class ODataV3Reader(ODataReader):
    """OData v3 reader"""

    def process_navigation_property_node(self, node: Element) -> Optional[PropertyInformation]:
        schema = self._new_navigation(node)

        relationship = node.get("Relationship")
        to_role = node.get("ToRole")
        if relationship is None or to_role is None:
            return None

        association_name = relationship.split(".")[-1] if "." in relationship else relationship

        assert self._root is not None
        association_node = self._root.find(f".//xmlns:Association[@Name='{association_name}']", self.xml_namespaces)
        if association_node is None:
            return None

        end_node = association_node.find(f".//xmlns:End[@Role='{to_role}']", self.xml_namespaces)
        if end_node is None:
            return None

        if end_node.get("Multiplicity") == "*":
            schema.TypeName = self._qualified_type_name(f"Collection({end_node.get('Type')})")
        else:
            schema.TypeName = self._qualified_type_name(end_node.get("Type"))

        return schema

    def process_operations(self, model: ODataModel) -> None:
        assert self._root is not None
        for node in self._root.findall(".//xmlns:FunctionImport", self.xml_namespaces):
            name = node.get("Name")
            if not name or node.get("EntitySet") is not None:
                continue  # entity-set accessor -> navigation property

            params = self.parse_parameters(node)
            is_bindable = node.get("IsBindable") == "true" or any(p.get("Name") == "this" for p in params)

            if is_bindable:
                binding_param = next((p for p in params if p.get("Name") == "this"), params[0] if params else None)
                if binding_param is None or binding_param.get("Type") is None:
                    continue
                binding_type = self._entity_binding_type(binding_param)
                if binding_type is None:
                    continue  # collection-bound -> hand-written on the <Item>Collection class
                method_name = name
                remaining = [p for p in params if p is not binding_param]
                is_static = False
            else:
                parts = name.split("_")
                if len(parts) < _MIN_TYPE_ENCODED_PARTS or parts[0] != "SP":
                    continue  # unbound, not type-encoded -> cannot attach
                binding_type = f"SP.{parts[1]}"
                method_name = "".join(parts[2:])
                remaining = params
                is_static = True

            is_composable = node.get("IsComposable") == "true"
            is_side_effecting = node.get("IsSideEffecting") != "false"
            self._attach_method(
                model,
                binding_type,
                MethodInformation(
                    Name=method_name,
                    Parameters=remaining,
                    ReturnTypeFullName=self._qualified_type_name(node.get("ReturnType")),
                    BindingTypeFullName=binding_type,
                    IsBound=is_bindable,
                    IsStatic=is_static,
                    Kind="function" if (is_composable or not is_side_effecting) else "action",
                    IsComposable=is_composable,
                    IsSideEffecting=is_side_effecting,
                ),
            )

    @property
    def xml_namespaces(self) -> Dict[str, str]:
        return {
            "xmlns": "http://schemas.microsoft.com/ado/2009/11/edm",
            "edmx": "http://schemas.microsoft.com/ado/2007/06/edmx",
            "m": "http://schemas.microsoft.com/ado/2007/08/dataservices/metadata",
        }
