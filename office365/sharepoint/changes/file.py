from office365.sharepoint.changes.change import Change


class ChangeFile(Change):
    """Specifies a change on a file not contained in a document library."""

    @property
    def unique_id(self):
        """Identifies the file that changed."""
        return self.properties.get("UniqueId", None)

    @property
    def web_id(self):
        """Identifies the site that contains the changed file."""
        return self.properties.get("WebId", None)
