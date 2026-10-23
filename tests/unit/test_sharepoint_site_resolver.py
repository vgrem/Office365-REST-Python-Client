"""Tests for the SharePoint whole-site (migrate_all) resolver and session wiring."""

import hashlib
import re
import unittest
from unittest import mock

from office365.migration.adapters.filesystem import FileSystemSource
from office365.migration.sharepoint.adapters import (
    SharePointLibrarySource,
    SharePointLibraryTarget,
    SharePointListSource,
    SharePointListTarget,
)
from office365.migration.sharepoint.resolvers import (
    resolve_site_task,
    resolve_task,
)
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


class TestResolveSingleListTask(_StructureStub, unittest.TestCase):
    def test_a_list_migrated_into_a_library_is_refused(self):
        # Live with provision_structure=False, this pair reported ``Success 2`` and
        # left two files named "1" and "2" whose content was the record's repr.
        source = _context([_docs(), _tasks()])
        task = MigrationTask.sharepoint(
            "https://contoso.sharepoint.com/sites/source",
            source.base_url,
            source_list="Tasks",
            target_list="Documents",
        )

        with self.assertRaises(ValueError) as caught:
            resolve_task(task, source)

        self.assertIn("'Tasks' holds list records and 'Documents' is a document library", str(caught.exception))


class TestFileShareTask(_StructureStub, unittest.TestCase):
    def test_a_file_share_into_a_document_library_resolves(self):
        source = _context([_docs()])
        task = MigrationTask.file_share("/data/share", source.base_url, target_list="Documents")

        src, dst = resolve_task(task, source)

        self.assertIsInstance(src, FileSystemSource)
        self.assertIsInstance(dst, SharePointLibraryTarget)


if __name__ == "__main__":
    unittest.main()
