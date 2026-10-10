from __future__ import annotations

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity
from office365.sharepoint.sites.language import Language


class LanguageCollection(Entity):
    """Represents a collection of SPLanguage objects"""

    def __init__(self, context, resource_path=None):
        """Represents a collection of SPLanguage objects."""
        super().__init__(context, resource_path)
        self.properties["Items"] = ClientValueCollection(Language)

    @property
    def items(self) -> ClientValueCollection[Language]:
        return self.properties.get("Items", ClientValueCollection(Language))

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        return repr(self.items)

    def set_property(self, name, value, persist_changes=True):  # type: ignore[override]
        self.items.set_property(name, value, persist_changes)  # type: ignore[arg-type]
        return self

    def get_by_id(self, id_: int) -> ClientResult[Language]:
        """GetById operation.

        Args:
            id_ (int):
                id parameter
        """
        from office365.sharepoint.sites.language import Language

        return_type = ClientResult(self.context, Language())
        qry = ServiceOperationQuery(self, "GetById", None, {"id": id_}, None, return_type)
        self.context.add_query(qry)
        return return_type
