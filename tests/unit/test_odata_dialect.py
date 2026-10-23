"""The dialect table is the only place a profile's spelling is decided.

These tests pin the table itself rather than the behaviour built on it: for every
level either family can ask for, which row answers, what media type names it, and
whether the row writes control information at all.
"""

from __future__ import annotations

import unittest

from office365.runtime.odata.dialect import (
    V3_VERBOSE,
    V4,
)
from office365.runtime.odata.v3.json_light_format import JsonLightFormat
from office365.runtime.odata.v3.metadata_level import ODataV3MetadataLevel
from office365.runtime.odata.v4.json_format import V4JsonFormat
from office365.runtime.odata.v4.metadata_level import ODataV4MetadataLevel


class TestEveryLevelIsARow(unittest.TestCase):
    def test_a_level_names_its_own_media_type(self):
        self.assertEqual(JsonLightFormat().media_type, "application/json;odata=verbose")
        self.assertEqual(
            JsonLightFormat(ODataV3MetadataLevel.MinimalMetadata).media_type,
            "application/json;odata=minimalmetadata",
        )
        self.assertEqual(
            JsonLightFormat(ODataV3MetadataLevel.NoMetadata).media_type,
            "application/json;odata=nometadata",
        )
        self.assertEqual(
            V4JsonFormat().media_type,
            "application/json;odata.metadata=minimal;odata.streaming=False;IEEE754Compatible=False",
        )
        self.assertEqual(
            V4JsonFormat(ODataV4MetadataLevel.Full).media_type,
            "application/json;odata.metadata=full;odata.streaming=False;IEEE754Compatible=False",
        )

    def test_only_the_level_that_omits_control_information_omits_it(self):
        self.assertTrue(JsonLightFormat().include_control_information)
        self.assertTrue(JsonLightFormat(ODataV3MetadataLevel.MinimalMetadata).include_control_information)
        self.assertFalse(JsonLightFormat(ODataV3MetadataLevel.NoMetadata).include_control_information)
        self.assertTrue(V4JsonFormat().include_control_information)
        self.assertFalse(V4JsonFormat(ODataV4MetadataLevel.NoMetadata).include_control_information)


class TestTheTableCannotDisagreeWithItself(unittest.TestCase):
    def test_an_unknown_level_falls_back_to_one_row(self):
        # Before the table carried control information, a profile could claim the
        # verbose spelling and simultaneously write no control information (a
        # `JsonLightFormat("typo")`). Both answers now come from the fallback row.
        for profile in (JsonLightFormat("typo"), V4JsonFormat("typo")):
            with self.subTest(profile=type(profile).__name__):
                self.assertIs(profile.dialect, profile._default_dialect)
                self.assertEqual(profile.include_control_information, profile.dialect.control_information)


class TestRowsDifferOnlyWhereTheDialectDoes(unittest.TestCase):
    def test_graph_and_sharepoint_marker_keys(self):
        self.assertEqual(V4.type_marker, "@odata.type")
        self.assertEqual(V3_VERBOSE.type_marker, "__metadata")
        self.assertTrue(V3_VERBOSE.type_wrapped)
        self.assertFalse(V4.type_wrapped)


class TestTheEnvelopeIsTheSameInBothDirections(unittest.TestCase):
    def test_a_collection_payload_is_the_collection_the_walk_reads_back(self):
        # `wrap` writes the envelope and `iter_payload` unwraps it; if a row spelled
        # one thing and read another, an echo of our own payload would not round-trip.
        from office365.runtime.client_value_collection import ClientValueCollection

        for level in (
            ODataV3MetadataLevel.Verbose,
            ODataV3MetadataLevel.MinimalMetadata,
            ODataV3MetadataLevel.NoMetadata,
        ):
            with self.subTest(level=level.value):
                fmt = JsonLightFormat(level)
                payload = fmt.wrap(ClientValueCollection(str, ["a"]), ["a"])
                self.assertEqual(dict(fmt.iter_payload(payload)), {0: "a"})
