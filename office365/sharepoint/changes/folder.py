from office365.sharepoint.changes.change import Change


class ChangeFolder(Change):
    """Specifies a change on a folder not contained in a list or document library."""

    @property
    def unique_id(self):
        return self.properties.get("UniqueId", None)

    @property
    def web_id(self):
        return self.properties.get("WebId", None)
