# Record rates in a data plugin

This page is for the author of a data plugin for a rates publisher: a
central bank's or a treasury's fixings, averages, index levels or curves.
It records them with `meridian.roles.data.rates` and passes the data
suite's rates cases. What a rate is, and how it is read, is in
[Rates](../concepts/rates.md). Start from
[Write a data plugin against its suite](write-a-data-plugin.md): this page
adds what is different for rates.

You need SDK 0.32.1 or later and a deployment on contract 27 (chart
0.1.309 or later).

## Declare the dataset

A dataset of rates declares the data type `meridian.v1.Rate`:

```python
DatasetDeclaration(
    key="ust_par",
    vendor="My publisher",
    data_types=["meridian.v1.Rate"],
    modes=["pull"],
    cadence=86_400,
    history=3650,
    licence_default=DatasetLicence(kept=True, display=True),
    day_time_zone="America/New_York",
)
```

## Resolve the subjects

A rate's subject is a referential record the platform seeds: a reference
rate, a curve or an index. `Feed.subject` resolves it by the identifiers
the publisher states, the administrator's code as a `symbol` at its source
and, where one exists, a FIGI or an ISIN, once per process. A record the
deployment does not hold is reported missing once a day, and its rows are
not recorded: a plugin never mints one.

```python
from meridian.roles.data import rates

feed = rates.Feed(plugin, "ust", wants=wants, day_zone="America/New_York")
curve = await feed.subject(("symbol", "PAR_NOMINAL", "ust"), instrument_type="rate_curve")
```

## Build the rows and record them

`Feed.rate` builds one rate; `Feed.curve` builds a curve's points for one
date, one row per tenor the publisher published, and none for a tenor it
left empty. A bare number is a percent; `rates.index_level(value, base)`
is an index's level. Name the convention as the publisher states it, with
the constants for the common ones: `MONEY_MARKET` (actual/360, simple),
`BOND_EQUIVALENT` (semi-annual compounding), `DISCOUNT` (actual/360, a
bill's discount) and `CONTINUOUS`.

```python
rows = feed.curve(
    curve, "ust_par", "par_yield",
    {"1 Mo": "4.12", "3 Mo": "4.09", "10 Yr": "4.21", "20 Yr": None},
    business_date=day, published_ns=published_at, convention=rates.BOND_EQUIVALENT,
    raw_key=raw,
)
await feed.record("ust_par", rows)
```

`rates.tenor` reads a publisher's labels (`1 Mo`, `13 WEEKS`, `10 Yr`,
`3M`, `ON`) as the contract's tenor; a fraction of a month, such as
`1.5 Month`, is refused, for the plugin to name a maturity date or a whole
tenor instead. `Feed.record` sends 500 rows a batch, against a want where
they answer one, and through the plugin's `Wants`, which counts them and
records their age at the edge.

**Row keys and revisions.** The row key names the series, kind, tenor or
maturity, convention, business date and subject, never the published time,
so a same-day revision is the next version of the same row and an identical
repeat is answered unchanged. Always pass `published_ns` where the
publisher states it: a read by publication time depends on it.

**One point of another source's curve.** A single-point series that is a
curve's point, such as a 10-year yield, is recorded against the curve's
record with its tenor (`Feed.rate(..., tenor="10Y")`), so it sits beside
the curve's own publisher under the source priority.

## Hold it to the suite

The data suite's rates cases are `about: rates`. Map each to the plugin's
own conversion of its publisher's recorded answer with
`data.testing.rates_producers`, and name everything a rates-only plugin
never presents with `data.testing.RATES_NOT_PRESENTED`: the cases about
prices, trades, quotes and outcomes (among them `an-exact-price` and
`a-want-recorded-against`, about `closes` from SDK 0.32.1), a stream's
liveness, and the feed delay, which is `about: latency` until contract 28.

```python
from meridian.roles.data import testing

PRODUCERS = {
    **testing.rates_producers(MY_CASES, source="ust"),
    **MY_OTHER_PRODUCERS,                   # the cases every data plugin answers
}
report = run("data", PRODUCERS, not_presented=testing.RATES_NOT_PRESENTED,
             instance_id="reference-1")
```

`MY_CASES` maps each of `data.testing.RATES_CASES` to
`async def case(feed, instruments)`, which converts the publisher's answer
for the case and records it through the `feed` given. A case your
publisher never presents goes in `not_presented` too, with why.

## Related

- [Rates](../concepts/rates.md).
- [Write a data plugin against its suite](write-a-data-plugin.md).
- [`record_rates`](../api/typed-operations.md#record_rates) and
  [`list_rates`](../api/typed-operations.md#list_rates).
- [The Python SDK's rates helpers](../api/python-sdk.md#rates).
