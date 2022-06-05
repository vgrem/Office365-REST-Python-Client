import base64

from office365.runtime.paths.resource_path import ResourcePath


def _url_to_shared_token(url):
    value = base64.b64encode(url.encode("ascii")).decode("ascii")
    if value.endswith("="):
        value = value[:-1]
    return "u!" + value.replace('/', '_').replace('+', '-')


class SharedPath(ResourcePath):
    """Shared token path"""

    def __init__(self, url, parent=None):
        super(SharedPath, self).__init__(_url_to_shared_token(url), parent)
