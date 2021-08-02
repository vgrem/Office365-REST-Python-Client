from office365.mail.message import Message


class EventMessage(Message):
    """A message that represents a meeting request, cancellation, or response (which can be one of the following:
    acceptance, tentative acceptance, or decline)."""
    pass
