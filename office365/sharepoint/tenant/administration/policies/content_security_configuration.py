from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import Self

from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.tenant.administration.spocontentsecuritypolicyentry import (
        SPOContentSecurityPolicyEntry,
    )


class SPOContentSecurityPolicyConfiguration(Entity):
    """"""

    @property
    def entity_type_name(self):  # type: ignore[override]
        return "Microsoft.Online.SharePoint.TenantAdministration.SPOContentSecurityPolicyConfiguration"

    @property
    def items(self) -> ClientValueCollection[SPOContentSecurityPolicyEntry]:
        """Gets the Items property"""
        from office365.sharepoint.tenant.administration.spocontentsecuritypolicyentry import (
            SPOContentSecurityPolicyEntry,
        )

        return self.properties.get(
            "Items", ClientValueCollection[SPOContentSecurityPolicyEntry](SPOContentSecurityPolicyEntry)
        )

    def add(self, source: str) -> Self:
        """Add operation.

        Args:
            source (str):
                source parameter
        """
        qry = ServiceOperationQuery(self, "Add", None, {"source": source}, None, None)
        self.context.add_query(qry)
        return self

    def remove(self, source: str) -> Self:
        """Remove operation.

        Args:
            source (str):
                source parameter
        """
        qry = ServiceOperationQuery(self, "Remove", None, {"source": source}, None, None)
        self.context.add_query(qry)
        return self

    def update_script_sources(self, added: list[str], removed: list[str]) -> Self:
        """UpdateScriptSources operation.

        Args:
            added (list[str]):
                added parameter
            removed (list[str]):
                removed parameter
        """
        qry = ServiceOperationQuery(
            self,
            "UpdateScriptSources",
            None,
            {"added": StringCollection(added), "removed": StringCollection(removed)},
            None,
            None,
        )
        self.context.add_query(qry)
        return self
