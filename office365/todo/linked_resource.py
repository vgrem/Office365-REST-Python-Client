from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class LinkedResource(Entity):
    """Represents an item in a partner application related to a todoTask. An example is an email from where the task
    was created. A linkedResource object stores information about that source application, and lets you link back to
    the related item. You can see the linkedResource in the task details view, as shown.
    """

    @property
    def application_name(self) -> Optional[str]:
        """Field indicating the app name of the source that is sending the linkedResource."""
        return self.properties.get("applicationName", None)

    @property
    def display_name(self) -> Optional[str]:
        """The title of the linkedResource."""
        return self.properties.get("displayName", None)

    @property
    def external_id(self) -> Optional[str]:
        """The identifier of the object in the source application."""
        return self.properties.get("externalId", None)

    @property
    def web_url(self) -> Optional[str]:
        """The deep link to the related item in the source application."""
        return self.properties.get("webUrl", None)

    @property
    def entity_type_name(self) -> str:
        return None  # type: ignore
