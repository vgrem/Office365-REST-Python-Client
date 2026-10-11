from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata
from office365.security.cases.ediscovery import EdiscoveryCase


class CasesRoot(Entity):
    """"""

    @odata(name="ediscoveryCases")
    @property
    def ediscovery_cases(self) -> EntityCollection[EdiscoveryCase]:
        return self.properties.get(
            "ediscoveryCases",
            EntityCollection(self.context, EdiscoveryCase, ResourcePath("ediscoveryCases", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.CasesRoot"
