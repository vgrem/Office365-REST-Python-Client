from office365.sharepoint.changes.change import Change


class ChangeUser(Change):
    """Specifies a change on a user."""

    @property
    def activate(self):
        """
        Specifies whether a user has changed from an inactive state to an active state.

        When a user is added to a site and only has browse permissions, the user is in an inactive state.
        However, once the user can author list items, add documents, be assigned tasks, or make any contribution
        to the site, the user is in an active state.

        :rtype: bool or None
        """
        return self.properties.get("Activate", None)

    @property
    def user_id(self):
        """Uniquely identifies the changed user.

        :rtype: str or None
        """
        return self.properties.get("UserId", None)
