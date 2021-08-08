from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.resource_path import ResourcePath
from office365.teams.schedule.scheduling_group import SchedulingGroup
from office365.teams.schedule.shift import Shift


class Schedule(Entity):
    """A collection of schedulingGroup objects, shift objects, timeOffReason objects,
    and timeOff objects within a team."""

    @property
    def time_zone(self):
        """Indicates the time zone of the schedule team using tz database format. Required."""
        return self.properties.get('timeZone', None)

    @time_zone.setter
    def time_zone(self, value):
        self.set_property("timeZone", value)

    @property
    def shifts(self):
        """The shifts in the schedule.

        :rtype: EntityCollection
        """
        return self.get_property('shifts',
                                 EntityCollection(self.context, Shift,
                                                  ResourcePath("shifts", self.resource_path)))

    @property
    def scheduling_group(self):
        """The logical grouping of users in the schedule (usually by role).

        :rtype: EntityCollection
        """
        return self.get_property('schedulingGroups',
                                 EntityCollection(self.context, SchedulingGroup,
                                                  ResourcePath("schedulingGroups", self.resource_path)))
