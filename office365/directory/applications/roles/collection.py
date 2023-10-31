from office365.directory.applications.roles.role import AppRole
from office365.runtime.client_value_collection import ClientValueCollection


class AppRoleCollection(ClientValueCollection[AppRole]):
    """"""

    def __init__(self, initial_values=None):
        super(AppRoleCollection, self).__init__(AppRole, initial_values)

    def __getitem__(self, name):
        # type: (str) -> AppRole
        return next(iter([item for item in self._data if item.value == name]), None)
