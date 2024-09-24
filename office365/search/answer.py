from office365.entity import Entity


class SearchAnswer(Entity):
    """Represents the base type for other search answers."""

    @property
    def entity_type_name(self):
        return "microsoft.graph.search.searchAnswer"
