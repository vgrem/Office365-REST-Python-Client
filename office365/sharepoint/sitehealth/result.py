from office365.runtime.client_value import ClientValue


class SiteHealthResult(ClientValue):
    """Specifies the result of running a site collection health rule."""

    @property
    def entity_type_name(self):
        return "SP.SiteHealth.SiteHealthResult"
