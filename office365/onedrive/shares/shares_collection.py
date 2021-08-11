import base64

from office365.entity_collection import EntityCollection
from office365.onedrive.shares.shared_drive_item import SharedDriveItem
from office365.runtime.resource_path import ResourcePath


def _url_to_shared_token(url):
    value = base64.b64encode(url).decode("ascii")
    return "u!" + value[:-1].replace('/', '_').replace('+', '-')


class SharesCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(SharesCollection, self).__init__(context, SharedDriveItem, resource_path)

    def by_url(self, url):
        return ResourcePath(_url_to_shared_token(url), self.resource_path)
