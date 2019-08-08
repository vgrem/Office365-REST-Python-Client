from json import JSONEncoder

from office365.runtime.client_object import ClientObject
from office365.runtime.client_value_object import ClientValueObject
from office365.runtime.odata.odata_metadata_level import ODataMetadataLevel


class ODataEncoder(JSONEncoder):
    """OData request payload serializer"""

    def __init__(self, json_format, **kwargs):
        super(ODataEncoder, self).__init__(**kwargs)
        self._json_format = json_format

    def default(self, payload):
        if isinstance(payload, ClientObject):
            return self.normalize_entity(payload)
        elif isinstance(payload, ClientValueObject):
            return self.normalize_property(payload)
        else:
            return payload

    def normalize_property(self, value):
        payload = dict((k, v) for k, v in value.__dict__.items() if v is not None)
        if self._json_format.metadata == ODataMetadataLevel.Verbose:
            payload["__metadata"] = {'type': value.type_name}
        if value.tag_name:
            payload = {value.tag_name: payload}
        return payload

    def normalize_entity(self, value):
        """Generates resource payload for OData endpoint"""
        payload = dict((k, v) for k, v in value.properties.items()
                       if k in value.properties_metadata and value.properties_metadata[k]['readonly'] is False)
        if self._json_format.metadata == ODataMetadataLevel.Verbose and "__metadata" not in payload.items():
            payload["__metadata"] = {'type': value.entity_type_name}
        else:
            payload = dict((k, v) for k, v in payload.items() if k != "__metadata")
        return payload
