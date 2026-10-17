"""Tests for the workflow / InfoPath / BCS handoff detector."""

from __future__ import annotations

import unittest

from office365.migration.sharepoint.handoff import (
    EXTERNAL_LIST_TEMPLATE,
    FormFinding,
    SiteHandoff,
    WorkflowFinding,
    detect_handoff,
    handoff_notes,
    is_infopath_form_url,
    workflow_findings,
)
from office365.migration.sharepoint.pages import PAGE_LIBRARY_TEMPLATE


class _Entity:
    """A typed ``$expand`` item (a ``ClientObject`` carrying ``properties``)."""

    def __init__(self, name):
        self.properties = {"Name": name}


class _WorkflowAssociations:
    def __init__(self, associations):
        self._associations = list(associations)

    def get(self):
        return self

    def execute_query(self):
        return self

    def __iter__(self):
        return iter(self._associations)


class _Lists:
    """The projected list collection: same objects, narrowed by ``$select``."""

    def __init__(self, lists):
        self._lists = list(lists)
        self.select_calls = []
        self.expand_calls = []

    def select(self, names):
        self.select_calls.append(list(names))
        return self

    def expand(self, names):
        self.expand_calls.append(list(names))
        return self

    def get(self):
        return self

    def execute_query(self):
        return list(self._lists)

    def __iter__(self):
        return iter(self._lists)


class _List:
    def __init__(self, title, base_template=100, hidden=False, **properties):
        self.title = title
        self.base_template = base_template
        self.hidden = hidden
        self.properties = {"Title": title, "BaseTemplate": base_template, "Hidden": hidden, **properties}


class _PagesLibrary(_List):
    """A Site Pages library; ``detect_page_handoff`` reads its ``items``."""

    def __init__(self, pages, title="Site Pages"):
        super().__init__(title, base_template=PAGE_LIBRARY_TEMPLATE, BaseType=1)
        self.items = _Items(pages)


class _Page:
    def __init__(self, name):
        self.properties = {"FileLeafRef": name}


class _Items:
    def __init__(self, items):
        self._items = list(items)

    def get(self):
        return self

    def select(self, names):
        return self

    def execute_query(self):
        return list(self._items)


class _Web:
    def __init__(self, lists, workflows=None):
        self.lists = lists
        self.workflow_associations = _WorkflowAssociations(workflows or [])


class HandoffUrlTests(unittest.TestCase):
    def test_browser_enabled_infopath_form_is_recognized(self):
        url = "/sites/x/_layouts/15/FormServer.aspx?XsnLocation=/sites/x/Forms/Requests.xsn"
        self.assertTrue(is_infopath_form_url(url))
        self.assertTrue(is_infopath_form_url("/sites/x/Forms/Requests.xsn"))
        self.assertTrue(is_infopath_form_url("/_layouts/FormServer.aspx?XmlLocation=/sites/x/a.xml"))

    def test_standard_platform_forms_are_not_infopath(self):
        self.assertFalse(is_infopath_form_url("/sites/x/Shared Documents/Forms/Upload.aspx"))
        self.assertFalse(is_infopath_form_url("/sites/x/Lists/Requests/NewForm.aspx"))
        self.assertFalse(is_infopath_form_url("/sites/x/_layouts/15/aclinv.aspx"))
        self.assertFalse(is_infopath_form_url("/sites/x/_catalogs/design/Upload.aspx"))
        self.assertFalse(is_infopath_form_url(None))


class WorkflowFindingTests(unittest.TestCase):
    def test_reads_typed_expand_items(self):
        findings = workflow_findings("Tasks", [_Entity("Approval"), _Entity("Escalation")])
        self.assertEqual(
            findings, [WorkflowFinding(name="Approval", scope="Tasks"), WorkflowFinding("Escalation", "Tasks")]
        )

    def test_reads_raw_json_shapes(self):
        self.assertEqual(workflow_findings("site", {"results": [{"Name": "Site"}]}), [WorkflowFinding("Site", "site")])
        self.assertEqual(workflow_findings("site", [{"Name": "Site"}]), [WorkflowFinding("Site", "site")])

    def test_empty_or_unnamed_associations_yield_nothing(self):
        for value in (None, {}, [], {"results": []}, [{"Name": None}], [{"NoName": "x"}]):
            self.assertEqual(workflow_findings("site", value), [])

    def test_label_names_the_scope(self):
        self.assertEqual(WorkflowFinding("Approval", "Tasks").label, "Approval (Tasks)")
        self.assertEqual(WorkflowFinding("Site", "site").label, "Site (site)")


class DetectHandoffTests(unittest.TestCase):
    def test_collects_every_category_from_one_projected_read(self):
        requests = "Requests"
        lists = _Lists(
            [
                _List(
                    requests,
                    DefaultNewFormUrl="/_layouts/15/FormServer.aspx?XsnLocation=/sites/x/Requests.xsn",
                    WorkflowAssociations={"results": [{"Name": "Approval"}]},
                ),
                _List("Customers", base_template=EXTERNAL_LIST_TEMPLATE),
                _List("Documents", BaseTemplate=101),
                _PagesLibrary([_Page("Home.aspx")]),
            ]
        )
        web = _Web(lists, workflows=[_Entity("Site Approval")])

        handoff = detect_handoff(web, lists)

        self.assertEqual(
            handoff.workflows, [WorkflowFinding("Site Approval", "site"), WorkflowFinding("Approval", requests)]
        )
        self.assertEqual(
            handoff.forms, [FormFinding(list_title=requests, urls=[lists._lists[0].properties["DefaultNewFormUrl"]])]
        )
        self.assertEqual(handoff.external_lists, ["Customers"])
        self.assertEqual([library.title for library in handoff.pages.libraries], ["Site Pages"])
        self.assertEqual(handoff.failures, [])
        # one request for the per-list signals, and it asks for both halves
        self.assertEqual(len(lists.select_calls), 1)
        self.assertIn("DefaultNewFormUrl", lists.select_calls[0])
        self.assertEqual(lists.expand_calls, [["WorkflowAssociations"]])

    def test_hidden_lists_are_not_reported(self):
        lists = _Lists(
            [
                _List(
                    "TaxonomyHiddenList",
                    hidden=True,
                    DefaultNewFormUrl="/_layouts/15/FormServer.aspx?XsnLocation=/sites/x/a.xsn",
                    WorkflowAssociations={"results": [{"Name": "Approval"}]},
                    BaseTemplate=EXTERNAL_LIST_TEMPLATE,
                )
            ]
        )
        handoff = detect_handoff(_Web(lists), lists)
        self.assertTrue(handoff.is_empty)

    def test_failed_detectors_degrade_to_failures(self):
        class _Bare:
            pass

        handoff = detect_handoff(_Bare(), "not a list collection")

        self.assertEqual(len(handoff.failures), 3)
        self.assertTrue(handoff.failures[0].startswith("page detection failed:"))
        self.assertTrue(handoff.failures[1].startswith("site workflow detection failed:"))
        self.assertTrue(handoff.failures[2].startswith("list workflow/form detection failed:"))
        self.assertEqual(handoff_notes(handoff), handoff.failures)


class HandoffNoteTests(unittest.TestCase):
    def test_empty_handoff_produces_no_notes(self):
        self.assertTrue(SiteHandoff().is_empty)
        self.assertEqual(handoff_notes(SiteHandoff()), [])

    def test_notes_name_the_artifact_and_ask_for_remediation(self):
        handoff = SiteHandoff(
            workflows=[WorkflowFinding("Approval", "Tasks")],
            forms=[FormFinding("Requests", ["/sites/x/Requests.xsn"])],
            external_lists=["Customers"],
        )
        notes = handoff_notes(handoff)
        self.assertEqual(
            notes,
            [
                "1 workflow(s) are not migrated — remediate out of band: Approval (Tasks)",
                "1 list(s) use an InfoPath form, which is not migrated — remediate out of band: Requests (1 form(s))",
                "1 business-data (BCS) external list(s) are not migrated — remediate out of band: Customers",
            ],
        )

    def test_long_lists_are_truncated(self):
        handoff = SiteHandoff(workflows=[WorkflowFinding(f"W{i}", "site") for i in range(7)])
        note = handoff_notes(handoff)[0]
        self.assertIn("7 workflow(s)", note)
        self.assertIn("W0 (site), W1 (site), W2 (site), W3 (site), W4 (site), +2 more", note)


if __name__ == "__main__":
    unittest.main()
