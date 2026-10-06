# The custodian's activity

A custodian keeps two records of an account: what it holds, and what happened
to it. A statement is the first: the street store keeps it, and the [book of record](the-book-of-record.md) is reconciled
with it. From contract v14 a custody plugin also reports the second, each
**activity** on the account as the custodian states it: a purchase, a sale,
a reinvested dividend, a dividend or interest, a fee or a tax, a split or
another corporate action, a transfer, a contribution, a withdrawal or a
journal. An `operations` plugin reads it, matches a break to the activity
that explains it, and proposes the adjustment for a person to confirm.

The rule is the book's own. **Activity is evidence that explains a break,
never a source.** The street keeps it as reported and derives no position,
lot or cash figure from it, and nothing moves the book until a person
confirms an entry. Nothing here books income: a reinvested dividend is
proposed as the lot it bought, no more.

!!! note "Released 2026-10-05"
    This page describes open-meridian 0.19.0 (contract v14), on PyPI, with
    CLI 0.1.34, the runtime chart 0.1.262, the SnapTrade plugin 0.11.1 and
    the sample operations plugin 0.8.1. The data dictionary marks the rows
    v14 adds `preview` in the contract. A plugin built on 0.19.0 is refused
    by a runtime serving v13, naming both versions.

Without it, every money market fund's monthly dividend, every split and
every fund bought in a retirement plan under the plan's own code shows as a
break a person explains by hand, while the custodian's own record of the
cause sits unread.

## What a custody plugin reports

One activity at a time, with
[`record_activity`](../api/typed-operations.md#record_activity), each as the
custodian states it:

| | What it carries |
|---|---|
| **Its identifier** | The custodian's own identifier for the activity, `external_activity_id`: never a time or a random value. |
| **Its kind** | One of the fourteen kinds below, converted by the plugin from the custodian's own type. |
| **Its instrument** | Resolved at the edge as a holding's is, or the currency's cash instrument. Empty where the activity concerns none. |
| **Its dates** | The trade date, when it was traded or took effect; the settlement date where the custodian states one. |
| **Its numbers** | The units it moved, the price where stated, and the cash it moved in its currency, each an exact decimal. |
| **Its description** | The custodian's own words, for a person. Nothing branches on them. |
| **Where it came from** | The raw record it was converted from, in the plugin's own storage, and the provenance of each value the plugin closed rather than read. |

Units are signed by what the activity did to the account, positive for units
added (a purchase, a reinvestment, the units a split added, a transfer in)
and negative for units removed (a sale, a fee taken in units, a transfer
out). The amount is signed by what it did to the account's cash, positive in
and negative out. A value the custodian did not state is left unset, never
zero: a split moves no cash, and a cash dividend moves no units. A price is
never worked out from the amount and the units.

Activity is never netted or deduplicated against holdings. A sweep fund's
purchases are reported as the custodian lists them, each one.

### The kinds

| Kind | What happened |
|---|---|
| Purchase | Units bought. |
| Sale | Units sold. |
| Reinvestment | Income the custodian reinvested in units, as a money market fund's monthly dividend is. |
| Dividend | A dividend paid in cash. |
| Interest | Interest paid in cash. |
| Fee | A fee, in cash or in units. |
| Tax | A tax withheld or paid. |
| Split | A split: the units it added or removed. |
| Corporate action | Another corporate action, as the custodian states it. |
| Transfer in, transfer out | Units or cash moved in from, or out to, another account. |
| Contribution, withdrawal | Cash paid into, or taken out of, the account. |
| Journal | A movement between the account's own positions or sub-accounts, as the custodian journals it. |

The list is closed and in the platform's own words. A custodian's type that
converts to none of them is sent as not known, with the custodian's type
beside it as reported, for a person to map. The same holds for an
instrument: a retirement plan's own fund code, a code only the plan uses for
the fund it holds, travels as reported when it does not resolve. An admin of
the plugin can link such a code to an instrument once, in a table on its
own tab beside the plugin's Settings (see
[A table setting](../how-to/set-a-plugins-settings.md#a-table-setting)), and
from then on it resolves to that instrument, with that person, and when they
linked it, named as where the value came from. From contract v15 the
activities recorded under the code before it was linked are re-resolved,
each kept as first recorded: see [An activity re-resolved](#an-activity-re-resolved).

### Sent twice, kept once

The street keeps an activity once, by its source, its account and the
custodian's identifier. Sent again, it is answered as already recorded, with
the first one's identifier, and announced once. A retry, a restart or a
backfill run again therefore records nothing twice, and the plugin needs to
remember nothing to make it so. A custodian restating an activity under a new
identifier has made a new one: it is reported, never merged, and a person
decides which applies.

An activity on an external account nobody has linked is refused, as a
holding is, and nothing is recorded. The plugin reports that account's
activity once it is linked.

### How far back: `history_from`

Each sync status a custody plugin reports says from when the source can read
the account's history, `history_from`, beside how fresh that history is. The
first time the plugin reads a linked account, it reports every activity back
to that date: a **backfill**. After that, it reports each sync's new
activity.

The street records each one with its own time, the moment it heard it,
never back-dated: an activity's own time is its trade date. So a backfill of
two years of history is two years of activity, each recorded today.

## An activity re-resolved

!!! note "Built, not released"
    This section describes a runtime serving contract v15 and open-meridian
    0.20.0, built and not yet released. Both rows are `preview` in v15.

An activity is recorded once, and sent again it is answered as already
recorded and changes nothing. So an activity recorded before its
instrument resolved would otherwise keep the custodian's code for good: a
backfill of a 401(k)'s history recorded before anyone linked the plan's
code `OQKR` to its fund, or a symbol the deployment's instrument records
complete later.

From contract v15 a custody plugin **re-resolves** such an activity
([`re_resolve_activity`](../api/typed-operations.md#re_resolve_activity)):
it names the activity as it was recorded (its source, its account and the
custodian's identifier), the instrument it now resolves to, how it was
resolved (the link and the person who set it, or the rule), and when that
was made. The street keeps the activity as first recorded, which never
changes, and the re-resolution beside it as **a record of its own**, with
its own time, never back-dated. Both stay visible: what the custodian said,
and what resolved it later, by whom.

- **The latest resolution is the instrument.** An activity's instrument is
  its latest re-resolution's, or its own where there is none. A link removed
  is re-resolved to no instrument, and the activity is unresolved again,
  its code as first reported.
- **Sent again, kept once.** A re-resolution naming what the latest
  resolution already names is answered as already recorded, so a plugin
  re-resolves an account's activities again whenever what resolves them
  changes, and records nothing twice.
- **Only what was recorded.** A re-resolution of an activity never recorded
  is refused, naming it: a re-resolution resolves nothing into existence.
- **Operations reads both.**
  [`list_activities`](../api/typed-operations.md#list_activities) answers
  each re-resolution beside the activities, and `operations` hears each as
  it is recorded and catches up from that read after a gap, so a break
  waiting on its cause can be compared again.

## The street keeps each sync status

From contract v14 the street also hears every sync status a custody plugin
reports, and keeps each as a record of its own, as it keeps an activity.
`operations` reads them
([`list_sync_statuses`](../api/typed-operations.md#list_sync_statuses)) and
hears each as it is kept, so it can tell a connection that **needs a person
to sign in again** apart from data that is merely old: the two look the same
on a holdings screen, and ask different things of different people.

A connection's record begins with the first sync status the street heard for
it; before that moment its sync status is not known, and the street records
that once, per connection. A sync status for an external account nobody has
linked is kept with no account: it reaches no plugin, and the dashboard alone
shows it.

## How operations explains a break

How a plugin matches is its own behaviour, as reconciling is. The contract's
`operations` suite asks for a reinvestment and a split each to explain the
units they added, for activity heard after a break to bring it up to date,
and for activity to book nothing by itself. What follows is what the sample
operations plugin 0.8.0 does.

When an `operations` plugin finds a difference in a security's units, it
reads the account's activity
([`list_activities`](../api/typed-operations.md#list_activities)) since the
last statement it reconciled before the difference was first seen, and looks
for an activity on the same instrument whose units are exactly the
difference. What it finds becomes the break's candidate cause, linked to the
activity by value, the most specific first:

| The activity | The candidate cause |
|---|---|
| A reinvestment | **Income reinvested**, a cause category of its own from contract v14: income the custodian reinvested in units that the book has not booked. |
| A split, or another corporate action | **Corporate action**, the activity linked, where before the plugin could say only that it found none. |
| A purchase or a sale | **Unbooked trade**: a trade made away from the platform. |
| A fee or a tax taken in units | **Unbooked trade**, the cause already offered for units removed, the activity linked. |

The link names the activity by value: its identifier, its record in the
street and its trade date. The book records it as given, and reads no other
store to check it, as it records a street record's reference.

Activity often arrives after the holdings it explains. The plugin hears each
activity as it is recorded, and compares the account's statement again, so
a break with no cause yet is brought up to date with the activity that
explains it. An activity that explains no open break changes nothing.

## What it proposes

A person confirms the cause, then resolves the break with an entry. Where
the cause links an activity whose units are the whole difference, the
adjustment the plugin proposes comes from that activity, names it (the
adjustment's `event_reference` is the activity's identifier), and says so in
its reason:

- **A reinvestment or a purchase** opens one specific lot: its units, the
  amount paid and its trade date, as the custodian states them.
- **A split or another corporate action** carries the book's lots through,
  each by its share of the units the custodian added, in proportion to its
  units, its cost and acquisition date unchanged. It is never a ratio worked
  out from prices. Where the units do not divide exactly among the lots, the
  person says how many each lot gained.
- **A sale, or a fee or tax taken in units**, relieves the lots the
  custodian says it reduced. Where the custodian names none, the plugin
  **asks the person** which lots, showing them in a table, adding up to the
  units taken. It never relieves first in, first out, and never by the
  account's default method.

A lot is specific: one purchase, its units, its amount and its date, as the
source states them. Nothing multiplies an average price by a quantity, and no
lot is proposed whose cost nothing states: the person supplies what is
missing, with its source.

## The opening balance's lots

An account enters the book with an opening balance a person confirms, and
every position in it needs its lots. Where the street lists no lots for a
long position, the opening draft proposes them from the activity: one lot
per purchase or reinvestment on or before the opening balance's date,
carried through any split the custodian states. Fractional shares bought by
notional orders, or shares bought in several lots, each become a lot of
their own.

It proposes them only when those activities account for the whole position
and nothing else moved it. Each lot names the activities it came from as its
source, and the person accepts it as offered, recorded as accepted by them,
or changes it with a source of their own. Otherwise it proposes none, and
says why: how much of the position the activity accounts for, and from when
the custodian's history reaches, so an opening balance older than the
history says so.

## In the plugins

### SnapTrade 0.11.0

[meridian-snaptrade](https://github.com/open-meridian/meridian-snaptrade)
reports each activity on every linked account as SnapTrade states it: on an
account's first read in a process, a backfill of every activity SnapTrade
holds back to its `history_from`, and on each read after, the activities that
read fetched. Because the street keeps each once, a restart's backfill
records nothing twice. It maps SnapTrade's types onto the kinds:

| SnapTrade | Kind |
|---|---|
| `BUY`, `SELL` | Purchase, sale |
| `REI` | Reinvestment |
| `DIVIDEND`, `INTEREST`, `FEE`, `TAX`, `SPLIT` | The kind of the same name |
| `STOCK_DIVIDEND` | Corporate action |
| The asset and cash transfers, in and out | Transfer in, transfer out |
| `CONTRIBUTION`, `WITHDRAWAL` | Contribution, withdrawal |
| `JOURNALED` | Journal |
| Anything else, such as an option's expiry | Not known, with SnapTrade's type as reported |

An activity naming a security the account holds is resolved by that
holding's identifiers. A plan's own fund code a person has linked resolves
to its instrument, that person named as its provenance (see
[SnapTrade: plan-code links](../how-to/set-a-plugins-settings.md#snaptrade-plan-code-links));
any other code
travels as reported, so an old activity naming a security the account no
longer holds mints no instrument record. Each reported activity's raw record
is kept seven years, so the record behind every activity the street holds
can be read back on the plugin's **Raw responses** tab. Its sync status
carries `history_from`, the first transaction SnapTrade holds for the
account.

### SnapTrade 0.12.0: a plan code linked later

!!! note "Built, not released"
    SnapTrade 0.12.0, on open-meridian 0.20.0 (contract v15), is built and
    not yet released.

From 0.12.0 SnapTrade [re-resolves](#an-activity-re-resolved) the
activities it reported under a plan's own code before anyone linked it.
When a person adds or changes a row on **Plan-code links**, the account the
row names is backfilled again on the read that change wakes, and each
activity the street already holds under a linked code on that account is
re-resolved through the link: to the instrument record the row names,
supplied by the person who added or last changed the row, at the time the
row says it was changed, never when the plugin happened to read it. The
street keeps each activity as first recorded and the re-resolution beside
it.

- **On start**, the first backfill does the same for every current link.
- **Nothing twice.** The street answers already recorded a re-resolution
  naming what an activity's latest resolution already names, so a restart,
  a settings delivery again, or an activity first recorded through the same
  link re-resolves nothing twice, and the plugin holds nothing to remember
  it by.
- **A row removed sends nothing.** The activities it re-resolved keep their
  latest resolution.
- A row saying no time it was changed re-resolves nothing, and the read
  says why.

Each backfill's log line counts the activities re-resolved through a
plan-code link. SnapTrade holds one role, so access per role changes nothing
of its pages or settings.

### The sample operations plugin 0.8.0

The sample operations plugin, the reference `operations` plugin, does what
the two sections above describe: it matches a break to the activity that
explains it, proposes the adjustment from it, and offers an opening
balance's lots from the purchases and reinvestments in the account's
history. A break's page is in tabs (**Break**, **Cause**, **Handling**,
**Resolve** and **Close**), and shows the activity a cause links. Its Summary
says when an account's connection needs sign-in, from the sync statuses the
street keeps.

## Related

- [Report the custodian's activity](../how-to/report-the-custodians-activity.md):
  what a custody plugin sends, and what an operations plugin reads, with the
  SDK.
- [The book of record](the-book-of-record.md): breaks, their causes, and how
  a person resolves them.
- [Typed operations](../api/typed-operations.md#record_activity): every
  argument of `record_activity`, `list_activities`, `list_sync_statuses`
  and, from contract v15, `re_resolve_activity`.
- [The street](../boundaries/street.md#meridian.v1.CustodialActivity): each
  field of an activity in the data dictionary.
