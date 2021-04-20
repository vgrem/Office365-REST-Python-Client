from office365.mail.outlook_entity import OutlookEntity


class Item(OutlookEntity):
    """"""

    @property
    def changeKey(self):
        """Identifies the version of the mail object. Every time the event is changed, ChangeKey changes as well.
           This allows Exchange to apply changes to the correct version of the object."""
        return self.properties.get('ChangeKey', None)
