class ClientValueObject(object):
    """Base client value object"""

    @property
    def type_name(self):
        return None

    @property
    def tag_name(self):
        return None
