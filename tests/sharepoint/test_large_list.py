from __future__ import annotations

from typing import ClassVar, Optional

from office365.sharepoint.listitems.caml import CamlQuery
from office365.sharepoint.lists.list import List
from office365.sharepoint.lists.templates.type import ListTemplateType
from office365.sharepoint.views.scope import ViewScope

from tests import create_unique_name
from tests.sharepoint.sharepoint_case import SPTestCase


class TestLargeListPaging(SPTestCase):
    """Paged reads over a small list — the mechanics of the large-list threshold.

    Uses four rows with a page size of two so the final page is exactly full,
    which is the shape that previously tripped the ``$skip``/``$skiptoken``
    conflict and CAML's collection-position paging.
    """

    target_list: ClassVar[Optional[List]] = None
    list_title = create_unique_name("LargeList_")
    folder_name = create_unique_name("LargeFolder_")

    def test_01_create_list(self):
        result = self.client.web.lists.add_list(
            title=self.list_title, template_type=ListTemplateType.GenericList
        ).execute_query()
        self.assertEqual(result.title, self.list_title)
        TestLargeListPaging.target_list = result

    def test_02_seed_four_items(self):
        self.assertIsNotNone(TestLargeListPaging.target_list)
        records = [{"Title": f"item{i}"} for i in range(4)]
        TestLargeListPaging.target_list.from_records([records]).execute_query()
        # ``List.ItemCount`` is a denormalised counter the service does not refresh
        # on this path, so the seeded rows are counted where they are authoritative.
        items = TestLargeListPaging.target_list.items.get().execute_query()
        self.assertEqual(len(items), 4)

    def test_03_get_all_pages_without_skip_conflict(self):
        """REST paging follows __next/$skiptoken and does not fall back to $skip."""
        self.assertIsNotNone(TestLargeListPaging.target_list)
        items = TestLargeListPaging.target_list.items.order_by("ID").get_all(page_size=2).execute_query()
        self.assertEqual(sum(1 for _ in items), 4)

    def test_04_caml_paging_continues_from_position(self):
        """CAML paging continues from the last item via ListItemCollectionPosition."""
        self.assertIsNotNone(TestLargeListPaging.target_list)
        query = CamlQuery.builder().order_by("ID").row_limit(2, paged=True).scope(ViewScope.RecursiveAll).build()
        items = TestLargeListPaging.target_list.get_items(query, page_size=2).execute_query()
        ids = [item.id for item in items]
        self.assertEqual(len(ids), 4)
        self.assertEqual(len(set(ids)), 4)

    def test_05_folder_get_files_pages(self):
        """Folder.get_files pages the Files endpoint (no __next; uses $skip)."""
        root = self.client.web.default_document_library().root_folder
        folder = root.folders.add(self.folder_name).execute_query()
        for i in range(4):
            folder.upload_file(f"probe{i}.txt", "x").execute_query()
        files = folder.get_files(page_size=2).execute_query()
        self.assertEqual(len(files), 4)
        folder.delete_object().execute_query()

    def test_06_delete_list(self):
        self.assertIsNotNone(TestLargeListPaging.target_list)
        TestLargeListPaging.target_list.delete_object().execute_query()
