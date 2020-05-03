from office365.runtime.client_value_object import ClientValueObject


class ContextWebInformation(ClientValueObject):
    """The context information for a site."""


    @property
    def formDigestValue(self):
        """The form digest value."""
        return self.get_property('FormDigestValue')
