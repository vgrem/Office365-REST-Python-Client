from __future__ import annotations

from typing import Optional

from office365.directory.domains.domain import Domain
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.v4.entity import EntityPath
from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.runtime.queries.get_or_create import get_or_create


class DomainCollection(EntityCollection[Domain]):
    """Collection of tenant domains."""

    def __init__(self, context, resource_path: Optional[ResourcePath] = None):
        super().__init__(context, Domain, resource_path)

    def add(self, domain_id: str) -> Domain:
        """Add an unverified domain to the tenant.

        The domain name is the entity ``id``. The tenant must then add the
        returned verification DNS records before calling :meth:`Domain.verify`.

        Args:
            domain_id (str): The fully qualified domain name, e.g. ``contoso.com``.
        """
        return super().add(id=domain_id)

    def get_by_id(self, domain_id: str) -> Domain:
        """Retrieve a domain by name (deferred — resolve with ``execute_query()``).

        Args:
            domain_id (str): The fully qualified domain name, e.g. ``contoso.com``.
        """
        return self.create_typed_object(resource_path=EntityPath(domain_id, self.resource_path))

    def ensure(self, domain_id: str) -> Domain:
        """Return the domain for ``domain_id``, adding it when it is not yet present.

        Idempotent and deferred — resolve with ``execute_query()``::

            domain = client.domains.ensure("contoso.com").execute_query()

        Args:
            domain_id: The fully qualified domain name, e.g. ``contoso.com``.

        Returns:
            Domain: The existing or newly added (unverified) domain.
        """
        return_type = self.create_typed_object({"id": domain_id}, EntityPath(None, self.resource_path))
        self.add_child(return_type)
        return get_or_create(
            find=lambda: self.get_by_id(domain_id).get(),
            create_query=lambda: CreateEntityQuery(self, return_type, return_type),
            return_type=return_type,
        )
