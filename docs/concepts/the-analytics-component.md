# The analytics component

The **analytics component** computes figures over the book and the lake for
the plugins that ask: an account's market value, its exposure, its
historical value at risk, what an event group pays if each outcome
resolves. Every question is a **job**, answered through one API, and every
answer names what it was computed from, with a hash, so the same inputs
always give the same answer, whichever plugin asks.

It is core's, beside the book and the lake: its own process, a coordinator
and a pool of workers, with an engine written in Rust as part of core.
Nothing outside it computes a figure, unless a deployment admin routes a
pricing model to a [`pricing` plugin](#the-pricing-roles-seam). It holds
no record: a job is a read, and nothing it answers is kept in the book.
Its operations are `preview`.

## A job

A job names four things:

| Part | What |
|---|---|
| **Accounts** | The accounts it is over, one or more, each in the asking plugin's read scope. One outside it is refused, naming it. A job of [options measures](#options-measures) alone names none. |
| **Measures** | Each a definition and a version the component serves, with the breakdowns wanted, and for an event measure, the event group. |
| **Inputs, by reference** | The book's watermark, the lake's recorded-time cut-off (its as-of) and the source choice, one of each for the whole job. Unset, each is now and the deployment's source priority, resolved and named in the answer. |
| **A what-if** | Optionally, trades added to one account's positions, answered beside the base. Never a book record. |

From contract 27 a job may also name:

- **A business date**, an ISO 8601 date in the deployment's
  [time zone](dates-and-time.md), in place of the watermark and the as-of:
  the book at that date's end, the last watermark recorded on or before
  it, and the lake at that date's closes, the daily rows whose business
  date it is, each in its dataset's own day. Naming a watermark or an as-of
  beside it, or a date after today, is refused, naming `business_date`.
  Without one a job reads the book and the lake now, and says "as of" the
  time read.
- **A reporting currency**, a currency's cash instrument by its `INS-` ID:
  each account's figures are converted to it, each leg named in the
  provenance. Without one each account is answered in its base currency,
  and an account with none is not evaluated, `CONVERSION_MISSING`.

From contract 28 it may also name **chains**, the listed series the
[options measures](#options-measures) read, and **a scenario set**, inline
(`scenario_set`) or saved in the lake by its row key and version
(`scenario_ref`), which the scenario grid applies (see
[Scenarios](scenarios.md)); naming both is refused.

A plugin holding `reporting`, `portfolio`, `compliance` or `signal` runs
one with [`run_job`](../api/typed-operations.md#run_job). Asking is a
read at the plugin's own role: the component reads the book within the
plugin's read scope, and the lake within its entitlements and its role's
kinds, exactly as the plugin would. In the Python SDK, `meridian.analytics`
builds a job from typed values, each checked as it is built:

```python
from decimal import Decimal
from meridian import analytics

job = analytics.job(
    analytics.measure("exposure", by=["asset_class", "currency"]),
    analytics.measure("historical_var"),
    accounts=["ACC-12"],
    business_date="2026-10-22",           # contract 27: the book at its end, the lake at its closes
    reporting_currency="INS-...",         # contract 27: USD's cash instrument, say
)
answer = await analytics.Jobs().run(plugin, job)        # inline, or waited for
for figure in answer.figures("exposure"):
    print(figure.breakdown, figure.value, figure.currency_instrument_id)
```

**Inline or later.** A job answered within the request's window, two
seconds by default (the chart's `analytics.inlineMs`), comes back in the
reply. A larger one is answered later: the component tells the instance
that ran it alone (`job_finished`), and the instance reads the answer by
its ID ([`read_job_answer`](../api/typed-operations.md#read_job_answer)).
After a gap it catches up the jobs finished since the last sequence it saw
([`list_finished_jobs`](../api/typed-operations.md#list_finished_jobs)).
`analytics.Jobs` does all of this. Answers are held in memory, the last
1,000, and a restart of the component loses them with any job in flight:
the plugin runs the job again, and gets the same answer for the same
inputs.

## What it computes

### The measures

The component ships each measure's **definition** at a version, every
parameter that changes its number fixed by that version.
[`list_measure_definitions`](../api/typed-operations.md#list_measure_definitions)
answers them, with their parameters, the breakdowns each allows and the
scale it rounds to. Each is served at version 1, and `pnl` at version 2
too (from contract 27); the options measures of contract 28 are
[below](#options-measures):

| Definition | What it answers | Breakdowns | Scale |
|---|---|---|---|
| `market_value` | Each position's quantity times its model's value per unit, net | account, asset class, currency, instrument, sleeve, country | 2 |
| `exposure` | Each bucket's market value two ways, under the breakdown `component`: `gross`, without its sign, and `net`, long minus short | as `market_value` | 2 |
| `concentration` | Each instrument's market value as a weight of its account's market value | instrument | 2 |
| `pnl` | Version 1: unrealized P&L, each bucket's market value less its open lots' cost, under `component` as `unrealized`. Version 2: realized P&L beside it, under `component` as `realized` | as `market_value` | 2 |
| `historical_var` | Historical value at risk by full revaluation over the lake's daily closes: 99%, one day, a 500-day window, relative returns, the daily cut 16:00 New York | account, asset class, currency, sleeve | 2 |
| `expected_shortfall` | The mean loss beyond historical value at risk, on the same terms | as `historical_var` | 2 |
| `resolution_payoff` | Each account's P&L if each member of an event group resolves YES | account | 2 |
| `implied_distribution` | Each outcome's price over the sum of the group's prices, as a numerator and a denominator, beside the raw sum | none | 18 |
| `execution_cost` | Added in contract 27. Each execution's cost against each standard benchmark, in basis points, and each account's notional-weighted mean per benchmark; under the breakdown `benchmark`; each result recorded in the lake. See [Execution costs](execution-costs.md) | account | 4 |

**Realized P&L** (`pnl` version 2) is each closed lot's proceeds less the
cost of the quantity relieved, as the book records them on the lot (see
[The book of record](the-book-of-record.md#a-closed-lots-proceeds)). A lot
whose cost the book does not record, such as an opening balance stated
without one, leaves the figure not evaluated, `COST_MISSING`, never zero.
Ask it with `analytics.measure("pnl", 2)`; version 1 is unchanged.

A breakdown by any other name is a classification scheme the deployment
holds; one it holds none of leaves the position not evaluated,
`SCHEME_NOT_HELD`, naming it.

**Historical value at risk** revalues every position under each of the
window's days: each market object a position reads moves by its return on
that day. A close missing is carried forward, up to five days running;
past that, the position is not evaluated, `HISTORY_INSUFFICIENT`. The
version-1 definitions leave binary event contracts out, since a price that
jumps to its payout or to nothing is not described by its past returns, and
answer beside the figure their exact worst case on resolution.

**The event measures** read an [event group](event-groups.md) at the
version in force at the job's as-of. `resolution_payoff` answers one figure
per member resolving YES, each keyed by that outcome, and one more for
**none of the named** where the group is mutually exclusive and not
stated exhaustive. `implied_distribution` takes each member's mid where its
market is two-sided and its spread at most 0.10, and its last trade
otherwise; over a group not stated exhaustive it answers the raw prices and
their sum, and the distribution is not evaluated,
`GROUP_NOT_EXHAUSTIVE`.

**A what-if** adds its trades to the account's positions, each at its
assumed price or at the price at the job's as-of, with its cash leg in the
account's base currency. Every figure of that account is answered twice,
under the base and under the what-if, side by side.

### The pricing models

Every [template](one-id.md#templates) version names the **pricing model**
its instruments are valued with, and the price kind its calculations read.
Each model id has a built-in implementation, so a deployment with no
`pricing` plugin values every template there is:

| Model id | Templates | Value per unit |
|---|---|---|
| `cash` | Cash and currency, fiat and token cash instruments alike | Exactly 1 in the account's base currency; any other cash instrument at its own conversion, a stablecoin's included, never at par by assumption |
| `quoted_price` | Equity, fund, money market fund, crypto asset | The price of the template's kind, times its conversion, rounded half to even to 18 decimal places per unit; the market value is that rounded value times the quantity, exact. A fund listed on a venue is marked at its close, one listed nowhere at its NAV; a money market fund at its NAV as published, never assumed to be 1.00 |
| `binary_event` | Binary event contract | Before the venue's final determination, its price times its conversion. After it, the settlement value per contract the [outcome](the-lake.md#an-event-contracts-outcome) states, times the conversion of the payout's currency. A proposed or disputed outcome keeps the price |

**A conversion** to the account's base currency, or the job's reporting
currency, goes leg by leg: each leg a price in the lake of the currency in
hand in another instrument, of kind `close`, then `mid`, then `last`; the
shortest chain, at most three legs, each named in the answer.

**Inverted and crossed fiat legs** (contract 27). Data plugins publish a
market's own direction only, and the lake never inverts or crosses. Where a
**fiat** cash leg has no direct rate in the direction needed, the component
derives one:

- **inverted**, 1 ÷ the rate the other way, rounded half to even to 18
  decimal places, where the lake holds that;
- **crossed** through a **pivot currency**, where it holds neither: through
  the first of the deployment's **FX pivot currencies** that both legs
  reach, USD's and then EUR's where a deployment admin has set none (see
  [Set the FX pivot currencies](../how-to/set-the-fx-pivot-currencies.md)).

A direct or inverted rate is always taken before a cross. A crypto asset's
or a stablecoin's leg is never inverted or crossed: a token is converted
only by its own price in the lake. Each derived leg is named in the
provenance, so an answer through another pivot is another answer, with
another hash. A position under a local `LCL-` record is
[never priced](one-id.md#a-local-line-is-never-priced): it is not
evaluated, `LOCAL_RECORD`, never zero.

### Options measures { #options-measures }

Added in contract 28. A job may name **chains** (`Job.chains`), each an
underlying's [listed series](listed-options-and-futures.md) in an
expiration window, or by their keys, and ask the options measures over
them. A job of chain measures alone names no account; the scenario grid
also reads each account's held options. The component reads each chain for
the job, read-only, as the asking plugin would: the series in the window
(`ListSeries`), each series' latest quote, open interest on the latest two
trading dates and the underlying's volume (`ListStatistics`), the
underlying's price, its declared cash dividends (`ListCorporateActions`, see
[Companies and corporate actions](companies-and-corporate-actions.md)), and
each series' settlement instant. A series not held is named by its key and
never minted.

| Definition | What it answers | Breakdowns |
|---|---|---|
| `implied_volatility` | Each series' implied volatility at bid, mid and ask; none below intrinsic | series, quote side |
| `implied_forward` | Each expiration's forward from put-call parity, and the borrow it implies | expiry |
| `greeks` | Each series' delta, gamma, theta, vega, rho, vanna and charm, from the node its implied volatility at mid came from | series, greek |
| `surface_fit` | Raw SVI per expiration and SSVI across them, no-arbitrage checked: the parameters (SVI `a`, `b`, `rho`, `m`, `sigma`; `ssvi_rho`, `ssvi_eta`, `ssvi_gamma`), `rmse` in vol points and the share `inside_bid_ask` | expiry, parameter |
| `surface_residual` | Each series' residual to the fitted surface in vol points; `rich_or_cheap` only outside the IV bid-ask | series |
| `term_and_skew` | `atm_iv`, constant-maturity `atm_iv_30d`, `atm_iv_60d` and `atm_iv_90d`, `risk_reversal_25d`, `butterfly_25d`, and the expected move from IV and from the straddle | expiry |
| `volatility_index` | Cboe's published volatility index method on the listed strip, 30 days; no option model | none |
| `scenario_grid` | Each position's value at each point of a [scenario set](scenarios.md), on the fitted surface, sticky strike; at an expiration column, intrinsic | instrument, account |
| `positioning_exposure` | GEX, DEX, VEX and CHEX by series and expiry: version 1 long calls and short puts, version 2 every series short | expiry, greek, series |
| `positioning_levels` | The zero-gamma crossings, the call, put and total gamma strikes, gamma to liquidity and the 0DTE share | none |
| `max_pain` | Each expiration's strike at which the holders' payout is least, exact | expiry |
| `open_interest_change` | Each series' open interest less the trading date's before, exact | series |

**The models.** Each series is priced by the model its template version's
calculation package binds for its exercise style and its underlying's
asset class, never by a table of the engine's own:

| Model id | For |
|---|---|
| `american_binomial` | An American option on a share or a fund: a Cox-Ross-Rubinstein tree of the share less its escrowed discrete cash dividends, early exercise tested at each node, 200 steps by default (`steps`) |
| `black_scholes` | A European, cash-settled index option |
| `black_76` | An option on a future |
| `svi`, `ssvi` | The surface: raw SVI per expiration on out-of-the-money mids weighted by the inverse IV width, and the power-law SSVI across them, each held to Gatheral and Jacquier's butterfly and calendar conditions |

Implied volatility is a bracketed root between 0.01% and 500%. Greeks are
in their declared units: delta and gamma per 1, vega and vanna per vol
point, theta and charm per calendar day, rho per 1%. Time counts in
calendar minutes to the series' settlement over 525,600 a year: an AM
series settles at its session's open, a PM series at 16:00, in the time zone
of the trading-sessions calendar of the quote's venue, else the dataset's
calendar. A series with no zone at all is not evaluated, never settled at a
guessed hour.

**The risk-free rate.** The option definitions read two parameters, each
fixed by the definition's version and overridable by a later version:
`risk_free_rate=ust_cmt`, the US Treasury's constant-maturity par yield
curve, read through the deployment's source priority for rates at the
job's as-of; and `rate_interpolation=cubic_spline`, a natural cubic spline
through its par yields read at each expiry, flat beyond the ends, as Cboe's
volatility index method reads it. Put-call parity gives each expiry's
forward and borrow at that rate, never the rate itself. A curve the
deployment does not hold, or no par yields at the as-of, leaves every
option not evaluated, `PRICE_MISSING`, naming the curve. A deployment
running option measures therefore holds a [rates](rates.md) plugin
recording Treasury's par yield curve.

**Model figures.** Every option figure is answered `computed_as` a model's,
with its series' key (`Figure.series_key`) and its oldest input's source
time; `max_pain` and `open_interest_change` are exact. The models compute
in floating point inside the engine; the figures they answer are decimals
rounded to their definition's scale. Every model is proved against
QuantLib, which is a test oracle only and never part of the deployment's
image.

## The pricing role's seam

A deployment admin may route a model id to a plugin holding the
[`pricing` role](roles.md#pricing), deployment-wide, on the dashboard's
settings, **Model routing** (under **Plugins**): each model id on one line, its
implementation (`built-in`, or a launched `pricing` instance), since when
and by whom, and the measures the component serves beside them. **Change**
takes the model id, the implementation and why, and each change is its own
record. Through an agent,
[`dashboard__list_model_routing`](../api/core-tools.md#dashboard__list_model_routing)
reads the table and
[`dashboard__set_model_routing`](../api/core-tools.md#dashboard__set_model_routing)
sets it, with a note; the set can be prepared for a person to make.

**Routed only to a model it declares** (contract 27). A `pricing` plugin's
version declares the model ids and versions it answers, 1 to 32, in its
declaration (`PluginDeclaration.pricing_models`). Routing a model id to an
instance whose launched version does not list it is refused
`FAILED_PRECONDITION`, naming `implementation`. A version built before
contract 27 declares none, and routing to it is not checked.

When a job needs a routed model, the component sends that plugin alone a
**price batch**: one per model id, its units each an instrument under one
scenario carrying exactly the market objects its model declares (the price
and each conversion leg, or the outcome), with a deadline and a hash naming
the batch. The plugin answers the batch whole, a value per unit for every
unit, in the base currency the unit's inputs convert to, and reads nothing
else for the job. A batch answered twice is harmless.

**There is no silent fallback.** A plugin that has not answered by the
deadline, five seconds by default (the chart's `analytics.priceDeadlineMs`),
or that leaves a unit out, leaves every figure through it not evaluated,
`IMPLEMENTATION_UNAVAILABLE`, naming the instance: the built-in model's
figure is never put in its place. The answer's provenance names which
implementation answered each model. See
[Write a pricing plugin](../how-to/write-a-pricing-plugin.md).

## Provenance and the answer hash

Every answer carries its **provenance**: the book's watermark and the
lake's as-of it read at; each dataset read; each instrument, with its
record's version, its template and template version and its calculation
version; each model with the implementation that answered it; the measures
asked; each event group at the version read; from contract 28 each chain
read and the scenario set; the routing table's version;
the component's version; and the **answer hash**. From contract 27 it also
names the job's `business_date`; `input_prices`, each position's input
price (its instrument, price, dataset, row key, version and source time);
and `conversion_legs`, each leg from one cash instrument to another, its
rate, how it was derived (`direct`, `inverted` or `crossed`), the pivot of a
cross and its dataset. Each enters the hash.

The hash is `sha256:` and the SHA-256 of the job's inputs written out as
canonical JSON (RFC 8785): the component's version, the job, the watermark
and as-of, the routing version, the positions, the records, every price
and close read, the outcomes and the event groups, and what a routed plugin
answered. **Two answers with the same hash are the same answer**, digit for
digit. A reader may store the hash beside a figure it shows, and know later
whether a figure computed again is that one.

**Every figure is exact.** Values are decimals, never floats: a sum is taken
over unrounded terms and rounded once, half to even, to its definition's
scale. A weight or a probability is answered as its numerator and its
denominator, so a bound is decided by cross-multiplication, never by a
rounded division (`JobFigure.compare` does it). Each figure says how it was
computed, `computed_as`: every figure but the options models' is `exact`,
and theirs `COMPUTED_AS_MODEL`; a reader treats an unset value as exact,
and any other as a model's. Each figure names its scenario, `scenario_key`:
the base, the what-if, a historical day by its date, an outcome by its
member, or from contract 28 a scenario set's point
(`SCENARIO_KIND_SCENARIO_POINT`, with the saved set's row key, version and
the point's axis positions).

The SDK carries the computations the engine must equal exactly, hashes
included, in `meridian.analytics.reference`: slow on purpose, every value a
`Decimal` or a `Fraction`, over a reference case, a job and every input it
reads written out. A plugin's author can read a definition there, line by
line.

## Not evaluated, and why

A position or a measure the component cannot answer is listed under
`not_evaluated` with its reason, never answered as zero:

| Reason | When |
|---|---|
| `NOT_EVALUATED_REASON_PRICE_MISSING` | No price of the kind its model declares at the as-of |
| `NOT_EVALUATED_REASON_PRICE_STALE` | A price older than its bound for its source; no job sets a bound yet (see below) |
| `NOT_EVALUATED_REASON_CONVERSION_MISSING` | No chain of conversion legs to the account's base currency |
| `NOT_EVALUATED_REASON_NOT_ENTITLED` | A dataset the asking plugin is not entitled to, named in `detail` |
| `NOT_EVALUATED_REASON_LOCAL_RECORD` | A position under a local `LCL-` record, never priced |
| `NOT_EVALUATED_REASON_IMPLEMENTATION_UNAVAILABLE` | The routed `pricing` plugin did not answer in time, named in `detail` |
| `NOT_EVALUATED_REASON_SCHEME_NOT_HELD` | A breakdown by a scheme the deployment does not hold, named in `detail` |
| `NOT_EVALUATED_REASON_GROUP_NOT_EXHAUSTIVE` | An implied distribution over a group not stated exhaustive; the raw prices and their sum are still answered |
| `NOT_EVALUATED_REASON_HISTORY_INSUFFICIENT` | Too few closes for the definition's window |
| `NOT_EVALUATED_REASON_COST_MISSING` | Added in contract 27. A lot's cost the book does not record, which realized P&L needs |
| `NOT_EVALUATED_REASON_BELOW_INTRINSIC` | Added in contract 28. A quote below the option's intrinsic value, which no volatility prices |
| `NOT_EVALUATED_REASON_FIT_FAILED` | Added in contract 28. A surface slice that failed its fit or its no-arbitrage checks, naming the expiry |

From contract 28 a series not evaluated names its key (`NotEvaluated.series_key`).
A series no model binding covers is `IMPLEMENTATION_UNAVAILABLE`.

## Current limits

- **No staleness bound.** The component sets no maximum age per source, so
  the latest price valid at the as-of is used however old it is, and
  `PRICE_STALE` does not arise from a job. The check at use, against the
  dataset's threshold in session, is not built yet (see
  [Data age and liveness](data-age-and-liveness.md#not-built-yet)).
- **The historical window's days** are the business dates the lake's
  closes carry, not a settlement calendar's days.
- **Interval VWAP and a fixing** are not measured by `execution_cost`
  version 1.
- **Exact figures, but the options models'.** The `cash`, `quoted_price`
  and `binary_event` models are arithmetic. The options models compute in
  floating point inside the engine and say so on each figure.
- **The scenario grid** holds the surface sticky to strike; sticky
  moneyness is a later definition version.
- **Answers are not kept.** They are held in memory and lost when the
  component restarts; the job is run again.

## Where you see it

Core draws no page of figures: a plugin that runs jobs shows them on its
own pages. On the dashboard's settings, **Model routing** (under
**Plugins**) and **FX pivot currencies** (under **Deployment**) are the
component's places. What a job and its answer carry, field by field, is in
[the analytics component's data dictionary](../boundaries/analytics.md).

## Related

- [Contract 26's operations](../api/typed-operations.md#contract-v26s-operations):
  [`run_job`](../api/typed-operations.md#run_job) and the other reads, and
  the pricing seam's two.
- [Write a pricing plugin](../how-to/write-a-pricing-plugin.md), from
  `plugin new --role pricing`.
- [Event groups](event-groups.md): what the event measures read.
- [The lake](the-lake.md): the prices, closes and outcomes a job reads.
- [One ID per instrument](one-id.md): templates, and why a local record is
  never priced.
- [Licences and entitlements](licences-and-entitlements.md): which
  datasets a plugin's job may read.
