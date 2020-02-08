from office365.runtime.odata.json_light_format import JsonLightFormat
from office365.runtime.odata.odata_metadata_level import ODataMetadataLevel


class ClientValueObject(object):
    """Base client value object"""

    def map_json(self, json):
        for key, val in json.items():
            # if hasattr(type(self), key):
            self.__dict__[key] = val

    def to_json(self, data_format):
        json = dict((k, v) for k, v in vars(self).items() if v is not None)
        if isinstance(data_format, JsonLightFormat) and data_format.metadata == ODataMetadataLevel.Verbose:
            json["__metadata"] = {'type': self.typeName}
        return json

    @property
    def typeName(self):
        return None
