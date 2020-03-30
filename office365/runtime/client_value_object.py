from office365.runtime.odata.json_light_format import JsonLightFormat
from office365.runtime.odata.odata_metadata_level import ODataMetadataLevel


class ClientValueObject(object):
    """Base client value object"""

    def map_json(self, json):
        for key, val in json.items():
            # if hasattr(type(self), key):
            self.__dict__[key] = val

    def to_json(self):
        return dict((k, v) for k, v in vars(self).items() if v is not None)

    @property
    def entityTypeName(self):
        return None
