from typing import Optional

from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity


class SiteVersionPolicyManager(Entity):
    """"""

    @property
    def major_version_limit(self):
        # type: () -> Optional[int]
        """ """
        return self.properties.get("MajorVersionLimit", None)

    def set_auto_expiration(self):
        """"""
        qry = ServiceOperationQuery(self, "SetAutoExpiration")
        self.context.add_query(qry)
        return self
