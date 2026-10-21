from typing import List, Optional

from office365.directory.permissions.require_permission import require_permission
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.v4.entity import EntityPath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.search.acronyms.acronym import Acronym
from office365.search.bookmarks.bookmark import Bookmark
from office365.search.entity_type import EntityType
from office365.search.hits.hit import SearchHit
from office365.search.qnas.qna import Qna
from office365.search.query import SearchQuery
from office365.search.request import SearchRequest
from office365.search.response import SearchResponse


class SearchEntity(Entity):
    """
    A top level object representing the Microsoft Search API endpoint. It does not behave as any other resource
    in Graph, but serves as an anchor to the query action.
    """

    @require_permission(
        delegated=[
            "Mail.Read",
            "Calendars.Read",
            "Files.Read.All",
            "Sites.Read.All",
            "People.Read",
            "ExternalItem.Read.All",
            "Chat.Read",
        ],
        application=[
            "Mail.Read",
            "Calendars.Read",
            "Files.Read.All",
            "Sites.Read.All",
            "People.Read",
            "ExternalItem.Read.All",
            "Chat.Read.All",
        ],
        licenses=["SPE_E5"],
        notes="Permissions depend on the entity types being queried",
    )
    def query(
        self,
        query_string: str,
        entity_types: Optional[List[str]] = None,
        page_from: Optional[int] = None,
        size: Optional[int] = None,
        enable_top_results: Optional[bool] = None,
        region: Optional[str] = None,
    ) -> ClientResult[ClientValueCollection[SearchResponse]]:
        """Runs the query specified in the request body. Search results are provided in the response.

        Args:
            query_string (str): Contains the query terms.
            entity_types (list[str]): One or more types of resources expected in the response.
              Possible values are: list, site, listItem, message, event, drive, driveItem, externalItem.
            page_from (int): Specifies the offset for the search results. Offset 0 returns the very first result.
            size (int): The size of the page to be retrieved. The maximum value is 500. Optional.
            enable_top_results (bool): This triggers hybrid sort for messages
            region (str): The geographic location for the search. Required for searches that use application
              permissions. For details, see Get the region value.
        """
        search_request = SearchRequest(
            query=SearchQuery(query_string),
            entityTypes=entity_types,
            page_from=page_from,
            size=size,
            enableTopResults=enable_top_results,
            region=region,
        )

        def _patch_hit(search_hit: SearchHit) -> None:
            resource_type_name = search_hit.get_property("resource").get("@odata.type", None)
            resource_type = EntityType.resolve(resource_type_name)
            resource = resource_type(self.context, EntityPath())
            self.context.pending_request().hydrate(resource, search_hit.resource)
            search_hit.set_property("resource", resource)

        def _handle_response(
            result: ClientResult[ClientValueCollection[SearchResponse]],
        ) -> None:
            result_items = result.value
            for item in result_items:
                for hcs in item.hitsContainers:  # type: ignore[attr-defined]
                    [_patch_hit(hit) for hit in hcs.hits]

        payload = {"requests": ClientValueCollection(SearchRequest, [search_request])}
        return_type = ClientResult(self.context, ClientValueCollection(SearchResponse))
        qry = ServiceOperationQuery(self, "query", None, payload, None, return_type)
        self.context.add_query(qry).after_execute(_handle_response)
        return return_type

    @require_permission(delegated=["Mail.Read"], application=["Mail.Read"])
    def query_messages(
        self,
        query_string: str,
        page_from: Optional[int] = None,
        size: Optional[int] = None,
        enable_top_results: Optional[bool] = None,
    ) -> ClientResult[ClientValueCollection[SearchResponse]]:
        """Searches Outlook messages. Alias to query method

        Args:
            query_string (str): Contains the query terms.
            page_from (int): Specifies the offset for the search results. Offset 0 returns the very first result.
            size (int): The size of the page to be retrieved. The maximum value is 500. Optional.
            enable_top_results (bool): This triggers hybrid sort for messages
        """
        return self.query(
            query_string,
            entity_types=[EntityType.message],
            page_from=page_from,
            size=size,
            enable_top_results=enable_top_results,
        )

    @require_permission(delegated=["Calendars.Read"], application=["Calendars.Read"])
    def query_events(self, query_string: str) -> ClientResult[ClientValueCollection[SearchResponse]]:
        """Searches Outlook calendar events. Alias to query method

        Args:
            query_string (str): Contains the query terms.
        """
        return self.query(query_string, entity_types=[EntityType.event])

    @require_permission(
        delegated=["Files.Read.All", "Files.ReadWrite.All"],
        application=["Files.Read.All", "Files.ReadWrite.All"],
    )
    def query_drive_items(
        self, query_string: str, page_from: Optional[int] = None, size: Optional[int] = None
    ) -> ClientResult[ClientValueCollection[SearchResponse]]:
        """Searches OneDrive items. Alias to query method

        Args:
            query_string (str): Contains the query terms.
            page_from (int): Specifies the offset for the search results. Offset 0 returns the very first result.
            size (int): The size of the page to be retrieved. The maximum value is 500.
        """
        return self.query(
            query_string,
            entity_types=[EntityType.driveItem],
            page_from=page_from,
            size=size,
        )

    @require_permission(
        delegated=["Sites.Read.All", "Sites.ReadWrite.All"],
        application=["Sites.Read.All", "Sites.ReadWrite.All"],
    )
    def query_list_items(
        self,
        query_string: str,
        page_from: Optional[int] = None,
        size: Optional[int] = None,
        region: Optional[str] = None,
    ) -> ClientResult[ClientValueCollection[SearchResponse]]:
        """Searches list items. Alias to query method

        Args:
            query_string (str): Contains the query terms.
            page_from (int): Specifies the offset for the search results. Offset 0 returns the very first result.
            size (int): The size of the page to be retrieved. The maximum value is 500.
            region (str): The geographic location for the search. Required for searches that use application
        """
        return self.query(
            query_string,
            entity_types=[EntityType.listItem],
            page_from=page_from,
            size=size,
            region=region,
        )

    @require_permission(delegated=["People.Read"], application=["People.Read"])
    def query_peoples(
        self,
        query_string: str,
        page_from: Optional[int] = None,
        size: Optional[int] = None,
        region: Optional[str] = None,
    ) -> ClientResult[ClientValueCollection[SearchResponse]]:
        """Searches peoples. Alias to query method

        Args:
            query_string (str): Contains the query terms.
            page_from (int): Specifies the offset for the search results. Offset 0 returns the very first result.
            size (int): The size of the page to be retrieved. The maximum value is 500.
            region (str): The geographic location for the search. Required for searches that use application
        """
        return self.query(
            query_string,
            entity_types=[EntityType.person],
            page_from=page_from,
            size=size,
            region=region,
        )

    @require_permission(
        delegated=["Sites.Read.All", "Sites.ReadWrite.All"],
        application=["Sites.Read.All", "Sites.ReadWrite.All"],
    )
    def query_sites(
        self,
        query_string: str,
        page_from: Optional[int] = None,
        size: Optional[int] = None,
        region: Optional[str] = None,
    ) -> ClientResult[ClientValueCollection[SearchResponse]]:
        """Searches sites. Alias to query method

        Args:
            query_string (str): Contains the query terms.
            page_from (int): Specifies the offset for the search results. Offset 0 returns the very first result.
            size (int): The size of the page to be retrieved. The maximum value is 500.
            region (str): The geographic location for the search. Required for searches that use application
        """
        return self.query(
            query_string,
            entity_types=[EntityType.site],
            page_from=page_from,
            size=size,
            region=region,
        )

    @require_permission(
        delegated=["Chat.Read", "Chat.ReadWrite"],
        application=["Chat.Read.All", "Chat.ReadWrite.All"],
    )
    def query_chat_messages(
        self,
        query_string: str,
        page_from: Optional[int] = None,
        size: Optional[int] = None,
        region: Optional[str] = None,
    ) -> ClientResult[ClientValueCollection[SearchResponse]]:
        """Searches Teams chat messages. Alias to query method

        Args:
            query_string (str): Contains the query terms.
            page_from (int): Specifies the offset for the search results. Offset 0 returns the very first result.
            size (int): The size of the page to be retrieved. The maximum value is 500.
            region (str): The geographic location for the search. Required for searches that use application
        """
        return self.query(
            query_string,
            entity_types=[EntityType.chatMessage],
            page_from=page_from,
            size=size,
            region=region,
        )

    @property
    @require_permission(
        delegated=["SearchConfiguration.Read.All", "SearchConfiguration.ReadWrite.All"],
        application=["SearchConfiguration.Read.All", "SearchConfiguration.ReadWrite.All"],
    )
    def acronyms(self) -> EntityCollection[Acronym]:
        """Administrative answer in Microsoft Search results to define common acronyms in an organization."""
        return self.properties.get(
            "acronyms",
            EntityCollection(
                self.context,
                Acronym,
                ResourcePath("acronyms", self.resource_path),
            ),
        )

    @property
    @require_permission(
        delegated=["SearchConfiguration.Read.All", "SearchConfiguration.ReadWrite.All"],
        application=["SearchConfiguration.Read.All", "SearchConfiguration.ReadWrite.All"],
    )
    def bookmarks(self) -> EntityCollection[Bookmark]:
        """Administrative answer in Microsoft Search results for common search queries in an organization."""
        return self.properties.get(
            "bookmarks",
            EntityCollection(
                self.context,
                Bookmark,
                ResourcePath("bookmarks", self.resource_path),
            ),
        )

    @property
    @require_permission(
        delegated=["SearchConfiguration.Read.All", "SearchConfiguration.ReadWrite.All"],
        application=["SearchConfiguration.Read.All", "SearchConfiguration.ReadWrite.All"],
    )
    def qnas(self) -> EntityCollection[Qna]:
        """Administrative answer in Microsoft Search results that provide answers for specific search keywords in
        an organization."""
        return self.properties.get(
            "qnas",
            EntityCollection(
                self.context,
                Qna,
                ResourcePath("qnas", self.resource_path),
            ),
        )
