class CalendarRoleType:

    def __init__(self):
        pass

    none = 0
    """Calendar is not shared with the user."""

    freeBusyRead = 1
    """User is a sharee who can view free/busy status of the owner on the calendar."""

    limitedRead = 2
    """User is a sharee who can view free/busy status, and titles and locations of the events on the calendar."""
