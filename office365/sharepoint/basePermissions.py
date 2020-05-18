from office365.runtime.client_value_object import ClientValueObject


class BasePermissions(ClientValueObject):
    """Specifies a set of built-in permissions."""

    def __init__(self):
        super(BasePermissions, self).__init__()
        self.High = 0
        self.Low = 0

    def has(self):
        """Determines whether the current instance has the specified permission."""
        pass

    def clear_all(self):
        """Clears all permissions for the current instance."""
        self.Low = 0
        self.High = 0
