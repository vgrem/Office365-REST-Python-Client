from office365.sharepoint.fields.field import Field


class FieldDateTime(Field):
    """Specifies a field (2) that contains date and time values. To set properties, call the Update method
    (section 3.2.5.44.2.1.5)."""

    @property
    def datetime_calendar_type(self):
        """
        Gets the calendar type of the field

        :rtype: int or None
        """
        return self.properties.get('DateTimeCalendarType', None)

    @datetime_calendar_type.setter
    def datetime_calendar_type(self, value):
        """
        Sets Gets the calendar type of the field

        :type value: int
        """
        self.set_property('DateTimeCalendarType', value)
