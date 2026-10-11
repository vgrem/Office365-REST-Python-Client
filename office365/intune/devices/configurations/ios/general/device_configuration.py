from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.intune.devices.compliance.requiredpasswordtype import (
        RequiredPasswordType,
    )
    from office365.intune.devices.configurations.applisttype import AppListType
    from office365.intune.devices.configurations.ios.general.ratingappstype import (
        RatingAppsType,
    )
    from office365.intune.devices.configurations.ios.network_usage_rule import (
        IosNetworkUsageRule,
    )
    from office365.intune.devices.configurations.media_content_rating_australia import (
        MediaContentRatingAustralia,
    )
    from office365.intune.devices.configurations.media_content_rating_canada import MediaContentRatingCanada
    from office365.intune.devices.configurations.media_content_rating_france import MediaContentRatingFrance
    from office365.intune.devices.configurations.media_content_rating_germany import MediaContentRatingGermany
    from office365.intune.devices.configurations.media_content_rating_ireland import MediaContentRatingIreland
    from office365.intune.devices.configurations.media_content_rating_japan import MediaContentRatingJapan
    from office365.intune.devices.configurations.media_content_rating_new_zealand import (
        MediaContentRatingNewZealand,
    )
    from office365.intune.devices.configurations.media_content_rating_united_kingdom import (
        MediaContentRatingUnitedKingdom,
    )
    from office365.intune.devices.configurations.media_content_rating_united_states import (
        MediaContentRatingUnitedStates,
    )
    from office365.intune.devices.configurations.webbrowsercookiesettings import (
        WebBrowserCookieSettings,
    )
    from office365.intune.devices.management.mobileapps.app_list_item import AppListItem


class IosGeneralDeviceConfiguration(Entity):
    @property
    def account_block_modification(self) -> Optional[bool]:
        """Gets the accountBlockModification property"""
        return self.properties.get("accountBlockModification", None)

    @property
    def activation_lock_allow_when_supervised(self) -> Optional[bool]:
        """Gets the activationLockAllowWhenSupervised property"""
        return self.properties.get("activationLockAllowWhenSupervised", None)

    @property
    def air_drop_blocked(self) -> Optional[bool]:
        """Gets the airDropBlocked property"""
        return self.properties.get("airDropBlocked", None)

    @property
    def air_drop_force_unmanaged_drop_target(self) -> Optional[bool]:
        """Gets the airDropForceUnmanagedDropTarget property"""
        return self.properties.get("airDropForceUnmanagedDropTarget", None)

    @property
    def air_play_force_pairing_password_for_outgoing_requests(self) -> Optional[bool]:
        """Gets the airPlayForcePairingPasswordForOutgoingRequests property"""
        return self.properties.get("airPlayForcePairingPasswordForOutgoingRequests", None)

    @property
    def apple_news_blocked(self) -> Optional[bool]:
        """Gets the appleNewsBlocked property"""
        return self.properties.get("appleNewsBlocked", None)

    @property
    def apple_watch_block_pairing(self) -> Optional[bool]:
        """Gets the appleWatchBlockPairing property"""
        return self.properties.get("appleWatchBlockPairing", None)

    @property
    def apple_watch_force_wrist_detection(self) -> Optional[bool]:
        """Gets the appleWatchForceWristDetection property"""
        return self.properties.get("appleWatchForceWristDetection", None)

    @property
    def apps_single_app_mode_list(self) -> ClientValueCollection[AppListItem]:
        """Gets the appsSingleAppModeList property"""
        from office365.intune.devices.management.mobileapps.app_list_item import AppListItem

        return self.properties.get("appsSingleAppModeList", ClientValueCollection[AppListItem](AppListItem))

    @property
    def app_store_block_automatic_downloads(self) -> Optional[bool]:
        """Gets the appStoreBlockAutomaticDownloads property"""
        return self.properties.get("appStoreBlockAutomaticDownloads", None)

    @property
    def app_store_blocked(self) -> Optional[bool]:
        """Gets the appStoreBlocked property"""
        return self.properties.get("appStoreBlocked", None)

    @property
    def app_store_block_in_app_purchases(self) -> Optional[bool]:
        """Gets the appStoreBlockInAppPurchases property"""
        return self.properties.get("appStoreBlockInAppPurchases", None)

    @property
    def app_store_block_ui_app_installation(self) -> Optional[bool]:
        """Gets the appStoreBlockUIAppInstallation property"""
        return self.properties.get("appStoreBlockUIAppInstallation", None)

    @property
    def app_store_require_password(self) -> Optional[bool]:
        """Gets the appStoreRequirePassword property"""
        return self.properties.get("appStoreRequirePassword", None)

    @property
    def apps_visibility_list(self) -> ClientValueCollection[AppListItem]:
        """Gets the appsVisibilityList property"""
        from office365.intune.devices.management.mobileapps.app_list_item import AppListItem

        return self.properties.get("appsVisibilityList", ClientValueCollection[AppListItem](AppListItem))

    @property
    def apps_visibility_list_type(self) -> AppListType:
        """Gets the appsVisibilityListType property"""
        from office365.intune.devices.configurations.applisttype import AppListType

        return self.properties.get("appsVisibilityListType", AppListType.none)

    @property
    def bluetooth_block_modification(self) -> Optional[bool]:
        """Gets the bluetoothBlockModification property"""
        return self.properties.get("bluetoothBlockModification", None)

    @property
    def camera_blocked(self) -> Optional[bool]:
        """Gets the cameraBlocked property"""
        return self.properties.get("cameraBlocked", None)

    @property
    def cellular_block_data_roaming(self) -> Optional[bool]:
        """Gets the cellularBlockDataRoaming property"""
        return self.properties.get("cellularBlockDataRoaming", None)

    @property
    def cellular_block_global_background_fetch_while_roaming(self) -> Optional[bool]:
        """Gets the cellularBlockGlobalBackgroundFetchWhileRoaming property"""
        return self.properties.get("cellularBlockGlobalBackgroundFetchWhileRoaming", None)

    @property
    def cellular_block_per_app_data_modification(self) -> Optional[bool]:
        """Gets the cellularBlockPerAppDataModification property"""
        return self.properties.get("cellularBlockPerAppDataModification", None)

    @property
    def cellular_block_personal_hotspot(self) -> Optional[bool]:
        """Gets the cellularBlockPersonalHotspot property"""
        return self.properties.get("cellularBlockPersonalHotspot", None)

    @property
    def cellular_block_voice_roaming(self) -> Optional[bool]:
        """Gets the cellularBlockVoiceRoaming property"""
        return self.properties.get("cellularBlockVoiceRoaming", None)

    @property
    def certificates_block_untrusted_tls_certificates(self) -> Optional[bool]:
        """Gets the certificatesBlockUntrustedTlsCertificates property"""
        return self.properties.get("certificatesBlockUntrustedTlsCertificates", None)

    @property
    def classroom_app_block_remote_screen_observation(self) -> Optional[bool]:
        """Gets the classroomAppBlockRemoteScreenObservation property"""
        return self.properties.get("classroomAppBlockRemoteScreenObservation", None)

    @property
    def classroom_app_force_unprompted_screen_observation(self) -> Optional[bool]:
        """Gets the classroomAppForceUnpromptedScreenObservation property"""
        return self.properties.get("classroomAppForceUnpromptedScreenObservation", None)

    @property
    def compliant_app_list_type(self) -> AppListType:
        """Gets the compliantAppListType property"""
        from office365.intune.devices.configurations.applisttype import AppListType

        return self.properties.get("compliantAppListType", AppListType.none)

    @property
    def compliant_apps_list(self) -> ClientValueCollection[AppListItem]:
        """Gets the compliantAppsList property"""
        from office365.intune.devices.management.mobileapps.app_list_item import AppListItem

        return self.properties.get("compliantAppsList", ClientValueCollection[AppListItem](AppListItem))

    @property
    def configuration_profile_block_changes(self) -> Optional[bool]:
        """Gets the configurationProfileBlockChanges property"""
        return self.properties.get("configurationProfileBlockChanges", None)

    @property
    def definition_lookup_blocked(self) -> Optional[bool]:
        """Gets the definitionLookupBlocked property"""
        return self.properties.get("definitionLookupBlocked", None)

    @property
    def device_block_enable_restrictions(self) -> Optional[bool]:
        """Gets the deviceBlockEnableRestrictions property"""
        return self.properties.get("deviceBlockEnableRestrictions", None)

    @property
    def device_block_erase_content_and_settings(self) -> Optional[bool]:
        """Gets the deviceBlockEraseContentAndSettings property"""
        return self.properties.get("deviceBlockEraseContentAndSettings", None)

    @property
    def device_block_name_modification(self) -> Optional[bool]:
        """Gets the deviceBlockNameModification property"""
        return self.properties.get("deviceBlockNameModification", None)

    @property
    def diagnostic_data_block_submission(self) -> Optional[bool]:
        """Gets the diagnosticDataBlockSubmission property"""
        return self.properties.get("diagnosticDataBlockSubmission", None)

    @property
    def diagnostic_data_block_submission_modification(self) -> Optional[bool]:
        """Gets the diagnosticDataBlockSubmissionModification property"""
        return self.properties.get("diagnosticDataBlockSubmissionModification", None)

    @property
    def documents_block_managed_documents_in_unmanaged_apps(self) -> Optional[bool]:
        """Gets the documentsBlockManagedDocumentsInUnmanagedApps property"""
        return self.properties.get("documentsBlockManagedDocumentsInUnmanagedApps", None)

    @property
    def documents_block_unmanaged_documents_in_managed_apps(self) -> Optional[bool]:
        """Gets the documentsBlockUnmanagedDocumentsInManagedApps property"""
        return self.properties.get("documentsBlockUnmanagedDocumentsInManagedApps", None)

    @property
    def email_in_domain_suffixes(self) -> StringCollection:
        """Gets the emailInDomainSuffixes property"""
        return self.properties.get("emailInDomainSuffixes", StringCollection())

    @property
    def enterprise_app_block_trust(self) -> Optional[bool]:
        """Gets the enterpriseAppBlockTrust property"""
        return self.properties.get("enterpriseAppBlockTrust", None)

    @property
    def enterprise_app_block_trust_modification(self) -> Optional[bool]:
        """Gets the enterpriseAppBlockTrustModification property"""
        return self.properties.get("enterpriseAppBlockTrustModification", None)

    @property
    def face_time_blocked(self) -> Optional[bool]:
        """Gets the faceTimeBlocked property"""
        return self.properties.get("faceTimeBlocked", None)

    @property
    def find_my_friends_blocked(self) -> Optional[bool]:
        """Gets the findMyFriendsBlocked property"""
        return self.properties.get("findMyFriendsBlocked", None)

    @property
    def game_center_blocked(self) -> Optional[bool]:
        """Gets the gameCenterBlocked property"""
        return self.properties.get("gameCenterBlocked", None)

    @property
    def gaming_block_game_center_friends(self) -> Optional[bool]:
        """Gets the gamingBlockGameCenterFriends property"""
        return self.properties.get("gamingBlockGameCenterFriends", None)

    @property
    def gaming_block_multiplayer(self) -> Optional[bool]:
        """Gets the gamingBlockMultiplayer property"""
        return self.properties.get("gamingBlockMultiplayer", None)

    @property
    def host_pairing_blocked(self) -> Optional[bool]:
        """Gets the hostPairingBlocked property"""
        return self.properties.get("hostPairingBlocked", None)

    @property
    def ibooks_store_blocked(self) -> Optional[bool]:
        """Gets the iBooksStoreBlocked property"""
        return self.properties.get("iBooksStoreBlocked", None)

    @property
    def ibooks_store_block_erotica(self) -> Optional[bool]:
        """Gets the iBooksStoreBlockErotica property"""
        return self.properties.get("iBooksStoreBlockErotica", None)

    @property
    def icloud_block_activity_continuation(self) -> Optional[bool]:
        """Gets the iCloudBlockActivityContinuation property"""
        return self.properties.get("iCloudBlockActivityContinuation", None)

    @property
    def icloud_block_backup(self) -> Optional[bool]:
        """Gets the iCloudBlockBackup property"""
        return self.properties.get("iCloudBlockBackup", None)

    @property
    def icloud_block_document_sync(self) -> Optional[bool]:
        """Gets the iCloudBlockDocumentSync property"""
        return self.properties.get("iCloudBlockDocumentSync", None)

    @property
    def icloud_block_managed_apps_sync(self) -> Optional[bool]:
        """Gets the iCloudBlockManagedAppsSync property"""
        return self.properties.get("iCloudBlockManagedAppsSync", None)

    @property
    def icloud_block_photo_library(self) -> Optional[bool]:
        """Gets the iCloudBlockPhotoLibrary property"""
        return self.properties.get("iCloudBlockPhotoLibrary", None)

    @property
    def icloud_block_photo_stream_sync(self) -> Optional[bool]:
        """Gets the iCloudBlockPhotoStreamSync property"""
        return self.properties.get("iCloudBlockPhotoStreamSync", None)

    @property
    def icloud_block_shared_photo_stream(self) -> Optional[bool]:
        """Gets the iCloudBlockSharedPhotoStream property"""
        return self.properties.get("iCloudBlockSharedPhotoStream", None)

    @property
    def icloud_require_encrypted_backup(self) -> Optional[bool]:
        """Gets the iCloudRequireEncryptedBackup property"""
        return self.properties.get("iCloudRequireEncryptedBackup", None)

    @property
    def itunes_block_explicit_content(self) -> Optional[bool]:
        """Gets the iTunesBlockExplicitContent property"""
        return self.properties.get("iTunesBlockExplicitContent", None)

    @property
    def itunes_block_music_service(self) -> Optional[bool]:
        """Gets the iTunesBlockMusicService property"""
        return self.properties.get("iTunesBlockMusicService", None)

    @property
    def itunes_block_radio(self) -> Optional[bool]:
        """Gets the iTunesBlockRadio property"""
        return self.properties.get("iTunesBlockRadio", None)

    @property
    def keyboard_block_auto_correct(self) -> Optional[bool]:
        """Gets the keyboardBlockAutoCorrect property"""
        return self.properties.get("keyboardBlockAutoCorrect", None)

    @property
    def keyboard_block_dictation(self) -> Optional[bool]:
        """Gets the keyboardBlockDictation property"""
        return self.properties.get("keyboardBlockDictation", None)

    @property
    def keyboard_block_predictive(self) -> Optional[bool]:
        """Gets the keyboardBlockPredictive property"""
        return self.properties.get("keyboardBlockPredictive", None)

    @property
    def keyboard_block_shortcuts(self) -> Optional[bool]:
        """Gets the keyboardBlockShortcuts property"""
        return self.properties.get("keyboardBlockShortcuts", None)

    @property
    def keyboard_block_spell_check(self) -> Optional[bool]:
        """Gets the keyboardBlockSpellCheck property"""
        return self.properties.get("keyboardBlockSpellCheck", None)

    @property
    def kiosk_mode_allow_assistive_speak(self) -> Optional[bool]:
        """Gets the kioskModeAllowAssistiveSpeak property"""
        return self.properties.get("kioskModeAllowAssistiveSpeak", None)

    @property
    def kiosk_mode_allow_assistive_touch_settings(self) -> Optional[bool]:
        """Gets the kioskModeAllowAssistiveTouchSettings property"""
        return self.properties.get("kioskModeAllowAssistiveTouchSettings", None)

    @property
    def kiosk_mode_allow_auto_lock(self) -> Optional[bool]:
        """Gets the kioskModeAllowAutoLock property"""
        return self.properties.get("kioskModeAllowAutoLock", None)

    @property
    def kiosk_mode_allow_color_inversion_settings(self) -> Optional[bool]:
        """Gets the kioskModeAllowColorInversionSettings property"""
        return self.properties.get("kioskModeAllowColorInversionSettings", None)

    @property
    def kiosk_mode_allow_ringer_switch(self) -> Optional[bool]:
        """Gets the kioskModeAllowRingerSwitch property"""
        return self.properties.get("kioskModeAllowRingerSwitch", None)

    @property
    def kiosk_mode_allow_screen_rotation(self) -> Optional[bool]:
        """Gets the kioskModeAllowScreenRotation property"""
        return self.properties.get("kioskModeAllowScreenRotation", None)

    @property
    def kiosk_mode_allow_sleep_button(self) -> Optional[bool]:
        """Gets the kioskModeAllowSleepButton property"""
        return self.properties.get("kioskModeAllowSleepButton", None)

    @property
    def kiosk_mode_allow_touchscreen(self) -> Optional[bool]:
        """Gets the kioskModeAllowTouchscreen property"""
        return self.properties.get("kioskModeAllowTouchscreen", None)

    @property
    def kiosk_mode_allow_voice_over_settings(self) -> Optional[bool]:
        """Gets the kioskModeAllowVoiceOverSettings property"""
        return self.properties.get("kioskModeAllowVoiceOverSettings", None)

    @property
    def kiosk_mode_allow_volume_buttons(self) -> Optional[bool]:
        """Gets the kioskModeAllowVolumeButtons property"""
        return self.properties.get("kioskModeAllowVolumeButtons", None)

    @property
    def kiosk_mode_allow_zoom_settings(self) -> Optional[bool]:
        """Gets the kioskModeAllowZoomSettings property"""
        return self.properties.get("kioskModeAllowZoomSettings", None)

    @property
    def kiosk_mode_app_store_url(self) -> Optional[str]:
        """Gets the kioskModeAppStoreUrl property"""
        return self.properties.get("kioskModeAppStoreUrl", None)

    @property
    def kiosk_mode_built_in_app_id(self) -> Optional[str]:
        """Gets the kioskModeBuiltInAppId property"""
        return self.properties.get("kioskModeBuiltInAppId", None)

    @property
    def kiosk_mode_managed_app_id(self) -> Optional[str]:
        """Gets the kioskModeManagedAppId property"""
        return self.properties.get("kioskModeManagedAppId", None)

    @property
    def kiosk_mode_require_assistive_touch(self) -> Optional[bool]:
        """Gets the kioskModeRequireAssistiveTouch property"""
        return self.properties.get("kioskModeRequireAssistiveTouch", None)

    @property
    def kiosk_mode_require_color_inversion(self) -> Optional[bool]:
        """Gets the kioskModeRequireColorInversion property"""
        return self.properties.get("kioskModeRequireColorInversion", None)

    @property
    def kiosk_mode_require_mono_audio(self) -> Optional[bool]:
        """Gets the kioskModeRequireMonoAudio property"""
        return self.properties.get("kioskModeRequireMonoAudio", None)

    @property
    def kiosk_mode_require_voice_over(self) -> Optional[bool]:
        """Gets the kioskModeRequireVoiceOver property"""
        return self.properties.get("kioskModeRequireVoiceOver", None)

    @property
    def kiosk_mode_require_zoom(self) -> Optional[bool]:
        """Gets the kioskModeRequireZoom property"""
        return self.properties.get("kioskModeRequireZoom", None)

    @property
    def lock_screen_block_control_center(self) -> Optional[bool]:
        """Gets the lockScreenBlockControlCenter property"""
        return self.properties.get("lockScreenBlockControlCenter", None)

    @property
    def lock_screen_block_notification_view(self) -> Optional[bool]:
        """Gets the lockScreenBlockNotificationView property"""
        return self.properties.get("lockScreenBlockNotificationView", None)

    @property
    def lock_screen_block_passbook(self) -> Optional[bool]:
        """Gets the lockScreenBlockPassbook property"""
        return self.properties.get("lockScreenBlockPassbook", None)

    @property
    def lock_screen_block_today_view(self) -> Optional[bool]:
        """Gets the lockScreenBlockTodayView property"""
        return self.properties.get("lockScreenBlockTodayView", None)

    @property
    def media_content_rating_apps(self) -> RatingAppsType:
        """Gets the mediaContentRatingApps property"""
        from office365.intune.devices.configurations.ios.general.ratingappstype import (
            RatingAppsType,
        )

        return self.properties.get("mediaContentRatingApps", RatingAppsType.allAllowed)

    @property
    def media_content_rating_australia(self) -> MediaContentRatingAustralia:
        """Gets the mediaContentRatingAustralia property"""
        from office365.intune.devices.configurations.media_content_rating_australia import (
            MediaContentRatingAustralia,
        )

        return self.properties.get("mediaContentRatingAustralia", MediaContentRatingAustralia())

    @property
    def media_content_rating_canada(self) -> MediaContentRatingCanada:
        """Gets the mediaContentRatingCanada property"""
        from office365.intune.devices.configurations.media_content_rating_canada import (
            MediaContentRatingCanada,
        )

        return self.properties.get("mediaContentRatingCanada", MediaContentRatingCanada())

    @property
    def media_content_rating_france(self) -> MediaContentRatingFrance:
        """Gets the mediaContentRatingFrance property"""
        from office365.intune.devices.configurations.media_content_rating_france import (
            MediaContentRatingFrance,
        )

        return self.properties.get("mediaContentRatingFrance", MediaContentRatingFrance())

    @property
    def media_content_rating_germany(self) -> MediaContentRatingGermany:
        """Gets the mediaContentRatingGermany property"""
        from office365.intune.devices.configurations.media_content_rating_germany import (
            MediaContentRatingGermany,
        )

        return self.properties.get("mediaContentRatingGermany", MediaContentRatingGermany())

    @property
    def media_content_rating_ireland(self) -> MediaContentRatingIreland:
        """Gets the mediaContentRatingIreland property"""
        from office365.intune.devices.configurations.media_content_rating_ireland import (
            MediaContentRatingIreland,
        )

        return self.properties.get("mediaContentRatingIreland", MediaContentRatingIreland())

    @property
    def media_content_rating_japan(self) -> MediaContentRatingJapan:
        """Gets the mediaContentRatingJapan property"""
        from office365.intune.devices.configurations.media_content_rating_japan import MediaContentRatingJapan

        return self.properties.get("mediaContentRatingJapan", MediaContentRatingJapan())

    @property
    def media_content_rating_new_zealand(self) -> MediaContentRatingNewZealand:
        """Gets the mediaContentRatingNewZealand property"""
        from office365.intune.devices.configurations.media_content_rating_new_zealand import (
            MediaContentRatingNewZealand,
        )

        return self.properties.get("mediaContentRatingNewZealand", MediaContentRatingNewZealand())

    @property
    def media_content_rating_united_kingdom(self) -> MediaContentRatingUnitedKingdom:
        """Gets the mediaContentRatingUnitedKingdom property"""
        from office365.intune.devices.configurations.media_content_rating_united_kingdom import (
            MediaContentRatingUnitedKingdom,
        )

        return self.properties.get("mediaContentRatingUnitedKingdom", MediaContentRatingUnitedKingdom())

    @property
    def media_content_rating_united_states(self) -> MediaContentRatingUnitedStates:
        """Gets the mediaContentRatingUnitedStates property"""
        from office365.intune.devices.configurations.media_content_rating_united_states import (
            MediaContentRatingUnitedStates,
        )

        return self.properties.get("mediaContentRatingUnitedStates", MediaContentRatingUnitedStates())

    @property
    def messages_blocked(self) -> Optional[bool]:
        """Gets the messagesBlocked property"""
        return self.properties.get("messagesBlocked", None)

    @property
    def network_usage_rules(self) -> ClientValueCollection[IosNetworkUsageRule]:
        """Gets the networkUsageRules property"""
        from office365.intune.devices.configurations.ios.network_usage_rule import (
            IosNetworkUsageRule,
        )

        return self.properties.get("networkUsageRules", ClientValueCollection[IosNetworkUsageRule](IosNetworkUsageRule))

    @property
    def notifications_block_settings_modification(self) -> Optional[bool]:
        """Gets the notificationsBlockSettingsModification property"""
        return self.properties.get("notificationsBlockSettingsModification", None)

    @property
    def passcode_block_fingerprint_modification(self) -> Optional[bool]:
        """Gets the passcodeBlockFingerprintModification property"""
        return self.properties.get("passcodeBlockFingerprintModification", None)

    @property
    def passcode_block_fingerprint_unlock(self) -> Optional[bool]:
        """Gets the passcodeBlockFingerprintUnlock property"""
        return self.properties.get("passcodeBlockFingerprintUnlock", None)

    @property
    def passcode_block_modification(self) -> Optional[bool]:
        """Gets the passcodeBlockModification property"""
        return self.properties.get("passcodeBlockModification", None)

    @property
    def passcode_block_simple(self) -> Optional[bool]:
        """Gets the passcodeBlockSimple property"""
        return self.properties.get("passcodeBlockSimple", None)

    @property
    def passcode_expiration_days(self) -> Optional[int]:
        """Gets the passcodeExpirationDays property"""
        return self.properties.get("passcodeExpirationDays", None)

    @property
    def passcode_minimum_character_set_count(self) -> Optional[int]:
        """Gets the passcodeMinimumCharacterSetCount property"""
        return self.properties.get("passcodeMinimumCharacterSetCount", None)

    @property
    def passcode_minimum_length(self) -> Optional[int]:
        """Gets the passcodeMinimumLength property"""
        return self.properties.get("passcodeMinimumLength", None)

    @property
    def passcode_minutes_of_inactivity_before_lock(self) -> Optional[int]:
        """Gets the passcodeMinutesOfInactivityBeforeLock property"""
        return self.properties.get("passcodeMinutesOfInactivityBeforeLock", None)

    @property
    def passcode_minutes_of_inactivity_before_screen_timeout(self) -> Optional[int]:
        """Gets the passcodeMinutesOfInactivityBeforeScreenTimeout property"""
        return self.properties.get("passcodeMinutesOfInactivityBeforeScreenTimeout", None)

    @property
    def passcode_previous_passcode_block_count(self) -> Optional[int]:
        """Gets the passcodePreviousPasscodeBlockCount property"""
        return self.properties.get("passcodePreviousPasscodeBlockCount", None)

    @property
    def passcode_required(self) -> Optional[bool]:
        """Gets the passcodeRequired property"""
        return self.properties.get("passcodeRequired", None)

    @property
    def passcode_required_type(self) -> RequiredPasswordType:
        """Gets the passcodeRequiredType property"""
        from office365.intune.devices.compliance.requiredpasswordtype import (
            RequiredPasswordType,
        )

        return self.properties.get("passcodeRequiredType", RequiredPasswordType.deviceDefault)

    @property
    def passcode_sign_in_failure_count_before_wipe(self) -> Optional[int]:
        """Gets the passcodeSignInFailureCountBeforeWipe property"""
        return self.properties.get("passcodeSignInFailureCountBeforeWipe", None)

    @property
    def podcasts_blocked(self) -> Optional[bool]:
        """Gets the podcastsBlocked property"""
        return self.properties.get("podcastsBlocked", None)

    @property
    def safari_block_autofill(self) -> Optional[bool]:
        """Gets the safariBlockAutofill property"""
        return self.properties.get("safariBlockAutofill", None)

    @property
    def safari_blocked(self) -> Optional[bool]:
        """Gets the safariBlocked property"""
        return self.properties.get("safariBlocked", None)

    @property
    def safari_block_java_script(self) -> Optional[bool]:
        """Gets the safariBlockJavaScript property"""
        return self.properties.get("safariBlockJavaScript", None)

    @property
    def safari_block_popups(self) -> Optional[bool]:
        """Gets the safariBlockPopups property"""
        return self.properties.get("safariBlockPopups", None)

    @property
    def safari_cookie_settings(self) -> WebBrowserCookieSettings:
        """Gets the safariCookieSettings property"""
        from office365.intune.devices.configurations.webbrowsercookiesettings import (
            WebBrowserCookieSettings,
        )

        return self.properties.get("safariCookieSettings", WebBrowserCookieSettings.browserDefault)

    @property
    def safari_managed_domains(self) -> StringCollection:
        """Gets the safariManagedDomains property"""
        return self.properties.get("safariManagedDomains", StringCollection())

    @property
    def safari_password_auto_fill_domains(self) -> StringCollection:
        """Gets the safariPasswordAutoFillDomains property"""
        return self.properties.get("safariPasswordAutoFillDomains", StringCollection())

    @property
    def safari_require_fraud_warning(self) -> Optional[bool]:
        """Gets the safariRequireFraudWarning property"""
        return self.properties.get("safariRequireFraudWarning", None)

    @property
    def screen_capture_blocked(self) -> Optional[bool]:
        """Gets the screenCaptureBlocked property"""
        return self.properties.get("screenCaptureBlocked", None)

    @property
    def siri_blocked(self) -> Optional[bool]:
        """Gets the siriBlocked property"""
        return self.properties.get("siriBlocked", None)

    @property
    def siri_blocked_when_locked(self) -> Optional[bool]:
        """Gets the siriBlockedWhenLocked property"""
        return self.properties.get("siriBlockedWhenLocked", None)

    @property
    def siri_block_user_generated_content(self) -> Optional[bool]:
        """Gets the siriBlockUserGeneratedContent property"""
        return self.properties.get("siriBlockUserGeneratedContent", None)

    @property
    def siri_require_profanity_filter(self) -> Optional[bool]:
        """Gets the siriRequireProfanityFilter property"""
        return self.properties.get("siriRequireProfanityFilter", None)

    @property
    def spotlight_block_internet_results(self) -> Optional[bool]:
        """Gets the spotlightBlockInternetResults property"""
        return self.properties.get("spotlightBlockInternetResults", None)

    @property
    def voice_dialing_blocked(self) -> Optional[bool]:
        """Gets the voiceDialingBlocked property"""
        return self.properties.get("voiceDialingBlocked", None)

    @property
    def wallpaper_block_modification(self) -> Optional[bool]:
        """Gets the wallpaperBlockModification property"""
        return self.properties.get("wallpaperBlockModification", None)

    @property
    def wi_fi_connect_only_to_configured_networks(self) -> Optional[bool]:
        """Gets the wiFiConnectOnlyToConfiguredNetworks property"""
        return self.properties.get("wiFiConnectOnlyToConfiguredNetworks", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IosGeneralDeviceConfiguration"
