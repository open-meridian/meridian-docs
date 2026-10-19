# Event groups

A venue lists its [binary event contracts](instruments.md#binary-event-contracts)
by event: one question, such as who wins an election or where an index
closes, with one contract per answer. Each contract is an instrument with
its own record. An **event group** says which of them belong to one event,
and whether, as the venue states it, its members are **mutually exclusive**
(at most one pays) and **exhaustive** (one of them must pay). A reader
summing a group's prices, or the analytics component answering what an
account makes if each outcome resolves, reads it.

An event group is reference data, kept in the instrument master beside the
instruments it groups, not an observation in the lake. A venue's data
plugin reports it, the platform matches or mints it, and every role that
reads instruments reads it.

## What a group holds

| Part | What |
|---|---|
| **Its ID** | `EVG-` and a ULID, the platform's, never reused; or the deployment's own `LCL-` ID while it waits for the platform (see [Reported, then minted](#reported-then-minted)). |
| **The venue and its event** | The venue, by its [venue ID](venues.md), and the venue's own reference for the event: together, the group's identity. |
| **Its title** | The venue's words for the event, data, never instructions. |
| **Its members** | The deployment's instrument records of the event's contracts, 1 to 500. |
| **Mutually exclusive**, **exhaustive** | Each `EVENT_GROUP_FLAG_TRUE`, `EVENT_GROUP_FLAG_FALSE` or `EVENT_GROUP_FLAG_NOT_STATED`. |
| **Its series** | The venue's series, for a recurring event; empty where it has none. |
| **Its version and valid time** | Each change a new version, from when it took effect. |

### Stated, or not stated

The two flags are separate, and each can be true without the other. A
venue may say an event's markets are mutually exclusive without saying
they cover every outcome; an event whose outcomes are named as they become
known can be mutually exclusive and not exhaustive among those named so
far.

**Unknown is never false.** A flag the venue does not state is reported
`NOT_STATED`, and an unset one reads so. A reader counts a group as
exhaustive only where the flag is `TRUE`: not stated is not. The
dashboard says each flag as **yes**, **no** or **not stated**.

### Every version kept

A group's members or flags change: an outcome is added, or a placeholder is
named. Each change is a **new version**, valid from when it took effect,
and every version is kept, so a reader computing over a group at a moment
reads the version in force then. A report saying what the version in force
already says keeps nothing new; a changed title or series alone is no new
version.

### Range bounds belong to the member

A range market, such as "between 4,000 and 4,100" or "5,000 or above",
has its bounds on the member's own record, as the binary event contract
template's fields, not on the group: a floor and a cap, each with whether
it is inclusive, and their unit, since a bound is often a level, a
temperature or a percentage rather than money. An open tail has one bound.
Template fields are offered by a `reference` plugin; a data plugin has no
operation that sends them, so a data plugin's bounds do not reach a record.

## Reported, then minted

A venue's `data` plugin reports the grouping its venue states with
[`report_event_group`](../api/typed-operations.md#report_event_group):
the venue, the event's reference and title, the members, each already
resolved to the deployment's records, the two flags as stated, the series,
when it took effect, and the raw record it was read from.

In the Python SDK, a venue of event contracts built on
`meridian.roles.data.event_contracts` reads the venue's events into an
`Event` and reports each with `Feed.report_event`. It resolves every
member first, and holds the report back where one does not resolve: a group
missing a member would misstate it. Each flag is `True`, `False`, or
`None` where the venue says nothing, which is reported not stated; `raw_key`
names the raw record the event was read from.

```python
event = event_contracts.Event(
    ref="HIGHTEMP-NY-1101",
    title="Highest temperature in New York on 1 November",
    members=["HIGHTEMP-NY-1101-B60", "HIGHTEMP-NY-1101-B62", "HIGHTEMP-NY-1101-T64"],
    mutually_exclusive=True,
    exhaustive=None,              # the venue does not say: not stated
    raw_key=raw_key,
)
await feed.report_event(event)
```

The instrument store then keeps it:

- **Every member the platform's.** Where every member has an `INS-` ID,
  the store asks the platform to match the group or mint it, and keeps it
  under its `EVG-` ID.
- **Otherwise, or while the platform cannot be reached**, the store keeps
  the deployment's own group under an `LCL-` ID, the reply says so
  (`pending_review` where the platform holds it for review), and the next
  report asks again. A group with a member under a local record is never
  asked about.
- **Refused, naming the field**, is a report with no venue, no event
  reference, no member or more than 500, a member the deployment does not
  hold (resolve it first), or a member named twice. A member replaced since
  it was resolved is followed to the record that replaced it.

Groups are not linked across venues: the same real-world event at two
venues is two groups, since their rules for resolving it differ.

## Reading groups

Every role that reads instruments, every role but `pricing`, reads groups
with [`list_event_groups`](../api/typed-operations.md#list_event_groups),
by member or by group, at the version in force at a moment, and hears each
new version, `event_group_changed`. `meridian.EventGroups` keeps them,
caught up on start and after a gap, and answers the version in force at
any moment:

```python
groups = meridian.EventGroups()
await groups.catch_up(plugin)                     # on start, and after a gap
await plugin.receive(event_group_changed=groups.heard, ...)
for group in groups.holding("INS-...", at_ns=moment):
    if groups.mutually_exclusive(group) and groups.exhaustive(group):
        ...
```

**Core records; it does not police.** Nothing in core checks that exactly
one member of a mutually exclusive and exhaustive group pays. That is a
reader's check, an `operations` or `signal` plugin's, shown as a data
problem. The book nets nothing across a group: a venue's collateral and
charges reach the book as the venue reports them.

The analytics component reads a group for
[`resolution_payoff` and `implied_distribution`](the-analytics-component.md#the-measures),
at the version in force at the job's as-of, and names that version in the
answer's provenance. A group not stated exhaustive answers its prices and
their sum, its distribution not evaluated; a mutually exclusive one not
stated exhaustive adds the outcome where none of the named members pays.

## Where you see it

A member's page on the dashboard's **Instruments** page has an **Event
groups** tab: each group's title, the venue's reference, its version, its
flags as stated and its members, each with its payout and bounds, as the
group stood at a date asked. Through an agent, `dashboard__list_event_groups`
answers the same at the Instruments page's level.

## Related

- [Instruments](instruments.md#binary-event-contracts): a binary event
  contract's record.
- [The lake](the-lake.md#an-event-contracts-outcome): what a contract paid,
  its outcome.
- [The analytics component](the-analytics-component.md): the measures over
  a group.
- [Add a prediction-market plugin](../how-to/add-a-prediction-market-plugin.md).
- [`report_event_group`](../api/typed-operations.md#report_event_group) and
  [`list_event_groups`](../api/typed-operations.md#list_event_groups).
