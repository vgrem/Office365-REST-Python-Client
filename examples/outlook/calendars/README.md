# Outlook calendars

The calendar object and everything around it: free/busy scheduling, sharing and
delegation, rooms, and calendar event housekeeping. Part of the
[Outlook tour](../README.md).

| What | File | Notes |
|------|------|-------|
| Find meeting times / free-busy | [`availability.py`](./availability.py) | `getSchedule` + `findMeetingTimes` |
| Share your calendar | [`share.py`](./share.py) | Grant another user read access |
| Delegate calendar access | [`delegate.py`](./delegate.py) | Editor / delegate rights |
| Rooms & room lists | [`rooms.py`](./rooms.py) | `places` API (`Place.Read.All`) |
| Calendar permissions report | [`permissions_report.py`](./permissions_report.py) | Who has access and what role |
| Export events to CSV | [`events_export_csv.py`](./events_export_csv.py) | Subject, organizer, attendees |
| Copy events between calendars | [`events_copy.py`](./events_copy.py) | Migration / backup |
| Find external attendees | [`external_attendees.py`](./external_attendees.py) | Outside the tenant domain |
| Clean up old events | [`events_cleanup.py`](./events_cleanup.py) | Dry-run first |

See [events/](../events/README.md) for creating and responding to individual events.
