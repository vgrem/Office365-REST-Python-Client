from office365.runtime.odata.v3.json_light_format import JsonLightFormat


class ClientValue(object):
    """Represent complex type.
    Complex types consist of a list of properties with no key, and can therefore only exist as properties of a
    containing entity or as a temporary value
    """

    def set_property(self, k, v, persist_changes=True):
        prop_type = getattr(self, k, None)
        if isinstance(prop_type, ClientValue) and v is not None:
            if isinstance(v, list):
                [prop_type.set_property(i, p_v, persist_changes) for i, p_v in enumerate(v)]
            else:
                [prop_type.set_property(k, p_v, persist_changes) for k, p_v in v.items()]
            setattr(self, k, prop_type)
        else:
            setattr(self, k, v)
        return self

    def get_property(self, k):
        return getattr(self, k)

    def to_json(self, json_format=None):
        """
        :type json_format: office365.runtime.odata.odata_json_format.ODataJsonFormat or None
        """
        json = dict((k, v) for k, v in vars(self).items() if v is not None)
        for n, v in json.items():
            if isinstance(v, ClientValue):
                json[n] = v.to_json(json_format)

        if isinstance(json_format, JsonLightFormat) and json_format.include_control_information() and self.entity_type_name is not None:
            json[json_format.metadata_type_tag_name] = {'type': self.entity_type_name}

        return json

    @property
    def entity_type_name(self):
        return type(self).__name__
