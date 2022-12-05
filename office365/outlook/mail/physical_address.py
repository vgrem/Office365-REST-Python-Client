from office365.runtime.client_value import ClientValue


class PhysicalAddress(ClientValue):
    """The physical address of a contact."""

    def __init__(self, city=None, country_or_region=None, postal_code=None):
        """
        :param str city: The city.
        :param str country_or_region: The country or region. It's a free-format string value, for example, "United States".
        :param str postal_code: The postal code.
        """
        super(PhysicalAddress, self).__init__()
        self.city = city
        self.countryOrRegion = country_or_region
        self.postalCode = postal_code
