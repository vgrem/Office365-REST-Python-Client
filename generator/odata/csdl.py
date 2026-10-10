"""Low-level traversal over a parsed CSDL (OData metadata) document.

Owns the XML namespaces, the schema ``Alias -> Namespace`` map, and namespace
qualification — the parts of reading that have nothing to do with building the
Python model.
"""

from __future__ import annotations

from typing import Dict, Optional
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element

from generator.odata.type_system import is_collection_name, normalize_class_name, strip_collection


class CsdlDocument:
    """Namespaces, schema aliases and traversal for one CSDL document."""

    def __init__(self, root: Element, namespaces: Dict[str, str]) -> None:
        self._root = root
        self._namespaces = namespaces
        self._aliases = self._load_aliases()

    @classmethod
    def load(cls, path: str, namespaces: Dict[str, str]) -> "CsdlDocument":
        """Parse a metadata file and wrap its root element."""
        return cls(ET.parse(path).getroot(), namespaces)

    @property
    def root(self) -> Element:
        return self._root

    @property
    def namespaces(self) -> Dict[str, str]:
        return self._namespaces

    def schemas(self) -> list[Element]:
        """The ``<Schema>`` elements of the document."""
        return self.findall("edmx:DataServices/xmlns:Schema")

    def findall(self, path: str) -> list[Element]:
        return self._root.findall(path, self._namespaces)

    def find(self, path: str) -> Optional[Element]:
        return self._root.find(path, self._namespaces)

    def _load_aliases(self) -> Dict[str, str]:
        """The ``Alias -> Namespace`` map declared by the schemas (e.g. ``graph``)."""
        aliases: Dict[str, str] = {}
        for schema_node in self.schemas():
            namespace = schema_node.get("Namespace")
            alias = schema_node.get("Alias")
            if namespace and alias:
                aliases[alias] = namespace
        return aliases

    def qualified_type_name(self, type_name: Optional[str]) -> Optional[str]:
        """Expand a schema alias to its namespace and normalize the class name.

        Graph metadata refers to types with aliases (``graph.user``,
        ``self.alertEvidence``); normalizing here keeps every ``TypeName``
        fully-qualified, so resolution and routing are unambiguous.
        """
        if not type_name:
            return type_name
        if is_collection_name(type_name):
            return f"Collection({self.qualified_type_name(strip_collection(type_name))})"
        namespace, sep, class_name = type_name.rpartition(".")
        if not sep or namespace == "Edm":
            return type_name
        namespace = self._aliases.get(namespace, namespace)
        return f"{namespace}.{normalize_class_name(class_name)}"

    def parse_parameters(self, node: Element) -> list:
        """Extract ``<Parameter>`` children into plain dicts (types qualified)."""
        return [
            {
                "Name": param.get("Name"),
                "Type": self.qualified_type_name(param.get("Type")),
                "Nullable": param.get("Nullable") != "false",
            }
            for param in node.findall("xmlns:Parameter", self._namespaces)
        ]

    def entity_anchors(self) -> dict[str, str]:
        """The root container name (entity set / singleton) for each root type.

        E.g. ``users -> microsoft.graph.User``, ``identityGovernance ->
        microsoft.graph.identityGovernance``. These anchor otherwise-unreferenced
        root types to a product area, for routing suggestions.
        """
        anchors: dict[str, str] = {}
        for container in self.findall("edmx:DataServices/xmlns:Schema/xmlns:EntityContainer"):
            for node in container.findall("xmlns:EntitySet", self._namespaces):
                type_name = self.qualified_type_name(node.get("EntityType"))
                if type_name:
                    anchors.setdefault(type_name, node.get("Name") or "")
            for node in container.findall("xmlns:Singleton", self._namespaces):
                type_name = self.qualified_type_name(node.get("Type"))
                if type_name:
                    anchors.setdefault(type_name, node.get("Name") or "")
        return anchors
