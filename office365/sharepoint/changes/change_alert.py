from office365.sharepoint.changes.change import Change


class ChangeAlert(Change):

    @property
    def alert_id(self):
        return self.properties.get("AlertId", None)
