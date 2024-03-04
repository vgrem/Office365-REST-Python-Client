from office365.outlook.mail.automatic_replies_mailtips import AutomaticRepliesMailTips
from office365.runtime.client_value import ClientValue


class MailTips(ClientValue):
    """Informative messages about a recipient, that are displayed to users while they're composing a message.
    For example, an out-of-office message as an automatic reply for a message recipient.
    """

    def __init__(self, automaticReplies=AutomaticRepliesMailTips(), customMailTip=None):
        """
        :param AutomaticRepliesMailTips automaticReplies: Mail tips for automatic reply if it has been set up by
            the recipient.
        :param str customMailTip: A custom mail tip that can be set on the recipient's mailbox.
        """
        self.automaticReplies = automaticReplies
        self.customMailTip = customMailTip
