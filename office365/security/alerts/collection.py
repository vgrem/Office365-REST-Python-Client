from office365.entity_collection import EntityCollection
from office365.runtime.http.request_options import RequestOptions
from office365.security.alerts.alert import Alert


class AlertCollection(EntityCollection[Alert]):
    """Service Principal's collection"""

    def __init__(self, context, resource_path=None):
        super().__init__(context, Alert, resource_path)

    def add(
        self,
        title,
        description=None,
        severity=None,
        category=None,
        status=None,
        source=None,
        vendor_information=None,
    ):
        """Creates an alert object.

        Args:
            title (str):
            description (str):
            severity (str):
            category (str):
            status (str):
            source (str):
            vendor_information (str):
        """

        def _construct_request(request: RequestOptions) -> None:
            request.set_header("Content-Type", "application/json")

        return (
            super()
            .add(
                title=title,
                description=description,
                severity=severity,
                category=category,
                status=status,
                source=source,
                vendorInformation=vendor_information,
            )
            .before_execute(_construct_request)
        )
