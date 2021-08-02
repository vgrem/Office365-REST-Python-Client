from office365.outlook.mail.message import Message


class EventMessage(Message):
    """A message that represents a meeting request, cancellation, or response (which can be one of the following:
    acceptance, tentative acceptance, or decline)."""
    pass
