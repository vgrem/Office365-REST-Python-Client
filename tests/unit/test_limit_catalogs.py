import subprocess
import sys
import unittest

from office365.communications import quotas as communications_quotas
from office365.directory import quotas as directory_quotas
from office365.onedrive import quotas as files_quotas
from office365.onedrive.workbooks import quotas as excel_quotas
from office365.outlook import quotas as outlook_quotas
from office365.reports import quotas as reports_quotas
from office365.runtime import limits as limits_module
from office365.runtime.limits import Limit, LimitKind, catalog, register_catalog
from office365.security import quotas as security_quotas
from office365.sharepoint import thresholds as sharepoint_limits
from office365.teams import quotas as teams_quotas

VALID_REQUEST_TYPES = {"", "read", "write", "delete", "any"}

#: (product name, its catalog module, one row from it) — the row is how the test
#: proves the module registered, without re-spelling the table in the test.
CATALOGS = (
    ("graph", limits_module, limits_module.GLOBAL_QUOTAS[0]),
    ("directory", directory_quotas, directory_quotas.IDENTITY_QUOTAS[0]),
    ("cloud-communications", communications_quotas, communications_quotas.CALL_QUOTAS[0]),
    ("sharepoint", sharepoint_limits, sharepoint_limits.Limits.LIST_VIEW),
    ("outlook", outlook_quotas, outlook_quotas.OUTLOOK_QUOTAS[0]),
    ("files", files_quotas, files_quotas.FILES_QUOTAS[0]),
    ("excel", excel_quotas, excel_quotas.EXCEL_QUOTAS[0]),
    ("reports", reports_quotas, reports_quotas.REPORT_QUOTAS[0]),
    ("security", security_quotas, security_quotas.SECURITY_QUOTAS[0]),
    ("teams", teams_quotas, teams_quotas.TEAMS_QUOTAS[0]),
)


def _rows(module) -> list[Limit]:
    """Every ``Limit`` tuple a catalog module exports, flattened."""
    found = []
    for value in vars(module).values():
        if isinstance(value, tuple) and value and all(isinstance(row, Limit) for row in value):
            found.extend(value)
        elif isinstance(value, type) and isinstance(value.__dict__.get("catalog"), classmethod):
            found.extend(value.catalog())
    return found


class TestCatalogRegistration(unittest.TestCase):
    """A catalog is data: it registers itself, and the registry can read it back."""

    def test_every_catalog_registers_itself(self):
        for product, _module, sample in CATALOGS:
            with self.subTest(product=product):
                self.assertIn(sample, catalog(product=product))

    def test_the_registry_returns_the_module_rows_and_nothing_else(self):
        # Identity, not equality: registration must not copy or re-spell a row.
        for product, module, _sample in CATALOGS:
            with self.subTest(product=product):
                self.assertEqual({id(row) for row in _rows(module)}, {id(row) for row in catalog(product=product)})

    def test_an_unknown_product_has_no_rows(self):
        self.assertEqual(catalog(product="no-such-product"), [])

    def test_a_row_belongs_to_one_product(self):
        owners: dict[int, list[str]] = {}
        for product, _module, _sample in CATALOGS:
            for row in catalog(product=product):
                owners.setdefault(id(row), []).append(product)
        self.assertEqual([products for products in owners.values() if len(products) > 1], [])

    def test_registering_the_same_catalog_twice_adds_nothing(self):
        before = len(catalog(product="excel"))
        register_catalog(excel_quotas.EXCEL_QUOTAS, product="excel")
        self.assertEqual(len(catalog(product="excel")), before)

    def test_a_source_that_is_not_a_catalog_is_rejected(self):
        product = "not-a-catalog"
        try:
            register_catalog(object(), product=product)
            with self.assertRaises(TypeError):
                catalog(product=product)
        finally:
            limits_module._SOURCES.pop(product, None)


class TestCatalogDiscovery(unittest.TestCase):
    """One import must expose every catalog — discovery cannot depend on import order."""

    def test_importing_the_public_module_alone_exposes_every_catalog(self):
        products = [product for product, _module, _sample in CATALOGS]
        code = f"from office365.limits import catalog\nprint([p for p in {products!r} if not catalog(product=p)])\n"
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout.strip(), "[]")


class TestCatalogCompleteness(unittest.TestCase):
    """A row lives in a catalog; a model references it. Importing models must not add rows."""

    def test_importing_the_models_adds_no_row_of_their_own(self):
        import office365.communications.callrecords.call_record  # noqa: F401
        import office365.graph_client  # noqa: F401
        import office365.onedrive.workbooks.workbook  # noqa: F401
        import office365.sharepoint.client_context  # noqa: F401

        in_catalogs = {id(row) for module in (module for _product, module, _sample in CATALOGS) for row in _rows(module)}
        self.assertEqual([repr(row) for row in catalog() if id(row) not in in_catalogs], [])


class TestCatalogRows(unittest.TestCase):
    """What a published row must carry, checked across every product at once."""

    def test_every_row_cites_its_documentation(self):
        for row in catalog():
            with self.subTest(row=str(row)):
                self.assertTrue(row.doc.startswith("https://"), f"{row.name!r} has no doc URL: {row.doc!r}")

    def test_every_row_is_well_formed(self):
        for row in catalog():
            with self.subTest(row=str(row)):
                self.assertIsInstance(row.kind, LimitKind)
                self.assertGreater(row.value, 0)
                self.assertTrue(row.name)
                self.assertTrue(row.unit)
                self.assertTrue(row.doc)
                self.assertIn(row.request_type, VALID_REQUEST_TYPES)
                if row.window_seconds is not None:
                    self.assertGreaterEqual(row.window_seconds, 0)

    def test_no_row_is_spelled_twice_in_one_catalog(self):
        # A row is identified by everything a caller reads off it; a second spelling of
        # the same fact would be two answers to one question.
        for product, _module, _sample in CATALOGS:
            rows = catalog(product=product)
            keys = [(r.name, r.unit, r.scope, r.request_type, r.window_seconds, r.note) for r in rows]
            with self.subTest(product=product):
                self.assertEqual([key for key in keys if keys.count(key) > 1], [])

    def test_a_concurrency_row_is_a_zero_second_window(self):
        # "Four at a time" is not "four per period"; the window is what says so.
        concurrency = [row for row in catalog() if row.window_seconds == 0]
        self.assertTrue(concurrency)
        self.assertTrue(all(row.is_rate for row in concurrency))


class TestOutlookQuotas(unittest.TestCase):
    """The per-mailbox numbers, which are the ones an Outlook caller must design around."""

    def setUp(self):
        self.facts = {(row.value, row.unit, row.scope, row.window_seconds) for row in catalog(product="outlook")}

    def test_ten_thousand_requests_per_ten_minutes_per_mailbox(self):
        self.assertIn((10_000, "requests", "app+mailbox", 600), self.facts)

    def test_four_requests_in_flight_per_mailbox(self):
        self.assertIn((4, "requests", "app+mailbox", 0), self.facts)

    def test_a_hundred_and_fifty_megabytes_of_upload_per_five_minutes(self):
        self.assertIn((150 * 1024 * 1024, "bytes", "app+mailbox", 300), self.facts)

    def test_json_batching_sends_four_sub_requests_at_a_time(self):
        self.assertIn((4, "requests", "batch", 0), self.facts)


class TestTeamsQuotas(unittest.TestCase):
    """Teams throttles four dimensions of the same request; the catalog must name all four."""

    def setUp(self):
        self.rows = catalog(product="teams")

    def test_the_default_read_row_covers_all_four_dimensions(self):
        defaults = [row for row in self.rows if row.request_type == "read" and "default" in row.note]
        self.assertEqual(
            [(row.scope, row.value) for row in defaults],
            [("app", 1_500), ("app+tenant", 30), ("team, channel or chat", 1), ("user", 1)],
        )

    def test_a_named_resource_overrides_the_default(self):
        channel = next(
            row for row in self.rows if row.note == "GET /teams/{id}/channels" and row.scope == "team, channel or chat"
        )
        self.assertEqual((channel.value, channel.window_seconds), (4, 1))


class TestGlobalQuota(unittest.TestCase):
    """The one row no product owns."""

    def test_every_graph_request_spends_the_app_wide_budget(self):
        (row,) = catalog(product="graph")
        self.assertEqual((row.value, row.unit, row.scope, row.window_seconds), (130_000, "requests", "app", 10))
