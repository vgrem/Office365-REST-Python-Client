from __future__ import annotations

from typing import TYPE_CHECKING

from office365.directory.authentication.methods.method import AuthenticationMethod
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.common.external_authentication_method import (
        ExternalAuthenticationMethod,
    )
    from office365.common.software_oath_authentication_method import (
        SoftwareOathAuthenticationMethod,
    )
    from office365.directory.authentication.platform_credential_authentication_method import (
        PlatformCredentialAuthenticationMethod,
    )
    from office365.directory.authentication.temporary_access_pass_authentication_method import (
        TemporaryAccessPassAuthenticationMethod,
    )
    from office365.directory.authentication.windows_hello_for_business_authentication_method import (
        WindowsHelloForBusinessAuthenticationMethod,
    )
    from office365.onedrive.operations.long_running import LongRunningOperation


class Authentication(Entity):
    """
    Exposes relationships that represent the authentication methods supported by Azure AD and that can configured
    for users.
    """

    @odata(name="emailMethods")
    @property
    def email_methods(self):
        """The email address registered to a user for authentication."""
        from office365.directory.authentication.methods.email import (
            EmailAuthenticationMethod,
        )

        return self.properties.get(
            "emailMethods",
            EntityCollection(self.context, EmailAuthenticationMethod, ResourcePath("emailMethods", self.resource_path)),
        )

    @odata(name="fido2Methods")
    @property
    def fido2_methods(self):
        """Represents the FIDO2 security keys registered to a user for authentication."""
        from office365.directory.authentication.methods.fido import (
            Fido2AuthenticationMethod,
        )

        return self.properties.get(
            "fido2Methods",
            EntityCollection(self.context, Fido2AuthenticationMethod, ResourcePath("fido2Methods", self.resource_path)),
        )

    @odata(name="microsoftAuthenticatorMethods")
    @property
    def microsoft_authenticator_methods(self):
        from office365.directory.authentication.methods.microsoft_authenticator import (
            MicrosoftAuthenticatorAuthenticationMethod,
        )

        return self.properties.get(
            "microsoftAuthenticatorMethods",
            EntityCollection(
                self.context,
                MicrosoftAuthenticatorAuthenticationMethod,
                ResourcePath("microsoftAuthenticatorMethods", self.resource_path),
            ),
        )

    @odata(name="phoneMethods")
    @property
    def phone_methods(self):
        """The phone numbers registered to a user for authentication."""
        from office365.directory.authentication.methods.phone import (
            PhoneAuthenticationMethod,
        )

        return self.properties.get(
            "phoneMethods",
            EntityCollection(self.context, PhoneAuthenticationMethod, ResourcePath("phoneMethods", self.resource_path)),
        )

    @odata(name="passwordMethods")
    @property
    def password_methods(self):
        """Represents the password that's registered to a user for authentication. For security, the password itself
        will never be returned in the object, but action can be taken to reset a password.
        """
        from office365.directory.authentication.methods.password import (
            PasswordAuthenticationMethod,
        )

        return self.properties.get(
            "passwordMethods",
            EntityCollection(
                self.context, PasswordAuthenticationMethod, ResourcePath("passwordMethods", self.resource_path)
            ),
        )

    @property
    def methods(self) -> EntityCollection[AuthenticationMethod]:
        """Represents all authentication methods registered to a user."""
        return self.properties.get(
            "methods", EntityCollection(self.context, AuthenticationMethod, ResourcePath("methods", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Authentication"

    @property
    def external_authentication_methods(self) -> EntityCollection[ExternalAuthenticationMethod]:
        """Gets the externalAuthenticationMethods property"""
        from office365.common.external_authentication_method import (
            ExternalAuthenticationMethod,
        )

        return self.properties.get(
            "externalAuthenticationMethods",
            EntityCollection[ExternalAuthenticationMethod](
                self.context,
                ExternalAuthenticationMethod,
                ResourcePath("externalAuthenticationMethods", self.resource_path),
            ),
        )

    @property
    def operations(self) -> EntityCollection[LongRunningOperation]:
        """Gets the operations property"""
        from office365.onedrive.operations.long_running import LongRunningOperation

        return self.properties.get(
            "operations",
            EntityCollection[LongRunningOperation](
                self.context, LongRunningOperation, ResourcePath("operations", self.resource_path)
            ),
        )

    @property
    def platform_credential_methods(self) -> EntityCollection[PlatformCredentialAuthenticationMethod]:
        """Gets the platformCredentialMethods property"""
        from office365.directory.authentication.platform_credential_authentication_method import (
            PlatformCredentialAuthenticationMethod,
        )

        return self.properties.get(
            "platformCredentialMethods",
            EntityCollection[PlatformCredentialAuthenticationMethod](
                self.context,
                PlatformCredentialAuthenticationMethod,
                ResourcePath("platformCredentialMethods", self.resource_path),
            ),
        )

    @property
    def software_oath_methods(self) -> EntityCollection[SoftwareOathAuthenticationMethod]:
        """Gets the softwareOathMethods property"""
        from office365.common.software_oath_authentication_method import (
            SoftwareOathAuthenticationMethod,
        )

        return self.properties.get(
            "softwareOathMethods",
            EntityCollection[SoftwareOathAuthenticationMethod](
                self.context, SoftwareOathAuthenticationMethod, ResourcePath("softwareOathMethods", self.resource_path)
            ),
        )

    @property
    def temporary_access_pass_methods(self) -> EntityCollection[TemporaryAccessPassAuthenticationMethod]:
        """Gets the temporaryAccessPassMethods property"""
        from office365.directory.authentication.temporary_access_pass_authentication_method import (
            TemporaryAccessPassAuthenticationMethod,
        )

        return self.properties.get(
            "temporaryAccessPassMethods",
            EntityCollection[TemporaryAccessPassAuthenticationMethod](
                self.context,
                TemporaryAccessPassAuthenticationMethod,
                ResourcePath("temporaryAccessPassMethods", self.resource_path),
            ),
        )

    @property
    def windows_hello_for_business_methods(self) -> EntityCollection[WindowsHelloForBusinessAuthenticationMethod]:
        """Gets the windowsHelloForBusinessMethods property"""
        from office365.directory.authentication.windows_hello_for_business_authentication_method import (
            WindowsHelloForBusinessAuthenticationMethod,
        )

        return self.properties.get(
            "windowsHelloForBusinessMethods",
            EntityCollection[WindowsHelloForBusinessAuthenticationMethod](
                self.context,
                WindowsHelloForBusinessAuthenticationMethod,
                ResourcePath("windowsHelloForBusinessMethods", self.resource_path),
            ),
        )
