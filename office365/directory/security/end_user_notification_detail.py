from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.permissions.email_identity import EmailIdentity


class EndUserNotificationDetail(Entity):
    @property
    def email_content(self) -> Optional[str]:
        """Gets the emailContent property"""
        return self.properties.get("emailContent", None)

    @property
    def is_default_langauge(self) -> Optional[bool]:
        """Gets the isDefaultLangauge property"""
        return self.properties.get("isDefaultLangauge", None)

    @property
    def language(self) -> Optional[str]:
        """Gets the language property"""
        return self.properties.get("language", None)

    @property
    def locale(self) -> Optional[str]:
        """Gets the locale property"""
        return self.properties.get("locale", None)

    @property
    def sent_from(self) -> EmailIdentity:
        """Gets the sentFrom property"""
        from office365.directory.permissions.email_identity import EmailIdentity

        return self.properties.get("sentFrom", EmailIdentity())

    @property
    def subject(self) -> Optional[str]:
        """Gets the subject property"""
        return self.properties.get("subject", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.EndUserNotificationDetail"
