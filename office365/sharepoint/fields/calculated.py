from office365.sharepoint.fields.field import Field


class FieldCalculated(Field):
    """
    Specifies a calculated field in a list. To set properties, call the Update method (section 3.2.5.38.2.1.5).

    The NoCrawl and SchemaXmlWithResourceTokens properties are not included in the default scalar property set
        for this type.
    """

    @property
    def currency_locale_id(self):
        """
        Gets the locale ID that is used for currency on the Web site.

        :rtype: int or None
        """
        return self.properties.get('CurrencyLocaleId', None)

    @property
    def formula(self):
        """
        Specifies the formula for the field

        :rtype: str or None
        """
        return self.properties.get('Formula', None)

    @formula.setter
    def formula(self, val):
        """Sets a value that specifies the Formula.

        :type val: str
        """
        self.set_property('Formula', val)
