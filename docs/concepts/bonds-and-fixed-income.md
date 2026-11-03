# Bonds and fixed income

Contract 29 holds fixed income: bonds, agency pools, TBAs, agency CMO
tranches and certificates of deposit. Each is a record under its own
template, held in face, priced per 100 of face and serviced in the
[book of record](the-book-of-record.md). Every operation and record here
is `preview`.

## The templates

| Template | What it describes |
|---|---|
| `bond` | A government, agency, supranational, municipal or corporate bond: its issuer, seniority, coupon (fixed, floating, zero or step) and frequency, day count and conventions, its dates and record dates, denominations, a floater's terms, its call, put and sinking-fund schedules, and what it was stripped from |
| `mbs_pool` | An agency pass-through pool: its agency, program, pass-through rate, payment day and payment delay |
| `tba` | A to-be-announced agency trade: its agency, program, coupon and settlement month |
| `cmo_tranche` | An agency REMIC class: its interest types (fixed, floating, inverse floating, interest only, principal only, Z) and principal types |
| `certificate_of_deposit` | A bank's CD: the bank as issuer, whether the deposit is insured, and its survivor option |

A bond known only by its CUSIP or ISIN stays a deployment-local `LCL-`
record, its CUSIP never sent to the platform: see
[One ID per instrument](one-id.md). A record lists what it lacks until it is
complete.

## Bond terms and offered terms

A record's terms are its template's fields. A plugin holding `reference`
**offers** the terms its source states for a security the deployment
lists, field by field, with
[`offer_template_fields`](../api/typed-operations.md#offer_template_fields):
under the `bond` template a bond's coupon, dates, day count and issuer (by
its LEI), and under `certificate_of_deposit` a CD's. An offer is kept with
its source and time beside the record. It never overwrites a value a
person set, and a person can see each offer on the instrument's record and
choose it.

An agency's disclosure plugin offers a pool's or a tranche's terms from
the same files it reads factors from.

## Money: face, percent of par and the dollar price

- **A debt record's quantity is face**, and its price is per 100 of face.
- **A fill's price is the dollar price per 100 of face** (`Execution.price`),
  always. A yield or a spread the source quoted travels beside it as it was
  quoted, never in its place (`price_basis`, `yield`).
- **Cash is face times price times 0.01**, exact: percent of par.
- **Accrued interest moves cash.** An allocation's accrued is its own cash
  line at booking, so settlement is principal plus accrued. A coupon
  received is two cash lines: the purchased accrued returned, and the
  income.
- **Accrual uses FIX's day counts.** A day count v29's engine does not
  compute is named, never guessed: `NOT_EVALUATED_REASON_NOT_SUPPORTED`.

The lake's prices take the same bases: `Price`, `Trade` and `Quote` carry a
`PriceBasis` of percent of par, yield or spread (with the benchmark a
spread is over), and a capped size, such as "5MM+", is recorded as at
least that size (`Trade.quantity_capped`, `Quote.bid_size_capped`).

## The factor is the security's { #the-factor }

A pool's or a tranche's outstanding principal is its **original face
times its factor**, which its agency publishes each month. In Open
Meridian the factor belongs to the security, not to a fill:

- **An agency's data plugin records each held pool's or class's factor**
  as published, one row per pool or class and factor month, with its record
  and payment dates and, where the disclosure states them, the pool's WAC,
  WAM and WALA ([`record_factors`](../api/typed-operations.md#record_factors)).
  Factors are recorded only for the records the deployment names. A
  corrected file's factor is the row's next version.
- **A fill states original face.** The book takes the factor published for
  the fill's settlement month (the row whose factor month is the one before
  the month it settles in) and keeps it with the fill as
  `Execution.factor_taken`, pricing its cash, its lots and any later relief.
- **`factor_used` is only an override**, final, changed only by a
  correction of the fill. A booking whose fills state conflicting overrides
  is refused, naming `factor_used`.
- **A paydown** relieves each lot's cost by its cost times the fall over the
  prior factor. A split cost is exact where it ends within the cost's
  places, and half-even at them otherwise, the remainder kept in the lot or
  given to the last part, so no cost is made or lost.

### A fill before its factor { #a-fill-before-its-factor }

A fill can settle in a month whose factor is not published yet. Then:

1. **It books provisionally.** The latest published factor prices it, and
   the fill and its lots say which month's factor they await
   (`Execution.factor_month_awaited`, `Lot.factor_month_awaited`).
2. **It is revised when the factor arrives.** On publication, or on a
   republication, the book writes its own record of the revision
   (`LIFECYCLE_EVENT_KIND_FACTOR_REVISION`): the old and new factor, the
   `cash` and `cost_change`, and the `execution_id` it revises. Before the
   fill's settlement date the revision is pending, and settles with the
   fill.
3. **After settlement, a claim is opened.** A revision arriving after the
   settlement date is held as an open claim
   (`LIFECYCLE_EVENT_STATE_CLAIM_OPEN`), the money difference to be
   collected or paid, until a person marks it settled. This follows the
   market's own practice of settling on the last available factor and
   correcting once the current one is published.

A fill whose settlement date is not yet known keeps its security and cash
pending, dated nothing, until a correction states the date.

**Rounding.** A pool's or a tranche's fill's cash rounds to the cent,
half-even; its lot's cost is that rounded cash; a provisional amount and
each revision's differences round alike.

## In force { #in-force }

**In force is the version a default read serves.** A row key's version in
force is its latest; a rate's is its latest by published time, so an older
publication heard late is kept as the next version and never takes force.
A change of quality state alone is a restatement, the next version of its
row key. Every count a dataset reports, its quality counts and its
unconverted, closed-day and outside-coverage counts, is of the rows in
force.

## The book's records { #the-books-records }

A custodian reports, once each: `coupon_received`, `redemption`,
`paydown`, `accretion`, `tba_allocation`, `strip` and `reconstitution`.
A `servicing` plugin proposes what it expects from the terms and the
published factors: `expected_coupon`, `expected_maturity` and
`expected_paydown` (a paydown, or an accretion for a Z or an IO class). A
factor revision is the book's own record, as above.

## The engine's measures

`analytics.DEBT_MEASURES`: accrued interest, bond yield, price, risk,
key-rate durations and spreads, the Treasury curve, historical prepayment,
WAL at the pool's own CPR (its 3-month historical CPR, else its life CPR,
naming the speed used) and the make-whole amount, and `expected_move`. See
[The analytics component](the-analytics-component.md).

## The SDK's helpers { #the-sdks-helpers }

`meridian.helpers.debt` holds the money rules once, so every plugin
computes them the same way:

| Names | What |
|---|---|
| `percent_of_par`, `current_face`, `fill_cash`, `paydown_cash`, `coupon_split` | Cash from face and price; current face from the latest factor; a fill's cash and a paydown's principal, half-even to the cent; a coupon's two lines |
| `year_fraction`, `accrued_per100`, `coupon_dates`, `coupon_period` | Accrual by FIX's day counts |
| `factor`, `read_factors`, `latest`, `factor_month`, `settlement_month` | A factor row built; a pool's history read every page; the version in force; the months |
| `taken`, `awaited`, `open_claims` | What the book decided: the factor taken, the month awaited, the open claims. Read them, never re-derive them |
| `quoted_yield`, `capped`, `characteristics` | A yield or spread quote, a capped size, and the fixed-income trade characteristics by meaning |

`meridian.helpers.lifecycle` reports the custodian's records once
(`lifecycle.report`), proposes servicing's expectations
(`lifecycle.expected_paydown`, `lifecycle.propose`), and marks an open claim
settled (`lifecycle.settle_claim`).

```python
from meridian.helpers import debt, lifecycle
from meridian.roles import servicing


class Servicing(servicing.Role):
    async def on_factors_recorded(self, heard) -> None:
        pool_id = heard.message.factor.meta.subjects[0].entity_id
        rows = await debt.read_factors(self, [pool_id], "2026-01-01", "2026-11-30")
        if len(rows) < 2:
            return
        prior, current = rows[-2], rows[-1]
        for account_id, original_face in held(pool_id):   # the plugin's own positions
            expected = lifecycle.expected_paydown(account_id, pool_id, original_face,
                                                  prior, current, currency="USD")
            if expected is not None:
                await lifecycle.propose(self, [expected])
```

## Where the data comes from

The data plugins listed on [Integrations](../how-to/integrations.md)
include fixed-income sources: bond terms and curves, quotes and prints,
new-issue prices, and the agencies' pool and class factors. Each plugin's
own documentation says what it records and what its access needs.

## Related

- [Typed operations: contract 29's](../api/typed-operations.md#contract-v29s-operations).
- [Booking](booking.md) and [The book of record](the-book-of-record.md).
- [The lake](the-lake.md) and [Rates](rates.md).
- [The lake's data dictionary](../boundaries/lake.md) and [the book's](../boundaries/bor.md).
