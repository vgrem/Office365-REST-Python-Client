"""Rendering of runtime objects, values and collections (``repr``/``str``)."""

from __future__ import annotations

import unittest
import uuid
from dataclasses import dataclass
from typing import Any, Optional, cast

from office365.directory.users.user import User
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.display import MAX_ITEMS
from office365.runtime.types.collections import GuidCollection, StringCollection


def _user_collection() -> ClientObjectCollection[User]:
    return ClientObjectCollection(cast(ClientRuntimeContext, None), User, None)


@dataclass
class _Node(ClientValue):
    name: Optional[str] = None
    child: Any = None


@dataclass
class _Address(ClientValue):
    city: Optional[str] = None


class TestClientValueRendering(unittest.TestCase):
    def test_dataclass_repr_is_bounded(self):
        # ``@dataclass`` must not shadow the bounded rendering.
        rendered = repr(_Node(name="root"))
        self.assertTrue(rendered.startswith("_Node("))
        self.assertIn("name=root", rendered)
        self.assertNotIn("child", rendered)


class TestValueCollectionRendering(unittest.TestCase):
    """A scalar collection prints as the list it is; the type survives in ``repr``."""

    def test_scalar_collection_prints_as_a_list(self):
        roles = StringCollection(["freeBusyRead", "limitedRead", "read"])
        self.assertEqual(str(roles), "[freeBusyRead, limitedRead, read]")

    def test_repr_is_type_qualified_and_quoted(self):
        # ``repr`` is pasted into a REPL: quoting keeps it unambiguous and constructible.
        roles = StringCollection(["freeBusyRead", "read"])
        self.assertEqual(repr(roles), "StringCollection(['freeBusyRead', 'read'])")

    def test_empty_collection(self):
        empty = StringCollection()
        self.assertEqual(str(empty), "[]")
        self.assertEqual(repr(empty), "StringCollection([])")

    def test_truncation_is_marked_in_both(self):
        roles = StringCollection([f"role{index}" for index in range(MAX_ITEMS + 2)])
        self.assertTrue(str(roles).endswith(", …]"))
        self.assertNotIn(f"role{MAX_ITEMS}", str(roles))
        self.assertIn("'…'", repr(roles))

    def test_an_alias_reports_its_own_name(self):
        # Not ``ClientValueCollection[str]``: the generic spelling is not the type you hold.
        ids = GuidCollection([uuid.UUID(int=1)])
        self.assertEqual(str(ids), "[00000000-0000-0000-0000-000000000001]")
        self.assertEqual(repr(ids), "GuidCollection([UUID('00000000-0000-0000-0000-000000000001')])")

    def test_record_collection_still_renders_a_table(self):
        collection = ClientValueCollection(_Address, [_Address(city="Oslo"), _Address(city="Kyiv")])
        self.assertIn("_Address(count=2)", str(collection))
        self.assertIn("Oslo", str(collection))

    def test_nested_scalar_collection_renders_as_a_list(self):
        # The nested rendering was already list-shaped; the top level now agrees with it.
        self.assertIn("child=[a, b]", repr(_Node(name="root", child=StringCollection(["a", "b"]))))


class TestObjectCollectionRendering(unittest.TestCase):
    def _loaded(self, count: int) -> ClientObjectCollection[User]:
        collection = _user_collection()
        for index in range(count):
            collection.add_child(
                collection.create_typed_object(
                    {"displayName": f"User {index}", "userPrincipalName": f"user{index}@contoso.com"}
                )
            )
        return collection

    def test_to_string_does_not_truncate_identifiers(self):
        collection = _user_collection()
        long_upn = "a.very.long.guest.address#EXT#@contoso.onmicrosoft.com"
        collection.add_child(collection.create_typed_object({"displayName": "Guest", "userPrincipalName": long_upn}))

        self.assertNotIn(long_upn, repr(collection))  # the preview bounds the column
        self.assertIn(long_upn, collection.to_string())  # the report keeps it intact


if __name__ == "__main__":
    unittest.main()
