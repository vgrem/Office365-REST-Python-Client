from __future__ import annotations

from typing import TYPE_CHECKING

from office365.directory.synchronization.job import SynchronizationJob
from office365.directory.synchronization.template import SynchronizationTemplate
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.synchronization.secret_key_string_value_pair import (
        SynchronizationSecretKeyStringValuePair,
    )


class Synchronization(Entity):
    """
    Represents the capability for Azure Active Directory (Azure AD) identity synchronization through
    the Microsoft Graph API. Identity synchronization (also called provisioning) allows you to automate
    the provisioning (creation, maintenance) and de-provisioning (removal) of user identities and roles from
    Azure AD to supported cloud applications. For more information, see How Application Provisioning works
    in Azure Active Directory
    """

    @property
    def jobs(self) -> EntityCollection[SynchronizationJob]:
        """
        Performs synchronization by periodically running in the background, polling for changes in one directory,
        and pushing them to another directory.
        """
        return self.properties.get(
            "jobs", EntityCollection(self.context, SynchronizationJob, ResourcePath("jobs", self.resource_path))
        )

    @property
    def templates(self) -> EntityCollection[SynchronizationTemplate]:
        """
        Performs synchronization by periodically running in the background, polling for changes in one directory,
        and pushing them to another directory.
        """
        return self.properties.get(
            "templates",
            EntityCollection(self.context, SynchronizationTemplate, ResourcePath("templates", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Synchronization"

    @property
    def secrets(self) -> ClientValueCollection[SynchronizationSecretKeyStringValuePair]:
        """Gets the secrets property"""
        from office365.directory.synchronization.secret_key_string_value_pair import (
            SynchronizationSecretKeyStringValuePair,
        )

        return self.properties.get(
            "secrets",
            ClientValueCollection[SynchronizationSecretKeyStringValuePair](SynchronizationSecretKeyStringValuePair),
        )
