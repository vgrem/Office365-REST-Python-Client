from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.attribute_mapping_parameter_schema import AttributeMappingParameterSchema


class AttributeMappingFunctionSchema(Entity):
    """Describes a function that can be used in an attribute mapping to transform values during synchronization."""

    @property
    def parameters(self) -> ClientValueCollection[AttributeMappingParameterSchema]:
        """Gets the parameters property"""
        return self.properties.get(
            "parameters", ClientValueCollection[AttributeMappingParameterSchema](AttributeMappingParameterSchema)
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AttributeMappingFunctionSchema"
