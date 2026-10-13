from __future__ import annotations

from office365.count_collection import CountCollection
from office365.directory.serviceprincipals.service_principal import ServicePrincipal
from office365.runtime.deprecated import deprecated
from office365.runtime.odata.literals import escape_odata_string


class ServicePrincipalCollection(CountCollection[ServicePrincipal]):
    """Service Principal's collection"""

    def __init__(self, context, resource_path=None):
        super().__init__(context, ServicePrincipal, resource_path)

    def add(self, app_id: str) -> ServicePrincipal:
        """Create a new servicePrincipal object.

        Args:
            app_id (str): The unique identifier for the associated application
        """
        return super().add(appId=app_id)

    def get_by_app_id(self, app_id: str) -> ServicePrincipal:
        """Retrieves the service principal using appId.

        Args:
            app_id (str): appId is referred to as Application (Client) ID, respectively, in the Azure portal
        """
        return self.get_by_alternate_key("appId", app_id)

    def find_by_name(self, name: str, *, required: bool = False) -> ServicePrincipal:
        """Look up a service principal by its ``displayName``.

        Deferred — run with ``execute_query()``. Tolerant by default: when no
        principal matches, the returned object is left uninitialized (check
        :attr:`~office365.runtime.client_object.ClientObject.is_loaded`). Pass
        ``required=True`` to raise instead (or on an ambiguous match).

        Args:
            name (str): The service principal display name
            required (bool): Raise on a missing or ambiguous match when ``True``
        """
        return self._find_by_filter(f"displayName eq '{escape_odata_string(name)}'", required=required)

    @deprecated("Use find_by_name() instead.", version="4.0")
    def get_by_name(self, name: str) -> ServicePrincipal:
        """Deprecated alias of :meth:`find_by_name` (strict)."""
        return self.find_by_name(name, required=True)

    def ensure(self, app_id: str) -> ServicePrincipal:
        """Return the service principal for ``app_id``, creating it when absent.

        Idempotent and deferred — resolve with ``execute_query()``. App-only
        (client-credentials) flows attach permissions and site grants to the
        service principal, not the application registration, so use this to make
        a freshly created app usable:

            client.service_principals.ensure(app.app_id).execute_query()

        Args:
            app_id: The application (client) ID of the app registration.

        Returns:
            ServicePrincipal: The existing or newly created service principal.
        """
        from office365.runtime.paths.v4.entity import EntityPath
        from office365.runtime.queries.create_entity import CreateEntityQuery
        from office365.runtime.queries.get_or_create import get_or_create

        return_type = self.create_typed_object({"appId": app_id}, EntityPath(None, self.resource_path))
        self.add_child(return_type)
        return get_or_create(
            find=lambda: self.get_by_app_id(app_id).get(),
            create_query=lambda: CreateEntityQuery(self, return_type, return_type),
            return_type=return_type,
        )
