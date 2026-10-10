from typing import Dict, Optional

from typing_extensions import Self

from generator.odata.type_information import TypeInformation


class ODataModel:
    """Represents the type system metadata for an OData service.

    Maintains a registry of entity and complex types that make up the service's data model.
    """

    def __init__(self):
        self._types: Dict[str, TypeInformation] = {}
        #: Root type name -> container name (entity set / singleton), if any.
        self.anchors: Dict[str, str] = {}

    @property
    def types(self) -> Dict[str, TypeInformation]:
        """Gets the type mapping dictionary."""
        return self._types

    def add_type(self, type_schema: TypeInformation) -> Self:
        """Registers a type schema in the model.

        Args:
            type_schema: The type schema to register.

        Example:
            >>> model = ODataModel()
            >>> model.add_type(TypeInformation(FullName="SP.User"))
        """
        self._types[type_schema.FullName] = type_schema
        return self

    def find_type(self, type_name: str) -> Optional[TypeInformation]:
        """Returns the type schema by name, or ``None`` when it is unknown."""
        return self._types.get(type_name)

    def get_type(self, type_name: str) -> TypeInformation:
        """Retrieves a type schema by name.

        Args:
            type_name: The name of the type to retrieve.

        Raises:
            KeyError: If the type is not registered.
        """
        return self._types[type_name]
