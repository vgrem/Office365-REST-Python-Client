"""Tests for the identifier-to-snake_case conversion used by the generator."""

from __future__ import annotations

import pytest
from generator.builders.naming import to_snake_case


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("EmailIDs", "email_ids"),
        ("emailIDs", "email_ids"),
        ("IDs", "ids"),
        ("URLs", "urls"),
        ("APIs", "apis"),
        ("LinkedPDFs", "linked_pdfs"),
        ("FailedContentTypeIDs", "failed_content_type_ids"),
        ("GBsArchived", "gbs_archived"),
        ("AllowSelectSGsInODBList", "allow_select_sgs_in_odb_list"),
        ("HTTPServer", "http_server"),
        ("getHTTPResponse", "get_http_response"),
        ("UTCToLocalTime", "utc_to_local_time"),
        ("ParentIDId", "parent_id_id"),
        ("ExportCategoryToCSVByGroup", "export_category_to_csv_by_group"),
        ("AmIFollowedBy", "am_i_followed_by"),
        ("DisplayStartASiteOption", "display_start_a_site_option"),
        ("siteId", "site_id"),
        ("webUrl", "web_url"),
        ("OData__AuthorByline", "o_data__author_byline"),
        ("Access_x0020_RequestsItem", "access_x0020_requests_item"),
        ("PageLoadTimeInMS", "page_load_time_in_ms"),
        ("minimumCpuSpeedInMHz", "minimum_cpu_speed_in_mhz"),
        ("cloudPCs", "cloud_pcs"),
        ("externalIPs", "external_ips"),
        ("iCalUId", "ical_uid"),
        ("iOS", "ios"),
        ("ASite", "a_site"),
        ("allowedPolicyOIDs", "allowed_policy_oids"),
        ("IsSharePointOnline", "is_sharepoint_online"),
        ("SharePointIds", "sharepoint_ids"),
        ("getSharePointUrl", "get_sharepoint_url"),
        ("OneDriveForBusiness", "onedrive_for_business"),
        ("enableOneNote", "enable_onenote"),
        ("ExpirationDateTime", "expiration_datetime"),
        ("CreatedDateTime", "created_datetime"),
    ],
)
def test_to_snake_case(name: str, expected: str):
    assert to_snake_case(name) == expected


def test_keywords_get_suffix_builtins_do_not():
    assert to_snake_case("Class") == "class_"
    assert to_snake_case("Import") == "import_"
    # builtins are valid member names and are used across the codebase
    assert to_snake_case("ID") == "id"
    assert to_snake_case("Type") == "type"
    assert to_snake_case("List") == "list"
    assert to_snake_case("ID", avoid_keywords=False) == "id"
