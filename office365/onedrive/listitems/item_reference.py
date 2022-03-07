from office365.runtime.client_value import ClientValue


class ItemReference(ClientValue):
    """The ItemReference resource provides information necessary to address a DriveItem via the API."""

    def __init__(self, name=None, path=None, drive_type=None, site_id=None):
        """
        :param str name: The name of the item being referenced. Read-only.
        :param str path: Path that can be used to navigate to the item. Read-only.
        :param str drive_type: Identifies the type of drive. See drive resource for values.
        :param str site_id: For OneDrive for Business and SharePoint, this property represents the ID of the site
            that contains the parent document library of the driveItem resource. The value is the same as the id
            property of that site resource. It is an opaque string that consists of three identifiers of the site.
            For OneDrive, this property is not populated.
        """
        super(ItemReference, self).__init__()
        self.name = name
        self.path = path
        self.driveType = drive_type
        self.siteId = site_id
