# Data age and liveness

A price is only as good as it is recent. A quote that has not changed for
a minute may still be the market, if its stream is alive and sends only on
change, or it may be a feed that stopped. This page explains how a
deployment tells the two apart: a dataset's **liveness**, its **declared
delay**, its **staleness threshold**, the **trading sessions** staleness
counts in, and the `ems`'s check of its reference price before it places.

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
| **Warn** | The placement is sent, carrying its `StaleReference`. The book records it with the condition `PLACEMENT_CONDITION_SENT_ON_STALE_REFERENCE`, a record of the warning |

The book refuses nothing for staleness: the check, its ceiling and the
choice are the `ems`'s, and the book records what it did. Both the hold's
cause and the warning are read typed, never from words. A cause on any
condition but held is refused `invalid`, naming `hold_cause`.

## Latency: recorded, not yet reported

A data or connectivity plugin on SDK 0.32 **records** its sessions'
latency (round trip, a venue's order acknowledgement and fill delay, each
dataset's feed delay, gaps, reconnects, its send backlog and clock skew) as
histograms, and an `ems` records the age of what it checks. Its connection
page's **Sessions** section shows each session's p50, p95 and p99 over the
last minute, and its plugin admin's **Session ceilings** setting holds each
session's ceilings.

**Nothing is reported to core yet.** Core receives `ReportLatency` from
contract 28: until then the SDK sends nothing, and no breach opens a
notice. The three suite cases about it, the data suite's
`reports-its-feed-delay`, connectivity's `reports-a-sessions-round-trip`
and the ems's `reports-its-pre-trade-checks-data-age`, carry the marker
`about: latency`: a contract-27 plugin marks them **not presented until
contract 28**, with the reason "core receives ReportLatency from contract
v28, ruling 515". In contract 28 the marker comes off and they are
required in full.

## Not built yet

These wait for contract 28:

- **Core's latency monitor**: receiving each plugin's latency, judging
  breaches, its notices in the inbox, the Summary's latency part, the
  **Data sources** page's data age, and the tool reading it.
- **Core's own hops' age**, each plugin's consumer lag, and the backlog
  alarm.
- **The analytics component's check at use**: a job's ceiling per source, a
  figure's oldest input and a stale figure's age. Today a job sets no
  ceiling, and `PRICE_STALE` does not arise from one.
- **What a deployment admin permits** of the `ems`'s stale-reference
  actions. Until then the `ems`'s plugin admin chooses, refuse by default.
- **Quality states**: a value's assessment and quarantine.

## Related

- [Set staleness thresholds and the stale-reference action](../how-to/set-staleness-thresholds.md).
- [The lake](the-lake.md): datasets, reads and who reads what.
- [Settlement calendars](settlement-calendars.md#trading-sessions):
  trading sessions.
- [The order lifecycle](the-order-lifecycle.md): holds and placements.
