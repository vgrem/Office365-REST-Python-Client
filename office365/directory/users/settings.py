from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath
from office365.teams.schedule.shifts.preferences import ShiftPreferences


class UserSettings(Entity):
    """The current user settings for content discovery."""

    @property
    def shift_preferences(self):
        return self.properties.get('shiftPreferences',
                                   ShiftPreferences(self.context, ResourcePath("shiftPreferences", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "shiftPreferences": self.shift_preferences
            }
            default_value = property_mapping.get(name, None)
        return super(UserSettings, self).get_property(name, default_value)
