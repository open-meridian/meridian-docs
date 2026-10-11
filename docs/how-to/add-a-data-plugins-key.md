# Add a data plugin's key

A data plugin (one holding `dgm`) reads a vendor's market data with the
vendor's key, and puts it into the deployment's
[lake](../concepts/the-lake.md). Its key is a **secret setting**: an admin of
the plugin enters it on the plugin's **Settings** form, and from then on it
is never shown, logged, put on a page, read by an agent or sent anywhere but
the vendor. This page covers the two retail equity plugins, Alpaca and
Tradier, which pass the same suite unchanged, and Tiingo, for mutual funds'
daily net asset values. The data plugins that need no key, Coinbase,
Kraken and the Federal Reserve's H.10, are in
[Add a public data plugin](add-a-public-data-plugin.md).

!!! note "Contract v19"
    meridian-alpaca 0.3.0 and meridian-tradier 0.2.1, released 2026-10-10,
    are built on open-meridian 0.23.0 (contract v19), and run on chart
    0.1.294 or later: each adds [trades and quotes](#trades-and-quotes-contract-v19).
    meridian-tiingo 0.1.0, and Alpaca 0.2.0 and Tradier 0.1.0, are built on
    open-meridian 0.22.0 (contract v18), and run on chart 0.1.292 or later.

## What each serves

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
  (`SPY:1d:2026-10-08@LCL-...`), never one recorded over the other. A day
  read again unchanged is kept unchanged. Rows recorded before Alpaca 0.3.0
  and Tradier 0.2.0 keep their keys and stand beside the new ones.
- Not served: options; Alpaca's crypto (the crypto pair's); mutual funds at
  Tradier.

- **An instrument another source named.** The lake asks for a price by
  the deployment's own instrument ID. An instrument the book holds from
  another source, known only by that source's identifiers (a custodian's
  symbol and CUSIP), is read from its record and priced under the vendor's
  symbol for the listing, and the vendor's symbol is added to the record.
  Only a record carrying no symbol is declined, as not covered, and the
  **Datasets** page says why. On a runtime before chart 0.1.292, which first
  lets a `dgm` read an instrument's record, such an instrument is declined.

### Trades and quotes (contract v19)

From meridian-alpaca 0.3.0 and meridian-tradier 0.2.0, each gains a
`trades` dataset, and quotes in `live`:

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
  code with no conversion is kept as reported, its eligibilities not known,
  and counted. Tradier documents its sessions and not its flags: a print
  outside the regular session is an extended-hours trade, counted in the
  volume only, and any flag is kept as reported for a person to map.
- **Withdrawals and corrections** are the trade's next version under its
  row key: at Alpaca a cancel, an error or a correction; at Tradier a cancel
  naming a print recorded here by its sequence number.
- **Gaps.** A stream that breaks is opened again a second later, the wait
  doubling to a minute, and subscribed again from what is wanted. Alpaca
  reads the gap after a reconnect from its trade history, sending only the
  trades not yet recorded, so a reader catches up from the lake. Tradier's
  history names no print by its sequence number, so a gap between two
  sessions is not filled, and a reader's range of trades is declined, not
  covered; each reconnect is counted on the Connection page.
- **A restart.** A plugin started anew, relaunched or upgraded, streams
  again once the lake delivers its standing wants again, within about a
  minute from chart 0.1.294. Neither fills that gap: Alpaca refills a drop
  only within a running process, and a process started anew has nothing to
  catch up from; Tradier refills neither. Trades printed while either
  restarts are not in the lake.
- **A quote's empty side** (sent as 0) is left unset.
- **The suite.** Alpaca passes 17 of the `dgm` suite's 21 cases, and marks
  four not presented with why (a currency's rate, a crypto asset's price,
  and the two asking for the side that took liquidity); Tradier passes 16
  and marks five (those, and an odd lot, which no documented flag says).
- **Connection** shows the stream's session; **Datasets** counts trades and
  quotes, and searches and pages the standing wants.

Trades and quotes are read by `signal` and `ems` plugins: license `trades`
on the Data sources page, and entitle those plugins to it and to `live`.

## The vendors' terms, summarised

Not legal advice: read each vendor's own terms before relying on this.
What a deployment may keep, show or use is for its deployment admin and its
users to settle with each vendor.

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

## Get the key

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

## Upload and launch the plugin

As the deployment's administrator, from the plugin's repository (see
[Command line](../api/cli.md#plugin-commands-on-a-deployment)):

```sh
meridian plugin upload --dir meridian-alpaca
meridian plugin launch alpaca <version> --instance alpaca-1
```

The launch prints the role the version declares, `dgm`, for you to approve.
The plugin's datasets are then `alpaca-1:daily` and `alpaca-1:live`, listed
on the Data sources page while the instance runs. Tradier is the same, from
`meridian-tradier`, named `tradier`, as `tradier-1`.

## Enter the key

1. In the dashboard, open the plugin under **Manage**, then **Settings**.
2. Enter the key, and **Save**:
    - Alpaca: **API key ID** and **API secret key**;
    - Tradier: **API access token**. Leave **Tradier's developer sandbox**
      (`sandbox`, off by default) off for a Tradier Brokerage account's
      token. From Tradier 0.2.1 it is for testing with a developer sandbox
      token instead: the plugin then asks `sandbox.tradier.com`, whose data
      is delayed 15 minutes and which does not stream, so its quotes are
      marked delayed, no trades are streamed, and live prices are still
      kept current once a minute.
3. Open the plugin's **Connection** page. It says whether each part of the
   key is set (never its value), whether the vendor answered, and which
   feeds the key is entitled to: for Alpaca, IEX in real time and SIP past
   15 minutes on a free key; for Tradier, whether its quotes are real time,
   or, with the sandbox on, "Tradier's developer sandbox: delayed 15
   minutes, no streaming". Tradier's **Datasets** page names the host it
   asks.

The form never shows a secret again: **set** says who set it, when, and
through which client. To replace a key, enter the new one; to remove it,
**Clear it**. See [Set a plugin's settings](set-a-plugins-settings.md).

## License and entitle its datasets

On **Settings**, **Data sources**, confirm each dataset's licence and
entitle the plugins that read prices: see
[License and entitle a dataset](license-and-entitle-a-dataset.md). Once a
reader asks for a close, the plugin's **Datasets** page counts it recorded.

Each plugin's two pages, **Connection** and **Datasets**, are under Manage
for its admin, and each is a tool for an agent, `read_connection` and
`read_datasets`, answering what the page shows. Neither shows a price.

## Checking it live

Each repository's `make live` asks for the key at a prompt that does not
echo, asks the vendor for a week of closes and the latest prices, and from
Alpaca 0.3.0 and Tradier 0.2.0 listens to its stream for twenty seconds,
printing the condition codes or flags seen; then it prints that the key is
in no raw record, never the key. Tradier's `make live SANDBOX=1` asks the
developer sandbox with a sandbox token. It runs on your own machine with
your own key, never in CI.

## Tiingo: mutual funds' daily NAVs

meridian-tiingo puts mutual funds' daily net asset values from Tiingo into
the lake, so a reporting plugin can value a fund no exchange prices, such as
VIGIX.

- **One dataset, `<instance>:daily`**: each listed fund's NAV, kind `nav`,
  for its business date, in US dollars, exact. Each fund's last days are
  pushed every six hours, and any past day is pulled when the lake wants it.
  New York's day, ending at 16:00; no venue; one person's terms by default.
- **NAVs after midnight New York time.** Tiingo gives a fund's NAV for a day
  the night after; each NAV shows its date.
- **Only mutual funds.** A ticker Tiingo files as a mutual fund is served.
  An ETF or a stock is shown as not a mutual fund and not recorded (its
  closes are the equity datasets'); a ticker Tiingo does not know is shown
  as not found.
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

**Its settings**, on the plugin's **Settings** form:

- **API token** (`tiingo_api_token`), secret: your own Tiingo account's
  token, from its API page. Sent only to Tiingo, in a header.
- **Funds** (`funds`), a table of up to 100 rows: each fund's **Ticker**,
  and optionally its **Instrument**, the deployment's record for it where
  the ticker alone does not find it, such as the one your custodian's
  positions name.
- **Synthetic mode**, on a development deployment only: invented responses
  for VIGIX and VOO, no token.

Upload and launch it as above, from `meridian-tiingo`, named `tiingo`, as
`tiingo-1`. Until the token is set it waits and reads nothing.

### Check it live

For the person who holds the Tiingo account:

1. In the dashboard, open the plugin under **Manage**, then **Settings**.
2. Enter your token in **API token**.
3. Under **Funds**, add `VIGIX`, and pick its **Instrument** where your
   custodian's positions already name one. **Save**.
4. Open **Connection**: within a minute it says "Tiingo read", and the
   token **Set**. Open **Datasets**: VIGIX is a mutual fund, resolved to an
   instrument, its latest recorded day the last business day. An agent sees
   the same with `read_datasets`.
5. On **Settings**, **Data sources**, license `tiingo-1:daily` as your terms
   say, and entitle your reporting plugin to it.

If Connection says Tiingo refused the token, enter it again; if it says the
limit was reached, the plugin waits and tries again.

`meridian plugin check --verified` refuses Tiingo 0.1.0, on open-meridian
0.22.0: a fund's NAV is no close, bar, FX rate, stablecoin or venue, and on
0.22.0 a source cannot mark those cases of the `dgm` suite not presented.
From 0.23.0 (contract v19) it can (see
[A kind of data your source never publishes](write-a-dgm.md#a-kind-of-data-your-source-never-publishes)),
and Tiingo is verified once it moves to 0.23.0. A plain
`meridian plugin upload` takes it.

## Related

- [Read trades and quotes in a `signal` or `ems` plugin](read-trades-and-quotes.md).
- [Add a public data plugin](add-a-public-data-plugin.md): Coinbase, Kraken
  and the Federal Reserve's H.10, no key.
- [Licences and entitlements](../concepts/licences-and-entitlements.md).
- [Write a `dgm` against its suite](write-a-dgm.md): your own data plugin.
- [Core's tools](../api/core-tools.md#the-data-sources-page): the Data
  sources page for an agent.
