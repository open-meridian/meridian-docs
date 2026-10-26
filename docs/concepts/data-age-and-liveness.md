# Data age and liveness

A price is only as good as it is recent. A quote that has not changed for
a minute may still be the market, if its stream is alive and sends only on
change, or it may be a feed that stopped. This page explains how a
deployment tells the two apart: a dataset's **liveness**, its **declared
delay**, its **staleness threshold**, the **trading sessions** staleness
counts in, the `ems`'s check of its reference price before it places, and
the latency every data, connectivity and `ems` plugin reports to core.

## Liveness

A stream that sends only on change, or a poll that finds nothing new,
still **confirms** every value in force. A data plugin records that sign of
life for each of its datasets, and for each venue where the dataset has
one: the source's last heartbeat or poll, as `alive_at_ns`
([`record_liveness`](../api/typed-operations.md#record_liveness)).

Liveness is not a row. The lake keeps the latest per dataset and venue,
delivers it as `liveness_recorded` to the plugins that read the dataset's
prices and quotes (`reporting`, `portfolio`, `compliance`, `signal` and the
`ems`), and answers it in the datasets' listing, `DatasetRef.liveness`
([`list_datasets`](../api/typed-operations.md#list_datasets)), where a
reader that lost an event reads it again.

**A value's confirmed time** is the later of its source time and its
dataset's last liveness after it. Without liveness, an illiquid stock's
quote, unchanged for a quiet minute, would turn stale in a normal session.

## The declared delay

A delayed dataset says so in its catalogue: `declared_delay_ns`, 0 for
real time. A value from it is judged against its delay plus its threshold,
so a 15-minute delayed feed is not stale for being 15 minutes old. One
dataset is one timeliness: a vendor serving both real-time and delayed data
declares two datasets.

## The dataset's threshold

How old a dataset's values may be before a reader treats them as stale is
its data plugin admin's choice, the plugin's **Dataset thresholds** setting
(`dataset_thresholds`): each row a dataset, the asset class its default
came from, and **Stale after**, in seconds. The plugin offers a default per
asset class until its admin changes it, and each change is recorded as
every setting change is. The lake reads it by that name and answers it on
each dataset, `DatasetRef.stale_after_ns`, so every reader judges by the
same number.

**The ceiling in force** is the tighter of the dataset's and the reader's
own, and it **counts only in session**: a price unchanged over a weekend is
not stale on Monday's open.

## Trading sessions

A venue's sessions are a calendar of the kind
`CALENDAR_KIND_TRADING_SESSIONS`, curated and pulled as every
[settlement calendar](settlement-calendars.md#trading-sessions) is: its
time zone, its sessions by weekday, and its early closes, each a dated day.
`meridian.roles.in_session(sessions, at_ns)` says whether a moment falls in
one. Halts stay a quote's own `halted` characteristic.

## The `ems` checks its reference price { #the-ems-checks-its-reference-price }

Before it places, an `ems` reads its reference price's confirmed time and
judges its age against the ceiling in force: the tighter of the dataset's
threshold and its own admin's, **Stale reference after**
(`stale_reference_after`, per asset class, in seconds), a delayed dataset's
delay added, counted only in session. Past the ceiling, its admin's
**Stale reference action** (`stale_reference_action`) applies:

| Action | What happens |
|---|---|
| **Refuse** (the default) | Nothing is placed. The order is **held**, its cause typed, `HOLD_CAUSE_REFERENCE_PRICE_STALE`, with the `StaleReference` found: the dataset, the price's age and the ceiling. A person, or an agent where the admins allow, places again once the price is fresh |
| **Warn** | Only where the deployment [permits it](#what-a-deployment-admin-permits). The placement is sent, carrying its `StaleReference`. The book records it with the condition `PLACEMENT_CONDITION_SENT_ON_STALE_REFERENCE`, a record of the warning |

The book refuses nothing for staleness: the check, its ceiling and the
choice are the `ems`'s, and the book records what it did. Both the hold's
cause and the warning are read typed, never from words. A cause on any
condition but held is refused `invalid`, naming `hold_cause`.

## Latency, reported to core { #latency }

Changed in contract 28. A data or connectivity plugin records its sessions'
latency (round trip, a venue's order acknowledgement and fill delay, each
dataset's feed delay, gaps, reconnects, its send backlog and clock skew) as
histograms, and an `ems` records the age of what it checks. From SDK
0.33.0 the SDK **reports** them to core every 10 seconds
([`report_latency`](../api/typed-operations.md#report_latency)), with the
ceilings in force from its plugin admin's **Session ceilings** setting. Its
connection page's **Sessions** section shows each session's p50, p95 and
p99 over the last minute, as before.

Core's own components report their hops the same way: each plugin's
sidecar its sidecar hop (a record batch accepted) and bus hop (a row
delivered), the lake its lake hop, and the analytics component its hop on a
job read at now. A daily value's age is its date's, so core measures the
hops of trades and quotes only.

**Core's latency monitor** merges what it receives, per minute for 7 days
and per hour for 30. Latency is a measurement, not a record: nothing is
journalled, and a restart begins the window again.

**Breaches.** The monitor judges each whole minute. A minute with
measurements is in session; it is **over** where its p99 is above the
ceiling, or more than three standard deviations above the series' own
in-session minutes of the trailing 7 days (with at least 20 of them). Three
minutes over in a row open a **latency episode**, and three clear close it.
A send backlog's peak past its ceiling opens a **backlog episode**, and the
first minute under closes it.

**Notices.** Each opening and each closing is one notice, its own record,
read in the **Inbox** and through `dashboard__read_inbox`
(`latency_notices`): `latency_breached`, `latency_recovered`,
`backlog_breached` or `backlog_recovered`. They go to each of the plugin's
admins and, for a connectivity plugin's session, to the admins of the `ems`
it is linked to; a core component's own hop is no plugin's, so its episodes
go to the deployment admins.

**Where you see it.**

- A plugin's **Summary**: its Status carries one latency line, "Breached
  since HH:MM UTC" while an episode is open, or "Within ceilings, p99 N ms",
  its title naming the series and the date.
  `dashboard__read_plugin_summary` answers its `latency` part: each series
  with its ceiling and its open episodes.
- The **Data sources** page's **Age** tab, a deployment admin's: a line per
  dataset and hop, and per plugin session and metric, over the last minute,
  p50, p95 and p99, the plugin that measured it, the session's last sign of
  life and its backlog's peak; searched and paged.
  `dashboard__read_data_age` answers the same.

The suite cases about latency, the data suite's `reports-its-feed-delay`,
connectivity's `reports-a-sessions-round-trip` and the ems's
`reports-its-pre-trade-checks-data-age`, are required of every plugin
holding the role from contract 28.

## What a deployment admin permits { #what-a-deployment-admin-permits }

Added in contract 28. Whether an `ems`'s admin may choose **Warn** at all is
the deployment's: a deployment admin's **Stale reference actions
permitted**, on the dashboard's settings home page (`/admin#stale-reference`),
**Refuse only** (the default) or **Refuse or warn**, its last change
shown. Each change takes a reason, can be prepared
for a person to make, and is its own record. An `ems` reads it at its own
role, with no person
([`read_stale_reference_actions_permitted`](../api/typed-operations.md#read_stale_reference_actions_permitted));
the SDK's `ems.ReferenceCheck.permitted` reads it, and honours **Warn** only
where it is permitted, refusing otherwise. Through an agent:
`dashboard__read_stale_reference_actions_permitted` and
`dashboard__set_stale_reference_actions_permitted`.

## Not built yet { #not-built-yet }

- **The analytics component's check at use**: a job's ceiling per source,
  a figure's age and ceiling, and a stale figure. Today a job sets no
  ceiling, and `PRICE_STALE` does not arise from one. A model figure names
  its oldest input's source time.
- **Each plugin's consumer lag and its conflation counts**, and the page
  hop's age.
- **Quality states**: a row's assessment and quarantine, which core serves
  in a later chart release on contract 28 (see
  [The lake: what core does not serve yet](the-lake.md#not-served-yet)).

## Related

- [Set staleness thresholds and the stale-reference action](../how-to/set-staleness-thresholds.md).
- [The lake](the-lake.md): datasets, reads and who reads what.
- [Settlement calendars](settlement-calendars.md#trading-sessions):
  trading sessions.
- [The order lifecycle](the-order-lifecycle.md): holds and placements.
