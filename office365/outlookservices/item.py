from office365.outlookservices.outlook_entity import OutlookEntity


class Item(OutlookEntity):
    """"""

    @property
    def changeKey(self):
        """Identifies the version of the outlook object. Every time the event is changed, ChangeKey changes as well.
           This allows Exchange to apply changes to the correct version of the object."""
        if self.is_property_available('ChangeKey'):
            return self.properties['ChangeKey']
        else:
            return None
