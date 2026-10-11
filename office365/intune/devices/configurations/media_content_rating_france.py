from __future__ import annotations

from dataclasses import dataclass

from office365.intune.devices.configurations.ios.general.ratingfrancemoviestype import (
    RatingFranceMoviesType,
)
from office365.intune.devices.configurations.ios.ratingfrancetelevisiontype import (
    RatingFranceTelevisionType,
)
from office365.runtime.client_value import ClientValue


@dataclass
class MediaContentRatingFrance(ClientValue):
    movieRating: RatingFranceMoviesType = RatingFranceMoviesType.allAllowed
    tvRating: RatingFranceTelevisionType = RatingFranceTelevisionType.allAllowed

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MediaContentRatingFrance"
