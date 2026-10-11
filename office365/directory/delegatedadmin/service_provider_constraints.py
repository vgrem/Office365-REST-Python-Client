from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection


class DelegatedAdminServiceProviderConstraints(Entity):
    @property
    def allowed_role_template_ids(self) -> StringCollection:
        """Gets the allowedRoleTemplateIds property"""
        return self.properties.get("allowedRoleTemplateIds", StringCollection())

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DelegatedAdminServiceProviderConstraints"
