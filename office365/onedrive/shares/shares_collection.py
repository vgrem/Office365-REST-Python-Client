import base64

from office365.entity_collection import EntityCollection
from office365.onedrive.shares.shared_drive_item import SharedDriveItem
from office365.runtime.paths.resource_path import ResourcePath


def _url_to_shared_token(url):
    value = base64.b64encode(url.encode("ascii")).decode("ascii")
    if value.endswith("="):
        value = value[:-1]
    return "u!" + value.replace('/', '_').replace('+', '-')


class SharesCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(SharesCollection, self).__init__(context, SharedDriveItem, resource_path)

    def by_url(self, url):
        """
        Address shared item by absolute url

        :type url: str
        """
        return SharedDriveItem(self.context, ResourcePath(_url_to_shared_token(url), self.resource_path))
