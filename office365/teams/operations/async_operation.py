from office365.entity import Entity


class TeamsAsyncOperation(Entity):
    """
    A Microsoft Teams async operation is an operation that transcends the lifetime of a single API request.
    These operations are long-running or too expensive to complete within the timeframe of their originating request.

    When an async operation is initiated, the method returns a 202 Accepted response code.
    The response will also contain a Location header, which contains the location of the teamsAsyncOperation.
    Periodically check the status of the operation by making a GET request to this location; wait >30 seconds
    between checks. When the request completes successfully, the status will be "succeeded" and
    the targetResourceLocation will point to the created/modified resource.

    """

    @property
    def target_resource_id(self):
        """The ID of the object that's created or modified as result of this async operation, typically a team.

        :rtype: str or None
        """
        return self.properties.get("targetResourceId", None)

    @property
    def target_resource_location(self):
        """The location of the object that's created or modified as result of this async operation.
        This URL should be treated as an opaque value and not parsed into its component paths.

        :rtype: str or None
        """
        return self.properties.get("targetResourceLocation", None)
