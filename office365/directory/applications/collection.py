from __future__ import annotations

from typing import Any

from office365.count_collection import CountCollection
from office365.directory.applications.application import Application


class ApplicationCollection(CountCollection[Application]):
    """DirectoryObject's collection"""

    def __init__(self, context, resource_path=None):
        super().__init__(context, Application, resource_path)

    def add(self, display_name: str, **kwargs: Any) -> Application:
        """Create a new application object.

        Args:
            display_name (str): Display name of the application.
        """
        props = {
            "displayName": display_name,
            **kwargs,
        }
        return super().add(**props)

    def get_by_app_id(self, app_id: str) -> Application:
        """Retrieves application by Application client identifier

        Args:
            app_id (str): Application client identifier
        """
        return self.get_by_alternate_key("appId", app_id)

    def ensure(self, display_name: str, *, sign_in_audience: str = "AzureADMyOrg") -> Application:
        """Get an existing application by display name or create it (idempotent).

        Mirrors the ``ensure(name)`` convention used elsewhere in the library
        (term store groups, To Do lists). Application display names are **not**
        unique in Entra, so this reuses the first match and only creates a
        registration when none exists. Deferred — resolve with
        ``execute_query()``:

            app = client.applications.ensure("my-app").execute_query()

        For app-only (client-credentials) flows, ensure the service principal
        too, so permissions and site grants have a principal to attach to:

            client.service_principals.ensure(app.app_id).execute_query()

        Args:
            display_name: Display name of the application.
            sign_in_audience: Audience for a newly created application.

        Returns:
            Application: The existing or newly created application.
        """
        from office365.runtime.queries.create_entity import CreateEntityQuery

        return_type = self.create_typed_object({"displayName": display_name, "signInAudience": sign_in_audience})
        self.add_child(return_type)

        def _ensure(col: ApplicationCollection) -> None:
            if len(col) == 0:
                self.context.add_query(CreateEntityQuery(self, return_type, return_type))
            else:
                return_type.copy_from(col[0])

        self.get().filter(f"displayName eq '{display_name}'").after_execute(_ensure)
        return return_type
