import json
import re
from datetime import date, datetime
from typing import TYPE_CHECKING, Any, Dict, List, Union
from urllib.parse import quote

from office365.runtime.client_value import ClientValue
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.runtime.paths.service_operation import ServiceOperationPath


class ODataPathBuilder:
    """A builder for constructing OData paths with proper encoding and URL handling."""

    # Characters that need special handling in OData URLs.
    # NOTE: "/" is intentionally *not* encoded — slashes are valid inside OData
    # string literals, and encoding them inflates path-based URLs (~3x) enough to
    # hit SharePoint's URL length limit for deep folder structures.
    _SPECIAL_CHARS = {
        "%": "%25",
        "+": "%2B",
        "?": "%3F",
        "#": "%23",
        "&": "%26",
        "'": "''",
        "*": "%2A",
    }

    @staticmethod
    def parse_url(path_str: str) -> ResourcePath:
        """
        Parses a path from a string into a ResourcePath object.

        Args:
            path_str: The URL path string to parse

        Returns:
            ResourcePath: The constructed resource path

        Raises:
            TypeError: If the input string is empty or invalid
        """
        segments = [n for n in re.split(r"[('')]|/", path_str) if n]  # noqa
        if not segments:
            raise TypeError("Invalid path format")
        path = ResourcePath(segments[0], None)
        for segment in segments[1:]:
            path = ResourcePath(segment, path)
        return path

    @staticmethod
    def build_segment(path: "ServiceOperationPath") -> str:
        """
        Constructs the URL segment for a ServiceOperationPath.

        Args:
            path: The ServiceOperationPath to convert to a URL segment

        Returns:
            str: The constructed URL segment
        """
        if not path.name:
            return ""

        url = path.name
        if path.parameters is None:
            return url

        if isinstance(path.parameters, ClientValue):
            return f"{url}(@v)?@v={json.dumps(path.parameters.to_json())}"

        param_str = ODataPathBuilder._build_parameters(path.parameters)
        return f"{url}({param_str})" if param_str else url

    @staticmethod
    def _build_parameters(parameters: Union[Dict, List]) -> str:
        """
        Builds the parameters portion of the URL segment.

        Args:
            parameters: Either a dictionary or list of parameters

        Returns:
            str: The encoded parameters string
        """
        if isinstance(parameters, dict):
            return ",".join(
                f"{key}={ODataPathBuilder._encode_odata_value(value)}"
                for key, value in parameters.items()
                if value is not None
            )
        elif isinstance(parameters, (list, tuple)):
            return ",".join(ODataPathBuilder._encode_odata_value(value) for value in parameters if value is not None)
        return ""

    @staticmethod
    def _encode_odata_value(value: Any) -> str:  # noqa: PLR0911 - one return per OData literal kind
        """
        Encodes a value for safe inclusion in an OData URL.

        Args:
            value: The value to encode

        Returns:
            str: The encoded string representation
        """
        if isinstance(value, str):
            return ODataPathBuilder._encode_string(value)
        elif isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, datetime):
            # OData v3 datetime literal (UTC); ``datetime`` is a subclass of
            # ``date`` so it must be checked first. Without this branch a datetime
            # argument was URL-quoted via ``str()`` and produced an invalid path.
            return f"datetime'{value.strftime('%Y-%m-%dT%H:%M:%S')}'"
        elif isinstance(value, date):
            return f"date'{value.isoformat()}'"
        elif value is None:
            return "null"
        else:
            return quote(str(value))

    @staticmethod
    def _encode_string(value: str) -> str:
        """
        Encodes a string value with OData-specific escaping rules.

        Args:
            value: The string to encode

        Returns:
            str: The encoded string
        """
        # _SPECIAL_CHARS also covers the single quote ("'" -> "''"); escaping it
        # separately here would double it twice.
        for char, replacement in ODataPathBuilder._SPECIAL_CHARS.items():
            value = value.replace(char, replacement)

        return f"'{value}'"
