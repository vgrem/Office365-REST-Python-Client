from __future__ import annotations

from typing import Optional

from typing_extensions import Self

from office365.directory.authentication.configuration.base import (
    ApiAuthenticationConfigurationBase,
)
from office365.entity import Entity
from office365.runtime.queries.service_operation import ServiceOperationQuery


class IdentityApiConnector(Entity):
    """
    Represents API connectors in an Azure Active Directory (Azure AD) tenants.

    An API connector used in your Azure AD External Identities self-service sign-up user flows allows you to call
    an API during the execution of the user flow. An API connector provides the information needed to call an API
    including an endpoint URL and authentication. An API connector can be used at a specific step in a user flow
    to affect the execution of the user flow. For example, the API response can block a user from signing up,
    show an input validation error, or overwrite user collected attributes.
    """

    def upload_client_certificate(self, pkcs12_value: str, password: str) -> Self:
        """Upload a PKCS 12 format key (.pfx) to an API connector's authentication configuration.
        The input is a base-64 encoded value of the PKCS 12 certificate contents.
        This method returns an apiConnector.

        Args:
            pkcs12_value (str):
            password (str):
        """

        payload = {"pkcs12Value": pkcs12_value, "password": password}
        qry = ServiceOperationQuery(self, "uploadClientCertificate", None, payload, None, None)
        self.context.add_query(qry)
        return self

    @property
    def authentication_configuration(self) -> ApiAuthenticationConfigurationBase:
        """The object which describes the authentication configuration details for calling the API.
        Basic and PKCS 12 client certificate are supported."""
        return self.properties.get("authenticationConfiguration", ApiAuthenticationConfigurationBase())

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def target_url(self) -> Optional[str]:
        """Gets the targetUrl property"""
        return self.properties.get("targetUrl", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IdentityApiConnector"
