# Team membership

Owners and members of a team are `ConversationMember` entities. A member carries
a `roles` list — `["owner"]` or `["member"]` — so "make this person an owner" is
a role change on the same object, not a separate collection. Guests appear like
any other member; they are recognisable by `#EXT#` in their UPN.

```python
team = client.teams["<team-id>"]

team.members.add("user@contoso.com", roles=["owner"]).execute_query()

for member in team.members.get().execute_query():
    print(member.display_name, member.email, list(member.roles or []))
```

Under the hood the library posts an `aadUserConversationMember` with
`user@odata.bind`; Graph rejects any other shape for Teams members.

## Scripts

| Script | What it does |
|---|---|
| [`lifecycle.py`](./lifecycle.py) | `list` · `add` · `set-role` · `remove` |
| [`guest_audit.py`](./guest_audit.py) | Teams with external guests, and who they are |
| [`audit.py`](./audit.py) | Orphaned teams (no owner) and over-owned teams |

## Common commands

```bash
python lifecycle.py list     --team <id>
python lifecycle.py add      --team <id> --user user@contoso.com --role owner
python lifecycle.py set-role --team <id> --user user@contoso.com --role member
python lifecycle.py remove   --team <id> --user user@contoso.com

python guest_audit.py
python audit.py --max-owners 5
```

`audit.py` runs both owner-hygiene checks in one membership pass: a team with
no owner is orphaned (nobody can approve requests), while a team with too many
owners has effectively handed admin rights to a crowd.

## Permissions (application)

| Operation | Permissions |
|---|---|
| List members | `TeamMember.Read.All` |
| Add / re-role / remove | `TeamMember.ReadWrite.All` |
| List teams | `Team.ReadBasic.All` |

## Reference

- <https://learn.microsoft.com/en-us/graph/api/team-list-members>
- <https://learn.microsoft.com/en-us/graph/api/conversationmember-add>
