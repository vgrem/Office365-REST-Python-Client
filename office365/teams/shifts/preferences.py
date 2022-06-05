from office365.runtime.client_value_collection import ClientValueCollection
from office365.teams.shifts.availability import ShiftAvailability
from office365.teams.shifts.change_tracked_entity import ChangeTrackedEntity


class ShiftPreferences(ChangeTrackedEntity):
    """Represents a user's availability to be assigned shifts in the schedule."""

    @property
    def availability(self):
        """
        Availability of the user to be scheduled for work and its recurrence pattern.
        """
        return self.properties.get('availability', ClientValueCollection(ShiftAvailability))
