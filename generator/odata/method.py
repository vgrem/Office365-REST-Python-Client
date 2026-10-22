from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Dict, List, Optional

from generator.odata.type_system import TypeRef


@dataclass
class MethodInformation:
    """Represents an executable OData operation (function/action).

    Attributes:
        Name: Method name as defined in OData metadata
        Parameters: Accepted parameters (name/type/nullable)
        ReturnTypeFullName: Fully qualified return type name (``None`` for void)
        BindingTypeFullName: Fully qualified type the operation is bound to
        IsBound: Whether the operation is bound to an entity (instance method)
        IsStatic: Whether the generated method should be static
        Kind: ``"function"`` (composable/GET) or ``"action"`` (side-effecting/POST)
        IsComposable: v3 ``IsComposable`` flag
        IsSideEffecting: v3 ``IsSideEffecting`` flag
        IsBeta: Whether this is a preview/beta method
    """

    Name: Optional[str] = None
    Parameters: List[Dict[str, Any]] = field(default_factory=list)
    ReturnTypeFullName: Optional[str] = None
    BindingTypeFullName: Optional[str] = None
    IsBound: Optional[bool] = None
    IsStatic: Optional[bool] = None
    Kind: Optional[str] = None
    IsComposable: Optional[bool] = None
    IsSideEffecting: Optional[bool] = None
    IsBeta: Optional[bool] = None

    @cached_property
    def return_type_ref(self) -> TypeRef:
        """The parsed return-type reference (parsed once, then cached)."""
        return TypeRef.parse(self.ReturnTypeFullName)
