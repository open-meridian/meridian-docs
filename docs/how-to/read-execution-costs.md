# Run a TCA job and read its costs

This page measures an account's fills against the standard benchmarks, and
reads the costs back: from a plugin with the Python SDK, and through an
agent. What the numbers mean is in
[Execution costs](../concepts/execution-costs.md).

You need SDK 0.32.0 or later, a deployment on contract 27 (chart 0.1.309 or
later), and a plugin holding a role that runs jobs (`reporting`,
`portfolio`, `compliance` or `signal`) with the account in its read scope.
The costs are measured against the mid of a dataset of quotes the plugin is
entitled to.

## Run the job

A job asking `execution_cost` measures each execution of its accounts on
its business date, or today's without one, and records one row per
execution per benchmark in the lake as it answers:

```python
from meridian import analytics

job = analytics.job(
    analytics.measure("execution_cost"),
    accounts=["ACC-12"],
    business_date="2026-10-22",
    reporting_currency="INS-...",         # the aggregates' currency; else each account's base
)
answer = await analytics.Jobs().run(plugin, job)
for figure in answer.figures("execution_cost"):
    print(figure.breakdown, figure.value)  # the notional-weighted mean, per benchmark
```

**Choose the benchmark's source.** The mids come from the job's sources,
`analytics.job(..., sources=...)`, a
[`SourceChoice`](../api/typed-operations.md#sourcechoice): a named dataset,
such as one broker's quotes or an independent feed. Without one, the
deployment's source priority for quotes decides. Every row names the
dataset it used.

## Read the rows

```python
page = await plugin.list_execution_costs(
    account_id="ACC-12",
    trade_date="2026-10-22",
    benchmarks=["arrival", "placement_arrival"],
)
for cost in page.costs:
    if cost.unanswered:
        print(cost.execution_id, cost.benchmark, "not measured:", cost.unanswered)
    else:
        print(cost.execution_id, cost.benchmark, cost.cost_bps.value, "bps")
```

Read by `execution_ids` or `order_id` instead of `trade_date`, and follow
`next_cursor` for the next page. A plugin holding `oms`, `ems` or
`operations` reads them too, without running a job. An account outside the
plugin's read scope is refused `PERMISSION_DENIED`, naming `account_id`.

A row with `TCA_UNANSWERED_NO_QUOTE` found no mid within its staleness
bound, 5 seconds by default; one with `TCA_UNANSWERED_NOT_MEASURED` had no
moment to measure from, as a venue-originated fill accepted to a new order
has no decision or arrival. Neither carries a cost.

## Through an agent

[`dashboard__list_execution_costs`](../api/core-tools.md#dashboard__list_execution_costs)
reads the same rows, for an account the person holds read on: by
execution, order, trade date or benchmark, paged.

## In a plugin's suite

The reading roles' suites, and the `ems`'s, `oms`'s and `operations`',
hold `reads-an-accounts-execution-costs`. It carries no `about`, so map it
to the plugin's own read with `list_execution_costs`.

## Related

- [Execution costs](../concepts/execution-costs.md).
- [The analytics component](../concepts/the-analytics-component.md).
- [`list_execution_costs`](../api/typed-operations.md#list_execution_costs).
