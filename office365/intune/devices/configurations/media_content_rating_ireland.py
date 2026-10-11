from __future__ import annotations

from dataclasses import dataclass

from office365.intune.devices.configurations.ios.ratingirelandmoviestype import (
    RatingIrelandMoviesType,
)
from office365.intune.devices.configurations.ios.ratingirelandtelevisiontype import (
    RatingIrelandTelevisionType,
)
from office365.runtime.client_value import ClientValue


@dataclass
class MediaContentRatingIreland(ClientValue):
    movieRating: RatingIrelandMoviesType = RatingIrelandMoviesType.allAllowed
    tvRating: RatingIrelandTelevisionType = RatingIrelandTelevisionType.allAllowed

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MediaContentRatingIreland"
