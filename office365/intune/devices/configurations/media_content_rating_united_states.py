from __future__ import annotations

from dataclasses import dataclass

from office365.intune.devices.configurations.ios.ratingunitedstatesmoviestype import (
    RatingUnitedStatesMoviesType,
)
from office365.intune.devices.configurations.ios.ratingunitedstatestelevisiontype import (
    RatingUnitedStatesTelevisionType,
)
from office365.runtime.client_value import ClientValue


@dataclass
class MediaContentRatingUnitedStates(ClientValue):
    movieRating: RatingUnitedStatesMoviesType = RatingUnitedStatesMoviesType.allAllowed
    tvRating: RatingUnitedStatesTelevisionType = RatingUnitedStatesTelevisionType.allAllowed

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MediaContentRatingUnitedStates"
