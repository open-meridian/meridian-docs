# Add a prediction-market plugin

Two data plugins (each holding `data`) put prediction markets' public market
data into the deployment's [lake](../concepts/the-lake.md), with no key and
no account: **Kalshi**, from
[plugin-kalshi](https://github.com/open-meridian/plugin-kalshi), and
**Polymarket**, from
[plugin-polymarket](https://github.com/open-meridian/plugin-polymarket).
They pass one data suite between them. Each contract they price is a
[binary event contract](../concepts/instruments.md#binary-event-contracts)
in the deployment's instrument store. From contract v23 each also records
its contracts' [outcomes](#outcomes), and a third, **Polymarket US**, from
plugin-polymarket-us, joins them.

!!! note "Contract v23, built, not released"
    plugin-kalshi 0.5.0 and plugin-polymarket 0.5.0 (Polymarket's
    international venue) record their contracts' outcomes, and
    plugin-polymarket-us 0.1.0 is a new data plugin for Polymarket US,
    each built on open-meridian 0.27.0 (contract v23) and to be released
    with it. They need a runtime serving contract v23.

!!! note "TODO: the prediction-market plugins on contract v23"
    Confirm each version and name its release date and the chart it runs
    on (`0.1.CHART23`) once released; and the repository link for
    plugin-polymarket-us once it is public.

!!! note "Contract v20"
    plugin-kalshi 0.2.0 and plugin-polymarket 0.2.0, released 2026-10-12,
    are built on open-meridian 0.24.0 (contract v20), and run on chart
    0.1.298 or later: each takes the data role's common pages and
    figures, reads its dataset's licence, and has its `synthetic` setting
    renamed `sample_data` (see [Using a data plugin](using-a-data-plugin.md)).

!!! note "Contract v19"
    plugin-kalshi 0.1.0 and plugin-polymarket 0.1.0, released 2026-10-10,
    are built on open-meridian 0.23.0 (contract v19), proven against core's
    runtime and plugin harness at chart 0.1.293, and run on chart 0.1.294
    or later.

## What each serves

Each serves one dataset, `<instance>:live`, for the contracts a reader asks
about, pulled for a read and kept current while a standing want stands, at
most once a second:

| Plugin | What | Its money | Day | Default licence |
|---|---|---|---|---|
| Kalshi | each contract's last trade price, best bid and best ask, as prices; its best bid and offer with their sizes, as a quote | US dollars, per contract | UTC, ending at 00:00 | served, not kept |
| Polymarket | each outcome token's last trade price, best bid and best offer, as prices; its best bid and offer with their sizes, as a quote | Polymarket's own USDC instrument, per token | UTC, ending at 00:00 | kept two days |

Neither records trades, daily closes or bars. Every figure is exact, read
from the venue's text, never through a float.

- **Per contract asked about, never the whole venue.** The lake asks for a
  contract by the deployment's instrument ID. The plugin reads that record
  and names the venue's market by its identifiers: the venue's own code
  (Kalshi's ticker, or Polymarket's token ID, a `symbol` at `kalshi` or
  `polymarket`), else another source's symbol the venue answers as one of
  its markets. It never reads the venue's whole list, and adds no record
  for a market nobody asked about. Another source's symbol is never matched
  to a record that is a security, or of a type other than a binary event
  contract.
- **Binary contracts only.** A market is served only where the venue states
  it binary, and only where its record states no other payout. Polymarket's
  two outcomes are two tokens, each its own binary event contract with its
  own record; a market with other than two outcomes is not served.
- **Money per contract, never a probability.** A price is what one contract
  costs: `0.43` US dollars at Kalshi. Each contract pays 1 (one dollar at
  Kalshi, one USDC at Polymarket), and a price outside nothing to the payout
  is counted and not recorded. The implied probability, the price over the
  payout, is a reader's computation, as the
  [Board](watch-the-board.md) shows it.
- **Kalshi's two sides.** Kalshi's book holds bids on its YES side and its
  NO side. A NO bid at p is an offer to sell YES at the payout less p, so
  the contract's ask is the payout less the best NO bid, with that bid's
  size, the raw book kept beside it.
- **Polymarket's USDC is a token, never a dollar.** Its prices name
  Polymarket's own USDC instrument, resolved by its code at `polymarket`,
  and a record is added where the deployment holds none. A reader values it
  through a price of that USDC, never by assuming 1.
- **The venue.** Kalshi is resolved in the venue master by its MIC (`KLSH`),
  and each row names its [venue ID](../concepts/venues.md). Polymarket has
  no MIC and the venue master carries no code for it yet, so each row
  leaves the venue empty with the code beside it, and the miss is reported,
  asked again the next day.
- **Wants** are recorded against or declined per subject: not covered (not
  one of the venue's binary contracts), beyond history (a day or a range
  already past: both venues' public reads answer now), or the source
  silent.

## Outcomes

From contract v23 each plugin serves a second dataset, `<instance>:outcomes`,
pushed and kept by default: once its venue resolves a contract it serves, it
records the [outcome](../concepts/the-lake.md#an-event-contracts-outcome)
unasked, one row key per contract, each change a new version, and stops
reading once the final stage is recorded.

| Plugin | Its stages | Its determination and settlement value | Kept as reported |
|---|---|---|---|
| Kalshi | `determined` is determined, `disputed` disputed, `amended` determined again as a new version, `finalized` final, with when it paid out | From Kalshi's settlement value against the payout: pays, pays nothing, or pays part (a scalar) | Kalshi's `result`: yes, no or scalar |
| Polymarket | Final only: its public reads state a resolution once made, never a proposal's or a dispute's answer | Each token's own stated price, in Polymarket's USDC: 1 pays, 0 pays nothing, 0.5 pays part (50-50); a NO token of a market resolved YES pays nothing | The token's stated price |
| Polymarket US | Final only, once a market's final settlement is published | The market's settlement price in US dollars: 1 pays, 0 pays nothing, between pays part | The settlement price |

None states when a contract was determined, so each outcome is valid from
when the answer first stating it arrived; Polymarket's and Polymarket US's
pay-out time stays 0. The data suite's `records-an-outcome` and
`records-a-partial-payout` pass on each; Polymarket and Polymarket US mark
`restates-a-disputed-outcome` not presented, with why, since neither states
a dispute. A reading plugin entitled to the `outcomes` dataset hears and
reads them; the payout itself is not in the book in v23.

## Polymarket US

From contract v23, built, not released: **plugin-polymarket-us** 0.1.0, a
data plugin for Polymarket US, apart from the international Polymarket,
which plugin-polymarket keeps serving. It reads Polymarket US's keyless
public gateway, polled at most five calls a second, with no key and no
account, and never trades.

- **One market, one instrument**: each market is one binary event contract,
  its YES side, paying one US dollar; its NO side is the same instrument
  held short. The venue is resolved by its MIC, `QCEX`.
- **Prices and quotes** (`<instance>:live`, kept two days by default): the
  book's best bid and offer with their sizes, and its last trade.
- **Outcomes** (`<instance>:outcomes`), as above. No daily bars: the
  venue's price history is display prices, not trades.

Launch it as the others, from `plugin-polymarket-us`, named
`polymarket-us`.

## The terms

No plugin's default licence says anything about Kalshi's, Polymarket's or
Polymarket US's terms. What a deployment may keep, show, or use in a
demonstration is for its deployment admin and its users to settle with each
venue; this is not legal advice. The deployment admin records the licence
they settled on the Data sources page, which replaces the default, and a
licence records only what was entered. Neither the plugins nor these docs
say a deployment meets any venue's terms, and no venue is affiliated with or
endorses Open Meridian.

## Upload and launch the plugin

As the deployment's administrator, from each plugin's repository:

```sh
meridian plugin upload --dir plugin-kalshi
meridian plugin launch kalshi <version> --instance kalshi-1
```

Polymarket is the same, from `plugin-polymarket`, named `polymarket`, as
`polymarket-1`. The repositories are named `plugin-<name>`; the plugins
keep their names, `kalshi` and `polymarket`. The launch asks for the `data`
role and storage for its raw responses, and no key. Their settings, on each
plugin's **Settings** form:

- **Raw responses' window** and what happens **past the window**: how long
  the venue's answers stay in the plugin's storage (30 days by default), and
  whether a day past it is archived, kept or deleted. See
  [Keep older records in the archive](keep-older-records-in-the-archive.md).
- **Synthetic mode**, on a development deployment only: answers from
  exchanges committed with the plugin instead of calling the venue.

Each marks the data suite's cases about kinds of data it never publishes
as not presented, with why (daily closes and bars, trades, a currency's
rate, a security's price, and at Kalshi a stablecoin's price), and passes
every other case.

## License, entitle, and complete the contracts

1. On **Settings**, **Data sources**, set the `live` dataset's licence, and
   entitle the plugins that read it: a `reporting` plugin such as the
   sample reporting plugin's Board reads its prices; only a `signal` or
   `ems` plugin reads its quotes. From contract v23 license and entitle
   its `outcomes` dataset too, for the `reporting`, `portfolio`,
   `compliance`, `signal` or `operations` plugins that read outcomes. See
   [License and entitle a dataset](license-and-entitle-a-dataset.md).
2. On **Instruments**, complete each contract's record. Where a record
   lacks the venue's code, its class or its type, the plugin reports the
   code beside the identifier it matched and offers `event_contract`,
   `binary_event_contract` and the venue's title (at Polymarket, the
   market's question and the token's outcome). Choose the type, and the
   form asks for the payout, 1 US dollar at Kalshi or 1 in Polymarket's
   USDC, and when trading closes.

## See it working

Each plugin's two pages are under Manage for its admin, and each is a read
tool for an agent, `read_connection` and `read_datasets`, answering what the
page shows. Neither shows a price.

- **Connection**: where it answers from (the venue, or synthetic mode), its
  endpoints (at Polymarket, Gamma for a token's market and the CLOB for its
  book), the limits it keeps (at most 5 requests a second, a 429 waited
  out), how its calls went, the last error, and the venue ID it resolved.
- **Datasets**: its dataset; the contracts mapped for the instruments the
  lake asked about, and those not served with why; the cash its prices and
  payouts are in and what each contract pays; and the wants it heard,
  standing ones first, under a search.

## Related

- [Binary event contracts](../concepts/instruments.md#binary-event-contracts).
- [Watch the market on the Board](watch-the-board.md): the Prediction
  markets panel.
- [Using a data plugin](using-a-data-plugin.md): every data plugin's
  first-use path and pages, and Alpaca, Tradier, Tiingo, Coinbase, Kraken
  and H.10.
