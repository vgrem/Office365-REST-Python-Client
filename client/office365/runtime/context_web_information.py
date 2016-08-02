class ContextWebInformation(object):
    """The context information for a site."""

    def __init__(self):
        self._properties = {}

    def from_json(self, properties):
        self._properties = properties

    @property
    def form_digest_value(self):
        """The form digest value."""
        return self._properties['FormDigestValue']
