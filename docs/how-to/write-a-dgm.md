# Write a `dgm` against its suite

A `dgm` plugin puts a vendor's market data into the deployment's
[lake](../concepts/the-lake.md), converted at the edge. The role has a
conformance suite, carried by the SDK: a plugin holding `dgm` is verified
for it only by passing every case, and two data plugins of a pair pass it
unchanged. This page starts one from the template and holds it to the
suite.

!!! note "Built, not released"
    This page describes open-meridian 0.22.0 (contract v18) and the CLI
    release after 0.1.36, whose `plugin new --role dgm` writes this
    template. Neither is released yet, nor is the runtime that serves
    contract v18, chart 0.1.291.

## Make the plugin

```sh
meridian plugin new my-prices --role dgm
cd my-prices
```

It writes a whole plugin holding `dgm`, pinned to `open-meridian==0.22.0`,
that puts a stand-in vendor's daily closes and bars into the lake:

| File | What it is |
|---|---|
| `src/my_prices/declaration.py` | The version's declaration: its settings, its storage for raw records, and its **catalogue**, the dataset it serves. |
| `src/my_prices/vendor.py` | The stand-in vendor, answering from responses written into it. Replace it with your vendor's client. |
| `src/my_prices/convert.py` | The conversion: the vendor's text into the lake's rows, every subject and venue resolved first, what does not resolve reported; and its answer to a want. |
| `src/my_prices/page.py`, `templates/` | Its two pages under Manage, **Connection** and **Datasets**, each also a read tool for an agent, `read_connection` and `read_datasets`. Neither shows a price. |
| `tests/test_suite.py` | The `dgm` suite, each case mapped to one of the vendor's responses. |
| `tests/test_page.py` | Its pages' tests. |

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
meets them. Put the vendor's key in a secret setting (see
[Add a data plugin's key](add-a-data-plugins-key.md)). Each part, and what
the SDK refuses, is in the
[Python SDK reference](../api/python-sdk.md#a-dgms-catalogue).

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

!!! note "TODO: instruments a `dgm` did not resolve itself"
    In contract v18 a `dgm` may resolve its own identifiers to an
    instrument, but may not read an instrument's record, so it names to its
    vendor only the listings it resolved itself: a want for an instrument
    known to the deployment only by another source's identifier is declined
    as not covered. A fix is in progress; this step changes when it lands.

## Hold it to the suite

`tests/test_suite.py` maps each case to one of the vendor's responses and
runs it through the plugin's own conversion, against a recorder that
answers as a sidecar does:

```python
from meridian.suites import run

def test_every_case_of_the_dgm_suite_passes() -> None:
    report = run("dgm", PRODUCERS, instance_id="reference-1")
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
| `a-subject-declined` | the lake wanting a subject it does not cover | declines it as not covered |
| `a-standing-want-withdrawn` | a standing want withdrawn | records nothing more for it |

A case your vendor never presents, such as an FX rate from an equity
source, maps to the recording path it would take. When you replace the
stand-in vendor, map each case to a recorded or synthetic exchange with your
own, and keep every case passing: a candle read through a `float`, or a
forming day recorded as a new row, fails it.

Then hold the plugin to the framework's rules as a verified plugin:

```sh
pip install -e . pytest
meridian plugin check --verified --run-tests
```

`--verified` fails `role-suite` where no test runs the `dgm` suite, and
`--run-tests` runs it; see [`plugin check`](../api/cli.md#plugin-check).

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
  conversion at the edge and raw records, for `custody`, which `dgm`
  follows.
