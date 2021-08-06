from office365.directory.extensions.extension import Extension
from office365.outlook.calendar.calendar import Calendar
from office365.outlook.calendar.calendar_group import CalendarGroup
from office365.outlook.calendar.event import Event
from office365.outlook.calendar.meeting_time_suggestions_result import MeetingTimeSuggestionsResult
from office365.outlook.calendar.reminder import Reminder
from office365.directory.licenses.assigned_license import AssignedLicense
from office365.directory.directory_object import DirectoryObject
from office365.directory.directoryObjectCollection import DirectoryObjectCollection
from office365.directory.licenses.license_details import LicenseDetails
from office365.directory.identities.object_identity import ObjectIdentity
from office365.directory.profile_photo import ProfilePhoto
from office365.entity_collection import EntityCollection
from office365.outlook.contacts.contact import Contact
from office365.outlook.mail.mailFolder import MailFolder
from office365.onedrive.drive import Drive
from office365.outlook.mail.message import Message
from office365.onedrive.siteCollection import SiteCollection
from office365.outlook.outlook_user import OutlookUser
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.teams.team_collection import TeamCollection


class User(DirectoryObject):
    """Represents an Azure AD user account. Inherits from directoryObject."""

    def assign_license(self, addLicenses, removeLicenses):
        """
        Add or remove licenses on the user.
        :param list[str] removeLicenses: A collection of skuIds that identify the licenses to remove.
        :param ClientValueCollection addLicenses: A collection of assignedLicense objects that specify
             the licenses to add.
        """
        params = {
            "addLicenses": addLicenses,
            "removeLicenses": removeLicenses
        }
        qry = ServiceOperationQuery(self, "assignLicense", None, params, None, self)
        self.context.add_query(qry)
        return self

    def change_password(self, currentPassword, newPassword):
        """

        :param str currentPassword:
        :param str newPassword:
        """
        qry = ServiceOperationQuery(self, "changePassword", None,
                                    {"currentPassword": currentPassword, "newPassword": newPassword})
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

    @property
    def account_enabled(self):
        return self.properties.get('accountEnabled', None)

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
        return self.properties.get('assignedLicenses',
                                   ClientValueCollection(AssignedLicense))

    @property
    def followed_sites(self):
        return self.properties.get('followedSites',
                                   SiteCollection(self.context, ResourcePath("followedSites", self.resource_path)))

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
        return self.get_property('licenseDetails',
                                 EntityCollection(self.context, LicenseDetails,
                                                  ResourcePath("licenseDetails", self.resource_path)))

    @property
    def drive(self):
        """Retrieve the properties and relationships of a Drive resource."""
        return self.get_property('drive',
                                 Drive(self.context, ResourcePath("drive", self.resource_path)))

    @property
    def contacts(self):
        """Get a contact collection from the default Contacts folder of the signed-in user (.../me/contacts),
        or from the specified contact folder."""
        return self.properties.get('contacts',
                                   EntityCollection(self.context, Contact,
                                                    ResourcePath("contacts", self.resource_path)))

    @property
    def events(self):
        """Get an event collection or an event."""
        return self.properties.get('events', EntityCollection(self.context, Event,
                                                              ResourcePath("events", self.resource_path)))

    @property
    def messages(self):
        """Get an event collection or an event."""
        return self.properties.get('messages',
                                   EntityCollection(self.context, Message,
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
                                   EntityCollection(self.context, MailFolder,
                                                    ResourcePath("mailFolders", self.resource_path)))

    @property
    def outlook(self):
        """Represents the Outlook services available to a user."""
        return self.properties.get('outlook',
                                   OutlookUser(self.context, ResourcePath("outlook", self.resource_path)))

    @property
    def extensions(self):
        """The collection of open extensions defined for the user. Nullable."""
        return self.get_property('extensions',
                                 EntityCollection(self.context, Extension,
                                                  ResourcePath("extensions", self.resource_path)))

    def get_property(self, name, default_value=None):
        property_mapping = {
            "transitiveMemberOf": self.transitive_member_of,
            "joinedTeams": self.joined_teams,
            "assignedLicenses": self.assigned_licenses,
            "mailFolders": self.mail_folders
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
