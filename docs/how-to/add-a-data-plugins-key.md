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

!!! note "Built, not released"
    meridian-alpaca, meridian-tradier and meridian-tiingo are built on
    open-meridian 0.22.0 (contract v18) and not yet released, and neither is
    the runtime they need, chart 0.1.292. Until they are, this page says how
    they will be set up.

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
- Not served: trades, quotes and streaming, which come with the lake's next
  revision; options; Alpaca's crypto; mutual funds at Tradier.

- **An instrument another source named.** The lake asks for a price by
  the deployment's own instrument ID. An instrument the book holds from
  another source, known only by that source's identifiers (a custodian's
  symbol and CUSIP), is read from its record and priced under the vendor's
  symbol for the listing, and the vendor's symbol is added to the record.
  Only a record carrying no symbol is declined, as not covered, and the
  **Datasets** page says why. On a runtime before chart 0.1.292, which first
  lets a `dgm` read an instrument's record, such an instrument is declined.

## The vendors' terms, summarised

Not legal advice: read each vendor's own terms before relying on this.

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
    - Tradier: **API access token**.
3. Open the plugin's **Connection** page. It says whether each part of the
   key is set (never its value), whether the vendor answered, and which
   feeds the key is entitled to: for Alpaca, IEX in real time and SIP past
   15 minutes on a free key; for Tradier, whether its quotes are real time.

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
echo, asks the vendor for a week of closes and the latest prices, and
prints what came back and that the key is in no raw record; never the key.
It runs on your own machine with your own key, never in CI.

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

`meridian plugin check --verified` refuses Tiingo until contract v19: a
fund's NAV is no close, bar, FX rate, stablecoin or venue, and a source
cannot yet mark those cases of the `dgm` suite not presented (see
[Write a `dgm` against its suite](write-a-dgm.md#hold-it-to-the-suite)). A
plain `meridian plugin upload` takes it.

## Related

- [Add a public data plugin](add-a-public-data-plugin.md): Coinbase, Kraken
  and the Federal Reserve's H.10, no key.
- [Licences and entitlements](../concepts/licences-and-entitlements.md).
- [Write a `dgm` against its suite](write-a-dgm.md): your own data plugin.
- [Core's tools](../api/core-tools.md#the-data-sources-page): the Data
  sources page for an agent.
