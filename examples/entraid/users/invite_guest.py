"""
Invite an external (B2B) guest user.

Sends an invitation to an external email address. The invited user will
receive an invitation email and must redeem it to access resources.

https://learn.microsoft.com/en-us/graph/api/invitation-post

Requires delegated permission ``User.Invite.All``
or ``User.ReadWrite.All``.
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient(tenant=test_tenant).with_username_and_password(test_client_id, test_username, test_password)

invitation = client.invitations.create(
    invited_user_email_address="guestuser@outlook.com",
    invite_redirect_url=f"https://myapps.microsoft.com/{test_tenant}",
).execute_query()

invited = invitation.invited_user
print(f"Invited: {invited.mail if invited else invitation.invited_user_email_address}")
print(f"Redeem URL: {invitation.invite_redeem_url}")
