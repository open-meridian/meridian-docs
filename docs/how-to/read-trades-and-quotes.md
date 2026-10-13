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

CLI 0.1.38 writes the plugin on open-meridian 0.23.0, CLI 0.1.39 on
0.24.0 (contract v20), whose move from 0.23.0 rewrites only the renamed
roles, neither `signal` nor `ems` among them, CLI 0.1.41 on 0.25.0
(contract v21), whose move from 0.24.0 changes only the pins, and CLI
0.1.42 on 0.26.0 (contract v22), whose move from 0.25.0 changes only the
pins and whose suites hold the cases below. A plugin CLI 0.1.37
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
plugin's own read or handler, run against the recorder. On open-meridian
0.26.0 (contract v22) the `ems` suite holds twenty cases, fourteen of
them new, and this test passes it, naming one case not presented:

```python
from datetime import date
from decimal import Decimal

import meridian
from meridian.plugin.v1 import operations_pb2 as ops
from meridian.suites import run
from meridian.testing import caller_header

BTC = ops.SubjectRef(entity_id="LCL-BTC")
open_ns = 1_760_000_000 * 10**9
ACCOUNT, ORDER, PLACEMENT = "ACC-1", "ORD-1", "PLC-1"
BROKER, CODE = "my-broker-1", "BRK-ACCT-7"   # a linked connectivity plugin, and a code mapped on it

async def reads_trades(recorder):
    await recorder.list_trades(subjects=[BTC], valid_from_ns=open_ns, valid_until_ns=open_ns + 60 * 10**9)

async def catches_up(recorder):
    await recorder.list_trades(subjects=[BTC],
                               after_watermark=ops.Watermark(partitions=[
                                   ops.PartitionSequence(partition="coinbase-1:trades", sequence=2)]))

def hearing(*heard_rows):
    async def produce(recorder):
        async def heard(_):
            return None
        for row, message, _ in heard_rows:
            recorder.answer(row, lambda _, message=message: message)
        await recorder.receive(**{arm: heard for _, _, arm in heard_rows}, subjects=["LCL-BTC"])
    return produce

def then(*steps):
    async def produce(recorder):
        for step in steps:
            await step(recorder)
    return produce

async def datasets(recorder):
    await recorder.list_datasets()

async def quotes(recorder):
    await recorder.list_quotes(subjects=[BTC])

# The order path (contract v22): what the desk does with each order it works.
async def maps_an_account(recorder):       # from the ems's own page, at admin
    await recorder.map_venue_account(connectivity_instance_id=BROKER, venue_account_code=CODE,
                                     account_id=ACCOUNT, acting_for=caller_header("admin"))

async def reads_the_catalogue(recorder):
    await recorder.read_venue_catalogue(connectivity_instance_id=BROKER, venue_account_code=CODE)

async def claims(recorder):
    await recorder.set_working_condition(order_id=ORDER, condition="claimed", set=True)

async def places(recorder):
    await recorder.resolve_instrument(instrument_id="LCL-AAPL")
    await recorder.resolve_venue(identifiers=[meridian.Identifier(scheme="mic", value="XNAS")], as_of_ns=open_ns)
    await recorder.create_placement(order_id=ORDER, connectivity_instance_id=BROKER, venue_account_code=CODE,
                                    quantity=Decimal("10"), destination="XNAS", idempotency_key="place:ORD-1:1")

async def proposes_a_child(recorder):
    await recorder.propose_order(account_id=ACCOUNT, instrument_id="LCL-AAPL", side="buy", quantity=Decimal("2"),
                                 link=meridian.OrderLink(kind="split", parent_order_id=ORDER),
                                 idempotency_key="slice:ORD-1:3")

async def cancels_a_placement(recorder):
    await recorder.request_placement_change(placement_id=PLACEMENT, change=meridian.PlacementChange(kind="cancel"))

async def cancels_the_order(recorder):
    await recorder.request_order_change(order_id=ORDER, change=meridian.OrderChange(kind="cancel"))

async def settlement_date(recorder):
    return await recorder.compute_date(
        settlement=meridian.SettlementDateInputs(instrument_id="LCL-AAPL", trade_date="2026-10-09"))

async def enters_a_manual_fill(recorder):   # for a person, at the desk's page
    await recorder.report_execution(placement_id=PLACEMENT, kind="manual", quantity=Decimal("5"),
                                    price=meridian.Money(Decimal("227.41"), "USD"),
                                    settlement_date=date(2026, 10, 13))

async def reads_orders(recorder):
    first = await recorder.list_orders(account_id=ACCOUNT)
    await recorder.list_orders(account_id=ACCOUNT, since=first.as_of)

async def reads_instructions(recorder):
    await recorder.list_trading_instructions()

async def reads_attributes(recorder):
    await recorder.list_account_attributes(account_id=ACCOUNT)

PRODUCERS = {
    "reads-the-datasets-it-may-read": datasets,
    "reads-trades-over-a-range": reads_trades,
    "hears-a-trade-recorded": hearing(("TradesRecorded", ops.TradesRecordedEvent(trade=ops.Trade()), "trades_recorded")),
    "catches-up-trades-after-a-watermark": catches_up,
    "reads-the-latest-quotes": quotes,
    "hears-a-quote-recorded": hearing(("QuotesRecorded", ops.QuotesRecordedEvent(quote=ops.Quote()), "quotes_recorded")),
    # contract v22
    "maps-an-account-to-a-venue-account-code": maps_an_account,
    "hears-and-reads-a-venues-catalogue": then(
        hearing(("ReportVenueCatalogue", ops.VenueCatalogueEvent(), "report_venue_catalogue")), reads_the_catalogue),
    "claims-a-released-order": then(hearing(("OrderUpdated", ops.OrderUpdatedEvent(), "order_updated")), claims),
    "places-at-a-linked-connectivity-plugin": places,
    "proposes-a-child-order": proposes_a_child,
    "hears-a-placement-and-an-execution": hearing(
        ("PlacementUpdated", ops.PlacementUpdatedEvent(), "placement_updated"),
        ("ExecutionRecorded", ops.ExecutionRecordedEvent(), "execution_recorded")),
    "cancels-a-placement": cancels_a_placement,
    "asks-to-cancel-an-order": cancels_the_order,
    "enters-a-manual-execution-for-a-person": enters_a_manual_fill,
    "reads-its-orders-and-catches-up": reads_orders,
    "reads-and-hears-the-trading-instructions": then(reads_instructions, hearing(
        ("TradingInstructionChanged", ops.TradingInstructionChangedEvent(), "trading_instruction_changed"))),
    "reads-and-hears-whether-releases-wait-for-compliance": then(reads_attributes, hearing(
        ("AccountAttributeChanged", ops.AccountAttributeChangedEvent(), "account_attribute_changed"))),
    "asks-for-a-settlement-date": settlement_date,
}

def test_the_ems_suite_passes() -> None:
    report = run("ems", PRODUCERS, not_presented={
        "reads-a-calendar": "the desk asks core for settlement dates and reads no calendar's days itself",
    })
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
| `maps-an-account-to-a-venue-account-code` | from v22 | | maps a book account to its code at a linked connectivity plugin, from its page at `admin`, acting for the admin |
| `hears-and-reads-a-venues-catalogue` | from v22 | | hears a linked connectivity plugin's catalogue, and reads it for a code |
| `claims-a-released-order` | from v22 | | hears an order released in its scope, and claims it |
| `places-at-a-linked-connectivity-plugin` | from v22 | | resolves the instrument and the venue, and places at one of its linked connectivity plugins |
| `proposes-a-child-order` | from v22 | | works a released order in house as child orders |
| `hears-a-placement-and-an-execution` | from v22 | | hears its placement acknowledged and filled |
| `cancels-a-placement`, `asks-to-cancel-an-order` | from v22 | | asks to cancel a placement, and an order, for a person |
| `enters-a-manual-execution-for-a-person` | from v22 | | enters a fill the venue did not report electronically, with its settlement date |
| `reads-its-orders-and-catches-up` | from v22 | | reads its orders on start, and those changed since after a loss |
| `reads-and-hears-the-trading-instructions`, `reads-and-hears-whether-releases-wait-for-compliance` | from v22 | | reads and hears the trading instructions, and each account's attributes |
| `reads-a-calendar`, `asks-for-a-settlement-date` | from v22 | from v22 | reads a settlement calendar's days, and asks core for a settlement date; about `calendars` and `settlement dates`, so either may be named not presented, with why |

A plugin catching up by range alone fails
`catches-up-trades-after-a-watermark`. Neither role records anything in the
lake.

From open-meridian 0.26.0 (contract v22) both suites
also hold `reads-a-calendar` and `asks-for-a-settlement-date`, about
`calendars` and `settlement dates`: map each, or, where your plugin's work
never uses them, name it in `not_presented`, with why (see
[A case not presented](../api/python-sdk.md#a-case-not-presented)). The
desk above asks core for the settlement date of a fill it enters, so it
maps `asks-for-a-settlement-date`, and names `reads-a-calendar`. The
`ems` suite holds the order path's cases too, each required (see
[The order path](../api/python-sdk.md#the-order-path)); a plugin holding
`signal` alone meets none of them.

`meridian plugin check --verified` does not hold the `signal` or `ems`
suite: it checks the `custody` and `data` suites, and from CLI 0.1.42
`connectivity`'s. Run your role's suite in your own tests, as above, and in
your CI.

**Gaps upstream.** Within a running data plugin, a dropped connection is
refilled from the venue's history by Alpaca, Coinbase and Kraken; Tradier
cannot refill it. In v19 a trade printed while a data plugin restarted was
recorded by none of them. From contract v20 a data
plugin starting again reads its last recorded trade from the lake and fills
the gap from the venue's history where the vendor allows: Alpaca 0.4.0,
Coinbase 0.3.0 and Kraken 0.3.0, not Tradier. Catching up by watermark gives
you every trade the lake has, and none it never had: see
[the lake](../concepts/the-lake.md#a-restarted-data-plugin-resumes).

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
- [Write a data plugin against its suite](write-a-data-plugin.md): recording them.
- [Using a data plugin](using-a-data-plugin.md#the-data-plugins): the
  sources that stream them.
