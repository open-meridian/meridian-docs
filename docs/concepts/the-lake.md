# The lake

The **lake** is where a deployment keeps what its data sources say: prices
and bars, and from contract v19 trades and quotes, each as one source stated
it, kept side by side, never overwritten. A plugin holding `dgm` puts them
in, converted at the edge from its vendor's form. The reading roles,
`reporting`, `portfolio`, `compliance` and `signal`, read prices and bars and
hear them as they are recorded; trades and quotes are read by `signal` and
`ems` alone (see [Who reads what](#who-reads-what)). The lake is core's,
beside the street and the book: it is not a plugin, and nothing in it leaves
the deployment.

!!! note "Contract v18"
    This page describes contract v18: core's lake from chart 0.1.292 and
    open-meridian 0.22.0. The lake's
    operations are `preview` in v18. A runtime serving v16 or earlier
    refuses a plugin built on 0.22.0 at registration, naming both versions.

!!! note "Contract v19: built, not released"
    The lake's second part, trades and quotes, is contract v19: core's lake
    from chart 0.1.293 and open-meridian 0.23.0. Its operations are
    `preview` in v19. A runtime serving v18 or earlier refuses a plugin
    built on 0.23.0 at registration, naming both versions; a plugin on
    0.22.0 runs unchanged on chart 0.1.293.

## Two stores, two questions

The [instrument store](instruments.md) says what something **is**: an
instrument's identity, its identifiers and its record. The lake says what
sources **say** about it: a close, a last price, a bar. Every row in the
lake names the deployment's own instruments as its subjects, resolved from
the vendor's codes before the row is recorded, never the vendor's codes
themselves. A row about an instrument the deployment does not hold is not
recorded: the plugin reports the miss, and the Data sources page counts it.

## What it holds

Four data types, each one message per row: prices and bars from contract
v18, trades and quotes from contract v19.

| Type | What one row is |
|---|---|
| **Price** | A price of one kind for one subject: `close` (the official close for a business date), `last` (the last eligible trade's price), `nav` (a fund's net asset value per share), `settlement`, `bid`, `ask` or `mid`. Its amount is a [Money](money-and-instruments.md), always per unit in v18. |
| **Bar** | Open, high, low and close over an interval, in one asset, with its volume, and its VWAP and trade count where the source gives them. A daily bar names its business date. |
| **Trade** | One trade as its source reported it: its price, a [Money](money-and-instruments.md) naming its cash instrument; its quantity, more than zero; its **trade attributes**; the side that took liquidity, where the source says it; the source's own number for it. From contract v19. |
| **Quote** | The best bid and offer, on a venue or consolidated, each with its quantity, both sides in one asset; a side the source left empty is unset, never zero. In force until the next quote for the same subject, dataset, venue and asset. From contract v19. |

**An FX rate is a price**: the price of one currency's cash instrument in
another, EUR at 1.0842 USD, of kind `mid`, `bid`, `ask` or `close`. A fixing
is a dataset of closes. The lake never inverts or crosses a rate: a reader
converting the other way reads the rate a source quotes that way, or
inverts it itself, so the lake never holds a value no source stated.

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

## Datasets

Every row belongs to a **dataset**: one plugin instance's stream of one
kind of data from one vendor. A `dgm`'s version declares its datasets in
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
| Its day | The time zone a business date is in and the minute the day ends. See [Dates and time](dates-and-time.md). |
| Its venue | The venue the dataset is, by its [venue ID](venues.md); none for a consolidated view. |

A catalogue is checked when the version is uploaded and again when its
plugin registers: a key twice, a type the lake does not have, a zone that is
no time zone, or a catalogue on a version not holding `dgm` is refused,
naming the field. A stopped instance's datasets leave the deployment's
configuration with it.

## Recorded once, restated as a new version

A `dgm` records rows in batches of 1 to 500, each batch recorded whole or
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

## Reading it, point in time

A reader asks for prices or bars for up to 500 subjects at one of:

- the latest in force at a moment (now, by default);
- a **business date**;
- a range of valid time.

**The latest is chosen per asset.** From contract v19 a latest read chooses
per subject, dataset, kind, venue and the asset the price is in, so a
subject priced in two assets on one venue, BTC in USD and in USDC, answers
both, never one for the other. Contract v18 chose without the asset, and
answered one of the two.

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
  fell through. From contract v19 trades and quotes take a priority too,
  with no kind.
- **named datasets**;
- **every dataset side by side**, each source's own row.

Each answer lists the datasets it includes once, with their vendor and
aggregator, and what it could not answer, per subject, dataset and field,
with a reason: not entitled, not covered, asked of the source, silent,
unresolved, beyond its history, or not kept.

## Wants: a read the lake cannot answer yet

A read the lake cannot answer from what it holds becomes a **want**, sent
to the instance serving the dataset alone: the subjects, the kinds and the
date or range wanted. The `dgm` fetches them and records them against the
want, or declines what it cannot serve, per subject, with a reason. The
reader's answer says the source was asked, and the reader hears the rows
when they are recorded. Identical wants from several readers are one want.

A reader that keeps asking for the same subjects, such as a reporting
plugin valuing the instruments in the book, leaves a **standing want**: the
`dgm` keeps those subjects current until no reader has asked for a whole
cadence, and the lake withdraws it. That is how a data plugin learns what
matters without reading the book, which its role does not reach.

**A decline stands for the date asked.** From contract v19, a decline holds
for the business date or range its want asked, or for the latest where the
want asked the latest, and for no other date: a later want of another date
is asked again. In contract v18 a decline stood for a day across every date
of that dataset and subject, so a daily want for the latest could record the
past week rather than decline a day just begun.

**Streamed.** From contract v19 a dataset declaring the `stream` mode keeps
a standing want current from its vendor's stream until the want is
withdrawn, its trades and quotes recorded in batches as they arrive. Which
subjects a plugin streams, and how often it records, are the plugin's; core
holds no stream. A streaming plugin records trades only for subjects under
a standing want, and declares its live trades in a dataset apart from its
live prices, so an admin licenses and keeps them apart.

!!! warning "Known in v19: a restarted `dgm` streams nothing until asked again"
    A `dgm` hears a standing want when it is made, and contract v19 gives it
    no way to read the standing wants back. A `dgm` process started anew
    streams nothing until a reader's read makes a want again. A reader
    reading on a timetable, as the sample reporting plugin's Board does,
    makes one within its next read.

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
later one. A price's key is its dataset, subjects, venue, kind and, from
contract v19, the asset it is in; a bar's its dataset, subjects, venue and
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
| Prices and bars | `reporting`, `portfolio`, `compliance`, `signal` |
| Trades and quotes, from contract v19 | `signal` and `ems` |
| The datasets a plugin may read | `reporting`, `portfolio`, `compliance`, `signal`, and from contract v19 `ems` |

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
dashboard's **Data sources** page, beside **Instruments** on **Settings**,
and through its five tools:
see [License and entitle a dataset](../how-to/license-and-entitle-a-dataset.md).
The page shows no price: prices are the reading roles', shown on their
plugins' pages. Each `dgm` shows its own connection and what it serves on
its pages under Manage.

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
- [Write a `dgm` against its suite](../how-to/write-a-dgm.md): a data
  plugin, from the template.
- [Read trades and quotes in a `signal` or `ems` plugin](../how-to/read-trades-and-quotes.md).
- [The lake in the Python SDK](../api/python-sdk.md#the-lake) and
  [its operations](../api/typed-operations.md#record_prices), trades and
  quotes from [`record_trades`](../api/typed-operations.md#record_trades).
- [The lake's data dictionary](../boundaries/lake.md).
