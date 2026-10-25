# Listed options and futures

Added in contract 28. A listed option or a future is an instrument like any
other: one platform `INS-` record, minted from a template, held in the book
in lots. What sets it apart is that an exchange lists thousands of series
under each underlying, most of which a firm never trades, and that each
series ends: it expires, is exercised or assigned, or, for a future, settles
its variation every day. This page explains how a deployment reads a chain
without minting it, how a series gets its record when it is wanted, how its
lifecycle reaches the book, and how a multi-leg order is one package.

What the analytics component computes on a chain, implied volatility,
greeks, the surface and the grid among them, is in
[The analytics component](the-analytics-component.md#options-measures).

## The templates

The platform publishes three templates for them, each a fixed set of fields
with its calculation package (see [One ID per instrument](one-id.md#templates)):

| Template | Type | What it is |
|---|---|---|
| `TPL-listed-option` | `listed_option` | A listed equity, ETF or index option |
| `TPL-future` | `future` | A cash-settled or financially settled future, or a physically delivered one held, closed or rolled |
| `TPL-future-option` | `future_option` | An option on a future |

An option's terms follow FIX's instrument block: its underlying (a platform
`INS-` record), `put_or_call`, `strike_price`, `expiration_date` and
`last_trade_date`, `exercise_style` (American or European),
`settlement_method` (physical or cash), `settlement_time` for a
cash-settled option (AM, settled on the expiration day's opening prints, or
PM, on its close), `contract_multiplier`, what one contract's premium is
multiplied by, and a **deliverable**: each instrument and its quantity, cash
among them. The deliverable is apart from the multiplier because an
adjustment can change one without the other: after a 3-for-2 split a
contract may deliver 150 shares on a multiplier of 150, and after a merger
another company's shares and cash. Each series also carries its
`option_root` (the OCC root, `SPX`, `SPXW`, `AAPL`) and `contract_month`.

A future's terms are its underlying (an index, an equity, a rate, or a
commodity's referential record), its exchange's `product_code` (`ES`, `CL`),
`contract_month`, `last_trade_date`, `final_settlement_date`,
`settlement_method`, `contract_multiplier` (what a one-point move is worth
per contract) and, where it is physically delivered, its
`first_notice_date`. A commodity is a referential record of its own type,
`commodity`, which the platform's staff seed and nobody holds.

**Each field has a requirement level** (contract 28): `mint`, needed to
mint the record; `complete`, needed before the book takes it; or `optional`.
A field may be `repeated`, as FIX's repeating groups are; the deliverable is
one.

**An adjusted contract keeps its `INS-` ID.** Its new deliverable, strike
or multiplier is a dated version of its terms, and its new OSI symbol a
dated identifier, so the position's history stays on one ID.

**A series that ended is marked `expired`** by the platform after its last
lifecycle date: its ID is kept and never reused, and the replacement feed
marks the deployment's copy expired as its next version, moving nothing. A
position still held in an expired series is a break.

## A series' key

Every series has a public key, which the chain's rows carry before any
record exists:

- **An option** by its OCC Options Symbology Initiative symbol, scheme
  `occ_osi`: 21 characters, the root padded with spaces to 6, the
  expiration as `yymmdd`, `C` or `P`, and the strike times 1,000 in 8
  digits. `AAPL  261120P00230000` is Apple's 230 put expiring 20 November
  2026.
- **A future, or an option on one,** by one `ticker` identifier, the
  exchange's symbol with its month code, carrying its venue's ISO 10383 MIC
  in `source`: `ESZ6` with source `XCME`. The same ticker on two venues is
  two series.

FIGI is kept where a series has one. A series is matched on these
identifiers only; its terms are checked when it is minted, and a
disagreement is minted and flagged for the platform's staff.

## The chain: read, never minted

A **chain** is an underlying's listed series. A `data` plugin records each
series it lists under the underlying, as the template's fields
([`record_series`](../api/typed-operations.md#record_series)), with the
series' key on the row's envelope (`ObservationMeta.series_key`). It
records each series' open interest and volume per trading date as a
**statistic** ([`record_statistics`](../api/typed-operations.md#record_statistics)),
and its quotes and trades of a series under the underlying with the series'
key. **A chain's row is never resolved**: recording a chain mints nothing.

A reader reads an underlying's series in an expiration window
([`list_series`](../api/typed-operations.md#list_series)): each with its
terms, and the deployment's `INS-` record for it where one is held, matched
read-only. The chain's open interest is read with
[`list_statistics`](../api/typed-operations.md#list_statistics), and its
quotes and trades with `list_quotes` and `list_trades` naming `series_keys`
or `all_series`. A read that asks for no series never receives a chain's
rows, so a reader of an underlying's own quotes is not handed thousands of
option quotes.

| Statistic kind | What it counts |
|---|---|
| `STATISTIC_KIND_OPEN_INTEREST` | Contracts open at the trading date's end |
| `STATISTIC_KIND_VOLUME` | Contracts traded on the date |
| `STATISTIC_KIND_BLOCK_VOLUME` | Contracts traded in blocks on the date |
| `STATISTIC_KIND_SHORT_VOLUME`, `STATISTIC_KIND_TOTAL_VOLUME` | Shares sold short, and all shares, reported to a FINRA facility on the date |

**The quote at print.** A trade may carry the best bid and offer in force
when it printed (`Trade.quote_at_trade`), as the source states it or as the
plugin last received it on the same feed (`as_last_received`), with that
quote's own source time.

## A series gets its record when it is wanted

A series is minted on the platform only when the deployment wants it: to
order it, or for a standing want. A `portfolio`, `oms`, `ems` or `signal`
plugin asks with
[`request_series_records`](../api/typed-operations.md#request_series_records),
naming each series by its key and its underlying, and its cause: `order` or
`standing`. Each series is answered with its `INS-` record where the
deployment holds one or the platform matches or mints it; `pending_review`
where the platform's staff review it first; or `refused_by_rule`, with
nothing sent, where the deployment's rule does not allow it. A key no chain
row holds is refused, naming it. The platform verifies a series against
OpenFIGI first and, where OpenFIGI holds none, mints it from the chain as
the stated source and flags it for its staff.

**The series request rule** is a deployment admin's, **Series request
rule** on the dashboard's settings home page (`/admin#series-rule`):

| Field | Label | Default |
|---|---|---|
| `orders` | **For an order** | On: a series an order or a proposal names is asked for with no person |
| `standing_wants` | **For a standing want** | Off |
| `daily_limit` | **A day, at most** | 500 series a day, 1 to 5,000 |

Each change carries a reason and is its own record, and each request the
rule refuses is its own record too, its day's count kept across a restart.
Its **Request series** button opens **Request series records**, which asks
for series by hand, with a note.
Through an agent: `dashboard__read_series_request_rule`,
`dashboard__set_series_request_rule` and
`dashboard__request_series_records` (see
[Core's tools](../api/core-tools.md#listed-series)).

## Lifecycle events in the book

An exercise, an assignment, an expiry and a future's day of variation are
each the book's own record, a **lifecycle event** with an `LCE-` ID,
journaled as its own entry. **The broker's report is the record**:

- **`custody` or `connectivity` reports** what its broker states
  ([`record_lifecycle_event`](../api/typed-operations.md#record_lifecycle_event)),
  once: a report sent twice is answered with the first.
- **`servicing` proposes** what it expects
  ([`propose_lifecycle_events`](../api/typed-operations.md#propose_lifecycle_events)),
  such as an exercise by exception, moving nothing. A report matching a
  proposal by account, instrument, kind and date answers it, and the
  proposal is never booked as well. A proposal no report answers, or a
  report that differs from it, is a break.
- **`operations` releases** a proposal no report answered
  ([`release_lifecycle_event`](../api/typed-operations.md#release_lifecycle_event)),
  with a note, and the book books it as proposed.

| Kind | What the book does |
|---|---|
| `EXPIRY` | Closes the option's lots at nothing |
| `EXERCISE` | Closes the long option's lots and moves the deliverable at the strike: the underlying's lots opened or relieved, the premium the closed lots cost carried into the cost of the first lot a delivery opens, and the cash. Cash-settled, the cash alone |
| `ASSIGNMENT` | The same for a short option assigned |
| `SETTLEMENT_VARIATION` | A future's day of variation against the exchange's settlement price: a cash line only. The future's lot keeps its trade price |

The book prices an option's or a future's fill by its series'
`contract_multiplier`: one option bought at 2.50 on a multiplier of 100
costs 250.00. A roll is a close and an open, or a package. A physically
delivered future is held, closed or rolled; the book records no delivery.

`operations`, `servicing`, `portfolio` and `reporting` read an account's
events ([`list_lifecycle_events`](../api/typed-operations.md#list_lifecycle_events))
and hear each as `lifecycle_event_recorded`.

## Package orders

A **package**, a vertical spread, a straddle or a covered call, is one order
with legs and no instrument of its own, after FIX's multileg order (35=AB):

- **2 to 16 legs**, each an instrument, a side and a ratio. The ratios are
  whole and in lowest terms; at most one leg is in an instrument that is
  neither an option nor a future (the stock leg of a covered call).
- **Open or close** (`position_effect`) is required on an order or a leg in
  an option or a future, and refused on any other.
- **One net price per package unit**: on a buy, positive is a debit and
  negative a credit; the order's quantity is the number of package units.
- **One placement** carries the legs. The venue's fill is reported once for
  the package and once per leg, each leg's execution naming the package's
  (`package_execution_id`, with `multi_leg_reporting_type` `PACKAGE` or
  `LEG`, FIX 442). The package's own execution books nothing; each leg books
  its own lots.

No leg may be in an expired series or one with no `INS-` record: ask for
the series first.

## For a plugin's author

The SDK's helpers, from SDK 0.33.0:

- `meridian.roles.chains`: `osi_symbol`, `osi_terms` and `osi_key` for the
  OSI symbol; `option_series`, `statistic` and `series_meta` to record a
  chain; `read_chain`, `read_open_interest` and `want_series` to read one
  and ask for a series.
- `meridian.roles.lifecycle`: `expiry`, `exercise`, `assignment` and
  `variation` built as the broker states them and sent once by `report`;
  `exercise_by_exception` (`EXERCISE_THRESHOLD`, a cent) and `propose` for
  `servicing`; `due_for_release` and `release` for `operations`;
  `read_events`.
- `meridian.roles.packages`: `legs` in lowest terms (`MOST_LEGS`, 16),
  `propose`, and `report_fill` with each `LegFill`.

See [Record and read an option chain](../how-to/record-and-read-an-option-chain.md)
and the [Python SDK](../api/python-sdk.md#listed-options-and-futures).

## Related

- [The analytics component](the-analytics-component.md#options-measures): IV, greeks, the surface, the grid and positioning.
- [Scenarios](scenarios.md): the shocks a grid applies.
- [One ID per instrument](one-id.md): templates and the platform's records.
- [The book of record](the-book-of-record.md) and [The order lifecycle](the-order-lifecycle.md).
- [Typed operations: contract 28's](../api/typed-operations.md#contract-v28s-operations).
