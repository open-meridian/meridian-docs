# Money and instruments

An amount in Open Meridian is a **Money**: an exact decimal and the asset it
is in. That asset is always an **instrument**: the cash
instrument of a currency or of a token, in the deployment's
[instrument store](instruments.md), named by its instrument ID as every
other instrument is. A US dollar amount names the US dollar's cash
instrument; a USDC amount names USDC's. A trade's price, a quote's two sides and a
[binary event contract](instruments.md#binary-event-contracts)'s payout are
each a Money too: 1 USD at Kalshi, 1 in the venue's own USDC instrument at
Polymarket.

## Why an instrument, not a code

A currency code cannot name every asset a price is quoted in. A crypto venue
quotes in USDT and USDC, which have no ISO 4217 code, and a venue's USDC and USDC on a network
may be two instruments. A USDT amount is never a US dollar amount, and a
stablecoin is never matched to the currency it tracks. Naming the cash
instrument lets a fiat amount and a token amount be the same kind of thing,
exact, with nothing guessed.

## What a plugin sends

A plugin may still name a fiat currency by its ISO 4217 code alone:

```python
meridian.Money(Decimal("12.50"), "USD")
```

Core resolves the code, dated, to the currency's cash instrument, as it
resolves a symbol, and what it keeps and answers names the instrument: a
Money read back carries `instrument_id` beside the code. A plugin names an
asset with no ISO 4217 code, a token, by its instrument alone, as
[`resolve_identifier`](../api/typed-operations.md#resolve_identifier)
resolved it from the token's identifiers:

```python
meridian.Money(Decimal("2410.5"), instrument_id=usdc)
```

Refused, naming the field:

- a token's code (`USDC`, `USDT`) given as a currency code;
- a code and an instrument that name two different assets;
- a Money naming neither, which the SDK refuses before anything is sent.

A bar's open, high, low, close and VWAP are in one asset, refused
otherwise. An amount's number is unchanged: an exact decimal, never a float,
refused rather than rounded past 18 decimal places or 38 digits.

## Where it shows

A person sees amounts with their currency. An agent reading the
book or the street through a plugin's tools reads each amount with its
instrument ID beside the code. In the [data dictionary](../boundaries/shared.md#meridian.v1.Money),
`Money.instrument_id` says what is named, and `Money.currency_code` that it
is empty for an asset with no ISO 4217 code.

## Related

- [The lake](the-lake.md): a price's amount names its cash instrument, an FX
  rate is the price of one currency's cash instrument in another.
- [Typed operations: `Money`](../api/typed-operations.md#money).
- [Instruments](instruments.md): identity, the security master and the
  deployment's own store.
