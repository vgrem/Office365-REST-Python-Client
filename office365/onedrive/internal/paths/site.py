from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.compat import urlparse, is_absolute_url


class SitePath(ResourcePath):
    """Resource path for addressing Site resource"""

    @property
    def segments(self):
        if is_absolute_url(self.name):
            url_info = urlparse(self.name)
            safe_path = url_info.path[:-1] if url_info.path.endswith("/") else url_info.path
            return [self.delimiter, url_info.hostname, ":", safe_path]
        else:
            return super(SitePath, self).segments
