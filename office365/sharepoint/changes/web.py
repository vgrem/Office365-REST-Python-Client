from office365.sharepoint.changes.change import Change


class ChangeWeb(Change):
    """Specifies a change on a site"""

    @property
    def web_id(self):
        """
        Identifies the site (2) that has changed

        :rtype: str or None
        """
        return self.properties.get("WebId", None)
