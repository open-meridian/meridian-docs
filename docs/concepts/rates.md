# Rates

Beside prices, bars, trades and quotes, [the lake](the-lake.md) keeps
**rates**: reference-rate fixings such as SOFR and €STR, their averages,
index levels such as the SOFR Index, and the points of a curve such as a
government par yield curve. A data plugin records them from the publisher,
and a `reporting`, `portfolio`, `compliance` or `signal` plugin reads them,
point in time, as it reads prices.

## What a rate is

A rate is one row, with the envelope every lake row has, and:

| Field | What |
|---|---|
| `kind` | `fixing`, `average`, `index_level`, `par_yield`, `zero`, `discount` or `coupon_equivalent` |
| `value` | A `UnitValue`: a decimal with its unit. 3.87 per cent is 3.87 `percent`, never an amount of money. The units are a closed list (`percent`, `basis_points`, `index` with its base period, and a few counts and ratios), or a UCUM code for a physical unit |
| `convention` | The rate's day count (`act_360`, `act_365_fixed`, `act_act`, `thirty_360`, `bus_252`) and compounding (`simple`, `compounded` with its periods a year, `continuous` or `discount`), as the publisher states them |
| `tenor` or `maturity_date` | A curve's point by its tenor, a count and a unit (`ON`, `3M`, `10Y`), or by an exact maturity date |
| `preliminary` | A fixing published as preliminary, made final by a later version |
| `volume`, `transaction_count`, `percentiles` | Where the publisher states them, as SOFR's volume and its 1st, 25th, 75th and 99th percentiles |

**What a publisher leaves out is no row.** A tenor not published that day
is not recorded, and reads as the source silent, never as zero.

**A curve is one record, its points rows.** A curve's subject is one
record; each point is a row with its tenor, and the curve for a date is
its rows on that business date. Two conventions for one tenor, a bill's
discount rate and its coupon-equivalent yield, are two rows. A
single-point series that is another source's curve point is recorded
against the curve's record with its tenor, so both sit under the
deployment's source priority.

## Their subjects

A rate is about a **referential** record: an `INS-` record of the asset
class `referential`, of one of three types.

| Type | For |
|---|---|
| `interest_rate` | A reference rate: SOFR, EFFR, OBFR, the SOFR averages, €STR and its averages; each bound of a target range a record of its own |
| `rate_curve` | A curve: a government's nominal and real par curves, its bill rates, a zero curve |
| `index` | An index level: the SOFR Index, €STR's compounded index |

The platform seeds these records, as it seeds calendars and venues, each
named by the administrator's code at its source and, where one exists, a
FIGI or an ISIN. A deployment resolves one by its administrator's code where
the platform's [licence list](one-id.md#the-licence-list) names that
administrator: the New York Fed, the Federal Reserve Board, the ECB and the
US Treasury, from chart 0.1.312. Core ships the platform's templates for the
three types, so a record names its template before its first pull. A
referential record names what the lake observes and is
**never held**: an entry moving a position in one is refused, `invalid`,
naming `instrument_id`, and no order names one. See
[One ID per instrument](one-id.md).

## Recorded once, revised by the publisher

Every rate carries its **published time**, where the publisher states it.
A publisher's revision, a preliminary fixing made final or a value
corrected, is the next version of the same row, ordered by published time;
a version whose only change is its raw reference is a confirmation,
recorded and not counted as a restatement. The row key names the series,
kind, tenor or maturity, convention, business date and subject, never the
published time.

## Reading them

[`list_rates`](../api/typed-operations.md#list_rates) reads rates as
[`list_prices`](../api/typed-operations.md#list_prices) reads prices: the
latest in force at a valid time, a business date, or a range of valid
times; as of a recorded time; from the deployment's source priority, named
datasets, or every entitled dataset side by side; narrowed by kind and
tenor.

**By publication time.** Beside the recorded-time cut, a read may ask what
the source **had published by a moment** (`published_as_of_ns`): the
version in force by published time among the rows recorded by the cut. A
backfill recorded today then still answers what was known on an earlier
date. The recorded-time cut stays the default, and the audit answer.

**Heard.** A new rate is delivered as `rates_recorded`, conflated: the
latest value first per subject, dataset, kind, tenor, maturity and
convention, since every rate is daily or slower. The bounded query,
[`query_lake`](../api/typed-operations.md#query_lake), takes the kind
`rates` too, for the roles that read them.

**Which source first.** A deployment admin orders the datasets a default
read of rates takes on the **Data sources** page's priority, as for prices,
bars, trades and quotes (see
[License and entitle a dataset](../how-to/license-and-entitle-a-dataset.md)).

## Who records and reads them

The public publishers' plugins record them: the New York Fed's reference
rates, the US Treasury's curves, the Federal Reserve Board's H.15 rates and
zero curve, the ECB's €STR, and FRED's copies of them, each recorded against
the publisher's record (see
[Using a data plugin](../how-to/using-a-data-plugin.md#the-new-york-fed-the-us-treasury-and-fred)).

| Role | Does |
|---|---|
| `data` | Records rates ([`record_rates`](../api/typed-operations.md#record_rates)) |
| `reporting`, `portfolio`, `compliance`, `signal` | Read them, hear them, and query them |

## Not built yet

- **Filings, fundamentals and economic series**: the lake's later kinds.
- **A deployment's licence counts**, for rates as for every kind: a
  dataset of rates is licensed and entitled as any other.

## Related

- [Record rates in a data plugin](../how-to/record-rates.md).
- [The lake](the-lake.md): datasets, versions, reads and wants.
- [The lake's data dictionary](../boundaries/lake.md).
