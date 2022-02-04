class FieldType:

    def __init__(self):
        """Specifies the type of the field (2), as specified in [MS-WSSTS] section 2.3.1."""
        pass

    Invalid = 0

    Integer = 1

    Text = 2

    Note = 3

    DateTime = 4
    """Specifies that the field (2) contains a date and time value or a date-only value."""

    Counter = 5
    """Specifies that the field (2) contains a monotonically increasing integer."""

    Choice = 6

    Lookup = 7
    """Specifies that the field (2) is a lookup field."""

    Boolean = 8

    Number = 9

    Currency = 10

    URL = 11

    Computed = 12

    Threading = 13

    Guid = 14

    MultiChoice = 15

    GridChoice = 16

    Calculated = 17

    File = 18

    Attachments = 19

    User = 20

    Recurrence = 21

    CrossProjectLink = 22

    ModStat = 23

    Error = 24

    ContentTypeId = 25

    PageSeparator = 26

    ThreadIndex = 27

    WorkflowStatus = 28

    AllDayEvent = 29

    WorkflowEventType = 30

    Geolocation = 31

    OutcomeChoice = 32

    MaxItems = 33
