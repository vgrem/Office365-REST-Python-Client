import time

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

    def poll_for_status(self, status_type="succeeded", max_polling_count=5, polling_interval_secs=15,
                        success_callback=None, failure_callback=None):
        """
        Poll to check for completion of an async Teams create call

        :param int polling_interval_secs:
        :param int max_polling_count:
        :param str status_type: The status of a teamsAsyncOperation
        :param (TeamsAsyncOperation)-> None success_callback: A callback to call
            if the request executes successfully.
        :param (TeamsAsyncOperation)-> None failure_callback: A callback to call if the request
            fails to execute
        """

        def _poll_for_status(polling_number):
            """
            :type polling_number: int
            """
            if polling_number > max_polling_count:
                if callable(failure_callback):
                    failure_callback(self)
                else:
                    raise TypeError("The maximum polling count has been reached")

            def _verify_status(return_type):
                if self.status != status_type:
                    time.sleep(polling_interval_secs)
                    _poll_for_status(polling_number + 1)
                else:
                    if callable(success_callback):
                        success_callback(self)
            self.context.load(self, after_loaded=_verify_status)

        self.ensure_property("id", _poll_for_status, 1)
        return self

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

    @property
    def status(self):
        """
        Operation status.

        :rtype: str
        """
        return self.properties.get("status", None)
