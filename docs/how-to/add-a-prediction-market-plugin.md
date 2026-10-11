# Add a prediction-market plugin

Two data plugins (each holding `dgm`) put prediction markets' public market
data into the deployment's [lake](../concepts/the-lake.md), with no key and
no account: **Kalshi**, from
[plugin-kalshi](https://github.com/open-meridian/plugin-kalshi), and
**Polymarket**, from
[plugin-polymarket](https://github.com/open-meridian/plugin-polymarket).
They pass one `dgm` suite between them. Each contract they price is a
[binary event contract](../concepts/instruments.md#binary-event-contracts)
in the deployment's instrument store.

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

## The terms

Neither plugin's default licence says anything about Kalshi's or
Polymarket's terms. What a deployment may keep, show, or use in a
demonstration is for its deployment admin and its users to settle with each
venue; this is not legal advice. The deployment admin records the licence
they settled on the Data sources page, which replaces the default, and a
licence records only what was entered. Neither the plugins nor these docs
say a deployment meets either venue's terms, and neither venue is
affiliated with or endorses Open Meridian.

## Upload and launch the plugin

As the deployment's administrator, from each plugin's repository:

```sh
meridian plugin upload --dir plugin-kalshi
meridian plugin launch kalshi <version> --instance kalshi-1
```

Polymarket is the same, from `plugin-polymarket`, named `polymarket`, as
`polymarket-1`. The repositories are named `plugin-<name>`; the plugins
keep their names, `kalshi` and `polymarket`. The launch asks for the `dgm`
role and storage for its raw responses, and no key. Their settings, on each
plugin's **Settings** form:

- **Raw responses' window** and what happens **past the window**: how long
  the venue's answers stay in the plugin's storage (30 days by default), and
  whether a day past it is archived, kept or deleted. See
  [Keep older records in the archive](keep-older-records-in-the-archive.md).
- **Synthetic mode**, on a development deployment only: answers from
  exchanges committed with the plugin instead of calling the venue.

Each marks the `dgm` suite's cases about kinds of data it never publishes
as not presented, with why (daily closes and bars, trades, a currency's
rate, a security's price, and at Kalshi a stablecoin's price), and passes
every other case.

## License, entitle, and complete the contracts

1. On **Settings**, **Data sources**, set the `live` dataset's licence, and
   entitle the plugins that read it: a `reporting` plugin such as the
   sample reporting plugin's Board reads its prices; only a `signal` or
   `ems` plugin reads its quotes. See
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
- [Add a public data plugin](add-a-public-data-plugin.md): Coinbase, Kraken
  and H.10.
