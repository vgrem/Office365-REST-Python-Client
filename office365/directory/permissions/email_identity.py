from typing import Optional

from office365.directory.permissions.identity import Identity


class EmailIdentity(Identity):
    """Represents the email identity of a user."""

    @property
    def email(self):
        # type: () -> Optional[str]
        """Email address of the user"""
        return self.properties.get("email", None)
