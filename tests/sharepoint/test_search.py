from datetime import datetime, timedelta
from unittest import TestCase

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.search.query.suggestion_results import QuerySuggestionResults
from office365.sharepoint.search.query_result import QueryResult
from office365.sharepoint.search.request import SearchRequest
from office365.sharepoint.search.result import SearchResult
from tests import test_user_credentials, test_site_url


class TestSearch(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestSearch, cls).setUpClass()
        cls.client = ClientContext(test_site_url).with_credentials(test_user_credentials)

    def test1_export_search_settings(self):
        current_user = self.client.web.current_user.get().execute_query()
        export_start_data = datetime.today() - timedelta(days=1)
        result = self.client.search.export(current_user.user_principal_name, export_start_data).execute_query()
        self.assertIsNotNone(result.value)

    def test2_export_popular_tenant_queries(self):
        result = self.client.search.export_popular_tenant_queries(10).execute_query()
        self.assertIsNotNone(result.value)

    def test3_get_search_center_url(self):
        result = self.client.search.search_center_url().execute_query()
        self.assertIsNotNone(result.value)

    def test4_search_post_query(self):
        result = self.client.search.post_query(query_text="filename:guide.docx").execute_query()
        self.assertIsInstance(result.value, SearchResult)
        self.assertIsInstance(result.value.PrimaryQueryResult, QueryResult)

    def test5_search_get_query(self):
        request = SearchRequest("guide.docx")
        result = self.client.search.query(request).execute_query()
        self.assertIsInstance(result.value, SearchResult)
        self.assertIsInstance(result.value.PrimaryQueryResult, QueryResult)

    def test6_search_suggest(self):
        result = self.client.search.suggest("guide.docx").execute_query()
        self.assertIsInstance(result.value, QuerySuggestionResults)

    # def test7_auto_completions(self):
    #    result = self.search.auto_completions("guide").execute_query()
    #    self.assertIsNotNone(result.value)

    def test8_get_query_configuration(self):
        result = self.client.search_setting.get_query_configuration().execute_query()
        self.assertIsNotNone(result.value)

    def test9_get_promoted_result_query_rules(self):
        result = self.client.search_setting.get_promoted_result_query_rules().execute_query()
        self.assertIsNotNone(result.value)

    # def test7_get_crawled_urls(self):
    #    doc_crawl_log = DocumentCrawlLog(self.client)
    #    result = doc_crawl_log.get_crawled_urls().execute_query()
    #    self.assertIsNotNone(result.value)

    #def test_10_auto_completions(self):
    #    result = self.client.search.auto_completions("guide.docx").execute_query()
    #    self.assertIsNotNone(result.value)

    #def test_11_get_crawled_urls(self):
    #    result = DocumentCrawlLog(self.client).get_crawled_urls().execute_query()
    #    self.assertIsNotNone(result.value)
