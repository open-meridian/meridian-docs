# Read trades and quotes in a `signal` or `ems` plugin

From contract v19 the [lake](../concepts/the-lake.md) holds every trade and
the best bid and offer that its data plugins record. Only two roles read
them: `signal`, which triggers orders on live data, and `ems`, which sends
orders in real time. This page writes a plugin holding one of them that
reads a day's trades, hears each new one, catches up what it missed, and
reads the latest quotes, then holds it to its role's suite.

!!! note "Contract v19"
    This page describes open-meridian 0.23.0 (contract v19) and CLI 0.1.38,
    for a runtime serving contract v19, chart 0.1.294 or later, all
    released 2026-10-10. The lake's 1b operations are `preview` in v19.

## Which role

| Your plugin | Holds |
|---|---|
| Computes signals from live trades and quotes, and will trigger orders | `signal` |
| Works orders across venues in real time | `ems` |
| A reporting page, a valuation, a dashboard | `reporting`: prices and bars only, never trades or quotes |
| Shapes orders (`portfolio`) or aggregates them (`oms`) and needs the tape | `portfolio` or `oms`, and also `signal` or `ems` |

`reporting` is for slower consumers: it reads conflated prices and bars. A
`portfolio` or `oms` plugin reads prices and bars too, and takes `signal`
(live order triggering) or `ems` (real-time order sending) where it needs
high-resolution data. Each role is approved when the plugin is launched.
See [Who reads what](../concepts/the-lake.md#who-reads-what).

## Make the plugin

There is no `signal` or `ems` template. Start from the reference plugin and
give it the role:

```sh
meridian plugin new my-desk
cd my-desk
```

CLI 0.1.38 writes the plugin on open-meridian 0.23.0. A plugin CLI 0.1.37
wrote is on 0.22.0: commit it, and `meridian plugin migrate --to 0.23.0`,
which works only on what git holds, moves its pins and changes no code.
Then, in `pyproject.toml`:

```toml
[tool.meridian]
roles = ["ems"]        # or ["signal"]
```

## Read a day's trades

Read the trades of up to 500 instruments over a range of valid time that
lies within one day of each dataset, as the dataset declares its day:

```python
from meridian.plugin.v1 import operations_pb2 as ops

held = [ops.SubjectRef(entity_id=btc), ops.SubjectRef(entity_id=spy)]
day = await plugin.list_trades(subjects=held, valid_from_ns=open_ns, valid_until_ns=now_ns)
for trade in day.trades:
    price = meridian.as_money(trade.price)          # names its cash instrument
    counts_for_close = trade.attributes.consolidated.close == ops.ELIGIBLE_ELIGIBLE
```

Each trade carries its [attributes](../concepts/the-lake.md#trades-and-their-attributes):
what it may set of a bar, in the consolidated view and its venue's, so a
plugin building its own bars needs no vendor's condition table; and the
aggressor, where the source said which side took liquidity. A withdrawn
trade comes as its next version, `cancelled` set. Page with `cursor`; keep
`day.watermark`.

A range wider than a day is refused, naming it. Choose the datasets with
`sources=`: the deployment's default (the source priority for trades), named
datasets, or every entitled dataset side by side.

## Hear each new trade, and catch up

```python
async def on_trade(heard: meridian.Heard) -> None:
    trade = heard.message.trade        # every trade, once, in its dataset's order
    if heard.caught_up:
        ...                            # read back after a loss: a late print among them
    vendor = heard.dataset.vendor if heard.dataset else ""

async def on_quote(heard: meridian.Heard) -> None:
    quote = heard.message.quote        # the latest per subject, dataset, venue and asset

await plugin.receive(
    trades_recorded=on_trade,
    quotes_recorded=on_quote,
    subjects=[btc, spy],               # by instrument ID; none named, none heard
)
```

**Trades are never conflated.** Every trade recorded is handed on. When the
sidecar drops some because the plugin was too slow, or the stream breaks,
the SDK reads the trades recorded **after the watermark it last saw**, per
dataset, and hands them on marked `caught_up` before anything heard after.
That read answers by when a trade was recorded, not when it was valid, so
a late or out-of-sequence print recorded after your range had passed is
caught too. On start it reads none: read the day by range first, as above.

To catch up yourself, for example after your own restart with a watermark
you kept:

```python
late = await plugin.list_trades(subjects=held, after_watermark=day.watermark)
```

Older than the lake keeps is answered `beyond_history`. A dataset licensed
as served, not kept, keeps nothing to catch up from.

**Quotes are conflated**, as prices are: under load the sidecar keeps the
latest per subject, dataset, venue and asset, and after a loss the SDK reads
the latest again.

## Read the latest quotes

```python
latest = await plugin.list_quotes(subjects=held)
for quote in latest.quotes:
    bid = meridian.as_money(quote.bid) if quote.HasField("bid") else None   # an empty side is unset
```

The latest is chosen per asset: bitcoin quoted in USD and in USDC on one
venue answers both. A quote nothing has recorded is wanted of the data
plugin serving it, answered `asked_source`, and heard when it is recorded;
asked again on a timetable, it becomes a standing want that the data plugin
keeps current from its stream.

## Hold it to its suite

`signal` and `ems` each have a suite in the SDK. Map each case to your
plugin's own read or handler, run against the recorder:

```python
from meridian.suites import run, suite

async def reads_trades(recorder):
    await recorder.list_trades(subjects=[ops.SubjectRef(entity_id="LCL-BTC")],
                               valid_from_ns=open_ns, valid_until_ns=open_ns + 60 * 10**9)

async def catches_up(recorder):
    await recorder.list_trades(subjects=[ops.SubjectRef(entity_id="LCL-BTC")],
                               after_watermark=ops.Watermark(partitions=[
                                   ops.PartitionSequence(partition="coinbase-1:trades", sequence=2)]))

def hearing(row, message, arm):
    async def produce(recorder):
        async def heard(_):
            return None
        recorder.answer(row, lambda _: message)
        await recorder.receive(**{arm: heard}, subjects=["LCL-BTC"])
    return produce

async def datasets(recorder):
    await recorder.list_datasets()

async def quotes(recorder):
    await recorder.list_quotes(subjects=[ops.SubjectRef(entity_id="LCL-BTC")])

PRODUCERS = {
    "reads-the-datasets-it-may-read": datasets,
    "reads-trades-over-a-range": reads_trades,
    "hears-a-trade-recorded": hearing("TradesRecorded", ops.TradesRecordedEvent(trade=ops.Trade()), "trades_recorded"),
    "catches-up-trades-after-a-watermark": catches_up,
    "reads-the-latest-quotes": quotes,
    "hears-a-quote-recorded": hearing("QuotesRecorded", ops.QuotesRecordedEvent(quote=ops.Quote()), "quotes_recorded"),
}

def test_the_ems_suite_passes() -> None:
    report = run("ems", PRODUCERS)
    assert report.passed, report.failures
```

| Case | `ems` | `signal` | The plugin |
|---|---|---|---|
| `reads-the-datasets-it-may-read` | yes | yes | reads the datasets it may read |
| `reads-a-business-dates-closes`, `reads-daily-bars-over-a-range`, `hears-a-price-recorded`, `hears-a-bar-recorded` | | yes | reads and hears prices and bars, as since v18 |
| `reads-trades-over-a-range` | yes | yes | reads trades over a range within a day |
| `hears-a-trade-recorded` | yes | yes | hears a trade for a subject it named |
| `catches-up-trades-after-a-watermark` | yes | yes | reads the trades after the watermark it last saw |
| `reads-the-latest-quotes` | yes | yes | reads the latest quotes |
| `hears-a-quote-recorded` | yes | yes | hears a quote for a subject it named |

A plugin catching up by range alone fails
`catches-up-trades-after-a-watermark`. Neither role records anything in the
lake.

`meridian plugin check --verified` does not hold the `signal` or `ems`
suite: in v19 it checks the `custody` and `dgm` suites only. Run your role's
suite in your own tests, as above, and in your CI.

**Gaps upstream.** Within a running data plugin, a dropped connection is
refilled from the venue's history by Alpaca, Coinbase and Kraken; Tradier
cannot refill it. A trade printed while a data plugin restarts is recorded
by none of them today: each resumes streaming within about a minute, and
the gap stays. Catching up by watermark gives you
every trade the lake has, and none it never had: see
[the lake](../concepts/the-lake.md#wants-a-read-the-lake-cannot-answer-yet).

## Put it in a deployment

```sh
meridian plugin upload
meridian plugin launch my-desk 0.1.0 --instance my-desk-1
```

The launch shows the role for a deployment admin to approve. Then, on the
**Data sources** page, the admin entitles `my-desk-1` to the datasets
serving trades and quotes, such as a crypto exchange's `trades` and `live`,
and sets the priority for trades and quotes where two sources serve the
same instruments: see [License and entitle a dataset](license-and-entitle-a-dataset.md).
A plugin reads nothing it is not entitled to, whatever its role.

## Related

- [The lake](../concepts/the-lake.md): trades, quotes and who reads them.
- [`list_trades`](../api/typed-operations.md#list_trades),
  [`list_quotes`](../api/typed-operations.md#list_quotes) and
  [Receive](../api/python-sdk.md#receive).
- [Write a `dgm` against its suite](write-a-dgm.md): recording them.
- [Add a public data plugin](add-a-public-data-plugin.md) and
  [Add a data plugin's key](add-a-data-plugins-key.md): the sources that
  stream them.
