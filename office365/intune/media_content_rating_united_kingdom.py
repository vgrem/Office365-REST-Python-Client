from __future__ import annotations

from dataclasses import dataclass

from office365.intune.devices.configurations.ios.ratingunitedkingdommoviestype import (
    RatingUnitedKingdomMoviesType,
)
from office365.intune.devices.configurations.ios.ratingunitedkingdomtelevisiontype import (
    RatingUnitedKingdomTelevisionType,
)
from office365.runtime.client_value import ClientValue


@dataclass
class MediaContentRatingUnitedKingdom(ClientValue):
    movieRating: RatingUnitedKingdomMoviesType = RatingUnitedKingdomMoviesType.allAllowed
    tvRating: RatingUnitedKingdomTelevisionType = RatingUnitedKingdomTelevisionType.allAllowed

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MediaContentRatingUnitedKingdom"
