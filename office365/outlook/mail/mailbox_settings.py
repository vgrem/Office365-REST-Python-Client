from office365.outlook.mail.automatic_replies_setting import AutomaticRepliesSetting
from office365.runtime.client_value import ClientValue


class MailboxSettings(ClientValue):
    """Settings for the primary mailbox of a user."""

    def __init__(self, time_format=None, time_zone=None, automatic_replies_setting=AutomaticRepliesSetting()):
        """
        :param str time_format: The time format for the user's mailbox.
        :param str time_zone: The default time zone for the user's mailbox.
        :param AutomaticRepliesSetting automatic_replies_setting: 	Configuration settings to automatically notify
            the sender of an incoming email with a message from the signed-in user.
        """
        super(MailboxSettings, self).__init__()
        self.timeFormat = time_format
        self.timeZone = time_zone
        self.automaticRepliesSetting = automatic_replies_setting
