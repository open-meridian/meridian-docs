# Add a public data plugin

Three data plugins (each holding `dgm`) read public market data, with no key
and no account, and put it into the deployment's
[lake](../concepts/the-lake.md): **Coinbase** and **Kraken**, the crypto
pair, which pass one suite between them, and the **Federal Reserve's H.10**,
weekly US dollar exchange rates. For the plugins that need a key, see
[Add a data plugin's key](add-a-data-plugins-key.md).

!!! note "Contract v18"
    meridian-coinbase 0.1.0, meridian-kraken 0.1.0 and meridian-fed-h10
    0.1.0 are built on open-meridian 0.22.0 (contract v18), and run on chart
    0.1.292 or later.

## What each serves

| Plugin | Dataset | What | Day | Default terms |
|---|---|---|---|---|
| Coinbase | `daily` | each product's close and daily bar: open, high, low, close, volume (Coinbase states no VWAP or trade count); pulled when a read wants it, pushed | UTC, ending at 00:00 | kept, shown inside the organisation |
| Coinbase | `live` | the last trade's price, the best bid and offer; pulled, kept current while a standing want stands | UTC, ending at 00:00 | kept two days, shown inside the organisation |
| Kraken | `daily` | each pair's close and daily bar, with its VWAP and trade count, 720 days back | UTC, ending at 00:00 | kept, one person's |
| Kraken | `live` | the last trade's price, the best bid and offer | UTC, ending at 00:00 | kept two days, one person's |
| H.10 | `daily` | each week's noon buying rates in New York for about two dozen currencies against the US dollar; pushed when each weekly release appears, pulled for any past week, ten years back | New York, ending at noon | kept, public domain |

**The crypto pair.**

- **The daily close** is the last price of the UTC day: neither exchange has
  an official close, so each declares its day. The day still forming is
  restated under the same row as it fills, until it ends. A Kraken day that
  traded nothing carries no VWAP.
- **A product names a market, not an asset**: its base asset is a row's
  subject, and its quote asset what the price is in. Reading the listing
  resolves nothing and adds no instrument to the deployment.
- **Each subject is the deployment's own record.** The lake asks for a
  price by the deployment's instrument ID, usually a record a custodian's
  positions made. The plugin reads that record and names the exchange's
  asset it is by its identifiers: the exchange's code, else the global
  identifier the exchange's asset carries (a currency's ISO 4217 code, a
  native coin's SLIP-44 CAIP-19), else another source's symbol that is the
  exchange's code. The exchange's code is then added to the record where it
  lacks it; where that meets another record it is reported, and the subject
  is priced all the same. A record naming none of the exchange's assets is
  declined as not covered, and the **Datasets** page says why.
    - **Kraken calls bitcoin `XXBT`**, so a custodian's record carrying only
      the symbol `BTC` names none of Kraken's assets and is declined. Add
      bitcoin's CAIP-19 to the record on the Instruments page, and Kraken
      names it at its next read, within a day. Coinbase's code for bitcoin is
      `BTC`, so it names that record by the custodian's symbol.
    - **Another source's symbol is never matched** to a record classed as a
      security, or carrying a CUSIP or an ISIN: Ethan Allen's shares trade
      as `ETH`, and are never taken for ether.
- **Only a wanted product's quote asset is resolved**, with the exchange's
  code as its `symbol`, and a record is added only where none resolves: a
  currency by its ISO 4217 code; a native coin (bitcoin, ether) by its
  SLIP-44 CAIP-19; a token Coinbase lists on exactly one network by that
  contract's CAIP-19; and any other token, such as Coinbase's USDC (listed
  on several networks) or any token at Kraken (which states no network), as
  the exchange's own instrument, by its code. Kraken's legacy codes, such as
  `XXBT` and `ZUSD`, are converted at the edge. A quote asset whose
  identifiers meet two records is reported, and every product quoted in it
  left out until a person resolves the conflict on the Instruments page.
- **A price in a stablecoin names the token**, never a fiat code: a USDC
  price is never a dollar price. A reader values it through a price of the
  stablecoin itself (USDC-USD, recorded like any product), never by
  assuming 1. See [Money and instruments](../concepts/money-and-instruments.md).
- **FX** comes from Kraken's fiat pairs: EUR/USD is the euro's price in
  dollars as Kraken's trades made it, a venue's price, not a fixing.
  Coinbase lists no pair of two currencies, so it serves no FX rate.
- **The venue** is resolved in the venue master by the exchange's code
  (neither has a MIC), and each row names its [venue ID](../concepts/venues.md).
  A deployment that does not hold it gets each row with the venue left
  empty and the code beside it, and the miss reported.
- **Wants** are recorded against, or declined per subject: not covered (its
  record names none of the exchange's assets, or no product's base is it),
  beyond history (at Kraken, older than its 720
  days), or the source silent. A standing want keeps a live price current at
  most once a second, and the forming day every five minutes.

**H.10.**

- **Each rate as the Board quotes it**, never inverted. Most currencies are
  quoted per US dollar, so CHF 0.8293 is the price of the dollar's cash
  instrument, in francs. The euro, the pound and the Australian and New
  Zealand dollars are quoted in US dollars per unit, so EUR 1.1259 is the
  price of the euro's cash instrument, in dollars. A reader wanting the
  other way inverts it, and says so.
- **A close for its business date**: the rate's date as the Board prints
  it, kind `close` (the noon rate), published weekly on Monday (the next
  business day after a holiday) for the week before. A valuation for
  yesterday has no H.10 rate until the next release.
- **Every currency resolved** to its cash instrument by its ISO 4217 code,
  a miss reported. A day the Board marks `ND` is no rate, never a zero; its
  dollar indexes are not recorded.
- Read from the Board's own site, not through FRED, whose API has terms and
  a key of its own.

**All three.** Every figure is exact, read from the source's text and never
through a float; a value that does not convert is counted on the plugin's
**Datasets** page, never recorded. Every response is kept first as a raw
record in the plugin's own storage, and every row names the one it came
from.

## The terms, summarised

Not legal advice: read each source's own terms before relying on this.
What a deployment's licence says is for its deployment admin and its users
to settle with each source.

- **Coinbase**: its Market Data Terms allow an organisation to use and show
  Coinbase's market data within itself, and forbid redistributing or
  displaying it outside the organisation, or building applications for
  other end users with it, without Coinbase's written consent. So the
  default licence is kept and shown, and not one person's.
- **Kraken**: it asks its prior permission for any non-personal commercial
  use of data from its public endpoints. Without it, a deployment keeps
  Kraken's data for one person's own use, so the default licence is one
  person's (`personal_use`).
- **The Federal Reserve Board**: its site says its information is in the
  public domain and may be copied and distributed without permission, and
  asks that the Board be cited as the source. So the default licence is
  kept, with no limit on retention, derived use or display, and not one
  person's.

The deployment admin confirms or changes each licence on the Data sources
page, which warns when more than one person can read a plugin entitled to a
one-person dataset. Neither the plugins nor these docs say a deployment
meets a source's terms: a licence records what the admin entered. None of
the three is affiliated with or endorses Open Meridian.

## Upload and launch the plugin

As the deployment's administrator, from the plugin's repository (see
[Command line](../api/cli.md#plugin-commands-on-a-deployment)):

```sh
meridian plugin upload --dir meridian-coinbase
meridian plugin launch coinbase <version> --instance coinbase-1
```

The launch prints the role the version declares, `dgm`, for you to approve.
Kraken is the same, from `meridian-kraken`, named `kraken`, as `kraken-1`;
H.10 from `meridian-fed-h10`, named `fed-h10`, as `fed-h10-1`. There is no
key to enter. Their settings, on each plugin's **Settings** form:

- **Raw responses' window** and what happens **past the window**: how long
  the source's answers stay in the plugin's storage (30 days by default for
  the crypto pair, ten years for H.10), and whether a day past it is
  archived, kept or deleted. See
  [Keep older records in the archive](keep-older-records-in-the-archive.md).
- **Synthetic mode**, on a development deployment only: answers from
  exchanges committed with the plugin instead of calling the source, to try
  it offline.

`meridian plugin check --verified` refuses H.10 and Coinbase until contract
v19: each never publishes some kinds of data the `dgm` suite asks about (at
H.10 a bar, a stablecoin's quote and a venue; at Coinbase an FX rate), and a
source cannot yet mark those cases not presented (see
[Write a `dgm` against its suite](write-a-dgm.md#hold-it-to-the-suite)). A
plain `meridian plugin upload` takes them.

## License and entitle its datasets

On **Settings**, **Data sources**, confirm each dataset's licence, entitle
the plugins that read prices, and set the source priority where two
datasets price the same thing (Coinbase and Kraken both price bitcoin): see
[License and entitle a dataset](license-and-entitle-a-dataset.md).

## See it working

Each plugin's two pages are under Manage for its admin, and each is a tool
for an agent, `read_connection` and `read_datasets`, answering what the
page shows. Neither shows a price.

- **Connection**: where it answers from (the source, or synthetic mode),
  the limits it keeps (Coinbase at most 5 requests a second of the 10
  Coinbase allows, Kraken at most one a second, H.10 one page every two
  seconds and a check every hour), how its last calls went and the last
  error; for the crypto pair, the venue ID it resolved; for H.10, the latest
  release and the next expected.
- **Datasets**: each dataset of its catalogue; for the crypto pair, the
  products mapped for the instruments the lake asked about, how many of the
  deployment's instruments it named as the exchange's assets, and the
  assets not resolved; for H.10, each currency's instrument, or why there
  is none; and the wants it heard, each with what it recorded and declined.
  On the crypto pair's page, a search above the wants narrows them by ID,
  dataset, what was asked or state.

## Related

- [Licences and entitlements](../concepts/licences-and-entitlements.md).
- [Add a data plugin's key](add-a-data-plugins-key.md): Alpaca, Tradier and
  Tiingo.
- [Value the book](value-the-book.md): the sample reporting plugin, which
  reads these prices and rates.
- [Write a `dgm` against its suite](write-a-dgm.md): your own data plugin.
