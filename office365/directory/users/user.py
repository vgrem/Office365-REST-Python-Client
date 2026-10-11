from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

from typing_extensions import Self

from office365.communications.onlinemeetings.collection import OnlineMeetingCollection
from office365.communications.presences.presence import Presence
from office365.delta_collection import DeltaCollection
from office365.directory.applications.roles.assignment_collection import (
    AppRoleAssignmentCollection,
)
from office365.directory.audit.signins.activity import SignInActivity
from office365.directory.authentication.authentication import Authentication
from office365.directory.extensions.extension import Extension
from office365.directory.extensions.open_type import OpenTypeExtension
from office365.directory.groups.on_premises_sync_behavior import OnPremisesSyncBehavior
from office365.directory.identities.object_identity import ObjectIdentity
from office365.directory.identitygovernance.termsofuse.agreement_acceptance import (
    AgreementAcceptance,
)
from office365.directory.insights.office_graph import OfficeGraphInsights
from office365.directory.licenses.assigned_license import AssignedLicense
from office365.directory.licenses.assigned_plan import AssignedPlan
from office365.directory.licenses.assignment_state import LicenseAssignmentState
from office365.directory.licenses.details import LicenseDetails
from office365.directory.objects.collection import DirectoryObjectCollection
from office365.directory.objects.customsecurityattributevalue import (
    CustomSecurityAttributeValue,
)
from office365.directory.objects.object import DirectoryObject
from office365.directory.objects.onpremisesprovisioningerror import (
    OnPremisesProvisioningError,
)
from office365.directory.objects.serviceprovisioningerror import (
    ServiceProvisioningError,
)
from office365.directory.permissions.grants.oauth2 import OAuth2PermissionGrant
from office365.directory.permissions.grants.resource_specific import (
    ResourceSpecificPermissionGrant,
)
from office365.directory.permissions.require_permission import require_permission
from office365.directory.permissions.scoped_role_membership import ScopedRoleMembership
from office365.directory.profile_photo import ProfilePhoto
from office365.directory.rolemanagement.roles.role import DirectoryRole
from office365.directory.users.activities.collection import UserActivityCollection
from office365.directory.users.authorizationinfo import AuthorizationInfo
from office365.directory.users.employeeorgdata import EmployeeOrgData
from office365.directory.users.onpremisesextensionattributes import (
    OnPremisesExtensionAttributes,
)
from office365.directory.users.password_profile import PasswordProfile
from office365.directory.users.provisioned_plan import ProvisionedPlan
from office365.directory.users.settings import UserSettings
from office365.entity_collection import EntityCollection
from office365.intune.devices.data import DeviceAndAppManagementData
from office365.intune.devices.management.managed.app.diagnostic_status import (
    ManagedAppDiagnosticStatus,
)
from office365.intune.devices.management.managed.app.registration import (
    ManagedAppRegistration,
)
from office365.intune.devices.management.managed.managed import ManagedDevice
from office365.intune.organizations.contact import OrgContact
from office365.intune.policies.managed_app import ManagedAppPolicy
from office365.intune.print.user_print import UserPrint
from office365.onedrive.drives.drive import Drive
from office365.onedrive.sites.site import Site
from office365.onenote.onenote import Onenote
from office365.outlook.calendar.attendees.base import AttendeeBase
from office365.outlook.calendar.calendar import Calendar
from office365.outlook.calendar.collection import CalendarCollection
from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone
from office365.outlook.calendar.email_address import EmailAddress
from office365.outlook.calendar.events.event import Event
from office365.outlook.calendar.events.reminder import Reminder
from office365.outlook.calendar.group import CalendarGroup
from office365.outlook.calendar.location_constraint import LocationConstraint
from office365.outlook.calendar.meetingtimes.suggestions_result import (
    MeetingTimeSuggestionsResult,
)
from office365.outlook.calendar.meetingtimes.time_constraint import TimeConstraint
from office365.outlook.contacts.collection import ContactCollection
from office365.outlook.contacts.folders.collection import ContactFolderCollection
from office365.outlook.convert_id_result import ConvertIdResult
from office365.outlook.exchangeidformat import ExchangeIdFormat
from office365.outlook.mail.folders.collection import MailFolderCollection
from office365.outlook.mail.item_body import ItemBody
from office365.outlook.mail.mailbox_settings import MailboxSettings
from office365.outlook.mail.messages.collection import MessageCollection
from office365.outlook.mail.messages.message import Message
from office365.outlook.mail.recipient import Recipient
from office365.outlook.mail.tips.tips import MailTips
from office365.outlook.person import Person
from office365.outlook.user import OutlookUser
from office365.planner.user import PlannerUser
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.v4.entity import EntityPath
from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.runtime.queries.delete_entity import DeleteEntityQuery
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.duration import Duration
from office365.runtime.types.odata_property import odata
from office365.teams.chats.collection import ChatCollection
from office365.teams.collection import TeamCollection
from office365.teams.internal.paths.joined_teams import JoinedTeamsPath
from office365.teams.teamwork.shiftmanagement.user_solution_root import UserSolutionRoot
from office365.teams.teamwork.user import UserTeamwork
from office365.teams.viva.employee_experience_user import EmployeeExperienceUser
from office365.todo.todo import Todo

if TYPE_CHECKING:
    from office365.communications.adhoc_call import AdhocCall
    from office365.directory.identitygovernance.user_data_security_and_governance import (
        UserDataSecurityAndGovernance,
    )
    from office365.directory.users.inference_classification import (
        InferenceClassification,
    )
    from office365.directory.users.note import Note
    from office365.intune.devices.cloud_pc import CloudPC
    from office365.intune.devices.management_troubleshooting_event import (
        DeviceManagementTroubleshootingEvent,
    )
    from office365.security.cloud_clipboard_root import CloudClipboardRoot


class User(DirectoryObject):
    """Represents an Azure AD user account. Inherits from directoryObject."""

    def __repr__(self):
        return self.user_principal_name or self.id or self.entity_type_name

    def enable_automatic_replies_setting(
        self,
        status: str,
        scheduled_start_datetime: datetime,
        scheduled_end_datetime: datetime,
        internal_reply_message: str | None = None,
        external_reply_message: str | None = None,
    ) -> Self:
        """
        Enable, configure, automatic replies (notify people automatically upon receipt of their email)

        """
        from office365.outlook.mail.automaticreplies.setting import (
            AutomaticRepliesSetting,
        )

        setting = AutomaticRepliesSetting(
            status=status,
            scheduledStartDateTime=DateTimeTimeZone.parse(scheduled_start_datetime),
            scheduledEndDateTime=DateTimeTimeZone.parse(scheduled_end_datetime),
            internalReplyMessage=internal_reply_message,
            externalReplyMessage=external_reply_message,
        )

        def _construct_request(request):
            payload = {"automaticRepliesSetting": setting.to_json()}
            request.data = payload
            request.url += "/mailboxSettings"

        self.update().before_execute(_construct_request)
        return self

    def disable_automatic_replies_setting(self, clear_all=False) -> Self:
        """Disable automatic replies (notify people automatically upon receipt of their email)

        Args:
            clear_all (bool): If true, clear all automatic replies settings
        """
        from office365.outlook.mail.automaticreplies.setting import (
            AutomaticRepliesSetting,
        )

        setting = AutomaticRepliesSetting(status="disabled")

        def _construct_request(request):
            payload = {"automaticRepliesSetting": setting.to_json()}
            request.data = payload
            request.url += "/mailboxSettings"

        self.update().before_execute(_construct_request)
        return self

    @require_permission(delegated=["User.ReadWrite", "User.ReadWrite.All"], application=["User.ReadWrite.All"])
    def add_extension(self, name: str) -> OpenTypeExtension:
        """Creates an open extension (openTypeExtension object) and add custom properties in a new or existing instance
        of a User resource.

        Args:
            name (str):
        """
        from office365.directory.extensions.open_type import OpenTypeExtension

        return_type = OpenTypeExtension(self.context)
        return_type.set_property("extensionName", name)
        self.extensions.add_child(return_type)
        qry = CreateEntityQuery(self.extensions, return_type, return_type)
        self.context.add_query(qry)
        return return_type

    @require_permission(delegated=["User.ReadWrite.All"], application=["User.ReadWrite.All"])
    def assign_license(
        self, add_licenses: list[str] | list[AssignedLicense], remove_licenses: list[str] | None = None
    ) -> Self:
        """Add or remove licenses on the user.

        Args:
            remove_licenses (list[str]): A collection of skuIds that identify the licenses to remove.
            add_licenses (list[AssignedLicense]): A collection of assignedLicense objects that specify the
              licenses to add.
        """
        from office365.directory.licenses.assigned_license import AssignedLicense

        params = {
            "addLicenses": ClientValueCollection(
                AssignedLicense,
                [
                    AssignedLicense(skuId=sku_id) if not isinstance(sku_id, AssignedLicense) else sku_id
                    for sku_id in add_licenses
                ],
            ),
            "removeLicenses": StringCollection(remove_licenses or []),
        }
        qry = ServiceOperationQuery(self, "assignLicense", None, params, None, self)
        self.context.add_query(qry)
        return self

    @require_permission(delegated=["User.ReadWrite.All"], application=["User.ReadWrite.All"])
    def assign_manager(self, user: str | User | OrgContact) -> DirectoryObject:
        """Assign a user's manager.

        Args:
            user (str or User or OrgContact): User or office365.intune.organizations.contact.OrgContact or identifier
        """

        def _construct_request(request: RequestOptions) -> None:
            request.method = HttpMethod.Put
            request.set_header("Content-Type", "application/json")
            request.set_header("Accept", "application/json")
            request.data = json.dumps(request.data)

        def _assign_manager(user_id: str | None) -> None:
            if user_id is None:
                return
            payload = {"@odata.id": f"{self.context.users.resource_url}/{user_id}"}
            qry = ServiceOperationQuery(self.manager, "$ref", None, payload)
            self.context.add_query(qry).before_execute(_construct_request)

        if isinstance(user, (User, OrgContact)):
            user.ensure_property("id").after_execute(lambda _: _assign_manager(user.id))
        else:
            _assign_manager(str(user))
        return self.manager

    def remove_manager(self) -> Self:
        """Remove a user's manager."""
        qry = ServiceOperationQuery(self.manager, "$ref")

        def _construct_request(request: RequestOptions) -> None:
            request.method = HttpMethod.Delete

        self.context.add_query(qry).before_execute(_construct_request)
        return self

    @require_permission(delegated=["User.ReadWrite"], application=["User.ReadWrite.All"])
    def change_password(self, current_password: str, new_password: str) -> Self:
        """Enable the user to update their password. Any user can update their password without belonging
        to any administrator role.

        Args:
            current_password (str): Your current password.
            new_password (str): Your new password.
        """
        qry = ServiceOperationQuery(
            self, "changePassword", None, {"currentPassword": current_password, "newPassword": new_password}
        )
        self.context.add_query(qry)
        return self

    def follow_site(self, site: str | Site) -> Self:
        """follow a site"""

        def _follow_site(site_id: str | None) -> None:
            if site_id is None:
                return
            payload = {"value": [{"id": site_id}]}
            query = ServiceOperationQuery(self.followed_sites, "add", None, payload)
            self.context.add_query(query)

        if isinstance(site, Site):
            site.ensure_property("id").after_execute(lambda _: _follow_site(site.id))
        else:
            _follow_site(str(site))
        return self

    def unfollow_site(self, site: str | Site) -> Self:
        """Unfollow a user's site or multiple sites."""

        def _unfollow_site(site_id: str | None) -> None:
            if site_id is None:
                return
            payload = {"value": [{"id": site_id}]}
            query = ServiceOperationQuery(self.followed_sites, "remove", None, payload)
            self.context.add_query(query)

        if isinstance(site, Site):
            site.ensure_property("id").after_execute(lambda _: _unfollow_site(site.id))
        else:
            _unfollow_site(str(site))
        return self

    def get_directory_roles(self) -> EntityCollection[DirectoryRole]:
        """
        Fetches all directory roles assigned to the user.

        Returns:
            EntityCollection[DirectoryRole]: The directory roles the user is a member of.

        Docs:
            https://learn.microsoft.com/en-us/graph/api/directoryrole-list?view=graph-rest-1.0
        """
        return_type = EntityCollection(self.context, DirectoryRole)

        def _directory_roles_loaded(directory_roles: DeltaCollection[DirectoryRole]):
            role_template_map = {role.role_template_id: role for role in directory_roles}

            def _memberships_loaded(memberships: EntityCollection[DirectoryObject]):
                for item in memberships:
                    role_id = item.properties.get("roleTemplateId")
                    if role_id in role_template_map:
                        return_type.add_child(role_template_map[role_id])

            self.member_of.get().after_execute(_memberships_loaded)

        self.context.directory_roles.get().after_execute(_directory_roles_loaded)
        return return_type

    @require_permission(delegated=["Mail.Read", "Mail.ReadWrite"], application=["Mail.Read", "Mail.ReadWrite"])
    def get_mail_tips(
        self, email_addresses: list[str], mail_tips_options: str | None = None
    ) -> ClientResult[ClientValueCollection[MailTips]]:
        """Get the MailTips of one or more recipients as available to the signed-in user.

        Args:
            email_addresses (list[str]): A collection of SMTP addresses of recipients to get MailTips for.
            mail_tips_options (str): A enumeration of flags that represents the requested mailtips.
              Possible values are: automaticReplies, customMailTip, deliveryRestriction, externalMemberCount,
              mailboxFullStatus, maxMessageSize, moderationStatus, recipientScope, recipientSuggestions,
              and totalMemberCount.
        """
        return_type = ClientResult(self.context, ClientValueCollection(MailTips))
        payload = {"EmailAddresses": StringCollection(email_addresses), "MailTipsOptions": mail_tips_options}
        qry = ServiceOperationQuery(self, "getMailTips", None, payload)
        self.context.add_query(qry)
        return return_type

    def get_my_site(self) -> Site:
        """Gets user's site"""
        return_type = Site(self.context)

        def _loaded():
            return_type.set_property("webUrl", self.my_site)

        self.ensure_property("mySite").after_execute(lambda _: _loaded())
        return return_type

    @require_permission(delegated=["Mail.Send"], application=["Mail.Send"])
    def send_mail(
        self,
        subject: str,
        body: str | ItemBody,
        to_recipients: list[str],
        cc_recipients: list[str] | None = None,
        bcc_recipients: list[str] | None = None,
        reply_to: list[str] | None = None,
        save_to_sent_items: bool = False,
        body_type: str = "Text",
    ) -> Message:
        """Send a new message on the fly

        Args:
            subject (str): The subject of the message.
            body (str): The body of the message. It can be in HTML or text format
            to_recipients (list[str]): The To: recipients for the message.
            cc_recipients (list[str]): The CC: recipients for the message.
            bcc_recipients (list[str]): The BCC: recipients for the message.
            reply_to (list[str]): The Reply-To: : recipients for the reply to the message.
            save_to_sent_items (bool): Indicates whether to save the message in Sent Items. Specify it only if the
              parameter is false; default is true
            body_type (str): The type of the message body. It can be "HTML" or "Text". Default is "Text".
        """
        return_type = Message(self.context)
        return_type.subject = subject
        return_type.body = (body, body_type)
        [return_type.to_recipients.add(Recipient.from_email(email)) for email in to_recipients]
        if bcc_recipients is not None:
            [return_type.bcc_recipients.add(Recipient.from_email(email)) for email in bcc_recipients]
        if cc_recipients is not None:
            [return_type.cc_recipients.add(Recipient.from_email(email)) for email in cc_recipients]
        if reply_to is not None:
            [return_type.reply_to.add(Recipient.from_email(email)) for email in reply_to]
        payload = {"message": return_type, "saveToSentItems": save_to_sent_items}
        qry = ServiceOperationQuery(self, "sendmail", None, payload)
        self.context.add_query(qry)
        return return_type

    def export_personal_data(self, storage_location) -> Self:
        """Submit a data policy operation request from a company administrator or an application to
        export an organizational user's data.

        If successful, this method returns a 202 Accepted response code.
        It does not return anything in the response body. The response contains the following response headers.

        Args:
            storage_location (str): This is a shared access signature (SAS) URL to an Azure Storage account, to where
              data should be exported.
        """
        qry = ServiceOperationQuery(self, "exportPersonalData", None, {"storage_location": storage_location})
        self.context.add_query(qry)
        return self

    def export_device_and_app_management_data(self) -> ClientResult[ClientValueCollection[DeviceAndAppManagementData]]:
        """"""
        return_type = ClientResult(self.context, ClientValueCollection(DeviceAndAppManagementData))
        qry = FunctionQuery(self, "exportDeviceAndAppManagementData", None, return_type)
        self.context.add_query(qry)
        return return_type

    def find_meeting_times(
        self,
        attendees: list[str] | None = None,
        location_constraint: LocationConstraint | None = None,
        time_constraint: TimeConstraint | None = None,
        meeting_duration: Duration | str | timedelta | None = None,
        max_candidates: int | None = None,
        is_organizer_optional: bool | None = None,
        return_suggestion_reasons: bool | None = None,
        minimum_attendee_percentage: float | None = None,
    ) -> ClientResult[MeetingTimeSuggestionsResult]:
        """Suggest meeting times and locations based on organizer and attendees availability, and time or location
        constraints specified as parameters.

        If findMeetingTimes cannot return any meeting suggestions, the response would indicate a reason in the
        emptySuggestionsReason property. Based on this value, you can better adjust the parameters
        and call findMeetingTimes again.

        The algorithm used to suggest meeting times and locations undergoes fine-tuning from time to time.
        In scenarios like test environments where the input parameters and calendar data remain static, expect
        that the suggested results may differ over time.

        Args:
            attendees (list[AttendeeBase] or None): A collection of attendees or resources for the meeting.
              Since findMeetingTimes assumes that any attendees who is a person is always required, specify required
              for a person and resource for a resource in the corresponding type property. An empty collection causes
              findMeetingTimes to look for free time slots for only the organizer. Optional.
            location_constraint (office365.outlook.calendar.location_constraint.LocationConstraint or None):
              The organizer's requirements about the meeting location, such as whether a suggestion for a meeting
              location is required, or there are specific locations only where the meeting can take place. Optional.
            time_constraint (TimeConstraint): Any time restrictions for a meeting, which can include the nature of
              the meeting (activityDomain property) and possible meeting time periods (timeSlots property).
              findMeetingTimes assumes activityDomain as work if you don't specify this parameter. Optional.
            meeting_duration (str): The length of the meeting, denoted in ISO8601 format. For example, 1 hour is
              denoted as 'PT1H', where 'P' is the duration designator, 'T' is the time designator, and 'H' is the
              hour designator. Use M to indicate minutes for the duration; for example, 2 hours and 30 minutes would
              be 'PT2H30M'. If no meeting duration is specified, findMeetingTimes uses the default of 30 minutes.
            max_candidates (int): The maximum number of meeting time suggestions to be returned. Optional.
            is_organizer_optional (bool): Specify True if the organizer doesn't necessarily have to attend.
              The default is false. Optional
            return_suggestion_reasons (bool): Specify True to return a reason for each meeting suggestion in the
              suggestionReason property. The default is false to not return that property. Optional.
            minimum_attendee_percentage (float): The minimum required confidence for a time slot to be returned
              in the response. It is a % value ranging from 0 to 100. Optional.
        """
        if isinstance(meeting_duration, timedelta):
            meeting_duration = Duration.parse(meeting_duration)
        payload = {
            "attendees": ClientValueCollection(
                AttendeeBase, [AttendeeBase(emailAddress=EmailAddress(a)) for a in attendees or []]
            ),
            "locationConstraint": location_constraint,
            "timeConstraint": time_constraint,
            "meetingDuration": meeting_duration,
            "maxCandidates": max_candidates,
            "isOrganizerOptional": is_organizer_optional,
            "returnSuggestionReasons": return_suggestion_reasons,
            "minimumAttendeePercentage": minimum_attendee_percentage,
        }
        return_type = ClientResult(self.context, MeetingTimeSuggestionsResult())
        qry = ServiceOperationQuery(self, "findMeetingTimes", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_calendar_view(self, start_dt: datetime, end_dt: datetime) -> EntityCollection[Event]:
        """Get the occurrences, exceptions, and single instances of events in a calendar view defined by a time range,
        from the user's default calendar, or from some other calendar of the user's.

        Args:
            end_dt (datetime.datetime): The end date and time of the time range, represented in ISO 8601 format.
              For example, "2019-11-08T20:00:00-08:00".
            start_dt (datetime.datetime): The start date and time of the time range, represented in ISO 8601 format.
              For example, "2019-11-08T19:00:00-08:00".
        """
        return_type = EntityCollection(self.context, Event, ResourcePath("calendarView", self.resource_path))
        qry = ServiceOperationQuery(self, "calendarView", None, None, None, return_type)

        def _construct_request(request: RequestOptions) -> None:
            request.method = HttpMethod.Get
            request.url += f"?startDateTime={start_dt.isoformat()}&endDateTime={end_dt.isoformat()}"

        self.context.add_query(qry).before_execute(_construct_request)
        return return_type

    def get_reminder_view(self, start_dt: datetime, end_dt: datetime) -> ClientResult[ClientValueCollection[Reminder]]:
        """Get the occurrences, exceptions, and single instances of events in a calendar view defined by a time range,
        from the user's default calendar, or from some other calendar of the user's.

        Args:
            end_dt (datetime.datetime): The end date and time of the event for which the reminder is set up.
              The value is represented in ISO 8601 format, for example, "2015-11-08T20:00:00.0000000"..
            start_dt (datetime.datetime): The start date and time of the event for which the reminder is set up.
              The value is represented in ISO 8601 format, for example, "2015-11-08T19:00:00.0000000".
        """
        return_type = ClientResult(self.context, ClientValueCollection(Reminder))
        params = {"startDateTime": start_dt.isoformat(), "endDateTime": end_dt.isoformat()}
        qry = FunctionQuery(self, "reminderView", params, return_type)
        self.context.add_query(qry)
        return return_type

    def get_managed_app_diagnostic_statuses(self) -> ClientResult[ClientValueCollection[ManagedAppDiagnosticStatus]]:
        """Gets diagnostics validation status for a given user."""
        return_type = ClientResult(self.context, ClientValueCollection(ManagedAppDiagnosticStatus))
        qry = FunctionQuery(self, "getManagedAppDiagnosticStatuses", None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_managed_app_policies(self) -> EntityCollection[ManagedAppPolicy]:
        """Gets app restrictions for a given user."""
        return_type = EntityCollection(self.context, ManagedAppPolicy)
        qry = FunctionQuery(self, "getManagedAppPolicies", None, return_type)
        self.context.add_query(qry)
        return return_type

    @require_permission(delegated=["User.ReadWrite.All"], application=["User.ReadWrite.All"])
    def delete_object(self, permanent_delete: bool = False, *, ignore_missing: bool = False) -> Self:
        """Args:
        permanent_delete (bool): Permanently deletes the user from directory
        ignore_missing (bool): Treat deleting a missing user as success
        """
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self._tolerate_missing(ignore_missing)
        if self._parent_collection is not None:
            self._parent_collection.remove_child(self)
        if permanent_delete:
            assert self.id is not None
            deleted_user = self.context.directory.deleted_users[self.id]
            deleted_user.delete_object(ignore_missing=ignore_missing)
        return self

    @require_permission(delegated=["User.ReadWrite.All"], application=["User.ReadWrite.All"])
    def revoke_signin_sessions(self) -> ClientResult[bool]:
        """
        Invalidates all the refresh tokens issued to applications for a user
        (as well as session cookies in a user's browser), by resetting the signInSessionsValidFromDateTime user
        property to the current date-time. Typically, this operation is performed (by the user or an administrator)
        if the user has a lost or stolen device. This operation prevents access to the organization's data through
        applications on the device by requiring the user to sign in again to all applications that they have previously
        consented to, independent of device.
        """
        result = ClientResult[bool](self.context)
        qry = ServiceOperationQuery(self, "revokeSignInSessions", None, None, None, result)
        self.context.add_query(qry)
        return result

    def reprocess_license_assignment(self) -> User:
        """
        Reprocess all group-based license assignments for the user. To learn more about group-based licensing,
        see What is group-based licensing in Azure Active Directory. Also see Identify and resolve license assignment
        problems for a group in Azure Active Directory for more details.
        """
        return_type = User(self.context)
        qry = ServiceOperationQuery(self, "reprocessLicenseAssignment", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def remove_all_devices_from_management(self) -> Self:
        """
        Retire all devices from management for this user
        """
        qry = ServiceOperationQuery(self, "removeAllDevicesFromManagement")
        self.context.add_query(qry)
        return self

    def wipe_managed_app_registrations_by_device_tag(self, device_tag: str) -> Self:
        """Issues a wipe operation on an app registration with specified device tag.

        Args:
            device_tag (str): device tag
        """
        payload = {"deviceTag": device_tag}
        qry = ServiceOperationQuery(self, "wipeManagedAppRegistrationsByDeviceTag", None, payload)
        self.context.add_query(qry)
        return self

    def translate_exchange_ids(
        self,
        input_ids: list[str],
        source_id_type: ExchangeIdFormat | None = None,
        target_id_type: ExchangeIdFormat | None = None,
    ) -> ClientResult[ConvertIdResult]:
        """Translate identifiers of Outlook-related resources between formats.

        Args:
            input_ids (list[str]): A collection of identifiers to convert. All identifiers in the collection
              MUST have the same source ID type, and MUST be for items in the same mailbox.
              Maximum size of this collection is 1000 strings.
            source_id_type (str): The ID type of the identifiers in the InputIds parameter.
            target_id_type (str): The requested ID type to convert to.
        """
        return_type = ClientResult(self.context, ConvertIdResult())
        payload = {
            "InputIds": StringCollection(input_ids),
            "TargetIdType": target_id_type.name if target_id_type else None,
            "SourceIdType": source_id_type.name if source_id_type else None,
        }
        qry = ServiceOperationQuery(self, "translateExchangeIds", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def created_datetime(self) -> Optional[datetime]:
        """
        The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time.
        For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
        """
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def last_password_change_datetime(self) -> Optional[datetime]:
        """
        The time when this Azure AD user last changed their password.
        """
        return self.properties.get("lastPasswordChangeDateTime", datetime.min)

    @odata(name="createdObjects")
    @property
    def created_objects(self) -> DirectoryObjectCollection:
        """Directory objects created by this user."""
        return self.properties.get(
            "createdObjects", DirectoryObjectCollection(self.context, ResourcePath("createdObjects", self.resource_path))
        )

    @property
    def device_enrollment_limit(self) -> Optional[str]:
        """ """
        return self.properties.get("deviceEnrollmentLimit", None)

    @odata(name="signInActivity")
    @property
    def sign_in_activity(self) -> SignInActivity:
        """Get the last signed-in date and request ID of the sign-in for a given user. Read-only."""
        return self.properties.get("signInActivity", SignInActivity())

    @property
    def account_enabled(self) -> bool | None:
        """True if the account is enabled; otherwise, false. This property is required when a user is created."""
        return self.properties.get("accountEnabled", None)

    @property
    def age_group(self) -> str | None:
        """Gets the age group of the user"""
        return self.properties.get("ageGroup", None)

    @property
    def app_role_assignments(self) -> AppRoleAssignmentCollection:
        """Get the apps and app roles which this user has been assigned."""
        return self.properties.get(
            "appRoleAssignments",
            AppRoleAssignmentCollection(self.context, ResourcePath("appRoleAssignments", self.resource_path)),
        )

    @property
    def chats(self) -> ChatCollection:
        """The user's chats."""
        return self.properties.get("chats", ChatCollection(self.context, ResourcePath("chats", self.resource_path)))

    @property
    def display_name(self) -> Optional[str]:
        """The DisplayName property specifies the users's display name."""
        return self.properties.get("displayName", None)

    @property
    def given_name(self) -> Optional[str]:
        """The given name (first name) of the user. Maximum length is 64 characters"""
        return self.properties.get("givenName", None)

    @property
    def my_site(self) -> Optional[str]:
        """The URL for the user's site."""
        return self.properties.get("mySite", None)

    @property
    def office_location(self) -> Optional[str]:
        """The office location in the user's place of business."""
        return self.properties.get("officeLocation", None)

    @property
    def user_principal_name(self) -> Optional[str]:
        """
        The user principal name (UPN) of the user. The UPN is an Internet-style login name for the user based on the
        Internet standard RFC 822. By convention, this should map to the user's email name.
        The general format is alias@domain, where domain must be present in the tenant's collection of verified domains.
        This property is required when a user is created. The verified domains for the tenant can be accessed from
        the verifiedDomains property of organization.
        NOTE: This property cannot contain accent characters.
        Only the following characters are allowed A - Z, a - z, 0 - 9, ' . - _ ! # ^ ~.
        For the complete list of allowed characters, see username policies.
        """
        return self.properties.get("userPrincipalName", None)

    @property
    def assigned_plans(self) -> ClientValueCollection[AssignedPlan]:
        """The plans that are assigned to the user."""
        return self.properties.get("assignedPlans", ClientValueCollection(AssignedPlan))

    @property
    def authentication(self) -> Authentication:
        """
        The authentication methods that are supported for the user.
        """
        return self.properties.get(
            "authentication", Authentication(self.context, ResourcePath("authentication", self.resource_path))
        )

    @property
    def business_phones(self) -> StringCollection:
        """String collection	The telephone numbers for the user. NOTE: Although this is a string collection,
        only one number can be set for this property. Read-only for users synced from on-premises directory.
        """
        return self.properties.get("businessPhones", StringCollection())

    @property
    def creation_type(self) -> Optional[str]:
        """Indicates whether the user account was created as a regular school or work account (null),
        an external account (Invitation), a local account for an Azure Active Directory B2C tenant (LocalAccount)
        or self-service sign-up using email verification (EmailVerified). Read-only.
        """
        return self.properties.get("creationType", None)

    @property
    def license_assignment_states(self) -> ClientValueCollection[LicenseAssignmentState]:
        """
        State of license assignments for this user. Also indicates licenses that are directly-assigned and those
        that the user has inherited through group memberships.
        """
        return self.properties.get("licenseAssignmentStates", ClientValueCollection(LicenseAssignmentState))

    @property
    def mail(self) -> Optional[str]:
        """The SMTP address for the user, for example, "jeff@contoso.onmicrosoft.com".
        Returned by default. Supports $filter and endsWith.
        """
        return self.properties.get("mail", None)

    @property
    def other_mails(self) -> StringCollection:
        """A list of additional email addresses for the user;
        for example: ["bob@contoso.com", "Robert@fabrikam.com"]. Supports $filter.
        """
        return self.properties.get("otherMails", StringCollection())

    @property
    def interests(self) -> StringCollection:
        """A list for the user to describe their interests."""
        return self.properties.get("interests", StringCollection())

    @property
    def identities(self) -> ClientValueCollection[ObjectIdentity]:
        """Represents the identities that can be used to sign in to this user account.
        An identity can be provided by Microsoft (also known as a local account), by organizations,
        or by social identity providers such as Facebook, Google, and Microsoft, and tied to a user account.
        May contain multiple items with the same signInType value.
        Supports $filter.
        """
        return self.properties.get("identities", ClientValueCollection(ObjectIdentity))

    @property
    def activities(self) -> UserActivityCollection:
        """The user's activities across devices."""
        return self.properties.get(
            "activities", UserActivityCollection(self.context, ResourcePath("activities", self.resource_path))
        )

    @odata(name="assignedLicenses")
    @property
    def assigned_licenses(self) -> ClientValueCollection[AssignedLicense]:
        """The licenses that are assigned to the user, including inherited (group-based) licenses."""
        return self.properties.get("assignedLicenses", ClientValueCollection(AssignedLicense))

    @odata(name="followedSites")
    @property
    def followed_sites(self) -> EntityCollection[Site]:
        """ """
        return self.properties.get(
            "followedSites", EntityCollection(self.context, Site, ResourcePath("followedSites", self.resource_path))
        )

    @property
    def insights(self) -> OfficeGraphInsights:
        """Insights are relationships calculated using advanced analytics and machine learning techniques."""
        return self.properties.get(
            "insights", OfficeGraphInsights(self.context, ResourcePath("insights", self.resource_path))
        )

    @property
    def photo(self) -> ProfilePhoto:
        """The user's profile photo. Read-only."""
        return self.properties.get("photo", ProfilePhoto(self.context, ResourcePath("photo", self.resource_path)))

    @property
    def photos(self) -> EntityCollection[ProfilePhoto]:
        """The collection of the user's profile photos in different sizes"""
        return self.properties.get(
            "photos", EntityCollection(self.context, ProfilePhoto, ResourcePath("photos", self.resource_path))
        )

    @property
    def manager(self) -> DirectoryObject:
        """The user or contact that is this user's manager"""
        return self.properties.get("manager", DirectoryObject(self.context, ResourcePath("manager", self.resource_path)))

    @property
    def preferred_language(self) -> Optional[str]:
        """
        The preferred language for the user. Should follow ISO 639-1 Code; for example en-US.
        """
        return self.properties.get("preferredLanguage", None)

    @odata(name="mailboxSettings")
    @property
    def mailbox_settings(self) -> MailboxSettings:
        """Get the user's mailboxSettings."""
        return self.properties.get("mailboxSettings", MailboxSettings())

    @mailbox_settings.setter
    def mailbox_settings(self, value: MailboxSettings):
        self.set_property("mailboxSettings", value)

    @property
    def calendar(self) -> Calendar:
        """The user's primary calendar. Read-only."""
        return self.properties.get("calendar", Calendar(self.context, ResourcePath("calendar", self.resource_path)))

    @property
    def calendars(self) -> CalendarCollection:
        """The user's calendar groups. Read-only. Nullable."""
        return self.properties.get(
            "calendars", CalendarCollection(self.context, ResourcePath("calendars", self.resource_path))
        )

    @property
    def calendar_groups(self) -> EntityCollection[CalendarGroup]:
        """The user's calendar groups. Read-only. Nullable."""
        return self.properties.get(
            "calendarGroups",
            EntityCollection(self.context, CalendarGroup, ResourcePath("calendarGroups", self.resource_path)),
        )

    @property
    def license_details(self) -> EntityCollection[LicenseDetails]:
        """Retrieve the properties and relationships of a Drive resource."""
        return self.properties.get(
            "licenseDetails",
            EntityCollection(self.context, LicenseDetails, ResourcePath("licenseDetails", self.resource_path)),
        )

    @property
    def drive(self) -> Drive:
        """Retrieve the properties and relationships of a Drive resource."""
        return self.properties.get(
            "drive", Drive(self.context, EntityPath("drive", self.resource_path, ResourcePath("drives")))
        )

    @property
    def contacts(self) -> ContactCollection:
        """Get a contact collection from the default Contacts folder of the signed-in user (.../me/contacts),
        or from the specified contact folder."""
        return self.properties.get(
            "contacts", ContactCollection(self.context, ResourcePath("contacts", self.resource_path))
        )

    @property
    def contact_folders(self) -> ContactFolderCollection:
        """Get the contact folder collection in the default Contacts folder of the signed-in user."""
        return self.properties.get(
            "contactFolders",
            ContactFolderCollection(self.context, ResourcePath("contactFolders", self.resource_path)),
        )

    @property
    def events(self) -> DeltaCollection[Event]:
        """Get an event collection or an event."""
        return self.properties.get(
            "events", DeltaCollection(self.context, Event, ResourcePath("events", self.resource_path))
        )

    @property
    def messages(self) -> MessageCollection:
        """Get an event collection or an event."""
        return self.properties.get(
            "messages", MessageCollection(self.context, ResourcePath("messages", self.resource_path))
        )

    @property
    def joined_teams(self) -> TeamCollection:
        """Get the teams in Microsoft Teams that the user is a direct member of."""
        return self.properties.get("joinedTeams", TeamCollection(self.context, JoinedTeamsPath(self.resource_path)))

    @property
    def managed_devices(self) -> EntityCollection[ManagedDevice]:
        """Devices that are managed or pre-enrolled through Intune"""
        return self.properties.get(
            "managedDevices",
            EntityCollection(self.context, ManagedDevice, ResourcePath("managedDevices", self.resource_path)),
        )

    @property
    def member_of(self) -> DirectoryObjectCollection:
        """Get groups and directory roles that the user is a direct member of."""
        return self.properties.get(
            "memberOf", DirectoryObjectCollection(self.context, ResourcePath("memberOf", self.resource_path))
        )

    @property
    def oauth2_permission_grants(self) -> DeltaCollection[OAuth2PermissionGrant]:
        """"""
        return self.properties.get(
            "oauth2PermissionGrants",
            DeltaCollection(
                self.context, OAuth2PermissionGrant, ResourcePath("oauth2PermissionGrants", self.resource_path)
            ),
        )

    @property
    def on_premises_distinguished_name(self) -> Optional[str]:
        """
        Contains the on-premises Active Directory distinguished name or DN. The property is only populated for
        customers who are synchronizing their on-premises directory to Azure Active Directory via Azure AD Connect
        """
        return self.properties.get("onPremisesDistinguishedName", None)

    @property
    def on_premises_domain_name(self) -> Optional[str]:
        """
        Contains the on-premises domainFQDN, also called dnsDomainName synchronized from the on-premises directory.
        The property is only populated for customers who are synchronizing their on-premises directory to
        Azure Active Directory via Azure AD Connect.
        """
        return self.properties.get("onPremisesDomainName", None)

    @property
    def owned_devices(self) -> DirectoryObjectCollection:
        """Devices that are owned by the user. Read-only. Nullable.
        Supports $expand and $filter (/$count eq 0, /$count ne 0, /$count eq 1, /$count ne 1).
        """
        return self.properties.get(
            "ownedDevices", DirectoryObjectCollection(self.context, ResourcePath("ownedDevices", self.resource_path))
        )

    @property
    def owned_objects(self) -> DirectoryObjectCollection:
        """Directory objects that are owned by the user. Read-only. Nullable. Supports $expand."""
        return self.properties.get(
            "ownedObjects", DirectoryObjectCollection(self.context, ResourcePath("ownedObjects", self.resource_path))
        )

    @property
    def proxy_addresses(self) -> StringCollection:
        """
        For example: ["SMTP: bob@contoso.com", "smtp: bob@sales.contoso.com"]. Changes to the mail property will
        also update this collection to include the value as an SMTP address. For more information, see mail and
        proxyAddresses properties. The proxy address prefixed with SMTP (capitalized) is the primary proxy address
        while those prefixed with smtp are the secondary proxy addresses. For Azure AD B2C accounts, this
        property has a limit of ten unique addresses. Read-only in Microsoft Graph; you can update this property
        only through the Microsoft 365 admin center. Not nullable.
        """
        return self.properties.get("proxyAddresses", StringCollection())

    @property
    def transitive_member_of(self) -> DirectoryObjectCollection:
        """Get groups, directory roles that the user is a member of. This API request is transitive, and will also
        return all groups the user is a nested member of."""
        return self.properties.get(
            "transitiveMemberOf",
            DirectoryObjectCollection(self.context, ResourcePath("transitiveMemberOf", self.resource_path)),
        )

    @property
    def mail_folders(self) -> MailFolderCollection:
        """Get the mail folder collection under the root folder of the signed-in user."""
        return self.properties.get(
            "mailFolders", MailFolderCollection(self.context, ResourcePath("mailFolders", self.resource_path))
        )

    @property
    def outlook(self) -> OutlookUser:
        """Represents the Outlook services available to a user."""
        return self.properties.get("outlook", OutlookUser(self.context, ResourcePath("outlook", self.resource_path)))

    @property
    def people(self) -> EntityCollection[Person]:
        """People that are relevant to the user. Read-only. Nullable."""
        return self.properties.get(
            "people", EntityCollection(self.context, Person, ResourcePath("people", self.resource_path))
        )

    @property
    def onenote(self) -> Onenote:
        """Represents the Onenote services available to a user."""
        return self.properties.get("onenote", Onenote(self.context, ResourcePath("onenote", self.resource_path)))

    @property
    def settings(self) -> UserSettings:
        """Represents the user and organization settings object."""
        return self.properties.get("settings", UserSettings(self.context, ResourcePath("settings", self.resource_path)))

    @property
    def planner(self) -> PlannerUser:
        """The plannerUser resource provide access to Planner resources for a user."""
        return self.properties.get("planner", PlannerUser(self.context, ResourcePath("planner", self.resource_path)))

    @property
    def agreement_acceptances(self) -> EntityCollection[AgreementAcceptance]:
        """
        The user's terms of use acceptance statuses
        """
        return self.properties.get(
            "agreementAcceptances",
            EntityCollection(
                self.context, AgreementAcceptance, ResourcePath("agreementAcceptances", self.resource_path)
            ),
        )

    @property
    def extensions(self) -> EntityCollection[Extension]:
        """The collection of open extensions defined for the user. Nullable."""
        return self.properties.get(
            "extensions", EntityCollection(self.context, Extension, ResourcePath("extensions", self.resource_path))
        )

    @property
    def direct_reports(self) -> DirectoryObjectCollection:
        """Get a user's direct reports"""
        return self.properties.get(
            "directReports", DirectoryObjectCollection(self.context, ResourcePath("directReports", self.resource_path))
        )

    @property
    def online_meetings(self) -> OnlineMeetingCollection:
        """Get a user's online meetings."""
        return self.properties.get(
            "onlineMeetings", OnlineMeetingCollection(self.context, ResourcePath("onlineMeetings", self.resource_path))
        )

    @property
    def password_policies(self) -> Optional[str]:
        """
        Specifies password policies for the user. This value is an enumeration with one possible value being
        DisableStrongPassword, which allows weaker passwords than the default policy to be specified.
        DisablePasswordExpiration can also be specified. The two may be specified together; for example:
        DisablePasswordExpiration, DisableStrongPassword.
        """
        return self.properties.get("passwordPolicies", None)

    @odata(name="passwordProfile", persist=True)
    @property
    def password_profile(self) -> PasswordProfile:
        """
        Specifies the password profile for the user. The profile contains the user's password.
        This property is required when a user is created. The password in the profile must satisfy minimum
        requirements as specified by the passwordPolicies property. By default, a strong password is required.
        """
        return self.properties.setdefault("passwordProfile", PasswordProfile())

    @property
    def presence(self) -> Presence:
        """Get a user's presence information."""
        return self.properties.get("presence", Presence(self.context, ResourcePath("presence", self.resource_path)))

    @property
    def registered_devices(self) -> DirectoryObjectCollection:
        """Get the devices that are registered for the user from the registeredDevices navigation property."""
        return self.properties.get(
            "registeredDevices",
            DirectoryObjectCollection(self.context, ResourcePath("registeredDevices", self.resource_path)),
        )

    @property
    def street_address(self) -> Optional[str]:
        """The street address of the user's place of business. Maximum length is 1024 characters."""
        return self.properties.get("streetAddress", None)

    @property
    def security_identifier(self) -> Optional[str]:
        """Security identifier (SID) of the user, used in Windows scenarios."""
        return self.properties.get("securityIdentifier", None)

    @property
    def teamwork(self) -> UserTeamwork:
        """A container for the range of Microsoft Teams functionalities that are available per user in the tenant."""
        return self.properties.get("teamwork", UserTeamwork(self.context, ResourcePath("teamwork", self.resource_path)))

    @property
    def solutions(self) -> UserSolutionRoot:
        """The identifier that relates the user to the working time schedule triggers. Read-Only. Nullable."""
        return self.properties.get(
            "solutions", UserSolutionRoot(self.context, ResourcePath("solutions", self.resource_path))
        )

    @property
    def todo(self) -> Todo:
        """Represents the To Do services available to a user."""
        return self.properties.get("todo", Todo(self.context, ResourcePath("todo", self.resource_path)))

    @property
    def employee_experience(self) -> EmployeeExperienceUser:
        """Represents the To Do services available to a user."""
        return self.properties.get(
            "employeeExperience",
            EmployeeExperienceUser(self.context, ResourcePath("employeeExperience", self.resource_path)),
        )

    @property
    def usage_location(self) -> Optional[str]:
        """
        A two letter country code (ISO standard 3166). Required for users that will be assigned licenses due to
        legal requirement to check for availability of services in countries. Examples include: US, JP, and GB.
        """
        return self.properties.get("usageLocation", None)

    @property
    def authorization_info(self) -> AuthorizationInfo:
        """Gets the authorizationInfo property"""
        return self.properties.get("authorizationInfo", AuthorizationInfo())

    @property
    def city(self) -> Optional[str]:
        """Gets the city property"""
        return self.properties.get("city", None)

    @property
    def company_name(self) -> Optional[str]:
        """Gets the companyName property"""
        return self.properties.get("companyName", None)

    @property
    def consent_provided_for_minor(self) -> Optional[str]:
        """Gets the consentProvidedForMinor property"""
        return self.properties.get("consentProvidedForMinor", None)

    @property
    def country(self) -> Optional[str]:
        """Gets the country property"""
        return self.properties.get("country", None)

    @property
    def created_date_time(self) -> datetime:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def custom_security_attributes(self) -> CustomSecurityAttributeValue:
        """Gets the customSecurityAttributes property"""
        return self.properties.get("customSecurityAttributes", CustomSecurityAttributeValue())

    @property
    def department(self) -> Optional[str]:
        """Gets the department property"""
        return self.properties.get("department", None)

    @property
    def employee_hire_date(self) -> datetime:
        """Gets the employeeHireDate property"""
        return self.properties.get("employeeHireDate", datetime.min)

    @property
    def employee_id(self) -> Optional[str]:
        """Gets the employeeId property"""
        return self.properties.get("employeeId", None)

    @property
    def employee_leave_date_time(self) -> datetime:
        """Gets the employeeLeaveDateTime property"""
        return self.properties.get("employeeLeaveDateTime", datetime.min)

    @property
    def employee_org_data(self) -> EmployeeOrgData:
        """Gets the employeeOrgData property"""
        return self.properties.get("employeeOrgData", EmployeeOrgData())

    @property
    def employee_type(self) -> Optional[str]:
        """Gets the employeeType property"""
        return self.properties.get("employeeType", None)

    @property
    def external_user_state(self) -> Optional[str]:
        """Gets the externalUserState property"""
        return self.properties.get("externalUserState", None)

    @property
    def external_user_state_change_date_time(self) -> datetime:
        """Gets the externalUserStateChangeDateTime property"""
        return self.properties.get("externalUserStateChangeDateTime", datetime.min)

    @property
    def fax_number(self) -> Optional[str]:
        """Gets the faxNumber property"""
        return self.properties.get("faxNumber", None)

    @property
    def identity_parent_id(self) -> Optional[str]:
        """Gets the identityParentId property"""
        return self.properties.get("identityParentId", None)

    @property
    def im_addresses(self) -> StringCollection:
        """Gets the imAddresses property"""
        return self.properties.get("imAddresses", StringCollection(None))

    @property
    def is_management_restricted(self) -> Optional[bool]:
        """Gets the isManagementRestricted property"""
        return self.properties.get("isManagementRestricted", None)

    @property
    def is_resource_account(self) -> Optional[bool]:
        """Gets the isResourceAccount property"""
        return self.properties.get("isResourceAccount", None)

    @property
    def job_title(self) -> Optional[str]:
        """Gets the jobTitle property"""
        return self.properties.get("jobTitle", None)

    @odata(name="lastPasswordChangeDateTime")
    @property
    def last_password_change_date_time(self) -> datetime:
        """Gets the lastPasswordChangeDateTime property"""
        return self.properties.get("lastPasswordChangeDateTime", datetime.min)

    @property
    def legal_age_group_classification(self) -> Optional[str]:
        """Gets the legalAgeGroupClassification property"""
        return self.properties.get("legalAgeGroupClassification", None)

    @property
    def mail_nickname(self) -> Optional[str]:
        """Gets the mailNickname property"""
        return self.properties.get("mailNickname", None)

    @property
    def mobile_phone(self) -> Optional[str]:
        """Gets the mobilePhone property"""
        return self.properties.get("mobilePhone", None)

    @property
    def on_premises_extension_attributes(self) -> OnPremisesExtensionAttributes:
        """Gets the onPremisesExtensionAttributes property"""
        return self.properties.get("onPremisesExtensionAttributes", OnPremisesExtensionAttributes())

    @property
    def on_premises_immutable_id(self) -> Optional[str]:
        """Gets the onPremisesImmutableId property"""
        return self.properties.get("onPremisesImmutableId", None)

    @odata(name="onPremisesLastSyncDateTime")
    @property
    def on_premises_last_sync_date_time(self) -> datetime:
        """Gets the onPremisesLastSyncDateTime property"""
        return self.properties.get("onPremisesLastSyncDateTime", datetime.min)

    @odata(name="onPremisesProvisioningErrors")
    @property
    def on_premises_provisioning_errors(self) -> ClientValueCollection[OnPremisesProvisioningError]:
        """Gets the onPremisesProvisioningErrors property"""
        return self.properties.get(
            "onPremisesProvisioningErrors",
            ClientValueCollection[OnPremisesProvisioningError](OnPremisesProvisioningError),
        )

    @property
    def on_premises_sam_account_name(self) -> Optional[str]:
        """Gets the onPremisesSamAccountName property"""
        return self.properties.get("onPremisesSamAccountName", None)

    @property
    def on_premises_security_identifier(self) -> Optional[str]:
        """Gets the onPremisesSecurityIdentifier property"""
        return self.properties.get("onPremisesSecurityIdentifier", None)

    @property
    def on_premises_sync_enabled(self) -> Optional[bool]:
        """Gets the onPremisesSyncEnabled property"""
        return self.properties.get("onPremisesSyncEnabled", None)

    @property
    def on_premises_user_principal_name(self) -> Optional[str]:
        """Gets the onPremisesUserPrincipalName property"""
        return self.properties.get("onPremisesUserPrincipalName", None)

    @property
    def postal_code(self) -> Optional[str]:
        """Gets the postalCode property"""
        return self.properties.get("postalCode", None)

    @property
    def preferred_data_location(self) -> Optional[str]:
        """Gets the preferredDataLocation property"""
        return self.properties.get("preferredDataLocation", None)

    @odata(name="provisionedPlans")
    @property
    def provisioned_plans(self) -> ClientValueCollection[ProvisionedPlan]:
        """Gets the provisionedPlans property"""
        return self.properties.get("provisionedPlans", ClientValueCollection[ProvisionedPlan](ProvisionedPlan))

    @odata(name="serviceProvisioningErrors")
    @property
    def service_provisioning_errors(self) -> ClientValueCollection[ServiceProvisioningError]:
        """Gets the serviceProvisioningErrors property"""
        return self.properties.get(
            "serviceProvisioningErrors", ClientValueCollection[ServiceProvisioningError](ServiceProvisioningError)
        )

    @property
    def show_in_address_list(self) -> Optional[bool]:
        """Gets the showInAddressList property"""
        return self.properties.get("showInAddressList", None)

    @odata(name="signInSessionsValidFromDateTime")
    @property
    def sign_in_sessions_valid_from_date_time(self) -> datetime:
        """Gets the signInSessionsValidFromDateTime property"""
        return self.properties.get("signInSessionsValidFromDateTime", datetime.min)

    @property
    def state(self) -> Optional[str]:
        """Gets the state property"""
        return self.properties.get("state", None)

    @property
    def surname(self) -> Optional[str]:
        """Gets the surname property"""
        return self.properties.get("surname", None)

    @property
    def user_type(self) -> Optional[str]:
        """Gets the userType property"""
        return self.properties.get("userType", None)

    @property
    def print_(self) -> UserPrint:
        """Gets the print property"""
        return self.properties.get("print", UserPrint())

    @property
    def about_me(self) -> Optional[str]:
        """Gets the aboutMe property"""
        return self.properties.get("aboutMe", None)

    @property
    def birthday(self) -> datetime:
        """Gets the birthday property"""
        return self.properties.get("birthday", datetime.min)

    @odata(name="hireDate")
    @property
    def hire_date(self) -> datetime:
        """Gets the hireDate property"""
        return self.properties.get("hireDate", datetime.min)

    @odata(name="pastProjects")
    @property
    def past_projects(self) -> StringCollection:
        """Gets the pastProjects property"""
        return self.properties.get("pastProjects", StringCollection(None))

    @property
    def preferred_name(self) -> Optional[str]:
        """Gets the preferredName property"""
        return self.properties.get("preferredName", None)

    @property
    def responsibilities(self) -> StringCollection:
        """Gets the responsibilities property"""
        return self.properties.get("responsibilities", StringCollection(None))

    @property
    def schools(self) -> StringCollection:
        """Gets the schools property"""
        return self.properties.get("schools", StringCollection(None))

    @property
    def skills(self) -> StringCollection:
        """Gets the skills property"""
        return self.properties.get("skills", StringCollection(None))

    @odata(name="onPremisesSyncBehavior")
    @property
    def on_premises_sync_behavior(self) -> OnPremisesSyncBehavior:
        """Gets the onPremisesSyncBehavior property"""
        return self.properties.get(
            "onPremisesSyncBehavior",
            OnPremisesSyncBehavior(self.context, ResourcePath("onPremisesSyncBehavior", self.resource_path)),
        )

    @odata(name="scopedRoleMemberOf")
    @property
    def scoped_role_member_of(self) -> EntityCollection[ScopedRoleMembership]:
        """Gets the scopedRoleMemberOf property"""
        return self.properties.get(
            "scopedRoleMemberOf",
            EntityCollection[ScopedRoleMembership](
                self.context, ScopedRoleMembership, ResourcePath("scopedRoleMemberOf", self.resource_path)
            ),
        )

    @property
    def sponsors(self) -> EntityCollection[DirectoryObject]:
        """Gets the sponsors property"""
        return self.properties.get(
            "sponsors",
            EntityCollection[DirectoryObject](
                self.context, DirectoryObject, ResourcePath("sponsors", self.resource_path)
            ),
        )

    @odata(name="calendarView")
    @property
    def calendar_view(self) -> EntityCollection[Event]:
        """Gets the calendarView property"""
        return self.properties.get(
            "calendarView",
            EntityCollection[Event](self.context, Event, ResourcePath("calendarView", self.resource_path)),
        )

    @property
    def drives(self) -> EntityCollection[Drive]:
        """Gets the drives property"""
        return self.properties.get(
            "drives", EntityCollection[Drive](self.context, Drive, ResourcePath("drives", self.resource_path))
        )

    @odata(name="managedAppRegistrations")
    @property
    def managed_app_registrations(self) -> EntityCollection[ManagedAppRegistration]:
        """Gets the managedAppRegistrations property"""
        return self.properties.get(
            "managedAppRegistrations",
            EntityCollection[ManagedAppRegistration](
                self.context, ManagedAppRegistration, ResourcePath("managedAppRegistrations", self.resource_path)
            ),
        )

    @odata(name="permissionGrants")
    @property
    def permission_grants(self) -> EntityCollection[ResourceSpecificPermissionGrant]:
        """Gets the permissionGrants property"""
        return self.properties.get(
            "permissionGrants",
            EntityCollection[ResourceSpecificPermissionGrant](
                self.context, ResourceSpecificPermissionGrant, ResourcePath("permissionGrants", self.resource_path)
            ),
        )

    def set_property(self, name, value, persist_changes=True):
        super().set_property(name, value, persist_changes)
        if self._resource_path is None:
            if name in {"id", "userPrincipalName"}:
                assert self.parent_collection is not None
                self._resource_path = ResourcePath(value, self.parent_collection.resource_path)
        return self

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.User"

    @property
    def cloud_pcs(self) -> EntityCollection[CloudPC]:
        """Gets the cloudPCs property"""
        from office365.intune.devices.cloud_pc import CloudPC

        return self.properties.get(
            "cloudPCs", EntityCollection[CloudPC](self.context, CloudPC, ResourcePath("cloudPCs", self.resource_path))
        )

    @property
    def data_security_and_governance(self) -> UserDataSecurityAndGovernance:
        """Gets the dataSecurityAndGovernance property"""
        from office365.directory.identitygovernance.user_data_security_and_governance import (
            UserDataSecurityAndGovernance,
        )

        return self.properties.get(
            "dataSecurityAndGovernance",
            UserDataSecurityAndGovernance(self.context, ResourcePath("dataSecurityAndGovernance", self.resource_path)),
        )

    @property
    def sponsor_of(self) -> EntityCollection[DirectoryObject]:
        """Gets the sponsorOf property"""
        from office365.directory.objects.object import DirectoryObject

        return self.properties.get(
            "sponsorOf",
            EntityCollection[DirectoryObject](
                self.context, DirectoryObject, ResourcePath("sponsorOf", self.resource_path)
            ),
        )

    @property
    def inference_classification(self) -> InferenceClassification:
        """Gets the inferenceClassification property"""
        from office365.directory.users.inference_classification import (
            InferenceClassification,
        )

        return self.properties.get(
            "inferenceClassification",
            InferenceClassification(self.context, ResourcePath("inferenceClassification", self.resource_path)),
        )

    @property
    def notes(self) -> EntityCollection[Note]:
        """Gets the notes property"""
        from office365.directory.users.note import Note

        return self.properties.get(
            "notes", EntityCollection[Note](self.context, Note, ResourcePath("notes", self.resource_path))
        )

    @property
    def device_management_troubleshooting_events(self) -> EntityCollection[DeviceManagementTroubleshootingEvent]:
        """Gets the deviceManagementTroubleshootingEvents property"""
        from office365.intune.devices.management_troubleshooting_event import (
            DeviceManagementTroubleshootingEvent,
        )

        return self.properties.get(
            "deviceManagementTroubleshootingEvents",
            EntityCollection[DeviceManagementTroubleshootingEvent](
                self.context,
                DeviceManagementTroubleshootingEvent,
                ResourcePath("deviceManagementTroubleshootingEvents", self.resource_path),
            ),
        )

    @property
    def cloud_clipboard(self) -> CloudClipboardRoot:
        """Gets the cloudClipboard property"""
        from office365.security.cloud_clipboard_root import CloudClipboardRoot

        return self.properties.get(
            "cloudClipboard", CloudClipboardRoot(self.context, ResourcePath("cloudClipboard", self.resource_path))
        )

    @property
    def adhoc_calls(self) -> EntityCollection[AdhocCall]:
        """Gets the adhocCalls property"""
        from office365.communications.adhoc_call import AdhocCall

        return self.properties.get(
            "adhocCalls",
            EntityCollection[AdhocCall](self.context, AdhocCall, ResourcePath("adhocCalls", self.resource_path)),
        )
