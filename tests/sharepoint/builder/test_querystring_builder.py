from unittest import TestCase

from office365.sharepoint.listitems.caml.querystring_builder import QueryStringBuilder


class QueryStringBuilderTestCase(TestCase):

    def test_empty(self):
        filters, expected = dict(), ''
        qs = QueryStringBuilder(filters).get_querystring()
        assert qs == expected

    def test_simple(self):
        filters, expected = {'name': 'toro'}, "Name eq 'toro'"
        qs = QueryStringBuilder(filters).get_querystring()
        assert qs == expected

    def test_not(self):
        filters, expected = {'name__not': 'toro'}, "Name ne 'toro'"
        qs = QueryStringBuilder(filters).get_querystring()
        assert qs == expected

    def test_contains(self):
        filters, expected = {'name__contains': 'toro'}, "substringof('toro', Name)"
        qs = QueryStringBuilder(filters).get_querystring()
        assert qs == expected

    def test_or(self):
        filters, expected = {'name': 'toro,loco'}, "(Name eq 'toro' or Name eq 'loco')"
        qs = QueryStringBuilder(filters).get_querystring()
        assert qs == expected

    def test_gt(self):
        filters, expected = {'date__gt': '2019-10-10'}, "Date gt datetime'2019-10-10T00:00:00Z'"
        qs = QueryStringBuilder(filters).get_querystring()
        assert qs == expected

    def test_gte(self):
        filters, expected = {'date__gte': '2019-10-10'}, "Date ge datetime'2019-10-10T00:00:00Z'"
        qs = QueryStringBuilder(filters).get_querystring()
        assert qs == expected

    def test_lt(self):
        filters, expected = {'date__lt': '2019-10-10'}, "Date lt datetime'2019-10-10T00:00:00Z'"
        qs = QueryStringBuilder(filters).get_querystring()
        assert qs == expected

    def test_lte(self):
        filters, expected = {'date__lte': '2019-10-10'}, "Date le datetime'2019-10-10T00:00:00Z'"
        qs = QueryStringBuilder(filters).get_querystring()
        assert qs == expected
