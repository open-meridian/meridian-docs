# Record and read an option chain

Record an underlying's listed option chain from a data plugin, read it and
its open interest from a reading plugin, ask for a series' record before an
order names it, and run the options measures over it. What each part means
is in [Listed options and futures](../concepts/listed-options-and-futures.md).

You need SDK 0.33.0 or later, CLI 0.1.53, and a deployment on contract 28
(chart 0.1.313 or later) whose platform publishes the `TPL-listed-option`
template. `meridian plugin new` on CLI 0.1.53 writes a plugin on 0.33.0.

## In a data plugin: record the chain

Declare a dataset serving the chain's kinds in the plugin's catalogue, one
dataset per timeliness: `meridian.v1.ListedSeries` for the series,
`meridian.v1.Statistic` for open interest and volume, and
`meridian.v1.Quote` for the chain's quotes.

For each underlying it lists, record each series as the `listed_option`
template's fields, keyed by its OSI symbol. The underlying is the
deployment's `INS-` record, resolved as any subject is; the series itself
is never resolved, and recording it mints nothing.

```python
import meridian
from decimal import Decimal
from meridian.roles import chains

symbol = chains.osi_symbol("AAPL", "2026-11-20", "put", "230")   # "AAPL  261120P00230000"
row = chains.option_series(
    aapl, symbol,
    template_id="TPL-listed-option", template_version="1",
    dataset=wants.dataset("options"), currency="USD",
    exercise_style="EXERCISE_STYLE_AMERICAN",
    settlement_method="SETTLEMENT_METHOD_PHYSICAL",
    deliverable=[(aapl, 100)],                     # 100 shares of the underlying
)
await wants.record("series", [row], "options")
```

Read the template's current version from the template catalogue
(`meridian.TemplateCatalogue`, or
[`read_template`](../api/typed-operations.md#read_template)) rather than
writing it in. An adjustment the source states, a new deliverable, strike or
multiplier, is recorded as the next version of the same row: the series
keeps its key.

Record each series' open interest for the trading date it is for, and its
quotes under the underlying with the series' key on the envelope:

```python
oi = chains.statistic(aapl, chains.osi_key(symbol), "open_interest", 12834, "2026-10-23",
                      dataset=wants.dataset("options"))
await wants.record("statistics", [oi], "options")

quote = meridian.Quote(
    meta=chains.series_meta(aapl, chains.osi_key(symbol), row_key=f"{symbol}:q:{at_ns}",
                            dataset=wants.dataset("options"), valid_from_ns=at_ns),
    bid=meridian.Money(Decimal("4.10"), "USD"), ask=meridian.Money(Decimal("4.25"), "USD"),
)
await wants.record("quotes", [quote], "options")
```

A future, or an option on one, is keyed by one `ticker` identifier, the
exchange's symbol with its month code, its venue's MIC in `source`:
`meridian.Identifier(scheme="ticker", value="ESZ6", source="XCME")`.

**The data suite.** `records-a-chains-series`, `records-open-interest` and
`a-chain-row-is-never-resolved` are `about: option chains`. A plugin
recording a chain maps them to its own producers; one whose source lists
no options names them not presented, with why.

## In a reading plugin: read the chain

A `portfolio`, `signal`, `oms` or `ems` plugin reads an underlying's series
expiring in a window, every page read, each with the deployment's record
where one is held:

```python
series = await chains.read_chain(plugin, aapl, "2026-11-01", "2026-12-31")
for s in series:
    print(s.meta.series_key[0].value, s.instrument_id or "(no record yet)")
```

`portfolio`, `reporting` and `signal` read the chain's open interest for a
trading date, the latest where none is named:

```python
open_interest = await chains.read_open_interest(plugin, aapl, "2026-10-23")
```

The chain's quotes are read with
[`list_quotes`](../api/typed-operations.md#list_quotes), naming
`series_keys` or `all_series=True`; a read naming neither never answers a
chain's rows.

## Ask for a series before an order names it

An order, a package's leg or a proposal names a series by its `INS-` ID.
Ask for the record first, with why:

```python
answer = await chains.want_series(plugin, aapl, chains.osi_key(symbol),
                                  note="Proposing a protective put", acting_for=caller)
```

Each series answers with its `INS-` record, `pending_review` while the
platform's staff review it, or `refused_by_rule` where the deployment's
**Series request rule** does not allow its cause, or the day's limit is
reached. A deployment admin sets the rule on the dashboard's settings home
page, **Series request rule** (`/admin#series-rule`), and may ask for
series by hand there with **Request series**.

## Run the options measures

A `signal`, `portfolio`, `reporting` or `compliance` plugin asks the
analytics component for the chain's measures with
[`run_job`](../api/typed-operations.md#run_job), naming the chain; a job of
chain measures alone names no account:

```python
import meridian
from meridian import analytics
from meridian.plugin.v1 import operations_pb2 as ops

job = meridian.Job(
    measures=[analytics.measure("implied_volatility", by=["series", "quote_side"]),
              analytics.measure("surface_fit", by=["expiry", "parameter"])],
    chains=[ops.ChainRef(underlying_instrument_id=aapl,
                         expiration_from="2026-11-01", expiration_to="2026-12-31")],
)
answer = await analytics.Jobs().run(plugin, job)        # inline, or waited for
```

The component prices at the US Treasury's par yield curve through the
deployment's source priority for rates, so the deployment needs a rates
plugin recording it (see [Rates](../concepts/rates.md)); without it every
option is not evaluated, naming the curve. Each measure, its parameters and
its breakdowns are in
[Options measures](../concepts/the-analytics-component.md#options-measures).

## Related

- [Listed options and futures](../concepts/listed-options-and-futures.md).
- [The analytics component](../concepts/the-analytics-component.md#options-measures).
- [Scenarios](../concepts/scenarios.md): a grid's shocks.
- [Write a data plugin against its suite](write-a-data-plugin.md).
- [Typed operations: contract 28's](../api/typed-operations.md#contract-v28s-operations).
