from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.entity import Entity
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.multigeo.service.alloweddatalocation import (
    AllowedDataLocation,
)
from office365.sharepoint.multigeo.service.contentdbschemaversion import (
    ContentDbSchemaVersion,
)
from office365.sharepoint.multigeo.service.crossfarmgroupmovejob import (
    CrossFarmGroupMoveJob,
)
from office365.sharepoint.multigeo.service.crossfarmsitemovejob import (
    CrossFarmSiteMoveJob,
)
from office365.sharepoint.multigeo.service.crossfarmusermovejob import (
    CrossFarmUserMoveJob,
)
from office365.sharepoint.multigeo.service.crossgeotenantbyok import CrossGeoTenantBYOK
from office365.sharepoint.multigeo.service.crossgeotenantcompatibility import (
    CrossGeoTenantCompatibility,
)
from office365.sharepoint.multigeo.service.crossgeotenantproperty import (
    CrossGeoTenantProperty,
)
from office365.sharepoint.multigeo.service.crossgeouserplacementjob import (
    CrossGeoUserPlacementJob,
)
from office365.sharepoint.multigeo.service.dblevelworkitementitydata import (
    DBLevelWorkItemEntityData,
)
from office365.sharepoint.multigeo.service.dfdeprecationjob import DfDeprecationJob
from office365.sharepoint.multigeo.service.geoadministrator import GeoAdministrator
from office365.sharepoint.multigeo.service.geoexperience import GeoExperience
from office365.sharepoint.multigeo.service.geolocationdata import GeoLocationData
from office365.sharepoint.multigeo.service.geotenantinstanceinformation import (
    GeoTenantInstanceInformation,
)
from office365.sharepoint.multigeo.service.globaladmincheck import GlobalAdminCheck
from office365.sharepoint.multigeo.service.groupmovejob import GroupMoveJob
from office365.sharepoint.multigeo.service.movesiterostate import MoveSiteROState
from office365.sharepoint.multigeo.service.siteattargetentitydata import (
    SiteAtTargetEntityData,
)
from office365.sharepoint.multigeo.service.sitemovejob import SiteMoveJob
from office365.sharepoint.multigeo.service.storage_quota import StorageQuota
from office365.sharepoint.multigeo.service.supportedgeolocationsfortenant import (
    SupportedGeoLocationsForTenant,
)
from office365.sharepoint.multigeo.service.taxonomyreplicationparameters import (
    TaxonomyReplicationParameters,
)
from office365.sharepoint.multigeo.service.tenant_information import TenantInformation
from office365.sharepoint.multigeo.service.unified_group import UnifiedGroup
from office365.sharepoint.multigeo.service.usermovejob import UserMoveJob

if TYPE_CHECKING:
    from office365.sharepoint.multigeo.service.move_job_report import MoveJobReport


class MultiGeoServicesBeta(Entity):
    @property
    def allowed_data_locations(self) -> EntityCollection[AllowedDataLocation]:
        """Gets the AllowedDataLocations property"""
        return self.properties.get(
            "AllowedDataLocations",
            EntityCollection[AllowedDataLocation](
                self.context, AllowedDataLocation, ResourcePath("AllowedDataLocations", self.resource_path)
            ),
        )

    @property
    def content_db_schema_version(self) -> ContentDbSchemaVersion:
        """Gets the ContentDbSchemaVersion property"""
        return self.properties.get(
            "ContentDbSchemaVersion",
            ContentDbSchemaVersion(self.context, ResourcePath("ContentDbSchemaVersion", self.resource_path)),
        )

    @property
    def cross_farm_group_move_jobs(self) -> EntityCollection[CrossFarmGroupMoveJob]:
        """Gets the CrossFarmGroupMoveJobs property"""
        return self.properties.get(
            "CrossFarmGroupMoveJobs",
            EntityCollection[CrossFarmGroupMoveJob](
                self.context, CrossFarmGroupMoveJob, ResourcePath("CrossFarmGroupMoveJobs", self.resource_path)
            ),
        )

    @property
    def cross_farm_site_move_jobs(self) -> EntityCollection[CrossFarmSiteMoveJob]:
        """Gets the CrossFarmSiteMoveJobs property"""
        return self.properties.get(
            "CrossFarmSiteMoveJobs",
            EntityCollection[CrossFarmSiteMoveJob](
                self.context, CrossFarmSiteMoveJob, ResourcePath("CrossFarmSiteMoveJobs", self.resource_path)
            ),
        )

    @property
    def cross_farm_user_move_jobs(self) -> EntityCollection[CrossFarmUserMoveJob]:
        """Gets the CrossFarmUserMoveJobs property"""
        return self.properties.get(
            "CrossFarmUserMoveJobs",
            EntityCollection[CrossFarmUserMoveJob](
                self.context, CrossFarmUserMoveJob, ResourcePath("CrossFarmUserMoveJobs", self.resource_path)
            ),
        )

    @property
    def cross_geo_tenant_byok(self) -> CrossGeoTenantBYOK:
        """Gets the CrossGeoTenantBYOK property"""
        return self.properties.get(
            "CrossGeoTenantBYOK",
            CrossGeoTenantBYOK(self.context, ResourcePath("CrossGeoTenantBYOK", self.resource_path)),
        )

    @property
    def cross_geo_tenant_compatibility(self) -> CrossGeoTenantCompatibility:
        """Gets the CrossGeoTenantCompatibility property"""
        return self.properties.get(
            "CrossGeoTenantCompatibility",
            CrossGeoTenantCompatibility(self.context, ResourcePath("CrossGeoTenantCompatibility", self.resource_path)),
        )

    @property
    def cross_geo_tenant_properties(self) -> EntityCollection[CrossGeoTenantProperty]:
        """Gets the CrossGeoTenantProperties property"""
        return self.properties.get(
            "CrossGeoTenantProperties",
            EntityCollection[CrossGeoTenantProperty](
                self.context, CrossGeoTenantProperty, ResourcePath("CrossGeoTenantProperties", self.resource_path)
            ),
        )

    @property
    def cross_geo_user_placement_jobs(self) -> EntityCollection[CrossGeoUserPlacementJob]:
        """Gets the CrossGeoUserPlacementJobs property"""
        return self.properties.get(
            "CrossGeoUserPlacementJobs",
            EntityCollection[CrossGeoUserPlacementJob](
                self.context, CrossGeoUserPlacementJob, ResourcePath("CrossGeoUserPlacementJobs", self.resource_path)
            ),
        )

    @property
    def db_level_work_items(self) -> EntityCollection[DBLevelWorkItemEntityData]:
        """Gets the DBLevelWorkItems property"""
        return self.properties.get(
            "DBLevelWorkItems",
            EntityCollection[DBLevelWorkItemEntityData](
                self.context, DBLevelWorkItemEntityData, ResourcePath("DBLevelWorkItems", self.resource_path)
            ),
        )

    @property
    def delete_target_site(self) -> EntityCollection[SiteAtTargetEntityData]:
        """Gets the DeleteTargetSite property"""
        return self.properties.get(
            "DeleteTargetSite",
            EntityCollection[SiteAtTargetEntityData](
                self.context, SiteAtTargetEntityData, ResourcePath("DeleteTargetSite", self.resource_path)
            ),
        )

    @property
    def df_deprecation_jobs(self) -> EntityCollection[DfDeprecationJob]:
        """Gets the DfDeprecationJobs property"""
        return self.properties.get(
            "DfDeprecationJobs",
            EntityCollection[DfDeprecationJob](
                self.context, DfDeprecationJob, ResourcePath("DfDeprecationJobs", self.resource_path)
            ),
        )

    @property
    def geo_administrators(self) -> EntityCollection[GeoAdministrator]:
        """Gets the GeoAdministrators property"""
        return self.properties.get(
            "GeoAdministrators",
            EntityCollection[GeoAdministrator](
                self.context, GeoAdministrator, ResourcePath("GeoAdministrators", self.resource_path)
            ),
        )

    @property
    def geo_experience(self) -> GeoExperience:
        """Gets the GeoExperience property"""
        return self.properties.get(
            "GeoExperience", GeoExperience(self.context, ResourcePath("GeoExperience", self.resource_path))
        )

    @property
    def geo_tenant_instance_information_collection(self) -> EntityCollection[GeoTenantInstanceInformation]:
        """Gets the GeoTenantInstanceInformationCollection property"""
        return self.properties.get(
            "GeoTenantInstanceInformationCollection",
            EntityCollection[GeoTenantInstanceInformation](
                self.context,
                GeoTenantInstanceInformation,
                ResourcePath("GeoTenantInstanceInformationCollection", self.resource_path),
            ),
        )

    @property
    def global_admin_check(self) -> GlobalAdminCheck:
        """Gets the GlobalAdminCheck property"""
        return self.properties.get(
            "GlobalAdminCheck", GlobalAdminCheck(self.context, ResourcePath("GlobalAdminCheck", self.resource_path))
        )

    @property
    def group_move_jobs(self) -> EntityCollection[GroupMoveJob]:
        """Gets the GroupMoveJobs property"""
        return self.properties.get(
            "GroupMoveJobs",
            EntityCollection[GroupMoveJob](
                self.context, GroupMoveJob, ResourcePath("GroupMoveJobs", self.resource_path)
            ),
        )

    @property
    def move_sites(self) -> EntityCollection[MoveSiteROState]:
        """Gets the MoveSites property"""
        return self.properties.get(
            "MoveSites",
            EntityCollection[MoveSiteROState](
                self.context, MoveSiteROState, ResourcePath("MoveSites", self.resource_path)
            ),
        )

    @property
    def site_move_jobs(self) -> EntityCollection[SiteMoveJob]:
        """Gets the SiteMoveJobs property"""
        return self.properties.get(
            "SiteMoveJobs",
            EntityCollection[SiteMoveJob](self.context, SiteMoveJob, ResourcePath("SiteMoveJobs", self.resource_path)),
        )

    @property
    def storage_quotas(self) -> EntityCollection[StorageQuota]:
        """Gets the StorageQuotas property"""
        return self.properties.get(
            "StorageQuotas",
            EntityCollection[StorageQuota](
                self.context, StorageQuota, ResourcePath("StorageQuotas", self.resource_path)
            ),
        )

    @property
    def supported_geo_locations_for_tenant(self) -> SupportedGeoLocationsForTenant:
        """Gets the SupportedGeoLocationsForTenant property"""
        return self.properties.get(
            "SupportedGeoLocationsForTenant",
            SupportedGeoLocationsForTenant(
                self.context, ResourcePath("SupportedGeoLocationsForTenant", self.resource_path)
            ),
        )

    @property
    def supportedgeolocationsmapdata(self) -> EntityCollection[GeoLocationData]:
        """Gets the supportedgeolocationsmapdata property"""
        return self.properties.get(
            "supportedgeolocationsmapdata",
            EntityCollection[GeoLocationData](
                self.context, GeoLocationData, ResourcePath("supportedgeolocationsmapdata", self.resource_path)
            ),
        )

    @property
    def taxonomy_replication_parameters(self) -> TaxonomyReplicationParameters:
        """Gets the TaxonomyReplicationParameters property"""
        return self.properties.get(
            "TaxonomyReplicationParameters",
            TaxonomyReplicationParameters(
                self.context, ResourcePath("TaxonomyReplicationParameters", self.resource_path)
            ),
        )

    @property
    def tenant_information_collection(self) -> EntityCollection[TenantInformation]:
        """Gets the TenantInformationCollection property"""
        return self.properties.get(
            "TenantInformationCollection",
            EntityCollection[TenantInformation](
                self.context, TenantInformation, ResourcePath("TenantInformationCollection", self.resource_path)
            ),
        )

    @property
    def unified_groups(self) -> EntityCollection[UnifiedGroup]:
        """Gets the UnifiedGroups property"""
        return self.properties.get(
            "UnifiedGroups",
            EntityCollection[UnifiedGroup](
                self.context, UnifiedGroup, ResourcePath("UnifiedGroups", self.resource_path)
            ),
        )

    @property
    def update_gls_registration(self) -> EntityCollection[SiteAtTargetEntityData]:
        """Gets the UpdateGLSRegistration property"""
        return self.properties.get(
            "UpdateGLSRegistration",
            EntityCollection[SiteAtTargetEntityData](
                self.context, SiteAtTargetEntityData, ResourcePath("UpdateGLSRegistration", self.resource_path)
            ),
        )

    @property
    def user_move_jobs(self) -> EntityCollection[UserMoveJob]:
        """Gets the UserMoveJobs property"""
        return self.properties.get(
            "UserMoveJobs",
            EntityCollection[UserMoveJob](self.context, UserMoveJob, ResourcePath("UserMoveJobs", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "Microsoft.Online.SharePoint.MultiGeo.Service.MultiGeoServicesBeta"

    @property
    def move_job_reports(self) -> MoveJobReport:
        """Gets the MoveJobReports property"""
        from office365.sharepoint.multigeo.service.move_job_report import MoveJobReport

        return self.properties.get(
            "MoveJobReports", MoveJobReport(self.context, ResourcePath("MoveJobReports", self.resource_path))
        )
