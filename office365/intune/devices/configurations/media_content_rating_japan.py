from __future__ import annotations

from dataclasses import dataclass

from office365.intune.devices.configurations.ios.ratingjapanmoviestype import (
    RatingJapanMoviesType,
)
from office365.intune.devices.configurations.ios.ratingjapantelevisiontype import (
    RatingJapanTelevisionType,
)
from office365.runtime.client_value import ClientValue


@dataclass
class MediaContentRatingJapan(ClientValue):
    movieRating: RatingJapanMoviesType = RatingJapanMoviesType.allAllowed
    tvRating: RatingJapanTelevisionType = RatingJapanTelevisionType.allAllowed

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MediaContentRatingJapan"
