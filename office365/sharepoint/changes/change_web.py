from office365.sharepoint.changes.change import Change


class ChangeWeb(Change):

    @property
    def web_id(self):
        return self.properties.get("WebId", None)
