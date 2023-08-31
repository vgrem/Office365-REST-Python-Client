from office365.delta_collection import DeltaCollection
from office365.outlook.calendar.email_address import EmailAddress
from office365.outlook.contacts.contact import Contact
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection


class ContactCollection(DeltaCollection):

    def __init__(self, context, resource_path=None):
        super(ContactCollection, self).__init__(context, Contact, resource_path)

    def add(self, given_name, surname, email_address=None, business_phone=None, **kwargs):
        """
        Add a contact to the root Contacts folder or to the contacts endpoint of another contact folder.
        :param str given_name: The contact's given name.
        :param str surname: The contact's surname.
        :param str email_address: Default email address
        :param str business_phone: Default contact's business phone number.
        :rtype: Contact
        """
        def _create_email_address(address):
            return EmailAddress(address, "{0} {1}".format(given_name, surname))

        kwargs["givenName"] = given_name
        kwargs["surname"] = surname
        if email_address:
            kwargs["emailAddresses"] = ClientValueCollection(EmailAddress,
                                                             [_create_email_address(email_address)])
        if business_phone:
            kwargs["businessPhones"] = StringCollection([business_phone])
        return super(ContactCollection, self).add(**kwargs)

    def __getitem__(self, key):
        """
        :param int or str key: Contact identifier or index
        :rtype: Contact
        """
        return super(ContactCollection, self).__getitem__(key)
