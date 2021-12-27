from office365.communications.onlinemeetings.online_meeting_collection import OnlineMeetingCollection
from office365.communications.presences.presence import Presence
from office365.directory.extensions.extension import Extension
from office365.directory.licenses.assigned_plan import AssignedPlan
from office365.onedrive.sites.site import Site
from office365.onenote.onenote import Onenote
from office365.outlook.calendar.calendar import Calendar
from office365.outlook.calendar.calendar_group import CalendarGroup
from office365.outlook.calendar.event import Event
from office365.outlook.calendar.meeting_time_suggestions_result import MeetingTimeSuggestionsResult
from office365.outlook.calendar.reminder import Reminder
from office365.directory.licenses.assigned_license import AssignedLicense
from office365.directory.directory_object import DirectoryObject
from office365.directory.directory_object_collection import DirectoryObjectCollection
from office365.directory.licenses.license_details import LicenseDetails
from office365.directory.identities.object_identity import ObjectIdentity
from office365.directory.profile_photo import ProfilePhoto
from office365.entity_collection import EntityCollection, DeltaCollection
from office365.outlook.contacts.contact import Contact
from office365.outlook.contacts.contact_folder import ContactFolder
from office365.outlook.mail.mail_folder import MailFolder
from office365.onedrive.drives.drive import Drive
from office365.outlook.mail.mailbox_settings import MailboxSettings
from office365.outlook.mail.messages.message import Message
from office365.outlook.outlook_user import OutlookUser
from office365.planner.planner_user import PlannerUser
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.teams.team_collection import TeamCollection
from office365.teams.user_teamwork import UserTeamwork


class User(DirectoryObject):
    """Represents an Azure AD user account. Inherits from directoryObject."""

    def assign_license(self, add_licenses, remove_licenses):
        """
        Add or remove licenses on the user.
        :param list[str] remove_licenses: A collection of skuIds that identify the licenses to remove.
        :param list[AssignedLicense] add_licenses: A collection of assignedLicense objects that specify
             the licenses to add.
        """
        params = {
            "addLicenses": ClientValueCollection(AssignedLicense, add_licenses),
            "removeLicenses": ClientValueCollection(str, remove_licenses)
        }
        qry = ServiceOperationQuery(self, "assignLicense", None, params, None, self)
        self.context.add_query(qry)
        return self

    def change_password(self, current_password, new_password):
        """

        :param str current_password:
        :param str new_password:
        """
        qry = ServiceOperationQuery(self, "changePassword", None,
                                    {"currentPassword": current_password, "newPassword": new_password})
        self.context.add_query(qry)
        return self

    def send_mail(self, message, save_to_sent_items=False):
        """Send a new message on the fly

        :type message: office365.mail.message.Message
        :type save_to_sent_items: bool
        """
        payload = {
            "message": message,
            "saveToSentItems": save_to_sent_items
        }
        qry = ServiceOperationQuery(self, "sendmail", None, payload)
        self.context.add_query(qry)
        return self

    def export_personal_data(self, storage_location):
        """
        Submit a data policy operation request from a company administrator or an application to
        export an organizational user's data.

        If successful, this method returns a 202 Accepted response code.
        It does not return anything in the response body. The response contains the following response headers.

        :param str storage_location: This is a shared access signature (SAS) URL to an Azure Storage account,
            to where data should be exported.
        """
        qry = ServiceOperationQuery(self, "exportPersonalData", None, {"storage_location": storage_location})
        self.context.add_query(qry)
        return self

    def find_meeting_times(self):
        """
        Suggest meeting times and locations based on organizer and attendee availability, and time or location
        constraints specified as parameters.

        If findMeetingTimes cannot return any meeting suggestions, the response would indicate a reason in the
        emptySuggestionsReason property. Based on this value, you can better adjust the parameters
        and call findMeetingTimes again.

        The algorithm used to suggest meeting times and locations undergoes fine-tuning from time to time.
        In scenarios like test environments where the input parameters and calendar data remain static, expect
        that the suggested results may differ over time.

        """
        result = ClientResult(self.context, MeetingTimeSuggestionsResult())
        qry = ServiceOperationQuery(self, "findMeetingTimes", None, None, None, result)
        self.context.add_query(qry)
        return result

    def get_calendar_view(self, start_dt, end_dt):
        """Get the occurrences, exceptions, and single instances of events in a calendar view defined by a time range,
           from the user's default calendar, or from some other calendar of the user's.

        :param datetime.datetime end_dt: The end date and time of the time range, represented in ISO 8601 format.
             For example, "2019-11-08T20:00:00-08:00".
        :param datetime.datetime start_dt: The start date and time of the time range, represented in ISO 8601 format.
            For example, "2019-11-08T19:00:00-08:00".

        """
        return_type = EntityCollection(self.context, Event, ResourcePath("calendarView", self.resource_path))
        qry = ServiceOperationQuery(self, "calendarView", None, None, None, return_type)
        self.context.add_query(qry)

        def _construct_request(request):
            """
            :type request: office365.runtime.http.request_options.RequestOptions
            """
            request.method = HttpMethod.Get
            request.url += "?startDateTime={0}&endDateTime={1}".format(start_dt.isoformat(), end_dt.isoformat())

        self.context.before_execute(_construct_request)
        return return_type

    def get_reminder_view(self, start_dt, end_dt):
        """Get the occurrences, exceptions, and single instances of events in a calendar view defined by a time range,
                   from the user's default calendar, or from some other calendar of the user's.

        :param datetime.datetime end_dt: The end date and time of the event for which the reminder is set up.
            The value is represented in ISO 8601 format, for example, "2015-11-08T20:00:00.0000000"..
        :param datetime.datetime start_dt: The start date and time of the event for which the reminder is set up.
            The value is represented in ISO 8601 format, for example, "2015-11-08T19:00:00.0000000".
        """
        result = ClientResult(self.context, ClientValueCollection(Reminder))
        params = {
            "startDateTime": start_dt.isoformat(),
            "endDateTime": end_dt.isoformat(),
        }
        qry = ServiceOperationQuery(self, "reminderView", params, None, None, result)
        self.context.add_query(qry)

        def _construct_request(request):
            request.method = HttpMethod.Get

        self.context.before_execute(_construct_request)
        return result

    def delete_object(self, permanent_delete=False):
        """
        :param permanent_delete: Permanently deletes the user from directory
        :type permanent_delete: bool

        """
        super(User, self).delete_object()
        if permanent_delete:
            deleted_user = self.context.directory.deleted_users[self.id]
            deleted_user.delete_object()
        return self

    def revoke_signin_sessions(self):
        """
        Invalidates all the refresh tokens issued to applications for a user
        (as well as session cookies in a user's browser), by resetting the signInSessionsValidFromDateTime user
        property to the current date-time. Typically, this operation is performed (by the user or an administrator)
        if the user has a lost or stolen device. This operation prevents access to the organization's data through
        applications on the device by requiring the user to sign in again to all applications that they have previously
        consented to, independent of device.
        """
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "revokeSignInSessions", None, None, None, result)
        self.context.add_query(qry)
        return result

    @property
    def account_enabled(self):
        return self.properties.get('accountEnabled', None)

    @property
    def assigned_plans(self):
        """The plans that are assigned to the user."""
        return self.properties.get('assignedPlans', ClientValueCollection(AssignedPlan))

    @property
    def creation_type(self):
        """Indicates whether the user account was created as a regular school or work account (null),
        an external account (Invitation), a local account for an Azure Active Directory B2C tenant (LocalAccount)
        or self-service sign-up using email verification (EmailVerified). Read-only.
        """
        return self.properties.get('creationType', None)

    @property
    def mail(self):
        """The SMTP address for the user, for example, "jeff@contoso.onmicrosoft.com".
           Returned by default. Supports $filter and endsWith.
        """
        return self.properties.get('mail', None)

    @property
    def other_mails(self):
        """A list of additional email addresses for the user;
        for example: ["bob@contoso.com", "Robert@fabrikam.com"]. Supports $filter.
        """
        return self.properties.get('otherMails', ClientValueCollection(str))

    @property
    def identities(self):
        """Represents the identities that can be used to sign in to this user account.
           An identity can be provided by Microsoft (also known as a local account), by organizations,
           or by social identity providers such as Facebook, Google, and Microsoft, and tied to a user account.
           May contain multiple items with the same signInType value.
           Supports $filter.
        """
        return self.properties.get('identities',
                                   ClientValueCollection(ObjectIdentity))

    @property
    def assigned_licenses(self):
        """The licenses that are assigned to the user, including inherited (group-based) licenses. """
        return self.properties.get('assignedLicenses',
                                   ClientValueCollection(AssignedLicense))

    @property
    def followed_sites(self):
        """

        """
        return self.properties.get('followedSites',
                                   EntityCollection(self.context, Site,
                                                    ResourcePath("followedSites", self.resource_path)))

    @property
    def photo(self):
        """
        The user's profile photo. Read-only.
        """
        return self.properties.get('photo',
                                   ProfilePhoto(self.context, ResourcePath("photo", self.resource_path)))

    @property
    def manager(self):
        """
        The user or contact that is this user's manager. Read-only. (HTTP Methods: GET, PUT, DELETE.)
        """
        return self.properties.get('manager',
                                   DirectoryObject(self.context, ResourcePath("manager", self.resource_path)))

    @property
    def preferred_language(self):
        """
        The preferred language for the user. Should follow ISO 639-1 Code; for example en-US.

        :rtype: str or None
        """
        return self.properties.get('preferredLanguage', None)

    @property
    def mailbox_settings(self):
        """
        Get the user's mailboxSettings.

        :rtype: str or None
        """
        return self.properties.get('mailboxSettings', MailboxSettings())

    @property
    def calendar(self):
        """The user's primary calendar. Read-only."""
        return self.properties.get('calendar',
                                   Calendar(self.context, ResourcePath("calendar", self.resource_path)))

    @property
    def calendars(self):
        """The user's calendar groups. Read-only. Nullable."""
        return self.properties.get('calendars',
                                   EntityCollection(self.context, Calendar,
                                                    ResourcePath("calendars", self.resource_path)))

    @property
    def calendar_groups(self):
        """The user's calendar groups. Read-only. Nullable."""
        return self.properties.get('calendarGroups',
                                   EntityCollection(self.context, CalendarGroup,
                                                    ResourcePath("calendarGroups", self.resource_path)))

    @property
    def license_details(self):
        """Retrieve the properties and relationships of a Drive resource."""
        return self.properties.get('licenseDetails',
                                   EntityCollection(self.context, LicenseDetails,
                                                    ResourcePath("licenseDetails", self.resource_path)))

    @property
    def drive(self):
        """Retrieve the properties and relationships of a Drive resource.

        :rtype: Drive
        """
        return self.get_property('drive',
                                 Drive(self.context, ResourcePath("drive", self.resource_path)))

    @property
    def contacts(self):
        """Get a contact collection from the default Contacts folder of the signed-in user (.../me/contacts),
        or from the specified contact folder."""
        return self.properties.get('contacts',
                                   DeltaCollection(self.context, Contact,
                                                   ResourcePath("contacts", self.resource_path)))

    @property
    def contact_folders(self):
        """Get the contact folder collection in the default Contacts folder of the signed-in user."""
        return self.properties.get('contactFolders',
                                   DeltaCollection(self.context, ContactFolder,
                                                   ResourcePath("contactFolders", self.resource_path)))

    @property
    def events(self):
        """Get an event collection or an event."""
        return self.properties.get('events', DeltaCollection(self.context, Event,
                                                             ResourcePath("events", self.resource_path)))

    @property
    def messages(self):
        """Get an event collection or an event."""
        return self.properties.get('messages',
                                   DeltaCollection(self.context, Message,
                                                   ResourcePath("messages", self.resource_path)))

    @property
    def joined_teams(self):
        """Get the teams in Microsoft Teams that the user is a direct member of."""
        return self.properties.get('joinedTeams',
                                   TeamCollection(self.context, ResourcePath("joinedTeams", self.resource_path)))

    @property
    def member_of(self):
        """Get groups and directory roles that the user is a direct member of."""
        return self.properties.get('memberOf',
                                   DirectoryObjectCollection(self.context,
                                                             ResourcePath("memberOf", self.resource_path)))

    @property
    def transitive_member_of(self):
        """Get groups, directory roles that the user is a member of. This API request is transitive, and will also
        return all groups the user is a nested member of. """
        return self.properties.get('transitiveMemberOf',
                                   DirectoryObjectCollection(self.context,
                                                             ResourcePath("transitiveMemberOf", self.resource_path)))

    @property
    def mail_folders(self):
        """Get the mail folder collection under the root folder of the signed-in user. """
        return self.properties.get('mailFolders',
                                   DeltaCollection(self.context, MailFolder,
                                                   ResourcePath("mailFolders", self.resource_path)))

    @property
    def outlook(self):
        """Represents the Outlook services available to a user."""
        return self.properties.get('outlook',
                                   OutlookUser(self.context, ResourcePath("outlook", self.resource_path)))

    @property
    def onenote(self):
        """Represents the Onenote services available to a user."""
        return self.properties.get('onenote',
                                   Onenote(self.context, ResourcePath("onenote", self.resource_path)))

    @property
    def planner(self):
        """The plannerUser resource provide access to Planner resources for a user."""
        return self.properties.get('planner',
                                   PlannerUser(self.context, ResourcePath("planner", self.resource_path)))

    @property
    def extensions(self):
        """The collection of open extensions defined for the user. Nullable.

        :rtype: EntityCollection
        """
        return self.get_property('extensions',
                                 EntityCollection(self.context, Extension,
                                                  ResourcePath("extensions", self.resource_path)))

    @property
    def direct_reports(self):
        """
        Get a user's direct reports.

        :rtype: EntityCollection
        """
        return self.get_property('directReports',
                                 DirectoryObjectCollection(self.context,
                                                           ResourcePath("directReports", self.resource_path)))

    @property
    def online_meetings(self):
        """
        Get a user's online meetings.

        :rtype: OnlineMeetingCollection
        """
        return self.get_property('onlineMeetings',
                                 OnlineMeetingCollection(self.context,
                                                         ResourcePath("onlineMeetings", self.resource_path)))

    @property
    def presence(self):
        """Get a user's presence information."""
        return self.properties.get('presence',
                                   Presence(self.context, ResourcePath("presence", self.resource_path)))

    @property
    def teamwork(self):
        """A container for the range of Microsoft Teams functionalities that are available per user in the tenant."""
        return self.properties.get('teamwork',
                                   UserTeamwork(self.context, ResourcePath("teamwork", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "calendarGroups": self.calendar_groups,
                "contactFolders": self.contact_folders,
                "licenseDetails": self.license_details,
                "memberOf": self.member_of,
                "transitiveMemberOf": self.transitive_member_of,
                "joinedTeams": self.joined_teams,
                "assignedLicenses": self.assigned_licenses,
                "mailFolders": self.mail_folders,
                "mailboxSettings": self.mailbox_settings,
                "directReports": self.direct_reports
            }
            default_value = property_mapping.get(name, None)
        return super(User, self).get_property(name, default_value)

    def set_property(self, name, value, persist_changes=True):
        super(User, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "id" or name == "userPrincipalName":
                self._resource_path = ResourcePath(value, self._parent_collection.resource_path)
        return self
