# The lake

The **lake** is where a deployment keeps what its data sources say: prices
and bars, each as one source stated it, kept side by side, never
overwritten. A plugin holding `dgm` puts them in, converted at the edge from
its vendor's form. The reading roles, `reporting`, `portfolio`,
`compliance` and `signal`, read them and hear them as they are recorded. The
lake is core's, beside the street and the book: it is not a plugin, and
nothing in it leaves the deployment.

!!! note "Built, not released"
    This page describes contract v18: core's lake in chart 0.1.291 and
    open-meridian 0.22.0, both built and not yet released. The lake's
    operations are `preview` in v18. A runtime serving v16 or earlier
    refuses a plugin built on 0.22.0 at registration, naming both versions.

## Two stores, two questions

The [instrument store](instruments.md) says what something **is**: an
instrument's identity, its identifiers and its record. The lake says what
sources **say** about it: a close, a last price, a bar. Every row in the
lake names the deployment's own instruments as its subjects, resolved from
the vendor's codes before the row is recorded, never the vendor's codes
themselves. A row about an instrument the deployment does not hold is not
recorded: the plugin reports the miss, and the Data sources page counts it.

## What it holds in v18

Two data types, each one message per row:

| Type | What one row is |
|---|---|
| **Price** | A price of one kind for one subject: `close` (the official close for a business date), `last` (the last eligible trade's price), `nav` (a fund's net asset value per share), `settlement`, `bid`, `ask` or `mid`. Its amount is a [Money](money-and-instruments.md), always per unit in v18. |
| **Bar** | Open, high, low and close over an interval, in one asset, with its volume, and its VWAP and trade count where the source gives them. A daily bar names its business date. |

**An FX rate is a price**: the price of one currency's cash instrument in
another, EUR at 1.0842 USD, of kind `mid`, `bid`, `ask` or `close`. A fixing
is a dataset of closes. The lake never inverts or crosses a rate: a reader
converting the other way reads the rate a source quotes that way, or
inverts it itself, so the lake never holds a value no source stated.

Prices are unadjusted by default. Trades and top-of-book quotes come with
the lake's next revision: they are specified and not built.

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

Every read can also be cut **as of** a recorded time: what the lake knew
then. A report re-run as of last Friday answers last Friday's version of
each close, even where a source restated it since.

And from one of three choices of source:

- **the deployment's default**: the datasets a deployment admin put first
  for that data type and price kind (the **source priority**), falling
  through to the next where the first is silent beyond its cadence, does
  not cover the subject, or is not entitled. The answer names why it fell
  through.
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
market. Its sidecar delivers the latest value first for each key (a price's
dataset, subjects, venue and kind; a bar's interval start), replacing one
not yet delivered with a later one, and the SDK reads the lake again on
start, after a loss and after a broken stream.

## Where you see it

A deployment admin sees and sets the lake's configuration on the
dashboard's **Data sources** page, beside **Instruments** on **Settings**,
and through its five tools:
see [License and entitle a dataset](../how-to/license-and-entitle-a-dataset.md).
The page shows no price: prices are the reading roles', shown on their
plugins' pages. Each `dgm` shows its own connection and what it serves on
its pages under Manage.

!!! note "TODO: valuing the book"
    The sample reporting plugin, which values the book at the close from the
    lake, consolidated and by account, is still being built. See
    [Value the book](../how-to/value-the-book.md).

## Related

- [Licences and entitlements](licences-and-entitlements.md): who may read a
  dataset, and on what terms it is kept.
- [Money and instruments](money-and-instruments.md),
  [Venues](venues.md) and [Dates and time](dates-and-time.md): what a row's
  amount, venue and date name.
- [Write a `dgm` against its suite](../how-to/write-a-dgm.md): a data
  plugin, from the template.
- [The lake in the Python SDK](../api/python-sdk.md#the-lake) and
  [its operations](../api/typed-operations.md#record_prices).
- [The lake's data dictionary](../boundaries/lake.md).
