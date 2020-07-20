from unittest import TestCase

from office365.sharepoint.search.search_request_builder import SearchRequestBuilder


class SearchBuilderTestCase(TestCase):

    def test_empty(self):
        filters, expected = dict(), '*'
        qry = SearchRequestBuilder(filters).get_query()
        assert qry == expected

    def test_simple(self):
        filters, expected = {'name': 'toro'}, "Name:toro"
        qry = SearchRequestBuilder(filters).get_query()
        assert qry == expected

    def test_not(self):
        filters, expected = {'name__not': 'toro'}, "Name<>toro"
        qry = SearchRequestBuilder(filters).get_query()
        assert qry == expected

    def test_contains(self):
        filters, expected = {'name__contains': 'toro'}, "Name:toro*"
        qry = SearchRequestBuilder(filters).get_query()
        assert qry == expected

    def test_or(self):
        filters, expected = {'name': 'toro,loco'}, "Name:(toro OR loco)"
        qry = SearchRequestBuilder(filters).get_query()
        assert qry == expected

    def test_gt(self):
        filters, expected = {'date__gt': '2019-10-10'}, "Date>2019-10-10"
        qry = SearchRequestBuilder(filters).get_query()
        assert qry == expected

    def test_gte(self):
        filters, expected = {'date__gte': '2019-10-10'}, "Date>=2019-10-10"
        qry = SearchRequestBuilder(filters).get_query()
        assert qry == expected

    def test_lt(self):
        filters, expected = {'date__lt': '2019-10-10'}, "Date<2019-10-10"
        qry = SearchRequestBuilder(filters).get_query()
        assert qry == expected

    def test_lte(self):
        filters, expected = {'date__lte': '2019-10-10'}, "Date<=2019-10-10"
        qry = SearchRequestBuilder(filters).get_query()
        assert qry == expected

    def test_between(self):
        filters, expected = {'date__between': '2019-10-10__2020-10-10'}, "Date:2019-10-10..2020-10-10"
        qry = SearchRequestBuilder(filters).get_query()
        assert qry == expected

    def test_complex(self):
        filters = {'file_type': 'pdf', 'title__contains': 'Humanitarian', 'last_modified_time__gte': '2019-10-10'}
        expected = "FileType:pdf AND Title:Humanitarian* AND LastModifiedTime>=2019-10-10"
        qry = SearchRequestBuilder(filters).get_query()
        assert qry == expected
