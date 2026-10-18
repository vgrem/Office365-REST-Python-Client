"""Tests for SharePoint search including queries, suggestions, settings, and administration."""

from __future__ import annotations

from datetime import datetime, timedelta

from office365.runtime.exceptions import AccessDeniedException
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.search.query.sort.sort import Sort
from office365.sharepoint.search.query.suggestion_results import QuerySuggestionResults
from office365.sharepoint.search.query_result import QueryResult
from office365.sharepoint.search.result import SearchResult

from tests import (
    test_client_id,
    test_password,
    test_site_url,
    test_tenant,
    test_username,
)
from tests.sharepoint.sharepoint_case import SPTestCase


class TestSearch(SPTestCase):
    """Test SharePoint search features."""

    @classmethod
    def setUpClass(cls):
        super(TestSearch, cls).setUpClass()
        cls.client = ClientContext(test_site_url).with_username_and_password(
            test_tenant, test_client_id, test_username, test_password
        )

    def test_01_get_search_service(self):
        """Get the search service object."""
        result = self.client.search.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test_02_export_search_settings(self):
        """Export search settings for the current user.

        Reading the query log is a search-administrator operation: on a tenant
        where the test account is not one, the service answers 403 Unauthorized.
        """
        current_user = self.client.web.current_user
        export_start_data = datetime.today() - timedelta(days=100)
        try:
            result = self.client.search.export(current_user, export_start_data).execute_query()
        except AccessDeniedException:
            self.skipTest(f"{test_username} is not a search administrator")
        self.assertIsNotNone(result.value)

    def test_03_export_popular_tenant_queries(self):
        """Export popular tenant search queries."""
        result = self.client.search.export_popular_tenant_queries(10).execute_query()
        self.assertIsNotNone(result.value)

    def test_04_get_search_center_url(self):
        """Get the search center URL."""
        result = self.client.search.search_center_url().execute_query()
        self.assertIsNotNone(result.value)

    def test_05_search_post_query(self):
        """Execute a search POST query."""
        result = self.client.search.post_query(query_text="filename:guide.docx").execute_query()
        self.assertIsInstance(result.value, SearchResult)
        self.assertIsInstance(result.value.PrimaryQueryResult, QueryResult)

    def test_06_search_get_query(self):
        """Execute a search GET query."""
        result = self.client.search.query("guide.docx").execute_query()
        self.assertIsInstance(result.value, SearchResult)
        self.assertIsInstance(result.value.PrimaryQueryResult, QueryResult)

    def test_07_search_get_query_with_select(self):
        """Execute a search query with selected properties."""
        result = self.client.search.query("guide.docx", select_properties=["Path", "LastModifiedTime"]).execute_query()
        self.assertIsInstance(result.value, SearchResult)
        self.assertIsInstance(result.value.PrimaryQueryResult, QueryResult)

    def test_08_search_get_query_with_sort_list(self):
        """Execute a search POST query with sort list."""
        result = self.client.search.post_query(
            query_text="guide.docx",
            enable_sorting=True,
            sort_list=[Sort(Property="LastModifiedTime", Direction=1)],
        ).execute_query()
        self.assertIsInstance(result.value.PrimaryQueryResult, QueryResult)

    def test_09_search_suggest(self):
        """Execute a search suggestion query."""
        result = self.client.search.suggest("guide").execute_query()
        self.assertIsInstance(result.value, QuerySuggestionResults)

    # def test9_auto_completions(self):
    #    result = self.search.auto_completions("guide").execute_query()
    #    self.assertIsNotNone(result.value)

    def test_10_get_query_configuration(self):
        """Get the search query configuration."""
        result = self.client.search_setting.get_query_configuration().execute_query()
        self.assertIsNotNone(result.value)

    def test_11_get_promoted_result_query_rules(self):
        """Get promoted result query rules."""
        result = self.client.search_setting.get_promoted_result_query_rules().execute_query()
        self.assertIsNotNone(result.value)

    # def test7_get_crawled_urls(self):
    #    from office365.sharepoint.search.administration.document_crawl_log import DocumentCrawlLog
    #    doc_crawl_log = DocumentCrawlLog(self.client)
    #    result = doc_crawl_log.get_crawled_urls().execute_query()
    #    self.assertIsNotNone(result.value)

    # def test_10_auto_completions(self):
    #    result = self.client.search.auto_completions("guide", number_of_completions=10).execute_query()
    #    self.assertIsNotNone(result.value)

    # def test_11_create_document_crawl_log(self):
    #    admin_client = ClientContext(test_admin_site_url).with_credentials(
    #        test_admin_credentials
    #    )
    #    result = DocumentCrawlLog.create(admin_client).execute_query()
    #    self.assertIsNotNone(result.resource_path)

    # def test_12_get_crawled_urls(self):
    #    result = self.client.document_crawl_log.get_crawled_urls().execute_query()
    #    self.assertIsNotNone(result.value)

    def test_12_results_page_address(self):
        """Get the search results page address."""
        result = self.client.search.results_page_address().execute_query()
        self.assertIsNotNone(result.value)
