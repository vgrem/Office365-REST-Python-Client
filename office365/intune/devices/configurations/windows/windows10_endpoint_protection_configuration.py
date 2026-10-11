from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.intune.devices.configurations.windows.applicationguardblockclipboardsharingtype import (
        ApplicationGuardBlockClipboardSharingType,
    )
    from office365.intune.devices.configurations.windows.applicationguardblockfiletransfertype import (
        ApplicationGuardBlockFileTransferType,
    )
    from office365.intune.devices.configurations.windows.applockerapplicationcontroltype import (
        AppLockerApplicationControlType,
    )
    from office365.intune.devices.configurations.windows.bit_locker_removable_drive_policy import (
        BitLockerRemovableDrivePolicy,
    )
    from office365.intune.devices.configurations.windows.firewall_network_profile import (
        WindowsFirewallNetworkProfile,
    )
    from office365.intune.devices.configurations.windows.firewallcertificaterevocationlistcheckmethodtype import (
        FirewallCertificateRevocationListCheckMethodType,
    )
    from office365.intune.devices.configurations.windows.firewallpacketqueueingmethodtype import (
        FirewallPacketQueueingMethodType,
    )
    from office365.intune.devices.configurations.windows.firewallpresharedkeyencodingmethodtype import (
        FirewallPreSharedKeyEncodingMethodType,
    )


class Windows10EndpointProtectionConfiguration(Entity):
    @property
    def application_guard_allow_persistence(self) -> Optional[bool]:
        """Gets the applicationGuardAllowPersistence property"""
        return self.properties.get("applicationGuardAllowPersistence", None)

    @property
    def application_guard_allow_print_to_local_printers(self) -> Optional[bool]:
        """Gets the applicationGuardAllowPrintToLocalPrinters property"""
        return self.properties.get("applicationGuardAllowPrintToLocalPrinters", None)

    @property
    def application_guard_allow_print_to_network_printers(self) -> Optional[bool]:
        """Gets the applicationGuardAllowPrintToNetworkPrinters property"""
        return self.properties.get("applicationGuardAllowPrintToNetworkPrinters", None)

    @property
    def application_guard_allow_print_to_pdf(self) -> Optional[bool]:
        """Gets the applicationGuardAllowPrintToPDF property"""
        return self.properties.get("applicationGuardAllowPrintToPDF", None)

    @property
    def application_guard_allow_print_to_xps(self) -> Optional[bool]:
        """Gets the applicationGuardAllowPrintToXPS property"""
        return self.properties.get("applicationGuardAllowPrintToXPS", None)

    @property
    def application_guard_block_clipboard_sharing(self) -> ApplicationGuardBlockClipboardSharingType:
        """Gets the applicationGuardBlockClipboardSharing property"""
        from office365.intune.devices.configurations.windows.applicationguardblockclipboardsharingtype import (
            ApplicationGuardBlockClipboardSharingType,
        )

        return self.properties.get(
            "applicationGuardBlockClipboardSharing", ApplicationGuardBlockClipboardSharingType.notConfigured
        )

    @property
    def application_guard_block_file_transfer(self) -> ApplicationGuardBlockFileTransferType:
        """Gets the applicationGuardBlockFileTransfer property"""
        from office365.intune.devices.configurations.windows.applicationguardblockfiletransfertype import (
            ApplicationGuardBlockFileTransferType,
        )

        return self.properties.get(
            "applicationGuardBlockFileTransfer", ApplicationGuardBlockFileTransferType.notConfigured
        )

    @property
    def application_guard_block_non_enterprise_content(self) -> Optional[bool]:
        """Gets the applicationGuardBlockNonEnterpriseContent property"""
        return self.properties.get("applicationGuardBlockNonEnterpriseContent", None)

    @property
    def application_guard_enabled(self) -> Optional[bool]:
        """Gets the applicationGuardEnabled property"""
        return self.properties.get("applicationGuardEnabled", None)

    @property
    def application_guard_force_auditing(self) -> Optional[bool]:
        """Gets the applicationGuardForceAuditing property"""
        return self.properties.get("applicationGuardForceAuditing", None)

    @property
    def app_locker_application_control(self) -> AppLockerApplicationControlType:
        """Gets the appLockerApplicationControl property"""
        from office365.intune.devices.configurations.windows.applockerapplicationcontroltype import (
            AppLockerApplicationControlType,
        )

        return self.properties.get("appLockerApplicationControl", AppLockerApplicationControlType.notConfigured)

    @property
    def bit_locker_disable_warning_for_other_disk_encryption(self) -> Optional[bool]:
        """Gets the bitLockerDisableWarningForOtherDiskEncryption property"""
        return self.properties.get("bitLockerDisableWarningForOtherDiskEncryption", None)

    @property
    def bit_locker_enable_storage_card_encryption_on_mobile(self) -> Optional[bool]:
        """Gets the bitLockerEnableStorageCardEncryptionOnMobile property"""
        return self.properties.get("bitLockerEnableStorageCardEncryptionOnMobile", None)

    @property
    def bit_locker_encrypt_device(self) -> Optional[bool]:
        """Gets the bitLockerEncryptDevice property"""
        return self.properties.get("bitLockerEncryptDevice", None)

    @property
    def bit_locker_removable_drive_policy(self) -> BitLockerRemovableDrivePolicy:
        """Gets the bitLockerRemovableDrivePolicy property"""
        from office365.intune.devices.configurations.windows.bit_locker_removable_drive_policy import (
            BitLockerRemovableDrivePolicy,
        )

        return self.properties.get("bitLockerRemovableDrivePolicy", BitLockerRemovableDrivePolicy())

    @property
    def defender_additional_guarded_folders(self) -> StringCollection:
        """Gets the defenderAdditionalGuardedFolders property"""
        return self.properties.get("defenderAdditionalGuardedFolders", StringCollection())

    @property
    def defender_attack_surface_reduction_excluded_paths(self) -> StringCollection:
        """Gets the defenderAttackSurfaceReductionExcludedPaths property"""
        return self.properties.get("defenderAttackSurfaceReductionExcludedPaths", StringCollection())

    @property
    def defender_exploit_protection_xml(self) -> Optional[bytes]:
        """Gets the defenderExploitProtectionXml property"""
        return self.properties.get("defenderExploitProtectionXml", None)

    @property
    def defender_exploit_protection_xml_file_name(self) -> Optional[str]:
        """Gets the defenderExploitProtectionXmlFileName property"""
        return self.properties.get("defenderExploitProtectionXmlFileName", None)

    @property
    def defender_guarded_folders_allowed_app_paths(self) -> StringCollection:
        """Gets the defenderGuardedFoldersAllowedAppPaths property"""
        return self.properties.get("defenderGuardedFoldersAllowedAppPaths", StringCollection())

    @property
    def defender_security_center_block_exploit_protection_override(self) -> Optional[bool]:
        """Gets the defenderSecurityCenterBlockExploitProtectionOverride property"""
        return self.properties.get("defenderSecurityCenterBlockExploitProtectionOverride", None)

    @property
    def firewall_block_stateful_ftp(self) -> Optional[bool]:
        """Gets the firewallBlockStatefulFTP property"""
        return self.properties.get("firewallBlockStatefulFTP", None)

    @property
    def firewall_certificate_revocation_list_check_method(self) -> FirewallCertificateRevocationListCheckMethodType:
        """Gets the firewallCertificateRevocationListCheckMethod property"""
        from office365.intune.devices.configurations.windows.firewallcertificaterevocationlistcheckmethodtype import (
            FirewallCertificateRevocationListCheckMethodType,
        )

        return self.properties.get(
            "firewallCertificateRevocationListCheckMethod",
            FirewallCertificateRevocationListCheckMethodType.deviceDefault,
        )

    @property
    def firewall_idle_timeout_for_security_association_in_seconds(self) -> Optional[int]:
        """Gets the firewallIdleTimeoutForSecurityAssociationInSeconds property"""
        return self.properties.get("firewallIdleTimeoutForSecurityAssociationInSeconds", None)

    @property
    def firewall_ip_sec_exemptions_allow_dhcp(self) -> Optional[bool]:
        """Gets the firewallIPSecExemptionsAllowDHCP property"""
        return self.properties.get("firewallIPSecExemptionsAllowDHCP", None)

    @property
    def firewall_ip_sec_exemptions_allow_icmp(self) -> Optional[bool]:
        """Gets the firewallIPSecExemptionsAllowICMP property"""
        return self.properties.get("firewallIPSecExemptionsAllowICMP", None)

    @property
    def firewall_ip_sec_exemptions_allow_neighbor_discovery(self) -> Optional[bool]:
        """Gets the firewallIPSecExemptionsAllowNeighborDiscovery property"""
        return self.properties.get("firewallIPSecExemptionsAllowNeighborDiscovery", None)

    @property
    def firewall_ip_sec_exemptions_allow_router_discovery(self) -> Optional[bool]:
        """Gets the firewallIPSecExemptionsAllowRouterDiscovery property"""
        return self.properties.get("firewallIPSecExemptionsAllowRouterDiscovery", None)

    @property
    def firewall_merge_keying_module_settings(self) -> Optional[bool]:
        """Gets the firewallMergeKeyingModuleSettings property"""
        return self.properties.get("firewallMergeKeyingModuleSettings", None)

    @property
    def firewall_packet_queueing_method(self) -> FirewallPacketQueueingMethodType:
        """Gets the firewallPacketQueueingMethod property"""
        from office365.intune.devices.configurations.windows.firewallpacketqueueingmethodtype import (
            FirewallPacketQueueingMethodType,
        )

        return self.properties.get("firewallPacketQueueingMethod", FirewallPacketQueueingMethodType.deviceDefault)

    @property
    def firewall_pre_shared_key_encoding_method(self) -> FirewallPreSharedKeyEncodingMethodType:
        """Gets the firewallPreSharedKeyEncodingMethod property"""
        from office365.intune.devices.configurations.windows.firewallpresharedkeyencodingmethodtype import (
            FirewallPreSharedKeyEncodingMethodType,
        )

        return self.properties.get(
            "firewallPreSharedKeyEncodingMethod", FirewallPreSharedKeyEncodingMethodType.deviceDefault
        )

    @property
    def firewall_profile_domain(self) -> Optional[WindowsFirewallNetworkProfile]:
        """Gets the firewallProfileDomain property"""
        return self.properties.get("firewallProfileDomain", None)

    @property
    def firewall_profile_private(self) -> Optional[WindowsFirewallNetworkProfile]:
        """Gets the firewallProfilePrivate property"""
        return self.properties.get("firewallProfilePrivate", None)

    @property
    def firewall_profile_public(self) -> Optional[WindowsFirewallNetworkProfile]:
        """Gets the firewallProfilePublic property"""
        return self.properties.get("firewallProfilePublic", None)

    @property
    def smart_screen_block_override_for_files(self) -> Optional[bool]:
        """Gets the smartScreenBlockOverrideForFiles property"""
        return self.properties.get("smartScreenBlockOverrideForFiles", None)

    @property
    def smart_screen_enable_in_shell(self) -> Optional[bool]:
        """Gets the smartScreenEnableInShell property"""
        return self.properties.get("smartScreenEnableInShell", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Windows10EndpointProtectionConfiguration"
