from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from typing_extensions import Self

from generator.odata.member import MemberInformation
from generator.odata.method import MethodInformation
from generator.odata.property import PropertyInformation


@dataclass
class TypeInformation:
    """Represents type metadata information in an OData service.

    Contains metadata about entity types, complex types, and other structural
    elements in an OData model. Used for type reflection and metadata operations.
    """

    BaseTypeFullName: str = ""
    FullName: str = ""
    #: OData name of the base type (CSDL ``BaseType``), or ``None``.
    BaseTypeName: Optional[str] = None
    IsValueObject: Optional[bool] = None
    Methods: Dict[str, MethodInformation] = field(default_factory=dict)
    Properties: Dict[str, PropertyInformation] = field(default_factory=dict)
    Members: Dict[str, MemberInformation] = field(default_factory=dict)
    #: Alternate keys declared on the type (CSDL ``Org.OData.Core.V1.AlternateKeys``).
    #: One tuple of property names per alternate key; Graph declares e.g. group
    #: ``uniqueName``, user ``userPrincipalName``, application/servicePrincipal
    #: ``appId``, device ``deviceId``, directoryRole ``roleTemplateId``.
    AlternateKeys: List[Tuple[str, ...]] = field(default_factory=list)

    @property
    def alternate_key_names(self) -> List[str]:
        """Flat list of every property name that participates in an alternate key."""
        return [name for key in self.AlternateKeys for name in key]

    def add_alternate_key(self, key: Tuple[str, ...]) -> Self:
        self.AlternateKeys.append(key)
        return self

    def add_property(self, schema: PropertyInformation) -> Self:
        self.Properties[schema.Name] = schema
        return self

    def add_member(self, schema: MemberInformation) -> Self:
        self.Members[schema.Name] = schema
        return self

    def add_method(self, schema: MethodInformation) -> Self:
        if schema.Name is not None:
            self.Methods[schema.Name] = schema
        return self
