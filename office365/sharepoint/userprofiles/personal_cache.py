from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.userprofiles.personal_cache_item import PersonalCacheItem


class PersonalCache(Entity):
    """Per user cache of key/value pairs organized by folders. Personal cache MAY be used for optimizing initial
    load performance of the protocol client, if obtaining initial set of data from personal cache is faster that
    requesting the data from the server."""

    def __init__(self, context):
        super().__init__(context, ResourcePath("SP.UserProfiles.PersonalCache"))

    def dispose(self):
        """ """
        qry = ServiceOperationQuery(self, "Dispose")
        self.context.add_query(qry)
        return self

    @property
    def cache_name(self) -> Optional[str]:
        """"""
        return self.properties.get("CacheName", None)

    @property
    def entity_type_name(self):
        return "SP.UserProfiles.PersonalCache"

    @property
    def my_site_url(self) -> Optional[str]:
        """Gets the MySiteUrl property"""
        return self.properties.get("MySiteUrl", None)

    @property
    def require_html_storage(self) -> Optional[bool]:
        """Gets the RequireHtmlStorage property"""
        return self.properties.get("RequireHtmlStorage", None)

    def delete_cache_items_async(self, cache_items: ClientValueCollection[PersonalCacheItem]) -> Self:
        """DeleteCacheItemsAsync operation.

        Args:
            cache_items (ClientValueCollection[PersonalCacheItem]):
                cacheItems parameter
        """
        qry = ServiceOperationQuery(self, "DeleteCacheItemsAsync", None, {"cacheItems": cache_items}, None, None)
        self.context.add_query(qry)
        return self

    def delete_cache_items_async2(self, cache_items: ClientValueCollection[PersonalCacheItem], my_site_url: str) -> Self:
        """DeleteCacheItemsAsync2 operation.

        Args:
            cache_items (ClientValueCollection[PersonalCacheItem]):
                cacheItems parameter
            my_site_url (str):
                mySiteUrl parameter
        """
        qry = ServiceOperationQuery(
            self, "DeleteCacheItemsAsync2", None, {"cacheItems": cache_items, "mySiteUrl": my_site_url}, None, None
        )
        self.context.add_query(qry)
        return self

    def read_cache(self, folder_path: str) -> ClientResult[ClientValueCollection[PersonalCacheItem]]:
        """ReadCache operation.

        Args:
            folder_path (str):
                folderPath parameter
        """
        from office365.sharepoint.userprofiles.personal_cache_item import (
            PersonalCacheItem,
        )

        return_type = ClientResult(self.context, ClientValueCollection[PersonalCacheItem]())
        qry = FunctionQuery(self, "ReadCache", [folder_path], return_type)
        self.context.add_query(qry)
        return return_type

    def read_cache2(self, folder_path: str, my_site_url: str) -> ClientResult[ClientValueCollection[PersonalCacheItem]]:
        """ReadCache2 operation.

        Args:
            folder_path (str):
                folderPath parameter
            my_site_url (str):
                mySiteUrl parameter
        """
        from office365.sharepoint.userprofiles.personal_cache_item import (
            PersonalCacheItem,
        )

        return_type = ClientResult(self.context, ClientValueCollection[PersonalCacheItem]())
        qry = FunctionQuery(self, "ReadCache2", [folder_path, my_site_url], return_type)
        self.context.add_query(qry)
        return return_type

    def read_cache_or_create(
        self, folder_path: ResourcePath, required_cache_keys: list[str], create_if_missing: bool
    ) -> ClientResult[ClientValueCollection[PersonalCacheItem]]:
        """ReadCacheOrCreate operation.

        Args:
            folder_path (ResourcePath):
                folderPath parameter
            required_cache_keys (list[str]):
                requiredCacheKeys parameter
            create_if_missing (bool):
                createIfMissing parameter
        """
        from office365.sharepoint.userprofiles.personal_cache_item import (
            PersonalCacheItem,
        )

        return_type = ClientResult(self.context, ClientValueCollection[PersonalCacheItem]())
        qry = ServiceOperationQuery(
            self,
            "ReadCacheOrCreate",
            None,
            {
                "folderPath": folder_path,
                "requiredCacheKeys": StringCollection(required_cache_keys),
                "createIfMissing": create_if_missing,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def read_cache_or_create2(
        self, folder_path: ResourcePath, required_cache_keys: list[str], create_if_missing: bool, my_site_url: str
    ) -> ClientResult[ClientValueCollection[PersonalCacheItem]]:
        """ReadCacheOrCreate2 operation.

        Args:
            folder_path (ResourcePath):
                folderPath parameter
            required_cache_keys (list[str]):
                requiredCacheKeys parameter
            create_if_missing (bool):
                createIfMissing parameter
            my_site_url (str):
                mySiteUrl parameter
        """
        from office365.sharepoint.userprofiles.personal_cache_item import (
            PersonalCacheItem,
        )

        return_type = ClientResult(self.context, ClientValueCollection[PersonalCacheItem]())
        qry = ServiceOperationQuery(
            self,
            "ReadCacheOrCreate2",
            None,
            {
                "folderPath": folder_path,
                "requiredCacheKeys": StringCollection(required_cache_keys),
                "createIfMissing": create_if_missing,
                "mySiteUrl": my_site_url,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def read_cache_or_create_order_by_id(
        self, folder_path: ResourcePath, required_cache_keys: list[str], create_if_missing: bool
    ) -> ClientResult[ClientValueCollection[PersonalCacheItem]]:
        """ReadCacheOrCreateOrderById operation.

        Args:
            folder_path (ResourcePath):
                folderPath parameter
            required_cache_keys (list[str]):
                requiredCacheKeys parameter
            create_if_missing (bool):
                createIfMissing parameter
        """
        from office365.sharepoint.userprofiles.personal_cache_item import (
            PersonalCacheItem,
        )

        return_type = ClientResult(self.context, ClientValueCollection[PersonalCacheItem]())
        qry = ServiceOperationQuery(
            self,
            "ReadCacheOrCreateOrderById",
            None,
            {
                "folderPath": folder_path,
                "requiredCacheKeys": StringCollection(required_cache_keys),
                "createIfMissing": create_if_missing,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def read_cache_or_create_order_by_id2(
        self, folder_path: ResourcePath, required_cache_keys: list[str], create_if_missing: bool, my_site_url: str
    ) -> ClientResult[ClientValueCollection[PersonalCacheItem]]:
        """ReadCacheOrCreateOrderById2 operation.

        Args:
            folder_path (ResourcePath):
                folderPath parameter
            required_cache_keys (list[str]):
                requiredCacheKeys parameter
            create_if_missing (bool):
                createIfMissing parameter
            my_site_url (str):
                mySiteUrl parameter
        """
        from office365.sharepoint.userprofiles.personal_cache_item import (
            PersonalCacheItem,
        )

        return_type = ClientResult(self.context, ClientValueCollection[PersonalCacheItem]())
        qry = ServiceOperationQuery(
            self,
            "ReadCacheOrCreateOrderById2",
            None,
            {
                "folderPath": folder_path,
                "requiredCacheKeys": StringCollection(required_cache_keys),
                "createIfMissing": create_if_missing,
                "mySiteUrl": my_site_url,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def write_cache(self, cache_items: ClientValueCollection[PersonalCacheItem]) -> Self:
        """WriteCache operation.

        Args:
            cache_items (ClientValueCollection[PersonalCacheItem]):
                cacheItems parameter
        """
        qry = ServiceOperationQuery(self, "WriteCache", None, {"cacheItems": cache_items}, None, None)
        self.context.add_query(qry)
        return self

    def write_cache2(self, cache_items: ClientValueCollection[PersonalCacheItem], my_site_url: str) -> Self:
        """WriteCache2 operation.

        Args:
            cache_items (ClientValueCollection[PersonalCacheItem]):
                cacheItems parameter
            my_site_url (str):
                mySiteUrl parameter
        """
        qry = ServiceOperationQuery(
            self, "WriteCache2", None, {"cacheItems": cache_items, "mySiteUrl": my_site_url}, None, None
        )
        self.context.add_query(qry)
        return self
