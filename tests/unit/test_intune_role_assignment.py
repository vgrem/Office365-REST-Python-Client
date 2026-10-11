"""Offline test for the Intune role-assignment model.

``DeviceAndAppManagementRoleAssignment`` shares everything with the generic
``RoleAssignment`` (``displayName``, ``description``, ``roleDefinition``) and
only adds ``members``; it must also keep its Intune-specific OData type name so
PATCH/POST payloads are correct.
"""

from __future__ import annotations

from office365.common.role_assignment import RoleAssignment
from office365.intune.devices.and_app_management_role_assignment import DeviceAndAppManagementRoleAssignment


def test_role_assignment_inherits_generic_model():
    assert issubclass(DeviceAndAppManagementRoleAssignment, RoleAssignment)


def test_role_assignment_exposes_members_and_odata_type():
    assignment = DeviceAndAppManagementRoleAssignment(None)
    assert assignment.entity_type_name == "microsoft.graph.deviceAndAppManagementRoleAssignment"
    assert list(assignment.members) == []
    assert assignment.display_name is None
