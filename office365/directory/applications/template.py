from office365.entity import Entity
from office365.runtime.types.collections import StringCollection


class ApplicationTemplate(Entity):
    """Represents an application in the Azure AD application gallery."""

    @property
    def display_name(self):
        """
        The name of the application.

        :rtype: str or None
        """
        return self.properties.get("displayName", None)

    @property
    def categories(self):
        """
        The list of categories for the application. Supported values can be: Collaboration, Business Management,
        Consumer, Content management, CRM, Data services, Developer services, E-commerce, Education, ERP, Finance,
        Health, Human resources, IT infrastructure, Mail, Management, Marketing, Media, Productivity,
        Project management, Telecommunications, Tools, Travel, and Web design & hosting.
        """
        return self.properties.get("categories", StringCollection())

    @property
    def supported_provisioning_types(self):
        """
        The list of provisioning modes supported by this application
        """
        return self.properties.get("supportedProvisioningTypes", StringCollection())

    @property
    def supported_single_signon_modes(self):
        """
        The list of single sign-on modes supported by this application.
        The supported values are oidc, password, saml, and notSupported.
        """
        return self.properties.get("supportedSingleSignOnModes", StringCollection())

