from __future__ import annotations

from dataclasses import dataclass

from office365.intune.devices.configurations.ios.ratingnewzealandmoviestype import (
    RatingNewZealandMoviesType,
)
from office365.intune.devices.configurations.ios.ratingnewzealandtelevisiontype import (
    RatingNewZealandTelevisionType,
)
from office365.runtime.client_value import ClientValue


@dataclass
class MediaContentRatingNewZealand(ClientValue):
    movieRating: RatingNewZealandMoviesType = RatingNewZealandMoviesType.allAllowed
    tvRating: RatingNewZealandTelevisionType = RatingNewZealandTelevisionType.allAllowed

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MediaContentRatingNewZealand"
