from unittest import TestCase

from office365.sharepoint.listitems.caml.camlquery_builder import CamlQueryBuilder


class CamlQueryBuilderTestCase(TestCase):

    def test_empty(self):
        filters, expected = dict(), ''
        qry = CamlQueryBuilder(filters).create_query()
        assert qry == '<View><Query><Where>' + expected + '</Where></Query></View>'

    def test_simple(self):
        filters = {'donor': 'Australia'}
        expected = '<Eq><FieldRef Name="Donor" /><Value Type="Text">Australia</Value></Eq>'
        qry = CamlQueryBuilder(filters).create_query()
        assert qry == '<View><Query><Where>' + expected + '</Where></Query></View>'

    def test_not(self):
        filters = {'donor__not': 'Australia'}
        expected = '<Neq><FieldRef Name="Donor" /><Value Type="Text">Australia</Value></Neq>'
        qry = CamlQueryBuilder(filters).create_query()
        assert qry == '<View><Query><Where>' + expected + '</Where></Query></View>'

    def test_contains(self):
        filters = {'recipient_office__contains': 'Afghanistan'}
        expected = '<Contains><FieldRef Name="RecipientOffice" /><Value Type="Text">Afghanistan</Value></Contains>'
        qry = CamlQueryBuilder(filters).create_query()
        assert qry == '<View><Query><Where>' + expected + '</Where></Query></View>'

    def test_or(self):
        filters = {'report_group': 'Grant,US Gov'}
        expected = '<Or>' \
                   '<Eq><FieldRef Name="ReportGroup" /><Value Type="Text">US Gov</Value></Eq>' \
                   '<Eq><FieldRef Name="ReportGroup" /><Value Type="Text">Grant</Value></Eq>' \
                   '</Or>'
        qry = CamlQueryBuilder(filters).create_query()
        assert qry == '<View><Query><Where>' + expected + '</Where></Query></View>'

    def test_gt(self):
        filters = {'report_end_date__gt': '2019-10-10'}
        expected = '<Gt><FieldRef Name="ReportEndDate" /><Value Type="DateTime">2019-10-10T00:00:00Z</Value></Gt>'
        qry = CamlQueryBuilder(filters).create_query()
        assert qry == '<View><Query><Where>' + expected + '</Where></Query></View>'

    def test_gte(self):
        filters = {'report_end_date__gte': '2019-10-10'}
        expected = '<Geq><FieldRef Name="ReportEndDate" /><Value Type="DateTime">2019-10-10T00:00:00Z</Value></Geq>'
        qry = CamlQueryBuilder(filters).create_query()
        assert qry == '<View><Query><Where>' + expected + '</Where></Query></View>'

    def test_lt(self):
        filters = {'report_end_date__lt': '2019-10-10'}
        expected = '<Lt><FieldRef Name="ReportEndDate" /><Value Type="DateTime">2019-10-10T00:00:00Z</Value></Lt>'
        qry = CamlQueryBuilder(filters).create_query()
        assert qry == '<View><Query><Where>' + expected + '</Where></Query></View>'

    def test_lte(self):
        filters = {'report_end_date__lte': '2019-10-10'}
        expected = '<Leq><FieldRef Name="ReportEndDate" /><Value Type="DateTime">2019-10-10T00:00:00Z</Value></Leq>'
        qry = CamlQueryBuilder(filters).create_query()
        assert qry == '<View><Query><Where>' + expected + '</Where></Query></View>'

    def test_complex(self):
        filters = {'donor': 'Australia', 'recipient_office__contains': 'Afghanistan'}
        expected = '<And>' \
                   '<Contains><FieldRef Name="RecipientOffice" /><Value Type="Text">Afghanistan</Value></Contains>' \
                   '<Eq><FieldRef Name="Donor" /><Value Type="Text">Australia</Value></Eq>' \
                   '</And>'
        qry = CamlQueryBuilder(filters).create_query()
        assert qry == '<View><Query><Where>' + expected + '</Where></Query></View>'

    def test_more_complex(self):
        filters = {
            'donor': 'Australia',
            'recipient_office__contains': 'Afghanistan',
            'donor_report_category': 'Financial'
        }
        expected = '<And>' \
                   '<Eq><FieldRef Name="DonorReportCategory" /><Value Type="Text">Financial</Value></Eq>' \
                   '<And>' \
                   '<Contains><FieldRef Name="RecipientOffice" /><Value Type="Text">Afghanistan</Value></Contains>' \
                   '<Eq>' \
                   '<FieldRef Name="Donor" /><Value Type="Text">Australia</Value></Eq>' \
                   '</And>' \
                   '</And>'
        qry = CamlQueryBuilder(filters).create_query()
        assert qry == '<View><Query><Where>' + expected + '</Where></Query></View>'
