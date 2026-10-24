from __future__ import annotations

from typing import Union

from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.features.feature import Feature
from office365.sharepoint.features.known_list import KnownFeaturesList


class FeatureCollection(EntityCollection[Feature]):
    """Represents a collection of Feature resources."""

    def __init__(self, context, resource_path=None, parent=None):
        super().__init__(context, Feature, resource_path, parent)

    def add(
        self,
        feature_id: Union[KnownFeaturesList, str],
        force: bool,
        featdef_scope: int,
        verify_if_activated: bool = False,
    ) -> Feature:
        """Adds the feature to the collection of activated features and returns the added feature.

        Args:
            feature_id: The feature identifier of the feature to be added.
            force: Whether to continue even if there are errors.
            featdef_scope: The feature scope for this feature.
            verify_if_activated: Verify if activated first to avoid System.Data.DuplicateNameException.
        """
        fid = feature_id.value if isinstance(feature_id, KnownFeaturesList) else feature_id

        return_type = self.get_by_id(fid)
        self.add_child(return_type)

        def _create_query():
            payload = {
                "featureId": fid,
                "force": force,
                "featdefScope": featdef_scope,
            }
            return ServiceOperationQuery(self, "Add", None, payload, None, return_type)

        def _create_if_not_activated(_: FeatureCollection) -> None:
            # The activation state is read from the collection, not from
            # ``GetById``: at site scope the latter answers a null payload even for
            # an activated feature, so a truthiness test on that response reports
            # "activated" and silently never queues the add.
            activated = "".join(str(f.definition_id).lower() for f in self)
            if str(fid).lower() not in activated:
                self.context.add_query(_create_query())

        if verify_if_activated:
            self.get().after_execute(_create_if_not_activated)
        else:
            self.context.add_query(_create_query())

        return return_type

    def get_by_id(self, feature_id: str) -> Feature:
        """Returns the feature for the given feature identifier.

        Args:
            feature_id: The feature identifier of the feature to be returned.
        """
        return Feature(
            self.context,
            ServiceOperationPath("GetById", [feature_id], self.resource_path),
        )
