from office365.runtime.client_value import ClientValue


class FieldGeolocationValue(ClientValue):

    def __init__(self, latitude, longitude, altitude=None):
        """
        :param float latitude: Specifies the latitude value for Geolocation field.
        :param float longitude: Specifies the longitude value for Geolocation field.
        :param float altitude: Specifies the altitude value for Geolocation field. It is a user defined value

        """
        super().__init__()
        self.Latitude = latitude
        self.Longitude = longitude
        self.Altitude = altitude

    @property
    def entity_type_name(self):
        return "SP.FieldGeolocationValue"
