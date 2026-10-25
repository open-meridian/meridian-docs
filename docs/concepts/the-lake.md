# The lake

The **lake** is where a deployment keeps what its data sources say: prices,
bars, trades and quotes, each as one source stated it, kept side by side,
never overwritten. A plugin holding `data` puts them in, converted at the
edge from its vendor's form. The reading roles, `reporting`, `portfolio`,
`compliance` and `signal`, read prices and bars and hear them as they are
recorded; trades and quotes are read by `signal` and `ems` alone, and an
event contract's outcome by prices' readers and `operations` (see
[Who reads what](#who-reads-what)). The lake is core's, beside the street
and the book: it is not a plugin, and nothing in it leaves the deployment.
The lake's operations are `preview`.

## Two stores, two questions

The [instrument store](instruments.md) says what something **is**: an
instrument's identity, its identifiers and its record. The lake says what
sources **say** about it: a close, a last price, a bar. Every row in the
lake names the deployment's own instruments as its subjects, resolved from
the vendor's codes before the row is recorded, never the vendor's codes
themselves. A row about an instrument the deployment does not hold is not
recorded: the plugin reports the miss, and the Data sources page counts it.

## What it holds

Twelve data types, each one message per row: prices, bars, trades, quotes,
an event contract's outcome, from contract 27 rates and execution costs,
and from contract 28 a chain's listed series and statistics, a signal's
derived series and saved scenarios, and corporate actions.

| Type | What one row is |
|---|---|
| **Price** | A price of one kind for one subject: `close` (the official close for a business date), `last` (the last eligible trade's price), `nav` (a fund's net asset value per share), `settlement`, `bid`, `ask` or `mid`. Its amount is a [Money](money-and-instruments.md), always per unit. |
| **Bar** | Open, high, low and close over an interval, in one asset, with its volume, and its VWAP and trade count where the source gives them. A daily bar names its business date. |
| **Trade** | One trade as its source reported it: its price, a [Money](money-and-instruments.md) naming its cash instrument; its quantity, more than zero; its **trade attributes**; the side that took liquidity, where the source says it; the source's own number for it. |
| **Quote** | The best bid and offer, on a venue or consolidated, each with its quantity, both sides in one asset; a side the source left empty is unset, never zero. In force until the next quote for the same subject, dataset, venue and asset. |
| **Outcome** | What an event contract pays, as its venue determined it, at one stage: see [An event contract's outcome](#an-event-contracts-outcome). |
| **Rate** | A reference rate's fixing, an average, an index level or a curve's point, its value with its unit, convention and tenor: see [Rates](rates.md). |
| **Execution cost** | One execution's cost against one benchmark, recorded by the analytics component, the lake's first row scoped to an account: see [Execution costs](execution-costs.md). |
| **Listed series** | Added in contract 28. One series of an underlying's chain, its terms as its template's fields, keyed by its OSI symbol or its ticker and MIC, never minted: see [Listed options and futures](listed-options-and-futures.md#the-chain-read-never-minted). |
| **Statistic** | Added in contract 28. A count for a trading date: a series' open interest, volume or block volume, or a share's short and total volume reported to a FINRA facility. |
| **Derived series** | Added in contract 28. A value a `signal` plugin computed from the lake, an underlying's 30-day IV say, recorded into its own dataset with the rule it used and every dataset it read: see [Derived series](#derived-series). |
| **Saved scenario** | Added in contract 28. A scenario or a scenario set a `signal` plugin saved, by its row key: see [Scenarios](scenarios.md). |
| **Corporate action** | Added in contract 28. A company's declared cash dividend, its security and its issuer each a subject: see [Companies and corporate actions](companies-and-corporate-actions.md). |

**An FX rate is a price**: the price of one currency's cash instrument in
another, EUR at 1.0842 USD, of kind `mid`, `bid`, `ask` or `close`. An FX
fixing is a dataset of closes; an interest rate is a [rate](rates.md). The
lake never inverts or crosses an FX rate: a reader converting the other
way reads the rate a source quotes that way, or inverts it itself, as the
[analytics component](the-analytics-component.md#the-pricing-models) does,
so the lake never holds a value no source stated.

**Liveness, delay and staleness** (contract 27). A dataset carries its
declared delay, its plugin admin's staleness threshold and its last sign of
life: see [Data age and liveness](data-age-and-liveness.md).

Prices are unadjusted by default.

### Trades and their attributes

A trade carries the platform's **trade attributes**, converted at the edge
from its feed's condition codes, so no reader needs a vendor's table to
build a bar:

- **Whether it may set** the high and low, the open, the close and the
  volume, once for the consolidated view and once for its own market
  centre's. Each is eligible, not eligible, or not known. It says what a
  trade may count for, not whether it did.
- **Its characteristics**, in the platform's words: an opening, closing or
  other auction print, an odd lot, extended hours, out of sequence, a late
  report, an average price, non-regular settlement, an intermarket sweep,
  derivatively priced, a prior reference price, contingent, a cross.
- **The aggressor**, the side that took liquidity, only where the source
  says it: a venue naming the resting order's side has the other recorded.
  Never guessed.

A code the plugin cannot convert travels as the source reported it, its
eligibilities not known, and is counted on the Data sources page for a
person to map. A crypto trade has no condition codes: it is regular, and
eligible for every statistic. A source correcting or withdrawing a trade
records its next version under the same row key, a withdrawal marked
`cancelled`. A quote carries what the source says of its state: indicative,
or the subject halted.

A trade's and a quote's venue is the [venue](venues.md) it printed on, by
its venue ID: a consolidated dataset's trade names the market centre it
printed on, a FINRA print its reporting facility. Both are keyed by UTC
instants and name **no business date**: see [Dates and time](dates-and-time.md).

### Derived series { #derived-series }

Added in contract 28. A `signal` plugin may record what it computes from
the lake back into the lake, as a row of its **own** dataset
([`record_derived_series`](../api/typed-operations.md#record_derived_series)):
each value names its subject, its own name for the series (`iv30`, an
index's level, a positioning summary's part), its value and unit, the
**rule** it was computed by (a definition and version, an analytics
measure's where one was used) and every dataset it read with the as-of it
read at, so the inputs' licences follow it. Its latest per series is
kept; it is never published as an event. `compliance`, `portfolio`,
`reporting` and `signal` read them
([`list_derived_series`](../api/typed-operations.md#list_derived_series)),
every readable derived dataset side by side. A signal plugin's catalogue
declares its own datasets, which serve derived series and saved scenarios
and nothing else.

## Datasets

Every row belongs to a **dataset**: one plugin instance's stream of one
kind of data from one vendor. A data plugin's version declares its datasets in
its **catalogue**, shown before it is launched and approved with it. Each
declares:

| Part | What |
|---|---|
| Key | Its name within the plugin, such as `daily`. In a deployment a dataset's ID is the instance, a colon and the key: `alpaca-1:daily`. |
| Vendor, aggregator | Who originated the data, and who carries it where an aggregator does. |
| Data types | The lake's types it serves, and the optional fields it fills, each by its [data dictionary](../boundaries/lake.md) entry: `meridian.v1.Bar.vwap`. |
| Modes | How its rows can arrive: `pull` (fetched when a read wants them), `push` (recorded on the source's own timetable) and `stream`. |
| Cadence, history | How often it updates, which says when it is silent; how far back it reaches. |
| Default licence | What the vendor's standard terms say: kept or not, derived use, display, the default fields, and whether the terms are one person's. See [Licences and entitlements](licences-and-entitlements.md). |
| Its day | The time zone a business date is in and the minute the day ends; the [settlement calendar](settlement-calendars.md) its business dates follow, by its `CAL-` ID, by which the lake flags a daily value dated on a closed day (see [A daily value on a closed day](#a-daily-value-on-a-closed-day)). See [Dates and time](dates-and-time.md). |
| Its venue | The venue the dataset is, by its [venue ID](venues.md); none for a consolidated view. |

A catalogue is checked when the version is uploaded and again when its
plugin registers: a key twice, a type the lake does not have, a zone that is
no time zone, or a catalogue on a version not holding `data` is refused,
naming the field. A stopped instance's datasets leave the deployment's
configuration with it.

## Recorded once, restated as a new version

A data plugin records rows in batches of 1 to 500, each batch recorded whole or
refused naming the row and the field. Each row carries:

- its **row key**, the plugin's own, made from its raw record, so the same
  candle sent twice is one row;
- its **subjects**, the deployment's instrument IDs;
- its **source**: the dataset, and the venue it printed on where the
  dataset has one; the instance and its version are stamped, never
  written by the plugin;
- its **valid time**, and for a daily value its **business date**;
- the source's own times (published, event, received) where it gives them;
- the **raw record** it was converted from, which only that plugin can
  follow.

The lake decides when it recorded the row, its sequence in the dataset and
its **version**. The same row key with the same values changes nothing,
compared by decimal value: 764.2 is 764.20. A changed value is the next
version, and the earlier one is kept. That is how a day still forming is
recorded: its close restated as it fills, under one row key, until it is
final.

### A daily value on a closed day

A daily price or bar dated on a day its dataset's
[calendar](settlement-calendars.md) says is closed is **recorded as
reported, never refused**, and flagged: its `closed_day` holds the date,
each calendar with its version, why the day is closed (a weekend, a named
holiday, or outside the calendar's coverage) and the holiday's name, the
same shape a break's cause carries. The lake decides it, as it decides when
it recorded the row.

- **Only rows with a business date** are checked: daily prices and daily
  bars. Trades, quotes, intraday rows and outcomes never are.
- **Outside coverage** is flagged and counted apart, so a calendar whose
  coverage has lapsed reads as a curation matter, not the vendor's.
- **A calendar not held yet** leaves the value unflagged, and the lake
  reports the calendar missing, so the deployment pulls it. When a calendar
  changes, the lake re-checks only the rows dated on days whose status the
  new version changes, each re-check journalled beside the row, never as a
  new version, since the source restated nothing; a point-in-time read shows
  the flag as it was known then.

The Data sources page counts both, per dataset: see
[Where you see it](#where-you-see-it).

## An event contract's outcome

A data plugin records what an
[event contract](instruments.md#binary-event-contracts) pays once its
venue determines it, an **outcome**, per instrument: Kalshi's one contract,
or each of Polymarket's tokens.

| Part | What |
|---|---|
| Its determination | `OUTCOME_DETERMINATION_PAYS` (its full payout), `OUTCOME_DETERMINATION_PAYS_NOTHING`, or `OUTCOME_DETERMINATION_PAYS_PART` (Kalshi's scalar, Polymarket's 50-50). The instrument's own: a NO token of a market resolved YES pays nothing. |
| Its settlement value | A [Money](money-and-instruments.md) per contract in the payout's asset, always set: 0.45 US dollars for a scalar. |
| The venue's word | Kept as reported beside it (`determination_as_reported`), such as Kalshi's `result`. |
| Its stage | `OUTCOME_STAGE_PROPOSED`, `_DETERMINED`, `_DISPUTED` or `_FINAL`. |
| Its times | Valid from the determination; `settled_at_ns`, when the venue paid out, 0 until then. No business date: an outcome is not a daily value. |

**Each change of stage is a new version** under the contract's one row key,
as any restatement is: a disputed resolution restated is version 2, and a
read as of a recorded time before it answers version 1. Void is not a
determination until a venue reports one.

**The lake records the outcome, not the payout.** Paying holders is a
servicing entitlement, in a later release, so the book keeps the position
until then. A `reporting` plugin may value a final outcome at its
settlement value, by its own policy, and a custodian's payout shows as a
break, which `operations` may explain with the outcome's row key as its
event reference.

**Delivered whole.** Every version is delivered, never conflated, as trades
are: outcomes are rare, and a missed dispute would mislead. A reader reads
them by subject, the version in force or as of a recorded time, and catches
up after a gap from the watermark it last saw. See
[Add a prediction-market plugin](../how-to/add-a-prediction-market-plugin.md#outcomes)
for what Kalshi and Polymarket record. Which contracts belong to one
event, and whether they are mutually exclusive and exhaustive, is not an
observation: it is an [event group](event-groups.md), kept in the
instrument master.

## Reading it, point in time

A reader asks for prices or bars for up to 500 subjects at one of:

- the latest in force at a moment (now, by default);
- a **business date**;
- a range of valid time.

**The latest is chosen per asset.** A latest read chooses per subject,
dataset, kind, venue and the asset the price is in, so a subject priced in
two assets on one venue, BTC in USD and in USDC, answers both, never one
for the other.

**Trades and quotes** are read over a range of valid time that lies within
one day of each dataset, as the dataset declares its day; a wider range is
refused, naming it. Quotes are also read at the latest in force, per
subject, dataset, venue and asset. Trades are also read **after a
watermark**: see [Catching up trades](#catching-up-trades).

Every read can also be cut **as of** a recorded time: what the lake knew
then. A report re-run as of last Friday answers last Friday's version of
each close, even where a source restated it since.

And from one of three choices of source:

- **the deployment's default**: the datasets a deployment admin put first
  for that data type and, for prices, kind (the **source priority**),
  falling through to the next where the first is silent beyond its cadence,
  does not cover the subject, or is not entitled. The answer names why it
  fell through. Trades and quotes take a priority too, with no kind.
- **named datasets**;
- **every dataset side by side**, each source's own row.

Each answer lists the datasets it includes once, with their vendor and
aggregator, and what it could not answer, per subject, dataset and field,
with a reason: not entitled, not covered, asked of the source, silent,
unresolved, beyond its history, or not kept.

## Wants: a read the lake cannot answer yet

A read the lake cannot answer from what it holds becomes a **want**, sent
to the instance serving the dataset alone: the subjects, the kinds and the
date or range wanted. The `data` fetches them and records them against the
want, or declines what it cannot serve, per subject, with a reason. The
reader's answer says the source was asked, and the reader hears the rows
when they are recorded. Identical wants from several readers are one want.

A reader that keeps asking for the same subjects, such as a reporting
plugin valuing the instruments in the book, leaves a **standing want**: the
`data` keeps those subjects current until no reader has asked for a whole
cadence, and the lake withdraws it. That is how a data plugin learns what
matters without reading the book, which its role does not reach.

**A decline stands for the date asked.** A decline holds for the business
date or range its want asked, or for the latest where the want asked the
latest, and for no other date: a later want of another date is asked again.

**Streamed.** A dataset declaring the `stream` mode keeps
a standing want current from its vendor's stream until the want is
withdrawn, its trades and quotes recorded in batches as they arrive. Which
subjects a plugin streams, and how often it records, are the plugin's; core
holds no stream. A streaming plugin records trades only for subjects under
a standing want, and declares its live trades in a dataset apart from its
live prices, so an admin licenses and keeps them apart.

### A restarted data plugin resumes

A data plugin holds nothing it cannot lose, and has no way to read the
standing wants back. So the lake delivers each standing want still asked
for again once a minute, the same want under the same ID: a data plugin
already holding it hears what it holds, and one relaunched or upgraded
resumes its stream within about a minute.

**The gap is filled from the venue's history.** Within a running plugin, a
dropped connection is refilled from the venue's history, from the last trade
the plugin recorded. Across a restart, a data plugin asks the lake: on
start, before resuming its stream, it reads the last trade its own instance recorded of each subject
it streams (`list_trades` with `latest_recorded`, its own rows only), reads
the venue's history from each, and records what it missed. A trade
recorded again is answered unchanged by its row key, so nothing is
doubled. The data suite holds a plugin that records trades to it
(`a-restarts-gap-backfilled`).

It reaches only as far as the vendor allows. A venue whose history names
each trade, and reaches back past the restart, fills it: Coinbase, Kraken
and Alpaca do. **Tradier cannot**: its
time and sales history names no trade by an ID, so a gap across a restart
stays, as a gap between two of its stream sessions does. A reader catches
up from the lake by its watermark, so it misses only what the lake never
had.

## Kept, or served and not kept

A dataset whose licence lets the lake keep its rows has them kept, for as
long as its licence's retention says; rows past it are removed, and each
removal is recorded. A dataset whose licence does not is **served, not
kept**: the lake answers the reader waiting for it and records only that it
served (the dataset, the subjects, the fields, the reader, when), never the
values.

## Hearing it

The lake publishes each row after it records it, on its dataset's own
subject, and only a plugin entitled to the dataset can hear it there. A
reader names the subjects it wants to hear, up to 500, and hears nothing
without them: a plugin holding ten instruments does not receive a whole
market. Its sidecar delivers prices, bars and quotes **conflated**: the
latest value first for each key, replacing one not yet delivered with a
later one. A price's key is its dataset, subjects, venue, kind and the
asset it is in; a bar's its dataset, subjects, venue and
interval start; a quote's its dataset, subjects, venue and asset. The SDK
reads the lake again on start, after a loss and after a broken stream.

**Trades are never conflated.** Every trade recorded is delivered, at most
once, in its dataset's order, none dropped for a later one.

### Catching up trades

A reader too slow for the trades meets a loss marker. It then reads the
trades **recorded after the watermark it last saw**, whatever their valid
time, so a late or out-of-sequence print recorded after its range had passed
is caught too; a range read alone would miss it. The SDK does this for a
plugin hearing trades: after a loss or a broken stream it reads them after
the watermark of the last trade it handed on, and hands them on marked
`caught_up`. On start it reads none: there is no latest trade to begin
from, so a plugin wanting the day's trades reads them by range. Quotes,
conflated, catch up by reading the latest in force.

## Who reads what

| Data | Read and heard by |
|---|---|
| Prices and bars | `reporting`, `portfolio`, `compliance`, `signal`; and from contract 27 `operations`, for closes and other conflated prices, to value a foreign-cash cost at a trade date's FX close |
| Trades and quotes | `signal` and `ems` |
| Rates | `reporting`, `portfolio`, `compliance`, `signal` |
| Execution costs | `reporting`, `portfolio`, `compliance`, `signal`, `oms`, `ems`, `operations`, each within its read scope's accounts |
| A dataset's liveness | `reporting`, `portfolio`, `compliance`, `signal` and `ems` |
| Listed series | `portfolio`, `signal`, `oms` and `ems` (added in contract 28) |
| Statistics | `portfolio`, `reporting`, `signal` (added in contract 28) |
| Corporate actions | `portfolio`, `reporting`, `signal` (added in contract 28) |
| Derived series and saved scenarios | `compliance`, `portfolio`, `reporting`, `signal` (added in contract 28) |
| Outcomes | `reporting`, `portfolio`, `compliance`, `signal`, and `operations`, which reads the lake for outcomes alone, to explain a payout's break |
| The datasets a plugin may read | `reporting`, `portfolio`, `compliance`, `signal` and `ems` |

**`reporting` is for slower consumers.** In the product owner's words,
"reporting is primarily aimed for slower consumers": it reads conflated
prices and bars, never trades or quotes. A dashboard or a valuation reads
the latest price or the close, and needs no tape.

**High-resolution data is `signal`'s and `ems`'s.** A `signal` plugin
triggers orders on live data; an `ems` plugin sends orders in real time.
`portfolio` and `oms` read prices and bars, not trades: "Portfolio primarily
exists to shape order, and oms focuses on aggregating orders", as the
product owner put it. A `portfolio` or `oms` plugin that needs
high-resolution data also takes `signal` (live order triggering) or `ems`
(real-time order sending), and is approved for that role when it is
launched.

A data source's higher-resolution or differently priced tier is a dataset of
its own, licensed by a deployment admin and entitled per plugin instance,
like any other: see [Licences and entitlements](licences-and-entitlements.md).

## Where you see it

A deployment admin sees and sets the lake's configuration on the
dashboard's **Data sources** page, beside **Instruments** under **Data** on
the settings' sidebar, and through its five tools; a source priority may
order rates' datasets too:
see [License and entitle a dataset](../how-to/license-and-entitle-a-dataset.md).
Its Datasets tab counts, per dataset, the rows flagged on
a closed day of its calendar, **Closed days**, those outside the calendar's
coverage beside them ("(2 outside)"), and `dashboard__list_datasets`
carries both counts (`closed_day_count`, `outside_coverage_count`); its
reads answer `unchanged`, as core's other reads do.
The page shows no price: prices are the reading roles', shown on their
plugins' pages. Each data plugin shows its own connection and what it
serves on its pages under Manage, the same pages on every one: see
[Using a data plugin](../how-to/using-a-data-plugin.md).

## What core does not serve yet { #not-served-yet }

Contract 28 carries three parts that core serves in later chart releases
on the same contract, one release each, in the order below, without a
contract change. Until a deployment's chart
serves one, its typed operations are answered `UNAVAILABLE`, nothing
serving them (the Python SDK raises `CallFailed`, `kind="no handler"`), its
tools are not listed, and each suite case about it carries its `about`
marker, so a plugin whose source or work presents none names it not
presented:

| Part | Its operations | Served from |
|---|---|---|
| **Quality states**: a row's state (`valid`, `suspicious`, `invalid`) and reasons as the edge judged it (`ObservationMeta.quality`, `.quality_reasons`), a signal's escalation and invalid rows held from default reads | [`record_quality_assessments`](../api/typed-operations.md#record_quality_assessments), `SourceChoice.include_quarantined` | the first later chart release. Until then the lake judges nothing: a row is kept with whatever state its plugin set, a default read holds no invalid row back, and `include_quarantined` is not acted on |
| **Filings, reported facts, holdings reports and holdings, and rating actions**, an 8-K's earnings date among the filings | [`record_filings`](../api/typed-operations.md#record_filings), [`list_filings`](../api/typed-operations.md#list_filings), [`record_reported_facts`](../api/typed-operations.md#record_reported_facts), [`list_reported_facts`](../api/typed-operations.md#list_reported_facts), [`record_holdings_reports`](../api/typed-operations.md#record_holdings_reports), [`record_holdings`](../api/typed-operations.md#record_holdings), [`list_holdings`](../api/typed-operations.md#list_holdings), [`record_rating_actions`](../api/typed-operations.md#record_rating_actions), [`list_rating_actions`](../api/typed-operations.md#list_rating_actions) | the second |
| **The data-use counts and the professional test**: display persons and non-display plugins counted against a dataset's meters, their CSV export, and a person's self-certification on first access | `dashboard__read_data_use`, `dashboard__export_data_use`, `dashboard__answer_professional_test` (core's tools) | the third |

The SDK's helpers for the first two already exist: `meridian.roles.data.quality`
judges a row at the edge, `meridian.roles.signal.escalate` records an
assessment, and `meridian.roles.data.filings` records the filings slice
(see [Python SDK](../api/python-sdk.md#the-filings-slice-and-quality-states)).
A plugin built on them runs on any contract-28 deployment; what it sends to
a part not yet served is refused as above, and the SDK's quality checks
mark rows at the edge whether or not the lake acts on the mark.

## Valuing the book, and the Board

The sample reporting plugin values the book at a business date's prices
from the lake, consolidated across every account a person may read and by
account, each price naming its dataset, kind and date, and a position with
no price shown unvalued with its reason, never as zero: see
[Value the book](../how-to/value-the-book.md). From its 0.2.0 its **Board**
shows a watchlist's latest prices from every source side by side, read again
every few seconds, conflated, with no tape: see
[Watch the market on the Board](../how-to/watch-the-board.md).

## Related

- [Licences and entitlements](licences-and-entitlements.md): who may read a
  dataset, and on what terms it is kept.
- [Money and instruments](money-and-instruments.md),
  [Venues](venues.md) and [Dates and time](dates-and-time.md): what a row's
  amount, venue and date name.
- [Write a data plugin against its suite](../how-to/write-a-data-plugin.md): a data
  plugin, from the template.
- [Read trades and quotes in a `signal` or `ems` plugin](../how-to/read-trades-and-quotes.md).
- [The lake in the Python SDK](../api/python-sdk.md#the-lake) and
  [its operations](../api/typed-operations.md#record_prices), trades and
  quotes from [`record_trades`](../api/typed-operations.md#record_trades),
  outcomes from [`record_outcomes`](../api/typed-operations.md#record_outcomes).
- [Listed options and futures](listed-options-and-futures.md), [Scenarios](scenarios.md) and [Companies and corporate actions](companies-and-corporate-actions.md): contract 28's kinds.
- [The lake's data dictionary](../boundaries/lake.md).
