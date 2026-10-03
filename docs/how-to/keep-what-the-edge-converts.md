# Keep what your custody plugin converts

A plugin at the edge speaks to a vendor and converts what the vendor says into the contract's words.
From contract v11 ("the edge keeps its own") the contract asks it to keep what it converted from,
say how it came by every value the vendor did not send, and count each asset once, so that a reader
written from the contract alone reconciles any custodian the same way. This page shows what a
custody plugin does for each, with [meridian-snaptrade](https://github.com/open-meridian/meridian-snaptrade)
0.9.0 as the worked example.

!!! note "Built, not released"
    This page describes the Python SDK 0.16.0 (contract v11) and the command line after 0.1.27,
    built and not yet released. The rest of these pages describe SDK 0.14.0 (contract v9).

## Declare what the version is

A version's **declaration** says three things beside its roles: the names of the secret settings it
will ask for, what it receives from its vendor and does not carry, and the storage it asks for. It
never holds a value, an account or an identifier.

```python
from meridian.declaration import Declaration, NotCarried, Storage

DECLARATION = Declaration(
    settings=SETTINGS,  # its secret settings' names are declared, never their values
    not_carried=(
        NotCarried("custody", "myvendor:position", "open_pnl", "no_contract_meaning"),
    ),
    storage=Storage(retention_days=30),
)
```

Name it in `pyproject.toml`, and register with it:

```toml
[tool.meridian]
roles = ["custody"]
declaration = "my_plugin.declaration:DECLARATION"
```

```python
async with await meridian.connect(settings=SETTINGS, declaration=DECLARATION) as plugin:
    ...
```

`meridian plugin upload` runs the SDK's `meridian-declaration` in the image it built, with no
network, and sends what it prints with the version, so a deployment admin sees it before launch.
A plugin holding no edge role (`ccm`, `custody`, `dgm`, `match`, `reporting`, `servicing`,
`settlement`) may not ask for storage: upload refuses it, `meridian plugin check` fails it
(`edge-storage`), and the deployment refuses it at registration.

Each time the plugin meets a name it declared as not carried, it counts it:
`plugin.note_not_carried("myvendor:position", "open_pnl")`. The counts ride on its heartbeat and
are drawn on its Summary, by name only, and they stay in the deployment.

## Keep the raw record, and name it on every row

A deployment grants a plugin holding an edge role storage of its own, kept across restarts and new
versions and reached by no other plugin. The SDK says where: `meridian.edge.storage_dir()`, or
`None` where none is granted. Keep what the vendor answered there, by your own key, for as long as
your declaration says.

Every row and statement then names the raw record it was converted from:

```python
await plugin.record_holding(
    ...,
    raw_record=plugin.raw_record("ACCT-1/20261003T120000Z/positions"),
)
```

The key is yours and opaque past your plugin; the sidecar fills in your instance, and refuses a
reference naming another's. A person follows it on your plugin's own page.

## Say how you came by what the vendor did not send

A value your vendor did not send, and you closed, carries its **provenance**:

```python
from meridian import edge

provenance=[
    edge.derived("settle_date_quantity", "the quantity less the account's trades not settled"),
]
```

`edge.derived(field, rule)` for a value derived by a named rule, `edge.supplied(field, person)` for
one a person gave on your page, `edge.second_source(field, source)` for one from a second source of
your own, and `edge.reported(field, raw_record)` for one the vendor reported in another raw record.
It is never presented as the vendor's word.

A value the vendor sent that you cannot convert travels as the field's not-known value, with the
vendor's beside it: `edge.as_reported(scheme, code, text)`. An account whose type says neither
cash, margin nor retirement is reported with `account_kind` unset and
`account_kind_as_reported=edge.as_reported("myvendor:account-type", "INDIVIDUAL")`;
`venue_account_type` is deprecated.

## Count each asset once

The street counts each asset once. A custodian that counts a money market fund both as a holding
and inside the cash of its currency is yours to net: send the fund as the holding and the cash net
of it, with the provenance `edge.derived("quantity", <your rule>)`, and keep the custodian's gross
cash in your raw records. Where you cannot serve the statement clean (no price for the fund, or a
fund worth more than the cash), withhold it and say why on your page. `also_counted_in_cash` and
`currency_assumed` are deprecated.

The settled quantity and the pending quantities by value date (`meridian.ReportedPending`) are the
custody role's: state them as the vendor reports them, or close them with their provenance.

When a later contract adds a field, re-send a row from your raw records with
`backfill=edge.backfill("v11", "raw_record")`; the street journals it beside the row as first
recorded.

## Pass the role's suite

A plugin holding `custody` is verified for it only by passing every case of the custody suite,
which the SDK carries. Map each case to your own exchange with your vendor, run your own conversion
against the runner's recorder, and assert the report:

```python
from meridian.suites import run

def test_every_case_of_the_custody_suite_passes() -> None:
    report = run("custody", PRODUCERS, not_presented=NOT_PRESENTED)
    assert report.passed, report.failures
```

A case asserting one value of a closed list your vendor never presents may be named in
`not_presented`, with why; every other case needs a producer. `meridian plugin check` fails a
custody plugin with no such test (`role-suite`), and `--run-tests` runs it.
