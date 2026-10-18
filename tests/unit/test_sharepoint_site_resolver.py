"""Tests for the SharePoint whole-site (migrate_all) resolver and session wiring."""

import hashlib
import re
import unittest
from types import SimpleNamespace
from unittest import mock

from office365.migration.session import MigrationSession
from office365.migration.settings import MigrationSettings
from office365.migration.sharepoint.adapters import (
    SharePointLibrarySource,
    SharePointLibraryTarget,
    SharePointListSource,
    SharePointListTarget,
)
from office365.migration.sharepoint.pages import PageCopyReport
from office365.migration.sharepoint.resolvers import (
    is_document_library,
    is_migratable_list,
    resolve_site_task,
    resolve_task,
)
from office365.migration.sharepoint.structure import normalize_guid
from office365.migration.tasks import MigrationTask

_DOCUMENT_LIBRARY_TEMPLATE = 101
_WIKI_PAGE_CONTENT_TYPE = "0x010108"
# A publishing page carries neither a canvas nor a wiki body.
_PUBLISHING_CONTENT_TYPE = "0x010100C568DB52D9D0A14D9B2FDCC96666E9F2007948130EC3DB064584E219954237AF39"
_SITE_PAGE_CONTENT_TYPE = "0x0101009D1CB255DA76424F860D91F20E6C4118005E10E40F8E37D94AB983A0181120EFFC"


class _Folder:
    server_relative_url = "/sites/x/Documents"

    def get(self):
        return self

    def execute_query(self):
        return self


class _FakeList:
    def __init__(self, title, base_type=0, base_template=100, hidden=False, allow_deletion=True, list_id=None):
        self.title = title
        self.base_type = base_type
        self.base_template = base_template
        self.hidden = hidden
        self.allow_deletion = allow_deletion
        self.root_folder = _Folder()
        self.properties = {
            "Id": list_id if list_id is not None else _guid_for(title),
            "Title": title,
            "BaseTemplate": base_template,
            "Hidden": hidden,
        }

    @property
    def id(self):
        return self.properties["Id"]

    def get(self):
        return self

    def execute_query(self):
        return self


def _guid_for(title):
    digest = hashlib.md5(title.encode()).hexdigest()
    return f"{{{digest[0:8]}-{digest[8:12]}-{digest[12:16]}-{digest[16:20]}-{digest[20:32]}}}"


class _Lists:
    def __init__(self, source_lists):
        self._source_lists = list(source_lists)
        self.ensure_calls = []

    def get(self):
        return self

    def select(self, names):
        return self

    def expand(self, names):
        return self

    def execute_query(self):
        return self._source_lists

    def __iter__(self):
        return iter(self._source_lists)

    def ensure_list(self, title, template_type=None):
        self.ensure_calls.append((title, template_type))
        base_type = 1 if int(template_type) == _DOCUMENT_LIBRARY_TEMPLATE else 0
        return _FakeList(
            title, base_type=base_type, base_template=int(template_type), list_id=_guid_for("target:" + title)
        )


class _PageItem:
    def __init__(self, name, canvas="", wiki="", content_type_id=_SITE_PAGE_CONTENT_TYPE):
        self.properties = {
            "FileLeafRef": name,
            "CanvasContent1": canvas,
            "WikiField": wiki,
            "ContentTypeId": content_type_id,
        }


class _PageItems:
    def __init__(self, items):
        self._items = list(items)

    def get(self):
        return self

    def select(self, fields):
        return self

    def execute_query(self):
        return list(self._items)


class _PageList:
    """A Site Pages library (template 119) whose items the handoff detector inspects."""

    def __init__(self, pages, title="Site Pages", template=119):
        self.title = title
        self.base_type = 1
        self.base_template = template
        self.hidden = False
        self.allow_deletion = True
        self.items = _PageItems(pages)
        self.properties = {"Id": _guid_for(title)}

    @property
    def id(self):
        return self.properties["Id"]


class _WorkflowAssociations:
    """Site-level workflow associations (empty unless a test seeds them)."""

    def __init__(self, associations=None):
        self._associations = list(associations or [])

    def get(self):
        return self

    def execute_query(self):
        return list(self._associations)


class _Field:
    """A web field as the web-scope comparison and provisioning see it."""

    def __init__(
        self,
        internal_name,
        hidden=False,
        from_base_type=False,
        can_be_deleted=True,
        sealed=False,
        schema_xml=None,
    ):
        self.internal_name = internal_name
        self.hidden = hidden
        self.from_base_type = from_base_type
        self.can_be_deleted = can_be_deleted
        self.sealed = sealed
        self.schema_xml = schema_xml
        self.title = internal_name
        self.field_type_kind = 2
        self.type_as_string = "Text"
        self.required = False
        self.read_only_field = False
        self.group = None
        self.description = None
        self.properties = {}

    def schema_xml_for_copy(self):
        return self.schema_xml


class _ContentType:
    """A web content type as the web-scope comparison sees it."""

    def __init__(self, name, hidden=False):
        self.name = name
        self.hidden = hidden


class _SingleFieldView:
    """``web.fields.get_by_internal_name_or_title(name)`` — a get that 404s when absent."""

    def __init__(self, entry):
        self._entry = entry

    def get(self):
        return self

    def execute_query(self):
        if self._entry is None:
            raise RuntimeError("Field not found")
        return self._entry


def _schema_name(schema_xml):
    match = re.search(r'Name="([^"]+)"', schema_xml)
    return match.group(1) if match else "Field"


class _WebCollectionView:
    """A projected ``web.fields`` / ``web.content_types`` collection."""

    def __init__(self, entries):
        self._entries = list(entries)

    def select(self, fields):
        return self

    def get(self):
        return self

    def execute_query(self):
        return list(self._entries)

    def get_by_internal_name_or_title(self, name):
        found = next((entry for entry in self._entries if getattr(entry, "internal_name", None) == name), None)
        return _SingleFieldView(found)

    def create_field_as_xml(self, schema_xml):
        self._entries.append(_Field(_schema_name(schema_xml), schema_xml=schema_xml))
        return self


class _Web:
    def __init__(
        self,
        lists,
        webs=None,
        title=None,
        web_template="STS#3",
        url=None,
        workflows=None,
        fields=None,
        content_types=None,
    ):
        self.lists = lists
        self.webs = webs if webs is not None else _WebCollection()
        self.title = title
        self.web_template = web_template
        self.workflow_associations = _WorkflowAssociations(workflows)
        self.fields = _WebCollectionView(fields or [])
        self.content_types = _WebCollectionView(content_types or [])
        self._props = {"Url": url} if url else {}
        self._props.update({"Title": title, "Description": None})
        self.written = {}

    def get_property(self, name):
        return self._props.get(name)

    @property
    def properties(self):
        return self._props

    def select(self, names):
        self._selected = names
        return self

    def set_property(self, name, value):
        self.written[name] = value
        self._props[name] = value
        return self

    def update(self):
        return self

    @property
    def url(self):
        return self._props.get("Url")

    @property
    def server_relative_url(self):
        return self._props.get("ServerRelativeUrl")

    def get(self):
        return self

    def execute_query(self):
        return self

    def get_list_by_title(self, title):
        for entry in self.lists._source_lists:
            if entry.title == title:
                return entry
        raise KeyError(title)


class _WebCollection:
    """A fake child-site collection that records ``add`` calls."""

    def __init__(self, children=None):
        self._children = list(children or [])
        self.add_calls = []

    def get(self):
        return self

    def execute_query(self):
        return list(self._children)

    def add(self, info):
        self.add_calls.append(info)
        created = _Web(_Lists([]), title=info.Title, web_template=info.WebTemplate, url=info.Url)
        self._children.append(created)
        return created


def _find_web(web, key):
    """Depth-first search for a web whose URL or URL leaf matches ``key``."""
    current = (web.get_property("Url") or "").rstrip("/").casefold()
    if current and (current == key or current.rsplit("/", 1)[-1] == key.rsplit("/", 1)[-1]):
        return web
    for child in web.webs._children:
        found = _find_web(child, key)
        if found is not None:
            return found
    return None


class _Context:
    def __init__(self, base_url, web, registry=None):
        self.base_url = base_url
        self.web = web if isinstance(web, _Web) else _Web(web)
        self._registry = registry if registry is not None else {base_url.rstrip("/").casefold(): self.web}
        self._registry.setdefault(base_url.rstrip("/").casefold(), self.web)
        self.clones = []

    def clone(self, url):
        self.clones.append(url)
        key = (url or "").rstrip("/").casefold()
        web = self._registry.get(key) or _find_web(self.web, key) or self.web
        return _Context(url, web, self._registry)


def _docs():
    return _FakeList("Documents", base_type=1, base_template=101)


def _tasks():
    return _FakeList("Tasks", base_type=0, base_template=107)


def _context(lists, base_url="https://contoso.sharepoint.com/sites/target"):
    return _Context(base_url, _Lists(lists))


class _StructureStub:
    """Stubs capture/provision so resolver tests need no real list structure."""

    def setUp(self):
        super().setUp()
        capture = mock.patch("office365.migration.sharepoint.resolvers.capture_list_structure", return_value=None)
        provision = mock.patch("office365.migration.sharepoint.resolvers.provision_list_structure", return_value=[])
        self.capture = capture.start()
        self.provision = provision.start()
        self.addCleanup(capture.stop)
        self.addCleanup(provision.stop)


class TestListSelection(unittest.TestCase):
    def test_document_library(self):
        self.assertTrue(is_document_library(_docs()))
        self.assertFalse(is_document_library(_tasks()))

    def test_skips_hidden_system_and_undeletable(self):
        self.assertTrue(is_migratable_list(_docs()))
        self.assertTrue(is_migratable_list(_tasks()))
        self.assertFalse(is_migratable_list(_FakeList("Hidden", hidden=True)))
        self.assertFalse(is_migratable_list(_FakeList("User Information", base_template=112)))
        self.assertFalse(is_migratable_list(_FakeList("Site Pages", base_template=119)))
        self.assertFalse(is_migratable_list(_FakeList("System", allow_deletion=False)))

    def test_skips_business_data_external_list(self):
        # A BCS external list is a view over a BDC model: a copy cannot provision it.
        self.assertFalse(is_migratable_list(_FakeList("Customers", base_template=600)))


class TestResolveSiteTask(_StructureStub, unittest.TestCase):
    def test_pairs_library_and_list_and_skips_infrastructure(self):
        source = _context([_docs(), _tasks(), _FakeList("User Information", base_template=112)])
        task = MigrationTask.sharepoint("https://contoso.sharepoint.com/sites/source", source.base_url, migrate_all=True)

        pairs = resolve_site_task(task, source)

        self.assertEqual(len(pairs), 2)
        self.assertIsInstance(pairs[0][0], SharePointLibrarySource)
        self.assertIsInstance(pairs[0][1], SharePointLibraryTarget)
        self.assertIsInstance(pairs[1][0], SharePointListSource)
        self.assertIsInstance(pairs[1][1], SharePointListTarget)
        self.assertEqual([call[0] for call in source.web.lists.ensure_calls], ["Documents", "Tasks"])
        # the source site differs from the registered (target) context → cloned once
        self.assertEqual(source.clones, ["https://contoso.sharepoint.com/sites/source"])

    def test_same_site_does_not_clone(self):
        source = _context([_docs()])
        task = MigrationTask.sharepoint(source.base_url, source.base_url, migrate_all=True)

        resolve_site_task(task, source)

        self.assertEqual(source.clones, [])

    def test_include_and_exclude_filter_by_title(self):
        source = _context([_docs(), _tasks()])
        task = MigrationTask.sharepoint("https://contoso.sharepoint.com/sites/source", source.base_url, migrate_all=True)

        only_tasks = resolve_site_task(task, source, include=["Tasks"])
        self.assertEqual(len(only_tasks), 1)
        self.assertIsInstance(only_tasks[0][0], SharePointListSource)

        source.web.lists.ensure_calls.clear()
        without_docs = resolve_site_task(task, source, exclude=["Documents"])
        self.assertEqual([call[0] for call in source.web.lists.ensure_calls], ["Tasks"])
        self.assertEqual(len(without_docs), 1)

    def test_reuses_existing_target_list_template(self):
        source = _context([_docs()])
        task = MigrationTask.sharepoint("https://contoso.sharepoint.com/sites/source", source.base_url, migrate_all=True)

        resolve_site_task(task, source)

        _, template = source.web.lists.ensure_calls[0]
        self.assertEqual(int(template), 101)

    def test_lookup_list_ids_are_threaded_into_provisioning(self):
        source = _context([_FakeList("Depts"), _FakeList("TypedSrc")])
        task = MigrationTask.sharepoint(source.base_url, source.base_url, migrate_all=True)

        resolve_site_task(task, source)

        # Every container is created first, then structure is replayed with the
        # source->target list-id map so lookup columns can be repointed.
        expected = {
            normalize_guid(_guid_for("Depts")): normalize_guid(_guid_for("target:Depts")),
            normalize_guid(_guid_for("TypedSrc")): normalize_guid(_guid_for("target:TypedSrc")),
        }
        provided = [call.kwargs["list_id_map"] for call in self.provision.call_args_list]
        self.assertEqual(len(provided), 2)
        self.assertEqual(provided[0], expected)
        self.assertEqual(provided[1], expected)

    def test_provisions_structure_by_default(self):
        source = _context([_docs()])
        task = MigrationTask.sharepoint("https://contoso.sharepoint.com/sites/source", source.base_url, migrate_all=True)

        resolve_site_task(task, source)

        self.assertEqual(self.capture.call_args[0][0].title, "Documents")
        target_arg, structure_arg = self.provision.call_args[0]
        self.assertEqual(target_arg.title, "Documents")
        self.assertIsNone(structure_arg)

    def test_structure_warnings_reach_the_target_adapter(self):
        self.provision.return_value = ["content type 'Project': column 'X' was not linked"]
        source = _context([_docs()])
        task = MigrationTask.sharepoint("https://contoso.sharepoint.com/sites/source", source.base_url, migrate_all=True)

        pairs = resolve_site_task(task, source)

        self.assertEqual(pairs[0][1].warnings, ["content type 'Project': column 'X' was not linked"])

    def test_page_library_is_reported_when_pages_are_not_copied(self):
        pages = _PageList(
            [
                _PageItem("Home.aspx"),
                _PageItem("CollabHome.aspx", canvas='data-sp-controldata="{&quot;controlType&quot;:4}"'),
            ]
        )
        source = _context([_docs(), pages])
        task = MigrationTask.sharepoint(source.base_url, source.base_url, migrate_all=True)

        warnings: list[str] = []
        pairs = resolve_site_task(task, source, migrate_pages=False, warnings=warnings)

        self.assertEqual(len(pairs), 1)  # the page library is not a content pair
        note = next(message for message in warnings if "pages are not migrated" in message)
        self.assertIn("Site Pages (2 page(s): Home.aspx, CollabHome.aspx)", note)
        self.assertIn("1 web part(s)", note)

    def test_modern_and_classic_wiki_pages_are_copied(self):
        pages = _PageList(
            [
                _PageItem("Home.aspx"),
                _PageItem("Guide.aspx", wiki="<p>classic</p>", content_type_id=_WIKI_PAGE_CONTENT_TYPE),
            ]
        )
        source = _context([_docs(), pages])
        task = MigrationTask.sharepoint(source.base_url, source.base_url, migrate_all=True)
        report = PageCopyReport(
            copied=["Home.aspx", "Guide.aspx"], published=["Home.aspx", "Guide.aspx"], wiki=["Guide.aspx"]
        )
        warnings: list[str] = []

        with mock.patch("office365.migration.sharepoint.resolvers.copy_site_pages", return_value=report) as copy:
            resolve_site_task(task, source, warnings=warnings)

        self.assertEqual(copy.call_args[0][:2], (source.web, source.web))
        self.assertIn("page copy: 2 page(s) copied (1 classic wiki), 2 published", warnings)
        self.assertFalse(any("are not migrated" in message for message in warnings))

    def test_a_page_with_no_copyable_body_is_still_reported(self):
        pages = _PageList(
            [
                _PageItem("Home.aspx"),
                _PageItem("Publishing.aspx", content_type_id=_PUBLISHING_CONTENT_TYPE),
            ]
        )
        source = _context([_docs(), pages])
        task = MigrationTask.sharepoint(source.base_url, source.base_url, migrate_all=True)
        report = PageCopyReport(copied=["Home.aspx"], published=["Home.aspx"])
        warnings: list[str] = []

        with mock.patch("office365.migration.sharepoint.resolvers.copy_site_pages", return_value=report):
            resolve_site_task(task, source, warnings=warnings)

        note = next(message for message in warnings if "page(s) are not migrated" in message)
        self.assertIn("Publishing.aspx", note)
        self.assertNotIn("Home.aspx", note)

    def test_a_failing_page_copy_degrades_to_a_warning(self):
        pages = _PageList([_PageItem("Home.aspx")])
        source = _context([_docs(), pages])
        task = MigrationTask.sharepoint(source.base_url, source.base_url, migrate_all=True)
        warnings: list[str] = []

        with mock.patch("office365.migration.sharepoint.resolvers.copy_site_pages", side_effect=RuntimeError("denied")):
            pairs = resolve_site_task(task, source, warnings=warnings)

        self.assertEqual(len(pairs), 1)
        self.assertTrue(any("page copy failed" in message for message in warnings))
        # The handoff note falls back to "not copied" wording.
        self.assertTrue(any("pages are not migrated" in message for message in warnings))

    def test_workflows_forms_and_external_lists_are_reported_as_handoff(self):
        forms = _FakeList("Requests")
        forms.properties.update(
            {
                "DefaultNewFormUrl": "/_layouts/15/FormServer.aspx?XsnLocation=/sites/x/Requests.xsn",
                "WorkflowAssociations": {"results": [{"Name": "Approval"}]},
            }
        )
        bcs = _FakeList("Customers", base_template=600)
        source = _context([forms, bcs])
        task = MigrationTask.sharepoint(source.base_url, source.base_url, migrate_all=True)

        warnings: list[str] = []
        resolve_site_task(task, source, warnings=warnings)

        # The external list is not a content pair, but it is named.
        self.assertEqual([call[0] for call in source.web.lists.ensure_calls], ["Requests"])
        self.assertIn("1 workflow(s) are not migrated — remediate out of band: Approval (Requests)", warnings)
        self.assertIn(
            "1 list(s) use an InfoPath form, which is not migrated — remediate out of band: Requests (1 form(s))",
            warnings,
        )
        self.assertIn(
            "1 business-data (BCS) external list(s) are not migrated — remediate out of band: Customers", warnings
        )

    def test_subwebs_are_detected_and_reported_when_skipped(self):
        child = _Web(
            _Lists([_docs()]),
            title="child",
            url="https://contoso.sharepoint.com/sites/source/child",
        )
        root = _Web(
            _Lists([_tasks()]),
            webs=_WebCollection([child]),
            title="Source",
            url="https://contoso.sharepoint.com/sites/source",
        )
        source = _Context("https://contoso.sharepoint.com/sites/source", root)
        task = MigrationTask.sharepoint(root.url, root.url, migrate_all=True)

        warnings: list[str] = []
        pairs = resolve_site_task(task, source, warnings=warnings)

        self.assertEqual(len(pairs), 1)  # root list only
        self.assertEqual(len(warnings), 1)
        self.assertIn("child", warnings[0])
        self.assertIn("include_subwebs=True", warnings[0])

    def test_include_subwebs_provisions_target_subsites_and_recurses(self):
        source_child = _Web(
            _Lists([_docs()]),
            title="child",
            web_template="GROUP",
            url="https://contoso.sharepoint.com/sites/source/child",
        )
        source_root = _Web(
            _Lists([_tasks()]),
            webs=_WebCollection([source_child]),
            title="Source",
            url="https://contoso.sharepoint.com/sites/source",
        )
        target_root = _Web(
            _Lists([]),
            webs=_WebCollection(),
            title="Target",
            url="https://contoso.sharepoint.com/sites/target",
        )
        registry = {
            source_root.url.rstrip("/").casefold(): source_root,
            target_root.url.rstrip("/").casefold(): target_root,
        }
        context = _Context(target_root.url, target_root, registry)
        task = MigrationTask.sharepoint(source_root.url, target_root.url, migrate_all=True)

        pairs = resolve_site_task(task, context, include_subwebs=True)

        # root Tasks + the subsite's Documents
        self.assertEqual(len(pairs), 2)
        self.assertEqual([pair[0].label() for pair in pairs], ["list:Tasks", "library:/sites/x/Documents"])
        created = target_root.webs._children[0]
        self.assertEqual(target_root.webs.add_calls[0].Url, "child")
        self.assertEqual(target_root.webs.add_calls[0].WebTemplate, "GROUP")
        self.assertEqual([call[0] for call in created.lists.ensure_calls], ["Documents"])

    def test_include_subwebs_reuses_an_existing_target_subsite(self):
        source_child = _Web(
            _Lists([_docs()]),
            title="child",
            url="https://contoso.sharepoint.com/sites/source/child",
        )
        source_root = _Web(
            _Lists([_tasks()]),
            webs=_WebCollection([source_child]),
            title="Source",
            url="https://contoso.sharepoint.com/sites/source",
        )
        target_child = _Web(
            _Lists([]),
            title="child",
            url="https://contoso.sharepoint.com/sites/target/child",
        )
        target_root = _Web(
            _Lists([]),
            webs=_WebCollection([target_child]),
            title="Target",
            url="https://contoso.sharepoint.com/sites/target",
        )
        registry = {
            source_root.url.rstrip("/").casefold(): source_root,
            target_root.url.rstrip("/").casefold(): target_root,
            target_child.url.rstrip("/").casefold(): target_child,
        }
        context = _Context(target_root.url, target_root, registry)
        task = MigrationTask.sharepoint(source_root.url, target_root.url, migrate_all=True)

        resolve_site_task(task, context, include_subwebs=True)

        # the existing target subsite is reused instead of created
        self.assertEqual(target_root.webs.add_calls, [])
        self.assertEqual([call[0] for call in target_child.lists.ensure_calls], ["Documents"])

    def test_include_subwebs_reports_web_scope_structure_the_target_lacks(self):
        source_child = _Web(
            _Lists([_docs()]),
            title="child",
            url="https://contoso.sharepoint.com/sites/source/child",
            fields=[_Field("RegionCol", schema_xml='<Field Type="Text" Name="RegionCol" StaticName="RegionCol" />')],
            content_types=[_ContentType("Contract")],
        )
        source_root = _Web(
            _Lists([_tasks()]),
            webs=_WebCollection([source_child]),
            title="Source",
            url="https://contoso.sharepoint.com/sites/source",
        )
        target_root = _Web(
            _Lists([]),
            webs=_WebCollection(),
            title="Target",
            url="https://contoso.sharepoint.com/sites/target",
        )
        registry = {
            source_root.url.rstrip("/").casefold(): source_root,
            target_root.url.rstrip("/").casefold(): target_root,
        }
        context = _Context(target_root.url, target_root, registry)
        task = MigrationTask.sharepoint(source_root.url, target_root.url, migrate_all=True)

        warnings: list[str] = []
        resolve_site_task(task, context, include_subwebs=True, warnings=warnings)

        # The created subsite's web-scope *column* is provisioned; a content type
        # cannot be (REST refuses its field links), so only that stays a finding.
        created = _find_web(target_root, "child")
        self.assertEqual([field.internal_name for field in created.fields.execute_query()], ["RegionCol"])
        note = next(message for message in warnings if "web-scope structure is incomplete" in message)
        self.assertIn("1 content type(s): Contract", note)
        self.assertNotIn("RegionCol", note)
        self.assertIn("list-scoped copy", note)

    def test_web_scope_structure_note_is_quiet_when_the_target_matches(self):
        source_child = _Web(
            _Lists([_docs()]),
            title="child",
            url="https://contoso.sharepoint.com/sites/source/child",
            fields=[_Field("RegionCol")],
            content_types=[_ContentType("Contract")],
        )
        source_root = _Web(
            _Lists([_tasks()]),
            webs=_WebCollection([source_child]),
            title="Source",
            url="https://contoso.sharepoint.com/sites/source",
        )
        target_child = _Web(
            _Lists([]),
            title="child",
            url="https://contoso.sharepoint.com/sites/target/child",
            fields=[_Field("RegionCol")],
            content_types=[_ContentType("Contract")],
        )
        target_root = _Web(
            _Lists([]),
            webs=_WebCollection([target_child]),
            title="Target",
            url="https://contoso.sharepoint.com/sites/target",
        )
        registry = {
            source_root.url.rstrip("/").casefold(): source_root,
            target_root.url.rstrip("/").casefold(): target_root,
            target_child.url.rstrip("/").casefold(): target_child,
        }
        context = _Context(target_root.url, target_root, registry)
        task = MigrationTask.sharepoint(source_root.url, target_root.url, migrate_all=True)

        warnings: list[str] = []
        resolve_site_task(task, context, include_subwebs=True, warnings=warnings)

        self.assertEqual([message for message in warnings if "web-scope structure" in message], [])

    def test_web_scope_columns_are_not_provisioned_when_structure_is_off(self):
        source = _Web(
            _Lists([_tasks()]),
            title="Source",
            url="https://contoso.sharepoint.com/sites/source",
            fields=[_Field("RegionCol", schema_xml='<Field Type="Text" Name="RegionCol" />')],
        )
        target = _Web(
            _Lists([]),
            title="Target",
            url="https://contoso.sharepoint.com/sites/target",
        )
        registry = {
            source.url.rstrip("/").casefold(): source,
            target.url.rstrip("/").casefold(): target,
        }
        context = _Context(target.url, target, registry)
        task = MigrationTask.sharepoint(source.url, target.url, migrate_all=True)

        warnings: list[str] = []
        resolve_site_task(task, context, provision_structure=False, warnings=warnings)

        self.assertEqual(target.fields.execute_query(), [])
        note = next(message for message in warnings if "web-scope structure is incomplete" in message)
        self.assertIn("1 column(s): RegionCol", note)

    def test_web_scope_columns_are_provisioned_before_the_list_replay(self):
        source = _Web(
            _Lists([_tasks()]),
            title="Source",
            url="https://contoso.sharepoint.com/sites/source",
            fields=[_Field("RegionCol", schema_xml='<Field Type="Text" Name="RegionCol" />')],
        )
        target = _Web(
            _Lists([]),
            title="Target",
            url="https://contoso.sharepoint.com/sites/target",
        )
        registry = {
            source.url.rstrip("/").casefold(): source,
            target.url.rstrip("/").casefold(): target,
        }
        context = _Context(target.url, target, registry)
        task = MigrationTask.sharepoint(source.url, target.url, migrate_all=True)
        # What the target web carried when each list's structure was replayed.
        seen: list[list[str]] = []

        def _record(*args, **kwargs):
            seen.append([field.internal_name for field in target.fields.execute_query()])
            return []

        self.provision.side_effect = _record

        resolve_site_task(task, context)

        self.assertEqual(seen, [["RegionCol"]])

    def test_provision_structure_can_be_disabled(self):
        source = _context([_docs()])
        task = MigrationTask.sharepoint("https://contoso.sharepoint.com/sites/source", source.base_url, migrate_all=True)

        resolve_site_task(task, source, provision_structure=False)

        self.capture.assert_not_called()
        self.provision.assert_not_called()

    def test_rejects_non_sharepoint_task(self):
        task = MigrationTask.file_share("src", "https://contoso.sharepoint.com/sites/target", "Documents")
        with self.assertRaises(ValueError):
            resolve_site_task(task, _context([]))

    def test_rejects_server_side_migration_api(self):
        source = _context([_docs()])
        task = MigrationTask.sharepoint("https://contoso.sharepoint.com/sites/source", source.base_url, migrate_all=True)
        with self.assertRaises(NotImplementedError):
            resolve_site_task(task, source, MigrationSettings(use_migration_api=True))


class TestResolveSingleListTask(_StructureStub, unittest.TestCase):
    def test_generic_list_uses_record_adapters(self):
        source = _context([_tasks()])
        task = MigrationTask.sharepoint(
            "https://contoso.sharepoint.com/sites/source",
            source.base_url,
            source_list="Tasks",
            target_list="Tasks",
        )

        src, dst = resolve_task(task, source)

        self.assertIsInstance(src, SharePointListSource)
        self.assertIsInstance(dst, SharePointListTarget)

    def test_library_uses_file_adapters(self):
        source = _context([_docs()])
        task = MigrationTask.sharepoint(
            "https://contoso.sharepoint.com/sites/source",
            source.base_url,
            source_list="Documents",
            target_list="Documents",
        )

        src, dst = resolve_task(task, source)

        self.assertIsInstance(src, SharePointLibrarySource)
        self.assertIsInstance(dst, SharePointLibraryTarget)

    def test_provisions_structure_by_default(self):
        source = _context([_tasks()])
        task = MigrationTask.sharepoint(
            "https://contoso.sharepoint.com/sites/source",
            source.base_url,
            source_list="Tasks",
            target_list="Tasks",
        )

        resolve_task(task, source)

        self.assertEqual(self.capture.call_args[0][0].title, "Tasks")
        target_arg, structure_arg = self.provision.call_args[0]
        self.assertEqual(target_arg.title, "Tasks")
        self.assertIsNone(structure_arg)

    def test_provision_structure_can_be_disabled(self):
        source = _context([_tasks()])
        task = MigrationTask.sharepoint(
            "https://contoso.sharepoint.com/sites/source",
            source.base_url,
            source_list="Tasks",
            target_list="Tasks",
        )

        resolve_task(task, source, provision_structure=False)

        self.capture.assert_not_called()
        self.provision.assert_not_called()

    def test_migration_api_still_provisions_structure(self):
        source = _context([_docs()])
        task = MigrationTask.sharepoint(
            "https://contoso.sharepoint.com/sites/source",
            source.base_url,
            source_list="Documents",
            target_list="Documents",
        )

        with mock.patch(
            "office365.migration.sharepoint.resolvers._package_target",
            return_value=SimpleNamespace(warnings=[]),
        ):
            resolve_task(task, source, MigrationSettings(use_migration_api=True))

        # The package builder emits no columns/content types/views, so structure is
        # still replayed over REST before the package target is used.
        self.assertEqual(self.capture.call_args[0][0].title, "Documents")
        self.assertEqual(self.provision.call_args[0][0].title, "Documents")

    def test_migrate_all_defers_to_site_resolver(self):
        task = MigrationTask.sharepoint(
            "https://contoso.sharepoint.com/sites/source",
            "https://contoso.sharepoint.com/sites/target",
            migrate_all=True,
        )
        with self.assertRaises(NotImplementedError):
            resolve_task(task, _context([]))


class TestSessionSiteTask(_StructureStub, unittest.TestCase):
    def test_add_task_rejects_migrate_all(self):
        session = MigrationSession()
        task = MigrationTask.sharepoint(
            "https://contoso.sharepoint.com/sites/source",
            "https://contoso.sharepoint.com/sites/target",
            migrate_all=True,
        )
        with self.assertRaises(ValueError):
            session.add_task(task=task)

    def test_add_site_task_creates_one_job_per_list(self):
        source = _context([_docs(), _tasks()])
        session = MigrationSession().register(context=source)
        task = MigrationTask.sharepoint("https://contoso.sharepoint.com/sites/source", source.base_url, migrate_all=True)

        jobs = session.add_site_task(task=task)

        self.assertEqual(len(jobs), 2)
        self.assertEqual(len(session.tasks), 2)
        self.assertEqual(len({entry.id for entry in session.tasks}), 2)
        self.assertIn("Documents", jobs[0].target_label)
        self.assertIn("Tasks", jobs[1].target_label)

    def test_add_site_task_can_skip_structure_provisioning(self):
        source = _context([_docs()])
        session = MigrationSession().register(context=source)
        task = MigrationTask.sharepoint("https://contoso.sharepoint.com/sites/source", source.base_url, migrate_all=True)

        session.add_site_task(task=task, provision_structure=False)

        self.capture.assert_not_called()

    def test_add_site_task_requires_context(self):
        session = MigrationSession()
        task = MigrationTask.sharepoint("https://contoso.sharepoint.com/sites/source", "https://x", migrate_all=True)
        with self.assertRaises(ValueError):
            session.add_site_task(task=task)

    def test_add_site_task_surfaces_skipped_subsites(self):
        child = _Web(
            _Lists([_docs()]),
            title="child",
            url="https://contoso.sharepoint.com/sites/source/child",
        )
        root = _Web(
            _Lists([_tasks()]),
            webs=_WebCollection([child]),
            title="Source",
            url="https://contoso.sharepoint.com/sites/source",
        )
        context = _Context(root.url, root)
        session = MigrationSession().register(context=context)
        task = MigrationTask.sharepoint(root.url, root.url, migrate_all=True)

        session.add_site_task(task=task)

        self.assertTrue(any("subsite" in message for message in session.warnings()))

    def test_add_task_provisions_structure_by_default(self):
        source = _context([_tasks()])
        session = MigrationSession().register(context=source)
        task = MigrationTask.sharepoint(
            "https://contoso.sharepoint.com/sites/source",
            source.base_url,
            source_list="Tasks",
            target_list="Tasks",
        )

        session.add_task(task=task)

        self.assertEqual(self.provision.call_count, 1)

    def test_add_task_can_skip_structure_provisioning(self):
        source = _context([_tasks()])
        session = MigrationSession().register(context=source)
        task = MigrationTask.sharepoint(
            "https://contoso.sharepoint.com/sites/source",
            source.base_url,
            source_list="Tasks",
            target_list="Tasks",
        )

        session.add_task(task=task, provision_structure=False)

        self.capture.assert_not_called()


if __name__ == "__main__":
    unittest.main()
