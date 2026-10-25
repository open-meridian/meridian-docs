# Scenarios

Added in contract 28. A **scenario** says how the market moves: spot up 5%,
volatility down 2 points, a week forward. Open Meridian writes every
scenario in one **common format**, so a grid a person saves on one plugin's
page, a stress a risk plugin runs and the analytics component's
`scenario_grid` all read the same shocks the same way.

## A shock

A scenario is a name and its **shocks**, applied together; a scenario with
none is the base, nothing moved. Each shock states four things, and none is
inferred:

| Part | What |
|---|---|
| **Object** | What moves: `SHOCK_OBJECT_SPOT` (an instrument's price, or an FX rate as its currency's cash instrument's price), `SHOCK_OBJECT_VOL_SURFACE` (an underlying's fitted surface), `SHOCK_OBJECT_RATE` (a referential rate or curve) or `SHOCK_OBJECT_TIME` (the valuation time) |
| **Target** | One object by its `INS-` ID (`subject_id`), or `every` object of its kind the job reads: every spot, every surface, every rate. Not set on a time shock |
| **Form** | How it moves, one of the forms its object takes |
| **Unit and value** | The unit its value is in, and the value, signed |

| Object | Forms | Units |
|---|---|---|
| Spot | `RELATIVE` (the default form), or `ABSOLUTE` | `PERCENT` (10 is +10%), or `PRICE` in the price's currency |
| Volatility surface | `PARALLEL`, or `BUCKETED` by expiry | `VOL_POINTS` (2 is +2 vol points), absolute |
| Rate | `PARALLEL`, or `BUCKETED` by key tenor, linear between key tenors | `BASIS_POINTS` (25 is +25 bp) |
| Time | `ABSOLUTE`, a shift by its unit, or `TO_SETTLEMENT`, each option moved to its own settlement time | `DAYS`, or `MINUTES` counted over 525,600 a year; none to settlement |

A bucketed shock carries its **buckets**, each a tenor (`1M`, `3M`, `10Y`)
and its value, in place of one value. A shock whose form does not fit its
object, with no unit, or naming both a subject and `every`, is refused,
naming the field.

## A scenario set

A **scenario set** is named **axes**, each axis an ordered list of steps,
each step a scenario. The set's points are the product of its axes: a spot
axis of nine steps by a date axis of six is 54 points. Only the axes are
saved, never the points; each point is keyed by its position on each axis
(`axis_positions`), so the same set always gives the same keys.

The lake keeps 1 to 4 axes of 1 to 32 steps each.

## Saved, and named by a job

A `signal` plugin saves a scenario, or a scenario set, as a row of its own
dataset under its row key
([`record_scenarios`](../api/typed-operations.md#record_scenarios)): a
person's grid saved on its page, say. Saving the same row key again is its
next version; every version stays readable
([`list_scenarios`](../api/typed-operations.md#list_scenarios), by row
key, the latest or the version asked). A signal plugin's catalogue declares
that dataset, as it declares its derived series (see
[The lake](the-lake.md#derived-series)).

A job names a scenario set inline (`Job.scenario_set`), or a saved one by
its row key and version (`Job.scenario_ref`), never both. The analytics
component's `scenario_grid` answers each position's value at each point,
each figure under `SCENARIO_KIND_SCENARIO_POINT` with the saved set's row
key, its version and the point's axis positions (see
[Options measures](the-analytics-component.md#options-measures)).

In the Python SDK, `meridian.roles.signal` builds the usual axes and saves
the set:

```python
import meridian
from meridian.roles import signal

grid = meridian.ScenarioSet(name="AAPL grid", axes=[
    signal.spot_steps([-10, -5, -2, 0, 2, 5, 10]),     # every spot, relative, in percent
    signal.date_steps([1, 7, 30]),                     # today, forward by days, and to settlement
])
row = signal.saved("aapl-grid", dataset=wants.dataset("scenarios"), scenario_set=grid)
await plugin.record_scenarios(scenarios=[row])
again = await signal.read_scenarios(plugin, ["aapl-grid"])
```

## What waits

A shock's target is one object or `every` object of its kind. Selections
of objects (every option on one underlying, every holding in a sector) and
historical replays come later, as additions to the same format.

## Related

- [The analytics component](the-analytics-component.md#options-measures): the scenario grid.
- [Listed options and futures](listed-options-and-futures.md).
- [The lake](the-lake.md): a signal plugin's own datasets.
- [Typed operations: `record_scenarios`](../api/typed-operations.md#record_scenarios).
