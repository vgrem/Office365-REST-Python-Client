from office365.sharepoint.changes.change import Change


class ChangeAlert(Change):
    """Specifies a change from an alert."""

    @property
    def alert_id(self):
        """Identifies the changed alert.

        :rtype: str or None
        """
        return self.properties.get("AlertId", None)
