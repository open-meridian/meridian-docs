# Add a data plugin's key

A data plugin (one holding `dgm`) reads a vendor's market data with the
vendor's key, and puts it into the deployment's
[lake](../concepts/the-lake.md). Its key is a **secret setting**: an admin of
the plugin enters it on the plugin's **Settings** form, and from then on it
is never shown, logged, put on a page, read by an agent or sent anywhere but
the vendor. This page covers the two retail equity plugins, Alpaca and
Tradier, which pass the same suite unchanged.

!!! note "Built, not released"
    meridian-alpaca and meridian-tradier are built on open-meridian 0.22.0
    (contract v18) and not yet released, and neither is the runtime they need,
    chart 0.1.291. Until they are, this page says how they will be set up.

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

!!! note "TODO: an instrument the plugin did not resolve itself"
    In contract v18 a `dgm` resolves its own identifiers to an instrument
    but may not read an instrument's record, so it can name to its vendor
    only the listings it resolved itself by the vendor's symbol. An
    instrument known to the deployment only by another source's identifier,
    such as a custodian's symbol, is declined as not covered, and the
    plugin's **Datasets** page says why. A fix is in progress; this note
    changes when it lands.

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

## The other data plugins

!!! note "TODO: still being built"
    These pages will cover the other first data plugins once each is built:

    - **Coinbase and Kraken**, the crypto pair: public market data, no key.
    - **The Federal Reserve's H.10**: FX rates, no key.
    - **Tiingo**: mutual funds' daily net asset values, with a key.

## Related

- [Licences and entitlements](../concepts/licences-and-entitlements.md).
- [Write a `dgm` against its suite](write-a-dgm.md): your own data plugin.
- [Core's tools](../api/core-tools.md#the-data-sources-page): the Data
  sources page for an agent.
