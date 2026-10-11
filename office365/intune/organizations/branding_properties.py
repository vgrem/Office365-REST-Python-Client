from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.intune.organizations.content_customization import (
        ContentCustomization,
    )
    from office365.intune.organizations.login_page_layout_configuration import (
        LoginPageLayoutConfiguration,
    )
    from office365.intune.organizations.login_page_text_visibility_settings import (
        LoginPageTextVisibilitySettings,
    )


class OrganizationalBrandingProperties(Entity):
    """
    An abstract type that exposes properties for configuring an organization's branding.

    Organizations can customize their Azure Active Directory (Azure AD) sign-in pages which appear when users sign in to
    their organization's tenant-specific apps, or when Azure AD identifies the user's tenant from their username.
    A developer can also read the company's branding information and customize their app experience to tailor
    it specifically for the signed-in user using their company's branding.

    You can't change your original configuration's language as represented by the organizationalBranding object.
    However, companies can add different branding based on locale. For language-specific branding,
    see the organizationalBrandingLocalization object.
    """

    @property
    def background_color(self) -> Optional[str]:
        """Gets the backgroundColor property"""
        return self.properties.get("backgroundColor", None)

    @property
    def background_image(self) -> Optional[bytes]:
        """Gets the backgroundImage property"""
        return self.properties.get("backgroundImage", None)

    @property
    def background_image_relative_url(self) -> Optional[str]:
        """Gets the backgroundImageRelativeUrl property"""
        return self.properties.get("backgroundImageRelativeUrl", None)

    @property
    def banner_logo(self) -> Optional[bytes]:
        """Gets the bannerLogo property"""
        return self.properties.get("bannerLogo", None)

    @property
    def banner_logo_relative_url(self) -> Optional[str]:
        """Gets the bannerLogoRelativeUrl property"""
        return self.properties.get("bannerLogoRelativeUrl", None)

    @property
    def cdn_list(self) -> StringCollection:
        """Gets the cdnList property"""
        return self.properties.get("cdnList", StringCollection())

    @property
    def content_customization(self) -> ContentCustomization:
        """Gets the contentCustomization property"""
        from office365.intune.organizations.content_customization import (
            ContentCustomization,
        )

        return self.properties.get("contentCustomization", ContentCustomization())

    @property
    def custom_account_reset_credentials_url(self) -> Optional[str]:
        """Gets the customAccountResetCredentialsUrl property"""
        return self.properties.get("customAccountResetCredentialsUrl", None)

    @property
    def custom_cannot_access_your_account_text(self) -> Optional[str]:
        """Gets the customCannotAccessYourAccountText property"""
        return self.properties.get("customCannotAccessYourAccountText", None)

    @property
    def custom_cannot_access_your_account_url(self) -> Optional[str]:
        """Gets the customCannotAccessYourAccountUrl property"""
        return self.properties.get("customCannotAccessYourAccountUrl", None)

    @property
    def custom_css(self) -> Optional[bytes]:
        """Gets the customCSS property"""
        return self.properties.get("customCSS", None)

    @property
    def custom_css_relative_url(self) -> Optional[str]:
        """Gets the customCSSRelativeUrl property"""
        return self.properties.get("customCSSRelativeUrl", None)

    @property
    def custom_forgot_my_password_text(self) -> Optional[str]:
        """Gets the customForgotMyPasswordText property"""
        return self.properties.get("customForgotMyPasswordText", None)

    @property
    def custom_privacy_and_cookies_text(self) -> Optional[str]:
        """Gets the customPrivacyAndCookiesText property"""
        return self.properties.get("customPrivacyAndCookiesText", None)

    @property
    def custom_privacy_and_cookies_url(self) -> Optional[str]:
        """Gets the customPrivacyAndCookiesUrl property"""
        return self.properties.get("customPrivacyAndCookiesUrl", None)

    @property
    def custom_reset_it_now_text(self) -> Optional[str]:
        """Gets the customResetItNowText property"""
        return self.properties.get("customResetItNowText", None)

    @property
    def custom_terms_of_use_text(self) -> Optional[str]:
        """Gets the customTermsOfUseText property"""
        return self.properties.get("customTermsOfUseText", None)

    @property
    def custom_terms_of_use_url(self) -> Optional[str]:
        """Gets the customTermsOfUseUrl property"""
        return self.properties.get("customTermsOfUseUrl", None)

    @property
    def favicon(self) -> Optional[bytes]:
        """Gets the favicon property"""
        return self.properties.get("favicon", None)

    @property
    def favicon_relative_url(self) -> Optional[str]:
        """Gets the faviconRelativeUrl property"""
        return self.properties.get("faviconRelativeUrl", None)

    @property
    def header_background_color(self) -> Optional[str]:
        """Gets the headerBackgroundColor property"""
        return self.properties.get("headerBackgroundColor", None)

    @property
    def header_logo(self) -> Optional[bytes]:
        """Gets the headerLogo property"""
        return self.properties.get("headerLogo", None)

    @property
    def header_logo_relative_url(self) -> Optional[str]:
        """Gets the headerLogoRelativeUrl property"""
        return self.properties.get("headerLogoRelativeUrl", None)

    @property
    def login_page_layout_configuration(self) -> LoginPageLayoutConfiguration:
        """Gets the loginPageLayoutConfiguration property"""
        from office365.intune.organizations.login_page_layout_configuration import (
            LoginPageLayoutConfiguration,
        )

        return self.properties.get("loginPageLayoutConfiguration", LoginPageLayoutConfiguration())

    @property
    def login_page_text_visibility_settings(self) -> LoginPageTextVisibilitySettings:
        """Gets the loginPageTextVisibilitySettings property"""
        from office365.intune.organizations.login_page_text_visibility_settings import (
            LoginPageTextVisibilitySettings,
        )

        return self.properties.get("loginPageTextVisibilitySettings", LoginPageTextVisibilitySettings())

    @property
    def sign_in_page_text(self) -> Optional[str]:
        """Gets the signInPageText property"""
        return self.properties.get("signInPageText", None)

    @property
    def square_logo(self) -> Optional[bytes]:
        """Gets the squareLogo property"""
        return self.properties.get("squareLogo", None)

    @property
    def square_logo_dark(self) -> Optional[bytes]:
        """Gets the squareLogoDark property"""
        return self.properties.get("squareLogoDark", None)

    @property
    def square_logo_dark_relative_url(self) -> Optional[str]:
        """Gets the squareLogoDarkRelativeUrl property"""
        return self.properties.get("squareLogoDarkRelativeUrl", None)

    @property
    def square_logo_relative_url(self) -> Optional[str]:
        """Gets the squareLogoRelativeUrl property"""
        return self.properties.get("squareLogoRelativeUrl", None)

    @property
    def username_hint_text(self) -> Optional[str]:
        """Gets the usernameHintText property"""
        return self.properties.get("usernameHintText", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OrganizationalBrandingProperties"
