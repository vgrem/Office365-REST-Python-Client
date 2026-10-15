"""Tests for the SharePoint whole-site (migrate_all) resolver and session wiring."""

import unittest
from unittest import mock

from office365.migration.session import MigrationSession
from office365.migration.settings import MigrationSettings
from office365.migration.sharepoint.adapters import (
    SharePointLibrarySource,
    SharePointLibraryTarget,
    SharePointListSource,
    SharePointListTarget,
)
from office365.migration.sharepoint.resolvers import (
    is_document_library,
    is_migratable_list,
    resolve_site_task,
    resolve_task,
)
from office365.migration.tasks import MigrationTask

_DOCUMENT_LIBRARY_TEMPLATE = 101


class _Folder:
    server_relative_url = "/sites/x/Documents"

    def get(self):
        return self

    def execute_query(self):
        return self


class _FakeList:
    def __init__(self, title, base_type=0, base_template=100, hidden=False, allow_deletion=True):
        self.title = title
        self.base_type = base_type
        self.base_template = base_template
        self.hidden = hidden
        self.allow_deletion = allow_deletion
        self.root_folder = _Folder()

    def get(self):
        return self

    def execute_query(self):
        return self


class _Lists:
    def __init__(self, source_lists):
        self._source_lists = list(source_lists)
        self.ensure_calls = []

    def get(self):
        return self

    def execute_query(self):
        return self._source_lists

    def __iter__(self):
        return iter(self._source_lists)

    def ensure_list(self, title, template_type=None):
        self.ensure_calls.append((title, template_type))
        base_type = 1 if int(template_type) == _DOCUMENT_LIBRARY_TEMPLATE else 0
        return _FakeList(title, base_type=base_type, base_template=int(template_type))


class _Web:
    def __init__(self, lists):
        self.lists = lists

    def get_list_by_title(self, title):
        for entry in self.lists._source_lists:
            if entry.title == title:
                return entry
        raise KeyError(title)


class _Context:
    def __init__(self, base_url, lists):
        self.base_url = base_url
        self.web = _Web(lists)
        self.clones = []

    def clone(self, url):
        self.clones.append(url)
        return _Context(url, self.web.lists)


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

    def test_provisions_structure_by_default(self):
        source = _context([_docs()])
        task = MigrationTask.sharepoint("https://contoso.sharepoint.com/sites/source", source.base_url, migrate_all=True)

        resolve_site_task(task, source)

        self.assertEqual(self.capture.call_args[0][0].title, "Documents")
        target_arg, structure_arg = self.provision.call_args[0]
        self.assertEqual(target_arg.title, "Documents")
        self.assertIsNone(structure_arg)

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

        with mock.patch("office365.migration.sharepoint.resolvers._package_target", return_value=object()):
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
