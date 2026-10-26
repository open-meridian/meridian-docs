# Write a data plugin against its suite

A data plugin, one holding the role `data`, puts a vendor's market data
into the deployment's [lake](../concepts/the-lake.md), converted at the
edge. The role has a conformance suite, carried by the SDK: a plugin
holding `data` is verified for it only by passing every case, and two data
plugins of a pair pass it unchanged. This page starts one from the template
and holds it to the suite. How a person then uses it is
[Using a data plugin](using-a-data-plugin.md).

You need CLI 0.1.53 and SDK 0.33.0 or later (contract 28): `meridian plugin new
--role data` writes this template on the role's common part, for a runtime
serving contract 28. A plugin made by an older CLI moves with
[`meridian plugin migrate`](../api/cli.md#plugin-migrate), then maps any new
cases as [below](#hold-it-to-the-suite).

## Make the plugin

```sh
meridian plugin new my-prices --role data
cd my-prices
```

It writes a whole plugin holding `data`, pinned to `open-meridian==0.33.0`,
that puts a stand-in vendor's daily closes and bars into the lake:

| File | What it is |
|---|---|
| `src/my_prices/declaration.py` | The version's declaration: its settings, its storage for raw records, and its **catalogue**, the dataset it serves. |
| `src/my_prices/vendor.py` | The stand-in vendor, answering from responses written into it. Replace it with your vendor's client. |
| `src/my_prices/convert.py` | The conversion: the vendor's text into the lake's rows, every subject and venue resolved first, what does not resolve reported; and its answer to a want. |
| `src/my_prices/page.py`, `templates/` | Its two pages under Manage, **Connection** and **Datasets**, the data role's common pages built on `meridian.roles.data`, each also a read tool for an agent, `read_connection` and `read_datasets`. Neither shows a price. Each template extends the role's and adds the vendor's nuance only at its blocks: see [The role's common pages](#the-roles-common-pages). |
| `tests/test_suite.py` | The data suite, each case mapped to one of the vendor's responses. |
| `tests/test_page.py` | Its pages' tests. |

The template leaves much of the data role's common work to
the SDK: `meridian.roles.data.Wants` hears and answers wants with your
conversion, and the Datasets page fills its rows from what it kept
(`data.served`, `data.want_rows`). `meridian.roles.data.pairs` and
`.event_contracts` do a venue's whole work for a venue listing pairs or
binary event contracts, with their pages and the checks a plugin runs
(`meridian.roles.data.testing`); a venue of event contracts also reports
how it groups them by event (see [Event groups](../concepts/event-groups.md)). A plugin made by an older CLI moves to the latest SDK, 0.33.0, with
`meridian plugin migrate`; see
[Each role's common logic](../api/python-sdk.md#each-roles-common-logic).

`AGENTS.md` teaches a coding agent the role's rules beside the template's
own. Use the SDK's `meridian` package and nothing of any vendor's: the SDK
carries no HTTP or WebSocket client and no vendor-file parser, so the
plugin chooses its own libraries.

## Declare what it serves

The catalogue, in `declaration.py`, declares each dataset from code. A
retail equity close might read:

```python
from meridian import DatasetDeclaration, DatasetLicence, Declaration, Storage

CATALOGUE = [
    DatasetDeclaration(
        key="daily",
        vendor="My vendor",
        data_types=["meridian.v1.Price", "meridian.v1.Bar", "meridian.v1.Bar.vwap"],
        modes=["pull", "push"],
        cadence=86_400,                # seconds between updates
        history=3650,                  # days it reaches back
        licence_default=DatasetLicence(kept=True, display=True, personal_use=True),
        day_time_zone="America/New_York",
        day_end_minute=16 * 60,        # the day ends at the 16:00 close
    ),
]

DECLARATION = Declaration(settings=SETTINGS, storage=Storage(retention_days=365),
                          catalogue=CATALOGUE)
```

The default licence is what the vendor's standard terms say, which a
deployment admin confirms or replaces; never a claim that a deployment
meets them. Put the vendor's key in a secret setting, and, for a vendor with
a sandbox as well as its live service, declare `meridian.environment()`
first (see [Using a data plugin](using-a-data-plugin.md#its-settings)).
From SDK 0.32.3 the licence also states the vendor's attribution terms,
such as its copyright class, the attribution's text and its not-affiliated
notice, set only for a deployment on chart 0.1.311 or later (see
[Record rates in a data plugin](record-rates.md#declare-the-dataset)).
Each part, and what the SDK refuses, is in the
[Python SDK reference](../api/python-sdk.md#a-data-plugins-catalogue).

## Convert at the edge

Replace the stand-in vendor, keeping the template's shape in `convert.py`:

1. **Keep the vendor's response first** as a raw record in the plugin's
   storage, without the key. Every row names it
   (`plugin.raw_record(...)`).
2. **Read every number from the vendor's text as a `Decimal`**, never
   through a `float`. A value that does not convert is counted, not
   recorded.
3. **Resolve every subject** to the deployment's instrument with
   [`resolve_identifier`](../api/typed-operations.md#resolve_identifier),
   reporting an ambiguous miss with
   [`report_missing_instrument`](../api/typed-operations.md#report_missing_instrument);
   and **every venue** with [`resolve_venue`](../api/typed-operations.md#resolve_venue),
   a MIC as `iso10383` or your vendor's code as a `symbol` with its source,
   reporting one the deployment does not hold with
   [`report_missing_venue`](../api/typed-operations.md#report_missing_venue).
4. **Record in batches** of 1 to 500 with
   [`record_prices`](../api/typed-operations.md#record_prices) and
   [`record_bars`](../api/typed-operations.md#record_bars), each row under a
   row key made from the raw record, a daily row with its business date as a
   `datetime.date`, a price in a stablecoin naming the token's cash
   instrument, never a fiat code.
5. **Restate a day still forming** under the same row key, its valid time
   ending after now, until its close is final.
6. **Answer wants**: hear `observations_wanted` and `want_withdrawn` with
   `receive`, record against a want with `want_id=`, and decline with
   [`decline_want`](../api/typed-operations.md#decline_want) what the vendor
   does not cover. A standing want is kept current until it is withdrawn.
   A decline stands only for the date or range its want asked.

7. **Name a subject another source resolved.** A want names the
   deployment's own instrument ID, which may be one your plugin never
   resolved: an instrument the book holds from a custodian's statement,
   known by the custodian's symbol and a CUSIP. Read its record with
   [`resolve_instrument`](../api/typed-operations.md#resolve_instrument),
   find among its identifiers one your vendor takes (a `symbol` your vendor
   serves), and record against the want under it. Decline as not covered
   only a record holding nothing your vendor takes. The template's
   `symbol_for` does this:

    ```python
    found = await self.plugin.resolve_instrument(instrument_id=instrument, as_of_ns=as_of_ns)
    named = {i.value for i in found.instrument.identifiers if i.scheme == "symbol"}
    ```

8. **Trades and quotes.** Declare them in a live dataset
   apart from the live prices, licensed by default kept two days or served,
   not kept:

    ```python
    DatasetDeclaration(
        key="trades",
        vendor="My vendor",
        data_types=["meridian.v1.Trade"],
        modes=["pull", "stream"],
        licence_default=DatasetLicence(kept=True, retention_days=2, personal_use=True),
        day_time_zone="America/New_York",
        day_end_minute=16 * 60,
    )
    ```

    Record them with
    [`record_trades`](../api/typed-operations.md#record_trades) and
    [`record_quotes`](../api/typed-operations.md#record_quotes), in batches
    of up to 500, only for subjects under a standing want, each keyed by
    UTC instants with no business date:

    - **Convert each condition code** into the trade's attributes (what it
      may set of the consolidated bar and its venue's, and its
      characteristics); keep a code you have no conversion for, as
      reported, in `meta.unconverted`, its eligibilities unset. Never keep
      the vendor's code table in the lake as the meaning of anything.
    - **The aggressor** is the side that took liquidity. Where your vendor
      names the resting order's side, record the other; where it says
      nothing, leave it unset.
    - **A correction or a withdrawal** is the next version under the same
      row key, a withdrawal `cancelled=True`.
    - **A quote's empty side** is unset, never zero.
    - **Keep the stream open while a standing want stands**, and after a
      drop read back what you missed from the vendor's history where it
      names each trade, so the lake has no gap; a trade heard twice is
      sent once. The SDK carries no WebSocket client: choose your own.

    A data plugin started anew hears each standing want again within about
    a minute, and opens its stream again.

9. **Backfill a restart's gap.** A plugin holds nothing it cannot lose, so
   the last trade it heard is gone when it restarts. It asks the lake
   instead: on start, before
   resuming its stream, it reads the last trade its own instance recorded of
   each subject it streams
   ([`list_trades`](../api/typed-operations.md#list_trades) with
   `latest_recorded=True`), reads the venue's history from each, and records
   what it missed. `meridian.roles.data.backfill_restart` does this, given
   the subjects and a function answering the venue's trades after a given
   one:

    ```python
    from meridian.roles import data

    async def missed(last) -> list[meridian.Trade]:
        # `last` is the lake's row: its subject, dataset, venue and time in `last.meta`.
        return await vendor.trades_since(last)

    await data.backfill_restart(plugin, subjects, missed)
    ```

    A trade recorded again is answered unchanged by its row key, so the
    overlap costs nothing. A subject never recorded starts from the stream.
    Where your vendor's history names no trade you can find again, or does
    not reach back far enough, say so on the Datasets page rather than
    guessing: the gap stays. See
    [the lake](../concepts/the-lake.md#a-restarted-data-plugin-resumes).

10. **Read its datasets' licences.**
    A data plugin reads [`list_datasets`](../api/typed-operations.md#list_datasets),
    answered only for the datasets its own catalogue declares, with the
    licence a deployment admin set on each, so its Datasets page says
    "Licensed" or "Not licensed yet" exactly. The template reads them on
    start and on a configuration change (`Converter.read_licences`).

## Hold it to the suite

`tests/test_suite.py` maps each case to one of the vendor's responses and
runs it through the plugin's own conversion, against a recorder that
answers as a sidecar does:

```python
from meridian.suites import run

def test_every_case_of_the_data_suite_passes() -> None:
    report = run("data", PRODUCERS, instance_id="reference-1")
    assert report.passed, report.failures
```

| Case | Given | The plugin |
|---|---|---|
| `a-daily-close` | a daily close, for a business date, with when it was published | resolves the security, and records a `close` per unit with its row key, business date, dataset, source times and raw record |
| `the-forming-day-restated` | the day's candle changing as it fills | records it under one row key, its valid time ending after now |
| `an-exact-price` | a price with more decimals than a float holds | records it exactly |
| `a-daily-bar` | open, high, low, close and volume, no VWAP | records the bar with its business date, the VWAP unset |
| `an-fx-rate` | a currency's rate for a business date | records it as a close |
| `a-stablecoin-quote` | an asset quoted in a stablecoin | names the token's instrument, and no currency code |
| `an-asset-that-does-not-resolve` | identifiers meeting two records | reports the miss as ambiguous |
| `a-venue-resolved` | a price's venue by its MIC | resolves it, and names its venue ID |
| `a-venue-not-held` | a venue the deployment does not hold | reports it missing |
| `a-want-recorded-against` | the lake wanting closes it covers | records them against the want |
| `a-subject-another-source-resolved` | the lake wanting a close for an instrument another source resolved, its record holding that source's symbol and a CUSIP | reads the record, and records the close against the want |
| `a-subject-declined` | the lake wanting a subject it does not cover | declines it as not covered |
| `a-standing-want-withdrawn` | a standing want withdrawn | records nothing more for it |

About trades and quotes:

| Case | Given | The plugin |
|---|---|---|
| `a-trade-recorded` | a trade with no condition codes, its event time and the side that took liquidity | records it with its price, quantity, aggressor and attributes, eligible for every statistic in both views, its row key, valid time, dataset and raw record |
| `the-makers-side-inverted` | a trade naming the resting order's side, a sell | records the aggressor as a buy |
| `a-condition-converted` | a trade whose condition says an odd lot, not to set the high and low or the close, its volume counted | records `odd_lot` and those eligibilities |
| `a-condition-not-converted` | a condition the plugin has no conversion for | keeps it in `meta.unconverted` |
| `a-trade-withdrawn` | the source withdrawing a trade it stated | records a version with `cancelled` under its row key |
| `a-quote-recorded` | the best bid and offer, each with its size | records both sides and sizes |
| `a-one-sided-quote` | a best bid and no offer | records the bid, the ask unset |
| `a-standing-want-streamed` | a standing want of a streamed dataset, and a trade for its subject on the stream | records the trade for that subject |

About the taker's side, a restart's gap and the datasets' licences:

| Case | Given | The plugin |
|---|---|---|
| `the-takers-side-stated` | a trade naming the side that took liquidity, a buy | records the aggressor as a buy |
| `a-restarts-gap-backfilled` | the plugin starting, the lake holding a trade it recorded of a streamed subject before it stopped, and the venue's history stating two trades since | reads its last recorded trade (`list_trades` with `latest_recorded`), and records the two |
| `reads-its-datasets-licences` | the plugin starting where a deployment admin licensed one of its declared datasets and not another | reads `list_datasets` |

About `calendars` and `settlement dates`, which every role's suite holds
(`asks-for-a-settlement-date` every role's but `connectivity`'s and
`operations`'):

| Case | Given | The plugin |
|---|---|---|
| `reads-a-calendar` | a calendar's days needed over a range | reads them from core, `read_calendar`, never a calendar of its own |
| `asks-for-a-settlement-date` | a settlement date needed for an instrument and a trade date | asks core, `compute_date(settlement=...)`, and never works it out itself |

About an event contract's [outcome](../concepts/the-lake.md#an-event-contracts-outcome):

| Case | Given | The plugin |
|---|---|---|
| `records-an-outcome` | the source determines an event contract to pay its full payout, stating its stage, its word and its settlement value | records the outcome, `pays`, at `determined` or `final` (either passes, `any_of`), its settlement value and the venue's word, with its row key and raw record and no business date |
| `restates-a-disputed-outcome` | the determination disputed after it was recorded | records `disputed` under the same row key, the next version |
| `records-a-partial-payout` | a scalar result or a 50-50 resolution | records `pays_part` with its settlement value |

The first and third are about `outcomes`, the second about `disputed
outcomes`, so a source that states no dispute marks it not presented, with
why, as a source with no event contracts marks all three. The data
template derives them from its catalogue, as below: declare a dataset of
`meridian.v1.Outcome` and they are required.

A producer for each calls the operation through the recorder, as the role
templates' `tests/test_suite.py` show:

```python
async def asks_for_a_settlement_date(recorder: Recorder) -> None:
    await recorder.compute_date(
        settlement=ops.SettlementDateInputs(instrument_id="LCL-1", trade_date="2026-10-09")
    )
```

A case your vendor never presents, such as an FX rate from an equity
source, maps to the recording path it would take. When you replace the
stand-in vendor, map each case to a recorded or synthetic exchange with your
own, and keep every case passing: a candle read through a `float`, or a
forming day recorded as a new row, fails it.

### A kind of data your source never publishes

Each case about one kind of data says which in its `about` (closes, bars,
trades, quotes, prices on a venue, a currency's rate against another
currency, a crypto asset's price, a security's price, outcomes and disputed
outcomes). A plugin that declares it never publishes that kind
names the case in `not_presented`, with why, and is verified on the rest;
a case with no `about` is every data plugin's, and stays required, as
`reads-its-datasets-licences` is. The template
derives its list from its own catalogue, so a dataset declaring trades or
quotes makes those cases required again:

```python
KINDS = {"trades": "meridian.v1.Trade", "quotes": "meridian.v1.Quote"}
DECLARED = {kind for dataset in DECLARATION.catalogue for kind in dataset.data_types}
NOT_PRESENTED = {
    case.name: f"its datasets publish daily closes and bars, and no {case.about}"
    for case in suite("data").cases
    if case.about in KINDS and KINDS[case.about] not in DECLARED
}
report = run("data", PRODUCERS, not_presented=NOT_PRESENTED, instance_id="reference-1")
```

**Contract 27's markers.** The data suite's seven rates cases are `about:
rates`, mapped by a rates publisher's plugin (see
[Record rates in a data plugin](record-rates.md)) and named by every other;
`records-a-datasets-liveness` is `about: streams`, for a source that is
polled; `queries-the-lake-within-bounds` is `about: trades`; and
`an-exact-price` and `a-want-recorded-against` are `about: closes` from SDK
0.32.1.

**Contract 28's markers.** `reports-its-feed-delay` is required of every
data plugin: its `roles.Latency` reports the feed delay, and
`meridian.roles.data.testing.feed_delay` maps the case for the SDK's
kinds. The chain's cases are `about: option chains`; the filings slice's
`about: filings`, `holdings`, `corporate actions` and `ratings`; and
`a-crossed-quote-is-recorded-invalid`, `a-duplicate-is-recorded-suspicious`
and `rows-after-a-gap-are-suspicious` `about: quotes`, since they expect
quote rows. A plugin whose source presents none of a kind names its cases
not presented, with why. See
[Record and read an option chain](record-and-read-an-option-chain.md).
`meridian.roles.data.testing`'s `PAIRS_NOT_PRESENTED`,
`EVENT_CONTRACTS_NOT_PRESENTED` and `RATES_NOT_PRESENTED` name what each
kind of venue never presents; from SDK 0.32.2 `RATES_NOT_PRESENTED` leaves
`records-a-datasets-liveness` for a polled plugin to present or name.

**Liveness and delay.** A dataset that is delayed declares it,
`DatasetDeclaration(declared_delay_ns=...)`; a stream that sends only on
change records its heartbeats with `Wants.liveness`, as a pairs feed and,
from SDK 0.32.3, a listings feed do for their live datasets; and the plugin
declares `meridian.dataset_thresholds()` for its admin to set each
dataset's staleness. See
[Data age and liveness](../concepts/data-age-and-liveness.md).

### A field your source never states

The same goes for one field of a kind you do publish. A case about a field says which in
its `about_field`: `meridian.v1.Trade.aggressor` for the side that took
liquidity (`the-takers-side-stated`, `the-makers-side-inverted`), and
`meridian.v1.TradeAttributes.characteristics` for what a condition says
(`a-condition-converted`, `a-condition-not-converted`). A source that
records trades but never states that field, as no US stock feed states the
aggressor, names those cases in `not_presented`, with why:

```python
NOT_PRESENTED["the-takers-side-stated"] = "the vendor's stock trades never say which side took liquidity"
NOT_PRESENTED["the-makers-side-inverted"] = "the vendor's stock trades never say which side took liquidity"
```

### A kind of work your plugin never does

`about` names a kind of work too: `reads-a-calendar` is about `calendars`, and
`asks-for-a-settlement-date` about `settlement dates`. A plugin whose work
never uses one names the case in `not_presented`, with why, and is verified
on the rest. The template maps both, so keep them mapped if your plugin
reads a calendar or asks for a date; otherwise:

```python
NOT_PRESENTED["asks-for-a-settlement-date"] = "it records closes as published and works out no settlement date"
```

The SDK's runner refuses a name in `not_presented` that is neither a
closed-list case nor a case with an `about` or an `about_field`, so every
other case stays required. It checks that the case carries a marker, not
that your catalogue lacks the kind: the template derives that from its
catalogue, as above.

The suite's test may not skip or expect a failure, and asserts `report.passed` in the statement after the
run, as above: mark what your source never presents instead (see
[`plugin check`](../api/cli.md#plugin-check)).

Then hold the plugin to the framework's rules as a verified plugin, installing it and pytest in a
virtual environment of the plugin's own:

```sh
python3 -m venv .venv && . .venv/bin/activate
pip install -e . pytest
meridian plugin check --verified --run-tests
```

A bare `pip install` outside a virtual environment is refused by some Pythons, such as Homebrew's on
macOS (`externally-managed-environment`). `--run-tests` runs the tests with `.venv/bin/python` when
the plugin has a `.venv`.

`--verified` fails `role-suite` where no test runs the data suite, and
`--run-tests` runs it; see [`plugin check`](../api/cli.md#plugin-check). It
holds only the `custody`, `data`, `connectivity` and `pricing` suites: a reading role
the plugin also holds is not checked for its suite. It also fails
`role-pages` where the plugin's Connection and Datasets pages,
their tools and its settings are not the role's, in the role's order (see
below); without `--verified` it says so as advice.

## The role's common pages

Every data plugin has the same pages, sections, labels and order, so a person who
knows one knows any (see [Using a data plugin](using-a-data-plugin.md)).
The SDK's `meridian.roles.data` holds the common part:

- **`ConnectionRead`** and **`DatasetsRead`**, the records the two pages
  draw and their tools answer (`answers=`), under fixed names: `mode`,
  `credentials` (each a `Credential`, its label and whether it is set),
  `entitled_at_vendor`, `limit`, `calls`, `rate_limited`, `last_call_at`,
  `last_error` and `sessions` (None for a source that does not stream); and
  `served` (each a `Served`, with `licensed`), `wants` (each a `Want`) and
  `reads_instruments`. Extend either with your own fields.
- **The templates** `meridian/roles/data/connection.html` and
  `datasets.html`, which draw the common sections (Connection's "Key",
  "Limits and use" and "Stream"; Datasets' "Served", "Wants" and
  "Subjects") and their "not set up yet" states. Your template extends
  one, and adds the vendor's nuance only at its blocks: `vendor_notices`,
  `vendor_rows` (one per section, its title in `section`),
  `vendor_columns` and `vendor_sections`:

    ```jinja
    {% extends "meridian/roles/data/connection.html" %}
    {% block vendor_rows %}
    {% if section == "Key" %}<tr><th scope="row">Feeds</th><td>IEX live, SIP history</td></tr>{% endif %}
    {% endblock %}
    ```

- **`figures(...)`**, the role's Summary figures in its order:
  "Connection", "Entitled at the vendor", "Stream", "Last recorded" and
  "Rate use", then up to three of your own.
- **Settings**: `meridian.environment()` first, for a vendor with a
  sandbox as well as its live service, each credential differing by it
  gated with `applies_when=("environment", "sandbox")`; your credentials,
  labelled in the vendor's own words; your own settings; then
  `meridian.sample_data()`.

Never rename, reorder or drop a common page, section, row, column, label,
setting or figure. A vendor without a common item says so in it ("No key
needed", "Does not stream") rather than leaving it out. `role-pages` checks
what the version declares, not whether the SDK drew it, so a plugin written
without the SDK keeps the role the same way.

## Put it in a deployment

```sh
meridian plugin upload
meridian plugin launch my-prices 0.1.0 --instance my-prices-1
```

or, on a development deployment, `meridian plugin dev --instance
my-prices-1`. Its dataset is `my-prices-1:daily`; a deployment admin
licenses it and entitles the plugins that read it, on the Data sources
page: see [License and entitle a dataset](license-and-entitle-a-dataset.md).

## Related

- [The lake in the Python SDK](../api/python-sdk.md#the-lake).
- [Prove a plugin against a released runtime](prove-a-plugin-against-a-released-runtime.md):
  the plugin on core's plugin harness, whose runner licenses and entitles a
  dataset and prints the lake's store.
- [Keep what your custody plugin converts](keep-what-the-edge-converts.md):
  conversion at the edge and raw records, for `custody`, which `data`
  follows.
