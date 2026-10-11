from enum import Enum


class DataSourceScopes(Enum):
    none = "0"
    allTenantMailboxes = "1"
    allTenantSites = "2"
    allCaseCustodians = "4"
    allCaseNoncustodialDataSources = "8"
    unknownFutureValue = "16"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.DataSourceScopes"
