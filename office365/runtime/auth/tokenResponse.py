import json


def _normalize_token_response(json_data):
    for key in json_data.keys():
        key_parts = key.split("_")
        if len(key_parts) == 2:
            new_key = "".join([key_parts[0], key_parts[1].title()])
            json_data[new_key] = json_data[key]
            del json_data[key]
    return json_data


class TokenResponse(object):

    def __init__(self, accessToken=None, tokenType=None, **kwargs):
        self.accessToken = accessToken
        self.tokenType = tokenType
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def is_valid(self):
        return self.accessToken is not None and self.tokenType == 'Bearer'

    @staticmethod
    def from_json(json_str):
        json_object = json.loads(json_str, object_hook=_normalize_token_response)
        return TokenResponse(**json_object)
