from __future__ import annotations

from typing import Optional, Union

from office365.runtime.paths.resource_path import ResourcePath


class AlternateKeyPath(ResourcePath):
    """Addresses a single entity by an alternate key rather than its primary id.

    OData renders an alternate key as a parenthesised literal appended to the
    entity-set segment, e.g. ``/groups(uniqueName='Group157')`` or
    ``/servicePrincipals(appId='00000000-0000-0000-0000-000000000000')``. The
    path contributes no ``/`` delimiter of its own, so it reads as part of the
    preceding collection segment.

    Microsoft Graph declares alternate keys for a handful of entity types (user
    ``userPrincipalName``, group ``uniqueName``, application/servicePrincipal
    ``appId``, device ``deviceId``, directoryRole ``roleTemplateId``, ...). They
    also make a resource addressable without a lookup, which is what the
    server-side upsert pattern needs.
    """

    def __init__(
        self,
        key_name: str,
        key_value: Union[int, str],
        parent: Optional[ResourcePath] = None,
    ) -> None:
        super().__init__(key_value, parent)
        self._key_name = key_name

    @property
    def key_name(self) -> str:
        """The alternate-key property name (e.g. ``uniqueName``)."""
        return self._key_name

    @property
    def segment(self) -> str:
        return f"({self._key_name}='{self._key}')"

    @property
    def delimiter(self) -> None:
        return None
