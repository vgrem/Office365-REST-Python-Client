"""Compatibility import for the canonical ``PartnerTenantType``.

``microsoft.graph.partnerTenantType`` is a single Graph enum; the canonical
model lives with the tenant information models.
"""

from __future__ import annotations

from office365.directory.tenantinformation.partner_tenant_type import PartnerTenantType

__all__ = ["PartnerTenantType"]
