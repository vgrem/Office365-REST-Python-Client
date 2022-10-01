from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.teams.shifts.scheduling_group import SchedulingGroup
from office365.teams.shifts.shift import Shift


class Schedule(Entity):
    """A collection of schedulingGroup objects, shift objects, timeOffReason objects,
    and timeOff objects within a team."""

    @property
    def time_zone(self):
        """Indicates the time zone of the shifts team using tz database format. Required."""
        return self.properties.get('timeZone', None)

    @time_zone.setter
    def time_zone(self, value):
        self.set_property("timeZone", value)

    @property
    def shifts(self):
        """The shifts in the shifts."""
        return self.properties.get('shifts',
                                   EntityCollection(self.context, Shift,
                                                    ResourcePath("shifts", self.resource_path)))

    @property
    def scheduling_group(self):
        """The logical grouping of users in the shifts (usually by role).
        """
        return self.properties.get('schedulingGroups',
                                   EntityCollection(self.context, SchedulingGroup,
                                                    ResourcePath("schedulingGroups", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "schedulingGroups": self.scheduling_group,
            }
            default_value = property_mapping.get(name, None)
        return super(Schedule, self).get_property(name, default_value)
