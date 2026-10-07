# Report the custodian's activity

From contract v14 a custody plugin reports each activity on an account as the
custodian states it, beside the statements it already reports, and an
operations plugin reads it to explain a break and propose its adjustment.
This page shows what each side does, with
[meridian-snaptrade](https://github.com/open-meridian/meridian-snaptrade)
0.11.0 as the worked example of a custody plugin. Why activity is evidence and
never a source, and what operations does with it, is in
[The custodian's activity](../concepts/the-custodians-activity.md).

!!! note "Released 2026-10-05"
    This page describes open-meridian 0.19.0 (contract v14), on PyPI, with
    CLI 0.1.34, the runtime chart 0.1.262 and the SnapTrade plugin 0.11.1.
    The data dictionary marks the rows of `record_activity`,
    `list_activities` and `list_sync_statuses` `preview` in the contract.
    The re-resolution, contract v15 and open-meridian 0.20.0, is released
    with the runtime chart 0.1.268 and the SnapTrade plugin 0.12.0; its two
    rows are `preview` in v15.

## Say how far back the history reaches

Each sync status says from when the source can read the account's activity,
as an ISO 8601 date, beside how fresh the history is. Report it as it
changes, with `state` saying what holds:

```python
await plugin.report_sync_status(
    source="myvendor",
    external_account_id="acct-1",
    state=meridian.SyncState.SYNC_STATE_CURRENT,
    connection_healthy=True,
    history_as_of_ns=history_synced_ns,
    history_from="2024-06-03",   # the first day of the account's history the vendor holds
)
```

The street keeps every sync status it hears, so an operations plugin can tell
`SYNC_STATE_NEEDS_SIGN_IN`, a person must sign in again at the venue, apart
from data that is merely old. SnapTrade sends the first transaction date it
holds for the account.

## Convert each activity

Convert the vendor's type into one of the fourteen
[`ActivityKind`](../api/typed-operations.md#activitykind)s. A type that
converts to none is sent as not known, with the vendor's type beside it as
reported:

```python
from decimal import Decimal
import meridian
from meridian import edge

KINDS = {
    "BUY": "purchase", "SELL": "sale", "REI": "reinvestment",
    "DIVIDEND": "dividend", "INTEREST": "interest", "FEE": "fee", "TAX": "tax",
    "SPLIT": "split", "CONTRIBUTION": "contribution", "WITHDRAWAL": "withdrawal",
    "JOURNALED": "journal",
}
ADDS, REMOVES = ("purchase", "reinvestment"), ("sale", "fee", "tax")


def money(value: str | None, currency: str) -> meridian.Money | None:
    number = Decimal(value or "0")
    return meridian.Money(number, currency) if number else None   # the vendor's 0: not stated


def activity_of(account: str, row: dict, instrument_id: str) -> meridian.CustodialActivity:
    kind = KINDS.get(row["type"])
    units = Decimal(row.get("units") or "0") or None                # the vendor's 0: not stated
    if units is not None and kind in ADDS:
        units = abs(units)                                          # signed by what it did to the account
    elif units is not None and kind in REMOVES:
        units = -abs(units)
    return meridian.CustodialActivity(
        external_activity_id=row["id"],
        kind=kind,
        kind_as_reported=None if kind else edge.as_reported("myvendor:activity-type", row["type"], row["type"]),
        instrument_id=instrument_id,
        trade_date=row["trade_date"],
        settlement_date=row.get("settlement_date") or "",
        units=units,
        price=money(row.get("price"), row["currency"]),
        amount=money(row.get("amount"), row["currency"]),
        description=row.get("description", ""),
        raw_record=plugin.raw_record(f"activities/{account}/{row['id']}"),
    )
```

- **Signs.** Units are positive for what the activity added to the account
  and negative for what it removed, whatever sign the vendor wrote; the
  amount is positive for cash in and negative for cash out.
- **A value not stated is unset, never zero.** A split moves no cash and a
  cash dividend moves no units. Never work a price out from the amount and
  the units.
- **The instrument** is resolved at the edge as a holding's is. Where a code
  does not resolve, such as a retirement plan's own fund code, leave
  `instrument_id` empty and send the code with
  `instrument_as_reported=edge.as_reported(...)`. Where a person has linked
  that code to an instrument, send the instrument with
  `provenance=[edge.supplied("instrument_id", person)]`, naming them. Take the
  link from a [table setting](set-a-plugins-settings.md#declare-a-table-setting-and-read-its-rows)
  an admin fills on its own tab beside the plugin's Settings, whose rows
  carry who changed each and when; the plugin never sets it. SnapTrade
  resolves a code only by a security the account holds, so an old activity
  naming one it no longer holds mints no instrument record.
- **Report each activity as listed.** Never net or merge them against
  holdings, or with each other: a sweep fund's purchases are each their own.

## Send each one, once

```python
try:
    reply = await plugin.record_activity(
        external_account_id="acct-1", source="myvendor", activity=activity_of("acct-1", row, instrument_id),
    )
except meridian.NotLinked:
    ...  # nobody has linked acct-1: report its activity once it is linked
```

The `external_activity_id` is the vendor's own identifier for the activity,
never a time or a random value. Sent again, the activity is answered
`already_recorded`, with the first one's `activity_id`, and recorded once, so
a retry, a restart or a resync is safe and the plugin keeps nothing to
remember what it sent. A vendor restating an activity under a new identifier
has made a new one: report it, and never merge it with the first.

**Backfill, then each sync.** The first time the plugin reads a linked
account, report every activity back to the `history_from` its sync status
names, page by page; then report each sync's new activity. SnapTrade
backfills on an account's first read in each process, up to 50 pages of
1,000, and reports the ten days each read fetches after that; the street
answers what it already holds as already recorded. The street records each
activity with its own time, never back-dated, and its trade date stays the
activity's.

## Re-resolve an activity once its instrument resolves

From contract v15 (open-meridian 0.20.0). An activity recorded before its
instrument resolved, such as one under a plan's own code a person links
later, is re-resolved, never sent again: sent again it would be answered
`already_recorded` and change nothing.

```python
reply = await plugin.re_resolve_activity(
    external_account_id="acct-1",
    source="myvendor",
    external_activity_id=row["id"],            # as first reported
    instrument_id=linked_instrument_id,        # empty where the link was removed
    provenance=meridian.Provenance(field="instrument_id",
                                   kind="PROVENANCE_KIND_SUPPLIED",
                                   person=link_row["changed_by"]),
    resolved_at_ns=changed_at_ns,              # the row's changed_at, as nanoseconds
)
reply.already_recorded   # True where the latest resolution already names it
```

- **Name what resolved it.** The provenance is supplied, naming the person
  who set the link (a table setting row's `changed_by`), or derived, naming
  the rule; never the custodian's word, which the street refuses.
  `resolved_at_ns` is when that was made: the row's `changed_at`, or when
  the rule ran.
- **Re-resolve an account's activities whenever what resolves them
  changes:** a link added, changed or removed. The street keeps each
  activity as first recorded and each re-resolution beside it, and answers
  one naming what the latest already names `already_recorded`, so running
  it again records nothing twice and the plugin remembers nothing.
- **A link removed** is re-resolved with an empty `instrument_id`: the
  activity is unresolved again, its code as first reported.
- **Only what was recorded.** One naming an activity never recorded under
  that source, account and identifier is refused, naming it.

## Keep its raw record as long as the history

Each activity names the raw record it was converted from. Give each its own
key, written once, and keep it as long as the history you reported, so the
record behind every activity the street holds can always be read back on
your plugin's page. Declare that retention with the storage your version asks
for (see [Keep what your custody plugin converts](keep-what-the-edge-converts.md)).
From contract v16 (open-meridian 0.21.0, built and not yet released), declare
the activity's record as a kind of raw record of its own, with a long window,
and past it move it to the archive rather than delete it (see
[The archive](../concepts/the-archive.md)). SnapTrade 0.13.0 keeps each
activity's record, `activities/<external account>/<activity ID>`, for its
`activity_window_days`, seven years by default, never deleting one within the
history it reported, and each read's responses for its `responses_window_days`,
30 days by default.

A vendor field you receive and do not carry, such as an activity's fee or
exchange rate, is declared as not carried and counted, as for holdings.

## Pass the custody suite's activity cases

The custody suite gains twenty cases at v14: one for each kind, a type that
converts to none, signs, an activity that moves no cash, a plan's code not
linked and one linked by a person, and `history_from` stated. Map each to
your vendor's exchange, as for the rest of the suite. SnapTrade presents all
of them, none declared not presented.

At v15 it gains one more, `activity-re-resolved-when-a-plan-code-is-linked-later`:
an activity recorded with a plan's own code unresolved, then the code linked
by a person in the plugin's settings, expects a `ReResolveActivity` naming
the activity, the instrument, a supplied provenance naming the person, and
when.

## Read it from an operations plugin

An `operations` plugin reads an account's activity by trade date, and is told
from when the source can read it:

```python
page = await plugin.list_activities(account_id=account, trade_date_from=last_reconciled_date)
page.history_from   # "" where the read names no account, or the source has not said
```

It hears each activity as it is recorded, so a break waiting on its cause can
be compared again:

```python
async def activity_recorded(heard: meridian.Heard) -> None:
    each = heard.message            # an ActivityRecordedEvent
    ...                             # compare the account's statement again


await plugin.receive(activity_recorded=activity_recorded, sync_status_recorded=sync_status_recorded)
```

From contract v15 it reads and hears each re-resolution too. The activities
`list_activities` answers stay as first recorded, and its `re_resolutions`
say what resolved each later: an activity's instrument is its latest
re-resolution's.

```python
latest = {each.activity_id: each.instrument_id for each in page.re_resolutions}  # in the order recorded
instrument = latest.get(item.activity_id, item.activity.instrument_id)


async def activity_re_resolved(heard: meridian.Heard) -> None:
    re = heard.message.re_resolution   # activity_id, instrument_id, provenance, resolved_at_ns
    ...                                # compare the account's statement again


await plugin.receive(activity_recorded=activity_recorded, activity_re_resolved=activity_re_resolved)
```

A break's candidate cause links the activity that explains it by value, an
[`ActivityRef`](../api/typed-operations.md#activityref), under
`income_reinvested` for a reinvestment; and an adjustment proposed from an
activity names its `activity_id` in `event_reference`. Every entry still
waits for a person. Never relieve lots first in, first out where the
custodian names none: ask the person which.

## Move a plugin to 0.19.0 { #move-a-plugin-to-0190 }

From 0.18.0, `meridian plugin migrate` moves only the pins: `open-meridian==0.19.0`
in `pyproject.toml`, and `plugin-python:0.19.0` in the `Dockerfile`. Nothing a
plugin calls changed. What 0.19.0 adds, a plugin adds by hand:

- **A custody plugin** sends `history_from` on its sync status and reports
  each activity with `record_activity`, its raw record kept as above, and
  maps the custody suite's new cases.
- **An operations plugin** may read and hear activity and sync statuses, and
  link a cause to an activity. One that does none of this needs nothing more.

A plugin built on 0.19.0 declares contract v14, and a runtime serving v13
refuses it at registration, naming both versions: upgrade the deployment
first ([Upgrade a deployment](upgrade-a-deployment.md)), then relaunch the
plugin on the new version. A test that stands in for the SDK's private
`Operations._receive` is now handed only the rows given a handler, not every
row with `None` for the rest.

## Move a plugin to 0.20.0 { #move-a-plugin-to-0200 }

`meridian plugin migrate` moves only the pins: `open-meridian==0.20.0` and
`plugin-python:0.20.0`. Nothing a plugin calls changed. A custody plugin
that resolves activities by anything a person can change later, such as a
plan code's link, adds `re_resolve_activity` as above; an operations plugin
that reads activities reads `re_resolutions` beside them. One that does
neither needs nothing more. A plugin built on 0.20.0 declares contract v15,
and a runtime serving v14 refuses it at registration, naming both versions.
0.20.0 also brings [access per role](../concepts/access.md#access-per-role),
which changes nothing for a plugin holding one role.

## Related

- [The custodian's activity](../concepts/the-custodians-activity.md)
- [Typed operations](../api/typed-operations.md#record_activity):
  `record_activity`, `list_activities`, `list_sync_statuses` and
  `re_resolve_activity`, argument by argument
- [Keep what your custody plugin converts](keep-what-the-edge-converts.md)
