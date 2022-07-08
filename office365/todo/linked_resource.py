from office365.entity import Entity


class LinkedResource(Entity):
    """Represents an item in a partner application related to a todoTask. An example is an email from where the task
    was created. A linkedResource object stores information about that source application, and lets you link back to
    the related item. You can see the linkedResource in the task details view, as shown."""
