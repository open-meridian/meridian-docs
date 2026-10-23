# Execution costs

**Execution costs** measure each fill against standard benchmarks: what a
trade cost, in basis points, against the market's mid at the moments that
matter. Open Meridian standardises the definitions and the record, not a
cost model. The [analytics component](the-analytics-component.md) computes
them as a measure, `execution_cost`, and records each result in the lake as
an `ExecutionCost` row, so every plugin that reads them reads the same
numbers.

## The four moments

Version 1 of `execution_cost` measures each execution against the mid in
force at four moments:

| Benchmark | The mid at | Who it evaluates |
|---|---|---|
| `TCA_BENCHMARK_DECISION` | the order's proposal | the decision: implementation shortfall |
| `TCA_BENCHMARK_ARRIVAL` | the order's release to the desk | the desk |
| `TCA_BENCHMARK_PLACEMENT_ARRIVAL` | the placement's routing time, `routed_at_ns`: the broker's arrival | the broker |
| `TCA_BENCHMARK_MID_AT_FILL` | the execution | the fill itself |

Three arrival times, because the desk, the broker and the decision are each
evaluated from their own moment, as equity TCA conventionally separates
them. The contract also names `TCA_BENCHMARK_INTERVAL_VWAP`, which needs
trades, and `TCA_BENCHMARK_FIX`, a named fixing the deployment licenses;
version 1 measures neither.

**What is not measured.** A venue-originated fill accepted to a new order
has no decision or arrival time, so it is measured at fill only, and its
other benchmarks say `TCA_UNANSWERED_NOT_MEASURED`. A manual fill is
measured at its stated time, and its row says how precisely that time is
known (`time_precision`).

## The sign and the units

A cost is in basis points, side-adjusted, **positive a cost**:

```
cost_bps = s × (execution price − benchmark) ÷ benchmark × 10⁴
```

where `s` is 1 for a buy and −1 for a sell, rounded half to even to four
places. Fees and financing are reported apart, each in basis points of the
execution's notional (`fees_bps`, `financing_bps`), never folded into the
cost. The figures a job answers are each account's notional-weighted mean
per benchmark, in the account's base currency or the job's reporting
currency; the rows are the detail.

## Which quote

The benchmark is the **mid in force** at the moment, from a dataset the row
names (`benchmark_dataset`, `benchmark_row_key`), never mixed silently from
several. It must be no older than the row's **staleness bound**, 5 seconds
by default, or the dataset's own stale ceiling where that is tighter (see
[Data age and liveness](data-age-and-liveness.md)). Past the bound, or with
no mid at all, the row says `TCA_UNANSWERED_NO_QUOTE`, with no price and
no cost: never an imputed value.

**Benchmarks chosen per job.** Which datasets the mids come from is the
job's own choice of sources (`InputRefs.sources`): a broker's, a venue's or
an independent feed for a liquid market, or a mastered dataset for an OTC
product. With none chosen, the deployment's source priority decides. Every
row records the dataset it used, so two jobs over different sources are
told apart.

**Quote retention.** A cost can only be measured while the lake still holds
the quotes for its moments. How long a dataset's rows are kept is its
licence's retention, the deployment's choice within its vendor's terms (see
[Licences and entitlements](licences-and-entitlements.md)).

## A row { #a-row }

One `ExecutionCost` row per execution per benchmark, its subject the
execution's instrument, its source the analytics component, its dataset
`analytics:execution_cost`:

| Field | What |
|---|---|
| `execution_id`, `order_id`, `placement_id`, `account_id` | The execution measured, its order, its placement and its account |
| `benchmark` | The benchmark |
| `benchmark_price`, `benchmark_at_ns` | The mid used, and the moment it was taken at |
| `benchmark_dataset`, `benchmark_row_key` | The quote's dataset and row |
| `fixing_id` | A fixing's ID, for `TCA_BENCHMARK_FIX` |
| `execution_price`, `side`, `notional` | The execution's price, side and notional, in its asset |
| `cost_bps`, `fees_bps`, `financing_bps` | The cost, and fees and financing apart |
| `liquidity_indicator`, `venue_id` | Whether the fill added or removed liquidity, and where, as the connectivity plugin reported them |
| `reject_count`, `time_to_fill_ns` | The placement's last-look rejections and its time to fill: an FX desk's measures, never a cost in bps |
| `unanswered` | `TCA_UNANSWERED_NO_QUOTE` or `TCA_UNANSWERED_NOT_MEASURED`, with no cost |
| `staleness_bound_ns` | The bound the quote was held to |
| `time_precision` | How precisely the moment is known |

A job run again with the same inputs records the same rows again, a
repeat; a different value is the row's next version. The book stores
nothing derived from them.

## Who reads them

The rows are the lake's **first account-scoped** rows: each names its
execution's account, and a read names one account, which the sidecar
checks against the reader's read scope, as the book's reads are. An account
outside it is refused `PERMISSION_DENIED`, naming `account_id`.

- **A plugin** holding `reporting`, `portfolio`, `compliance`, `signal`,
  `oms`, `ems` or `operations` reads them with
  [`list_execution_costs`](../api/typed-operations.md#list_execution_costs),
  by execution, by order or by trade date, narrowed to some benchmarks. A
  reporting plugin reads the stored rows, slow and conflated by nature, and
  never ticks.
- **A person's agent** reads them with
  [`dashboard__list_execution_costs`](../api/core-tools.md#dashboard__list_execution_costs),
  at the read level on that account.
- **Recording** is the analytics component's alone: a job asking
  `execution_cost` reads each execution of its accounts, on its business
  date or today, with the order's and the placement's moments from the
  book, and records the rows as it answers.

**Live, at the desk.** An `ems` computes its own live "vs arrival" from
the quotes and trades it reads, by the same definitions. Nothing records
that: the stored row is post-trade only.

## Not built yet

- **Interval VWAP and a fixing** as benchmarks, which a version-1 job does
  not read.
- **A default source per benchmark**: a job names its sources, or the
  source priority decides.
- **Pre-trade expected costs**, which are a plugin's or later work, and
  peers: a deployment measures only its own flow.

## Related

- [Run a TCA job and read its costs](../how-to/read-execution-costs.md).
- [The analytics component](the-analytics-component.md): jobs, measures and
  provenance.
- [Placement types and RFQ quotes](placement-types-and-rfq-quotes.md): what a
  placement records, the quotes received among it.
- [The analytics component's data dictionary](../boundaries/analytics.md)
  and [the lake's](../boundaries/lake.md).
