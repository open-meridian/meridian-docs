# Using a data plugin

A **data plugin** (the role `data`) reads a vendor's market data and puts it
into the deployment's [lake](../concepts/the-lake.md), where the plugins
that read prices find it. Every data plugin has the same first-use path,
the same pages, sections and labels in the same order, and the same "not
set up yet" states naming the next step, so someone who has set up one
knows how to set up any. This page is that path, valid for every data
plugin; the vendors' own parts, what each serves and its terms, follow it
under [The data plugins](#the-data-plugins).

!!! note "Contract v20"
    The common part is in open-meridian 0.24.0 (contract v20), the kit
    0.12.0 and core's **Setting up**, released 2026-10-12 in chart
    0.1.298. From contract v20 the role `dgm` is named `data`. Alpaca
    0.4.0, Tradier 0.3.0, Tiingo 0.2.0, H.10 0.2.0, Coinbase 0.3.0, Kraken
    0.3.0, Kalshi 0.2.0 and Polymarket 0.2.0, released 2026-10-12, are built
    on open-meridian 0.24.0 and run on chart 0.1.298 or later. Each
    takes the common pages and figures, reads its datasets' licences, and
    has its `synthetic` setting renamed `sample_data`; Tradier's `sandbox`
    becomes the **Environment** choice; Alpaca, Coinbase and Kraken fill a
    restart's gap from the venue's history, and Tradier cannot. An earlier
    version keeps the pages described under its own section below, with the
    same two page names, Connection and Datasets.

## The first-use path

| # | Step | Whose | Where |
|---|---|---|---|
| 1 | **Enter the key** | the plugin's admin | the plugin's **Settings**, under Manage. A vendor needing none says "No key needed", and the step is done. |
| 2 | **Check the connection** | the plugin's admin | the plugin's **Connection** page: the vendor answers, and what it serves this key |
| 3 | **License and entitle its datasets** | a deployment admin | **Settings**, **Data sources**: each dataset's licence, and the plugins entitled to read it. See [License and entitle a dataset](license-and-entitle-a-dataset.md). |
| 4 | **See data arrive** | the plugin's admin | the plugin's **Datasets** page: each dataset's rows recorded |

Prices themselves are seen in a plugin that reads them, such as a reporting
plugin's pages, never on a data plugin's: its pages show its connection and
its datasets, and the people who manage it reach no account.

### Setting up, on the Summary

From contract v20 core draws a **Setting up** part on
every plugin's **Summary**, first under its status while any step is
undone: one line a step, done or not, each linking to where it is done. It
is drawn from core's own records, never from what the plugin says, so a
plugin cannot misreport it:

- **Enter the key** is done when every required secret is set; "No key
  needed" where the plugin declares none.
- **Check the connection** is done when the plugin reports itself healthy.
- **License and entitle its datasets** is done when each dataset it
  declares has a licence set and at least one plugin entitled to it. To a
  deployment admin it links to Data sources; to anyone else it reads "Ask a
  deployment admin to license and entitle its datasets".
- **See data arrive** is the Datasets page's own to say; Setting up does not
  judge it.

When every step core judges is done, the part folds to one line, **Set
up**, with the steps a click away. An agent reads the same part in
[`dashboard__read_plugin_summary`](../api/core-tools.md#dashboard__read_plugin_summary),
under `setting-up`.

## Its settings

On the plugin's **Settings** form, in this order on every data plugin:

1. **Environment**, first, only for a vendor with more than one: **Live**
   or **Sandbox**, required, Live by default. A credential that differs by
   environment is shown only for the environment chosen.
2. **The credentials**, each a secret, labelled in the vendor's own words
   ("API key ID", "Access token") so you find the same words on the
   vendor's page, each saying where at the vendor it is found.
3. **The vendor's own settings**, such as Tiingo's Funds table.
4. **Sample data**, on a development deployment only: the plugin answers
   from recorded responses and the vendor is not called.

A secret is write-only: its field is always empty and says in its
placeholder where it stands, "Not set", or who set it and when, and from
contract v20, for a key of 16 characters or more, its last four characters
("Ends in a9F2 · set by Ada, ..."). The value itself is never shown, logged,
put on a page, read by an agent or sent anywhere but the vendor. Leave the
field empty to keep it; type to replace it. A required key is only ever
replaced; an optional one that is set has a small **Remove** beside it. See
[Set a plugin's settings](set-a-plugins-settings.md#a-secret).

## Connection

The plugin's first page under Manage, `/`, at `admin`. Its sections, in
order:

1. **Notices.** "No key yet: enter it in Settings", with the link; "Sample
   data: the plugin answers from recorded responses; the vendor is not
   called"; the last error, when there is one.
2. **Key.** **Mode** (Live, Sandbox, Sample data or No key); **Key**, each
   credential's label with "set" or "not set", never its value ("No key
   needed" for a public source); **Entitled at the vendor**, what the vendor
   serves this key; **Not entitled**; and, for a source of one venue,
   **Venue**, its [venue ID](../concepts/venues.md) or "Not held by the
   deployment".
3. **Limits and use.** **Limit**, the vendor's and this plugin's share of
   it; **Calls**, since start, and how many were rate-limited and waited
   out; **Last call**, when, and the answer's status; **Last error**.
4. **Stream.** The session's state, how many listings it streams of the
   session's limit, reconnects, messages and the last message; or "Does not
   stream".
5. The vendor's own sections, such as H.10's release calendar.

## Datasets

The second page under Manage, `/datasets`, at `admin`:

1. **Notices.** "No wants yet: nothing reads these datasets until a
   deployment admin licenses them and entitles a plugin on Data sources",
   with the link for a deployment admin; values the plugin could not
   convert.
2. **Served.** One row a dataset, as its catalogue declares it: **Dataset**,
   **Data**, **Arrives**, **Day**, **Default terms**, **Entitled at the
   vendor**, **Recorded**, **Declined**, **Last recorded**, its detail
   holding history, cadence, restated and unconverted counts. From contract
   v20 a data plugin reads its own datasets' licences,
   so each says **Licensed** or **Not licensed yet** exactly: before it, a
   data plugin could only guess from the wants it heard.
3. **Wants.** The standing wants it keeps current and the wants it answered,
   one row each, searched and paged: **Dataset**, **Asked**, **Subjects**,
   **Recorded**, **Declined**, **State**.
4. **Subjects.** What it resolved, read, mapped or not resolved, and whether
   the deployment lets it read an instrument's record.
5. The vendor's own sections, such as Tiingo's Funds list.

## Its figures

The Summary's figures, the role's first, in this order: **Connection**
(Answering, Not answering, No key or Sample data), **Entitled at the
vendor** ("3 of 4 datasets"), **Stream** ("12 listings", Off or "Does not
stream"), **Last recorded** and **Rate use** ("41 of 100 a minute", a
warning at four fifths of the vendor's limit). Up to three of the vendor's
own follow.

## After a restart

A data plugin holds nothing it cannot lose, so it may be stopped, restarted,
moved or upgraded at any time. Started again, it hears each standing want
within about a minute and opens its stream again. From contract v20 a data plugin that records trades also **fills the gap**: on
start it reads the last trade it recorded of each subject from the lake,
and records what the venue's history states since, where the vendor's
history allows it. Before contract v20 the trades printed while a plugin
restarted were not in the lake. Which vendors allow it is said under each,
below; Tradier's history cannot, so a restart leaves a gap there.

## For an agent

Each page is a read tool under the role's name, so an agent that has read
one data plugin reads every one: `<instance>__read_connection` answers
`mode`, `credentials` (each label and whether it is set), `entitled_at_vendor`,
`limit`, `calls`, `rate_limited`, `last_call_at`, `last_error` and
`sessions`; `<instance>__read_datasets` answers `served` (each with
`licensed`), `wants` and `reads_instruments`, the vendor's fields beside
them. Settings and the Summary are core's tools: see
[Core's tools](../api/core-tools.md).

## Upload and launch a data plugin

As the deployment's administrator, from the plugin's repository (see
[Command line](../api/cli.md#plugin-commands-on-a-deployment)):

```sh
meridian plugin upload --dir plugin-alpaca
meridian plugin launch alpaca <version> --instance alpaca-1
```

The launch prints the role the version declares, `data` (`dgm` before
contract v20), for you to approve, and asks for storage for its raw
responses. Its datasets are then `alpaca-1:daily` and so on, listed on the
Data sources page while the instance runs. From v20 the plugin
repositories are named `plugin-<name>`; the plugins keep their names.

## The data plugins

### Alpaca and Tradier

The two retail equity plugins, from plugin-alpaca and plugin-tradier
(`alpaca`, `tradier`), pass the same suite unchanged.

!!! note "Contract v20"
    Alpaca 0.4.0 and Tradier 0.3.0, released 2026-10-12, are built on
    open-meridian 0.24.0 (contract v20), and run on chart 0.1.298 or
    later. Alpaca 0.3.0 and Tradier 0.2.1, released 2026-10-10, are built on
    open-meridian 0.23.0 (contract v19), and run on chart 0.1.294 or later.

Each serves two datasets, US equities and ETFs, daily prices keyed by a
plain date in New York's day ending at the 16:00 close:

| Plugin | Dataset | What | From | Arrives | Default terms |
|---|---|---|---|---|---|
| Alpaca | `daily` | each listing's close and daily bar: open, high, low, close, volume, VWAP and trade count | Alpaca's consolidated history (SIP), past the free plan's restricted latest 15 minutes | pulled when a read wants it; pushed once a session's close is final | kept; one person's |
| Alpaca | `live` | the last trade's price, the best bid and ask | SIP where the key has it in real time, otherwise IEX, the one exchange a free account sees | pulled for a read; kept current once a minute while a standing want stands | served, not kept; one person's |
| Tradier | `daily` | each listing's close and daily bar: open, high, low, close, volume (Tradier states no VWAP or trade count) | Tradier's daily history, consolidated | as Alpaca's | kept; one person's |
| Tradier | `live` | the last trade's price, the best bid and ask | Tradier's quotes, consolidated, real time for a Tradier Brokerage account holder | as Alpaca's | served, not kept; one person's |

- A day still forming is restated under the same row as it fills, until
  its close is final.
- A last price names the exchange it printed on, by its
  [venue ID](../concepts/venues.md); a consolidated price names none.
  Alpaca's exchange codes are in the venue master. Tradier's are not yet, so
  each is reported as a venue the deployment does not hold and kept as
  Tradier reported it.
- Berkshire's B shares are `BRK.B` in both; Tradier is asked in its own
  spelling, `BRK/B`.
- Every number is exact, read from the vendor's text and never through a
  float. A value that does not convert is counted on the plugin's
  **Datasets** page and the deployment's Data sources page, never recorded.
- Every response is kept first as a raw record in the plugin's own storage,
  without the key, and every row names the one it came from.
- **Each record's rows under its own key.** Where the deployment holds two
  records of one listing, one the vendor's and one a custodian's not yet
  merged, each record's rows are its own, the row key naming the record
  (`SPY:1d:2026-10-08@LCL-...`), never one recorded over the other.
- **An instrument another source named.** The lake asks for a price by the
  deployment's own instrument ID. An instrument the book holds from another
  source, known only by that source's identifiers (a custodian's symbol and
  CUSIP), is read from its record and priced under the vendor's symbol for
  the listing, and the vendor's symbol is added to the record. Only a record
  carrying no symbol is declined, as not covered, and the **Datasets** page
  says why.
- Not served: options; Alpaca's crypto; mutual funds at Tradier.

**Trades and quotes.** Each also serves a `trades` dataset, and quotes in
`live`:

| Plugin | Dataset | What | Arrives | Default terms |
|---|---|---|---|---|
| Alpaca | `trades` | each trade with the platform's trade attributes, converted from its conditions on its tape (the CTA's letters on tapes A and B, the UTP's on C) | streamed for the listings under a standing want; pulled for a range a reader wants | kept two days; one person's |
| Alpaca | `live` | gains quotes: the best bid and offer with their sizes | streamed at most once a second a listing, or read for a want | as before |
| Tradier | `trades` | each time and sale with the platform's trade attributes and Tradier's sequence number | streamed only | kept two days; one person's |
| Tradier | `live` | gains quotes: the consolidated best bid and offer, sizes in shares from Tradier's hundreds | as Alpaca's | as before |

- **Only what a reader follows** is streamed: the listings under a standing
  want, and nothing while there is none. A free Alpaca account streams IEX
  alone, at most 30 listings; a listing past that is declined, not
  entitled, and counted on the Datasets page.
- **No aggressor.** Neither vendor's stock trades say which side took
  liquidity, and none is guessed.
- **Conditions.** Alpaca's are converted into the trade's attributes: what
  it may set of the consolidated bar and its exchange's, and what it was
  (an odd lot, extended hours, an intermarket sweep, an auction print). A
  code with no conversion is kept as reported and counted. Tradier
  documents its sessions and not its flags: a print outside the regular
  session is an extended-hours trade, counted in the volume only, and any
  flag is kept as reported for a person to map.
- **Withdrawals and corrections** are the trade's next version under its
  row key.
- **Gaps.** A stream that breaks is opened again a second later, the wait
  doubling to a minute. Alpaca reads the gap after a reconnect from its
  trade history, sending only the trades not yet recorded. Tradier's history
  names no print by its sequence number, so a gap between two sessions is
  not filled, and a reader's range of trades is declined, not covered.
- **A restart.** In v19 neither fills the trades printed while it restarts.
  From Alpaca 0.4.0 Alpaca reads its last recorded trade from the lake and
  fills the gap from its history, two days back at most (see
  [After a restart](#after-a-restart)); Tradier cannot, for the reason
  above, and its Datasets page says why.
- **The suite.** Alpaca passes 17 of the data suite's 21 v19 cases, and
  marks four not presented with why (a currency's rate, a crypto asset's
  price, and the two asking for the side that took liquidity); Tradier
  passes 16 and marks five (those, and an odd lot, which no documented flag
  says). Of contract v20's three new cases, each presents
  `reads-its-datasets-licences` and marks `the-takers-side-stated` not
  presented; Alpaca 0.4.0 presents `a-restarts-gap-backfilled`, and Tradier
  0.3.0 marks it not presented, with why.

Trades and quotes are read by `signal` and `ems` plugins: license `trades`
on the Data sources page, and entitle those plugins to it and to `live`.

**The vendors' terms, summarised.** Not legal advice: read each vendor's own
terms before relying on this. What a deployment may keep, show or use is
for its deployment admin and its users to settle with each vendor.

- **Alpaca**: its market data is for personal, non-commercial use, and is
  not republished or redistributed without Alpaca's written consent. The
  free plan gives real-time data from IEX alone, 30 symbols on the stream
  and 200 calls a minute, with the latest 15 minutes of history
  restricted; a paid plan gives every US exchange in real time.
- **Tradier**: unless you are a Tradier Partner, its APIs are for personal
  use only, and its market data goes only to active Tradier Brokerage
  account holders and is never redistributed. An account holder's data is
  real time and consolidated, up to 120 requests a minute per token; the
  developer sandbox is delayed 15 minutes.

So each dataset's default licence is one person's (`personal_use`). The
deployment admin confirms or changes it on the Data sources page, which
warns when more than one person can read a plugin entitled to a one-person
dataset. Neither the plugins nor these docs say a deployment meets a
vendor's terms: a licence records what the admin entered.

**Get the key.**

=== "Alpaca"

    An Alpaca account's API key: a free account's, or a paper account's. It
    does not expire.

    1. In Alpaca's dashboard, under **API keys**, generate a key.
    2. Copy the **key ID** and the **secret key**. Alpaca shows the secret
       key once.

=== "Tradier"

    A Tradier Brokerage account's personal API access token. For an
    individual it does not expire.

    1. In your Tradier Brokerage account, open the **API** settings page.
    2. Copy your access token.

**Enter the key** on the plugin's **Settings**: Alpaca's **API key ID** and
**API secret key**; Tradier's **API access token**. Tradier has a developer
sandbox as well as its live service: in Tradier 0.2.1 its setting
**Tradier's developer sandbox** (`sandbox`, off by default) is for testing
with a sandbox token, the plugin then asking `sandbox.tradier.com`, delayed
15 minutes and not streaming, its quotes marked delayed. From Tradier 0.3.0
it is the common **Environment** choice, shown first, **Live** or
**Sandbox**: one token serves either, its value carried over, on the
Settings form as **Access token**, which must match the environment, and
the plugin's pages say which environment the data comes from. Then open **Connection**: it says whether each
part of the key is set, whether the vendor answered, and which feeds the
key is entitled to (for Alpaca, IEX in real time and SIP past 15 minutes on
a free key; for Tradier, whether its quotes are real time).

**Check it live.** Each repository's `make live` asks for the key at a
prompt that does not echo, asks the vendor for a week of closes and the
latest prices, and listens to its stream for twenty seconds, printing the
condition codes or flags seen; then it prints that the key is in no raw
record, never the key. Tradier's `make live SANDBOX=1` asks the developer
sandbox with a sandbox token. It runs on your own machine with your own
key, never in CI.

### Tiingo: mutual funds' daily NAVs

plugin-tiingo (`tiingo`) puts mutual funds' daily net asset values from
Tiingo into the lake, so a reporting plugin can value a fund no exchange
prices, such as VIGIX. Tiingo 0.2.0, released 2026-10-12, is built on
open-meridian 0.24.0 (contract v20), and runs on chart 0.1.298 or
later. Tiingo 0.1.0 is built on open-meridian 0.22.0 (contract v18), and
runs on chart 0.1.292 or later.

- **One dataset, `<instance>:daily`**: each listed fund's NAV, kind `nav`,
  for its business date, in US dollars, exact. Each fund's last days are
  pushed every six hours, and any past day is pulled when the lake wants it.
  New York's day, ending at 16:00; no venue; one person's terms by default.
- **NAVs after midnight New York time.** Tiingo gives a fund's NAV for a day
  the night after; each NAV shows its date.
- **Only mutual funds.** A ticker Tiingo files as a mutual fund is served.
  An ETF or a stock is shown as not a mutual fund and not recorded; a ticker
  Tiingo does not know is shown as not found.
- **Each fund resolved** to the deployment's record: the one its row in the
  **Funds** setting names, or its ticker as Tiingo's symbol, a miss
  reported.
- Every response is kept as received, without the token, in the plugin's
  own storage, and named by each row read from it.

**Its terms, summarised.** Not legal advice: read Tiingo's own terms and
pricing before relying on them, as they change. You use Tiingo under your
own account and its terms; the plugin calls it with your token. Tiingo's
free and Power plans are for internal and personal use, with no
redistribution, so the dataset's default licence is one person's
(`personal_use`); a firm's use needs Tiingo's commercial terms. The free
plan's limits, as Tiingo states them, are 50 requests an hour, 1,000 a day
and 500 symbols a month, and the plugin keeps inside them. Whether a
deployment's use fits Tiingo's terms is for its admin and the account holder
to settle with Tiingo; neither the plugin nor these docs say it does.

**Its settings:** **API token** (`tiingo_api_token`), secret, your own
Tiingo account's token from its API page, sent only to Tiingo; **Funds**
(`funds`), a table of up to 100 rows, each fund's **Ticker** and optionally
its **Instrument**, the deployment's record for it where the ticker alone
does not find it, such as the one your custodian's positions name; and
sample data on a development deployment. From contract v20 the Instrument column is a search-as-you-type picker: type a
name, a symbol or an identifier and choose the record (see
[A table setting](set-a-plugins-settings.md#a-table-setting)). Until the
token is set the plugin waits and reads nothing.

**Check it live**, for the person who holds the Tiingo account: enter your
token in **API token**; under **Funds**, add `VIGIX`, and pick its
**Instrument** where your custodian's positions already name one; **Save**.
Within a minute **Connection** says "Tiingo read", and the token set;
**Datasets** shows VIGIX as a mutual fund resolved to an instrument, its
latest recorded day the last business day. Then license `tiingo-1:daily` on
Data sources as your terms say, and entitle your reporting plugin to it. If
Connection says Tiingo refused the token, enter it again; if it says the
limit was reached, the plugin waits and tries again.

`meridian plugin check --verified` refuses Tiingo 0.1.0, on open-meridian
0.22.0: a fund's NAV is no close, bar, FX rate, stablecoin or venue, and on
0.22.0 a source cannot mark those cases not presented. From 0.23.0 it can
(see [A kind of data your source never publishes](write-a-data-plugin.md#a-kind-of-data-your-source-never-publishes)).
A plain `meridian plugin upload` takes it. Tiingo 0.2.0 passes the whole
data suite: it presents seven cases, its licences among them, and names
every case about a kind of data it never publishes in `not_presented`, with
why.

### Coinbase and Kraken

The crypto pair, from plugin-coinbase and plugin-kraken (`coinbase`,
`kraken`), read public market data with no key and no account, and pass one
suite between them. Coinbase 0.3.0 and Kraken 0.3.0, released 2026-10-12,
are built on open-meridian 0.24.0 (contract v20), and run on chart
0.1.298 or later. Coinbase 0.2.0 and Kraken 0.2.0, released 2026-10-10,
are built on open-meridian 0.23.0 (contract v19), and run on chart 0.1.294
or later.

| Plugin | Dataset | What | Day | Default terms |
|---|---|---|---|---|
| Coinbase | `daily` | each product's close and daily bar: open, high, low, close, volume (Coinbase states no VWAP or trade count); pulled when a read wants it, pushed | UTC, ending at 00:00 | kept, shown inside the organisation |
| Coinbase | `live` | the last trade's price, the best bid and offer, with their sizes as a quote; pulled, kept current while a standing want stands | UTC, ending at 00:00 | kept two days, shown inside the organisation |
| Coinbase | `trades` | every trade, streamed from Coinbase's WebSocket feed; a range read from its REST history | UTC | kept two days, as `live` |
| Kraken | `daily` | each pair's close and daily bar, with its VWAP and trade count, 720 days back | UTC, ending at 00:00 | kept, one person's |
| Kraken | `live` | the last trade's price, the best bid and offer, with their sizes as a quote | UTC, ending at 00:00 | kept two days, one person's |
| Kraken | `trades` | every trade, streamed from Kraken's v2 WebSocket; a range read from its REST history | UTC | kept two days, as `live` |

- **The daily close** is the last price of the UTC day: neither exchange has
  an official close, so each declares its day. The day still forming is
  restated under the same row as it fills, until it ends. A Kraken day that
  traded nothing carries no VWAP.
- **A product names a market, not an asset**: its base asset is a row's
  subject, and its quote asset what the price is in. Reading the listing
  resolves nothing and adds no instrument to the deployment.
- **Each subject is the deployment's own record.** The plugin reads the
  record the lake asks about and names the exchange's asset it is by its
  identifiers: the exchange's code, else the global identifier the
  exchange's asset carries (a currency's ISO 4217 code, a native coin's
  SLIP-44 CAIP-19), else another source's symbol that is the exchange's
  code. The exchange's code is then added to the record where it lacks it.
  A record naming none of the exchange's assets is declined as not covered.
    - **Kraken calls bitcoin `XXBT`**, so a custodian's record carrying only
      the symbol `BTC` names none of Kraken's assets and is declined. Add
      bitcoin's CAIP-19 to the record on the Instruments page, and Kraken
      names it at its next read, within a day.
    - **Another source's symbol is never matched** to a record classed as a
      security, or carrying a CUSIP or an ISIN: Ethan Allen's shares trade
      as `ETH`, and are never taken for ether.
- **Only a wanted product's quote asset is resolved**, and a record is
  added only where none resolves: a currency by its ISO 4217 code (from
  contract v20 the deployment pulls a currency it
  does not hold from the platform's master instead: see
  [Instruments](../concepts/instruments.md#a-currency-is-fetched-from-the-master)),
  a native coin by its SLIP-44 CAIP-19, a token Coinbase lists on exactly
  one network by that contract's CAIP-19, and any other token as the
  exchange's own instrument, by its code.
- **A price in a stablecoin names the token**, never a fiat code: a USDC
  price is never a dollar price. See
  [Money and instruments](../concepts/money-and-instruments.md).
- **FX** comes from Kraken's fiat pairs, a venue's price, not a fixing.
  Coinbase lists no pair of two currencies, so it serves no FX rate.
- **The venue** is resolved in the venue master by the exchange's code
  (neither has a MIC), and each row names its venue ID.
- **Trades.** Only what a reader follows is streamed, every trade recorded,
  never conflated; quotes at most once a second a product. A crypto trade
  has no condition codes. **The aggressor**: Coinbase names the resting
  order's side, so the plugin records the other; Kraken names the side that
  took liquidity, recorded as sent. A stream that drops is opened again and
  the trades since the last one recorded are read back from the exchange's
  history, at most ten pages of 1,000.
- **A restart.** In v19 the last trade recorded is held in memory, which a
  restart loses, so the trades printed while either restarts are not
  recorded. From Coinbase 0.3.0 and Kraken 0.3.0 each reads its last
  recorded trade from the lake on start and fills the gap from the exchange's history, within
  the same ten pages (see [After a restart](#after-a-restart)).
- **The suite.** Of the data suite's 21 v19 cases each passes 17 and marks
  four not presented, with why. Of contract v20's three new cases, each
  presents `a-restarts-gap-backfilled` and `reads-its-datasets-licences`;
  Kraken presents `the-takers-side-stated`, and Coinbase, naming the resting
  order's side, marks it not presented.

**The terms, summarised.** Not legal advice: read each source's own terms
before relying on this. What a deployment's licence says is for its
deployment admin and its users to settle with each source.

- **Coinbase**: its Market Data Terms allow an organisation to use and show
  Coinbase's market data within itself, and forbid redistributing or
  displaying it outside the organisation, or building applications for
  other end users with it, without Coinbase's written consent. So the
  default licence is kept and shown, and not one person's.
- **Kraken**: it asks its prior permission for any non-personal commercial
  use of data from its public endpoints. Without it, a deployment keeps
  Kraken's data for one person's own use, so the default licence is one
  person's (`personal_use`).

Neither is affiliated with or endorses Open Meridian.

### The Federal Reserve's H.10

plugin-fed-h10 (`fed-h10`) puts the Board's weekly noon buying rates in New
York for about two dozen currencies against the US dollar into one dataset,
`daily`: pushed when each weekly release appears, pulled for any past week,
ten years back, kept, public domain. H.10 0.2.0, released 2026-10-12, is
built on open-meridian 0.24.0 (contract v20), and runs on chart 0.1.298
or later. H.10 0.1.0 is built on open-meridian 0.22.0 (contract v18).

- **Each rate as the Board quotes it**, never inverted. Most currencies are
  quoted per US dollar, so CHF 0.8293 is the price of the dollar's cash
  instrument, in francs. The euro, the pound and the Australian and New
  Zealand dollars are quoted in US dollars per unit. A reader wanting the
  other way inverts it, and says so.
- **A close for its business date**, kind `close` (the noon rate),
  published weekly on Monday for the week before. A valuation for yesterday
  has no H.10 rate until the next release.
- **Every currency resolved** to its cash instrument by its ISO 4217 code.
  In v19 a currency the deployment did not hold was minted as a local
  record, which left 23 stubs beside the platform's; from contract v20 the deployment fetches it from the platform's master
  instead. A day the Board marks `ND` is no rate, never a zero.
- Read from the Board's own site, not through FRED.
- **Its terms.** The Board's site says its information is in the public
  domain and may be copied and distributed without permission, and asks
  that the Board be cited as the source. So the default licence is kept,
  with no limit on retention, derived use or display.

`meridian plugin check --verified` refuses H.10 0.1.0, on open-meridian
0.22.0, as it refuses Tiingo 0.1.0, and a plain upload takes it. H.10
0.2.0 passes the whole data suite: it presents nine cases, its licences
among them, and names every case about a kind of data the Board never
states in `not_presented`, with why.

### Kalshi and Polymarket

The two prediction-market plugins are data plugins too: see
[Add a prediction-market plugin](add-a-prediction-market-plugin.md).

## Related

- [License and entitle a dataset](license-and-entitle-a-dataset.md).
- [Licences and entitlements](../concepts/licences-and-entitlements.md).
- [Read trades and quotes in a `signal` or `ems` plugin](read-trades-and-quotes.md).
- [Value the book](value-the-book.md): the sample reporting plugin, which
  reads these prices and rates.
- [Write a data plugin against its suite](write-a-data-plugin.md): your own.
- [Keep older records in the archive](keep-older-records-in-the-archive.md):
  each plugin's raw responses' window.
