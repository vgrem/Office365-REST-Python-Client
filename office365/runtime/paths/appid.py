from __future__ import annotations

from typing import Optional, Union

from office365.runtime.paths.alternate_key import AlternateKeyPath
from office365.runtime.paths.resource_path import ResourcePath


class AppIdPath(AlternateKeyPath):
    """Path for addressing a Service Principal or Application by appId where
    appId is referred to as Application (client) ID on the Azure portal"""

    def __init__(self, app_id: Union[int, str], parent: Optional[ResourcePath] = None) -> None:
        super().__init__("appId", app_id, parent)
