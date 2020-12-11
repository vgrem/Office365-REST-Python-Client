from datetime import datetime, timedelta
from unittest import TestCase

from settings import settings

from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.search.query.querySuggestionResults import QuerySuggestionResults
from office365.sharepoint.search.queryResult import QueryResult
from office365.sharepoint.search.searchRequest import SearchRequest
from office365.sharepoint.search.searchResult import SearchResult
from office365.sharepoint.search.searchService import SearchService


class TestSearch(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestSearch, cls).setUpClass()
        user_credentials = UserCredential(settings['user_credentials']['username'],
                                          settings['user_credentials']['password'])
        cls.client = ClientContext(settings['url']).with_credentials(user_credentials)
        cls.search = SearchService(cls.client)

    def test1_export_search_settings(self):
        current_user = self.client.web.current_user.get().execute_query()

        export_start_data = datetime.today() - timedelta(days=1)
        result = self.search.export(current_user.user_principal_name, export_start_data)
        self.client.execute_query()
        self.assertIsNotNone(result.value)

    def test2_export_popular_tenant_queries(self):
        result = self.search.export_popular_tenant_queries(10)
        self.client.execute_query()
        self.assertIsNotNone(result)

    def test3_get_search_center_url(self):
        result = self.search.search_center_url()
        self.client.execute_query()
        self.assertIsNotNone(result.value)

    def test4_search_post_query(self):
        request = SearchRequest("filename:guide.docx")
        result = self.search.post_query(request)
        self.client.execute_query()
        self.assertIsInstance(result, SearchResult)
        self.assertIsInstance(result.PrimaryQueryResult, QueryResult)

    def test5_search_get_query(self):
        request = SearchRequest("guide.docx")
        result = self.search.query(request)
        self.client.execute_query()
        self.assertIsInstance(result, SearchResult)
        self.assertIsInstance(result.PrimaryQueryResult, QueryResult)

    def test6_search_suggest(self):
        result = self.search.suggest("guide.docx")
        self.client.execute_query()
        self.assertIsInstance(result, QuerySuggestionResults)
