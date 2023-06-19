from office365.runtime.client_value import ClientValue
from office365.runtime.compat import is_absolute_url, get_absolute_url, urlparse


class ResourcePath(ClientValue):

    def __init__(self, decoded_url=None):
        """
        Represents the full (absolute) or parts (relative) path of a site collection, web, file, folder or
        other artifacts in the database.

        :param str decoded_url: Gets the path in the decoded form.
        """
        super(ResourcePath, self).__init__()
        self.DecodedUrl = decoded_url

    @staticmethod
    def create_absolute(site_url, path):
        """
        :param str site_url: Site url
        :param str path: Resource path
        """
        if is_absolute_url(path):
            return ResourcePath(path)
        else:
            path = str(ResourcePath.create_relative(site_url, path))
            return ResourcePath("".join([get_absolute_url(site_url), path]))

    @staticmethod
    def create_relative(site_url, path):
        """
        :param str site_url: Site url
        :param str path: Resource path
        """
        site_path = urlparse(site_url).path
        if not path.startswith(site_path):
            return ResourcePath("/".join([site_path, path]))
        else:
            return ResourcePath(path)

    @property
    def entity_type_name(self):
        return "SP.ResourcePath"

    def __str__(self):
        return str(self.DecodedUrl)

    def __repr__(self):
        return str(self.DecodedUrl)
