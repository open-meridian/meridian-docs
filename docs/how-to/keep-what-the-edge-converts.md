# Keep what your custody plugin converts

A plugin at the edge speaks to a vendor and converts what the vendor says into the contract's words.
From contract v11 ("the edge keeps its own") the contract asks it to keep what it converted from,
say how it came by every value the vendor did not send, and count each asset once, so that a reader
written from the contract alone reconciles any custodian the same way. This page shows what a
custody plugin does for each, with [meridian-snaptrade](https://github.com/open-meridian/meridian-snaptrade)
0.9.0 as the worked example.

!!! note "Released 2026-10-05"
    This page describes the Python SDK 0.19.0 (contract v14), on PyPI, and CLI 0.1.34, saying
    where a part arrived in an earlier version.

From contract v14 a custody plugin also reports each activity on an account, each with a raw
record of its own: see [Report the custodian's activity](report-the-custodians-activity.md).

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

## Declare its kinds, and move them past their window

From contract v16 a version declares the kinds of raw record it keeps, each with its default
window, rather than one retention for all of them, and the deployment's admins decide what is done
past each window (see [The archive](../concepts/the-archive.md)):

```python
from meridian.declaration import Declaration, RecordKind, Storage

DECLARATION = Declaration(
    settings=SETTINGS,
    storage=Storage(kinds=[
        RecordKind("activity", "Reported activity", window_days=2555),
        RecordKind("responses", "Raw responses", window_days=30),
    ]),
)
```

- **Declare no window setting of your own.** The SDK declares `<kind>_window_days` and
  `<kind>_past_window` for each kind, and refuses a plugin that takes either name;
  `meridian plugin check` says so first (`window-settings`).
- **Keep each kind in units you can find again**, a file or directory per account and day or
  month, and name a record by its path within its unit.
- **When a unit's last record is past its window**, do what `<kind>_past_window` says:
  `archived`, `plugin.archive_unit(...)`; `deleted`, `plugin.delete_unit(...)`; `kept`, nothing.
  Never remove a unit any other way: the SDK reports each move before it removes anything, and a
  deletion inside the deployment's hold is refused, `CommandRefused` with
  `REFUSAL_REASON_WITHIN_HOLD`, and the unit kept.
- **Say what each kind holds** in storage whenever it changes: `plugin.stored`.
- **On your page**, resolve a row's record with `plugin.find_record(key)`, and offer a restore
  under Open as a form posting `record_kind` and `unit` to `/archive/restore`, which the SDK
  declares.

Each call, argument by argument, is in [The archive](../api/python-sdk.md#the-archive).

### Move a plugin to 0.21.0 { #move-a-plugin-to-0210 }

`meridian plugin migrate` moves only the pins: `open-meridian==0.21.0` and
`plugin-python:0.21.0`. Nothing a plugin calls changed, and a plugin keeping one retention,
`Storage(retention_days=...)`, keeps its records under it as before. A plugin adopting kinds drops
any setting of its own that held a window, and its release notes name that setting and the
window setting it maps to, for the admin to set once at upgrade, as SnapTrade 0.13.0's do (see
[Upgrade SnapTrade to 0.13.0](keep-older-records-in-the-archive.md#upgrade-snaptrade-to-0130)). A
plugin built on 0.21.0 declares contract v16, and a runtime serving v15 refuses it at
registration, naming both versions.

### Move a plugin to 0.22.0 { #move-a-plugin-to-0220 }

`meridian plugin migrate` moves only the pins: `open-meridian==0.22.0` and
`plugin-python:0.22.0`, built and not yet released. A `Money` naming its currency by its ISO 4217
code keeps its shape, and core resolves the code to the currency's cash instrument; a date sent as
valid ISO text is sent as before. Left for you: a test comparing a `Money` read back with one it
made, which now carries `instrument_id` (compare `amount` and `currency_code`), and a date sent as
text that is no date, now refused. A plugin built on 0.22.0 declares contract v18, and a runtime
serving v16 refuses it at registration, naming both versions. SnapTrade 0.13.1 and the sample
operations plugin 0.9.1 are this move and nothing else. See
[Money and instruments](../concepts/money-and-instruments.md).

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

Whether a position is cash at all is yours to decide too, from what your vendor says: the street
and operations assume how cash and a money market fund behave, never how a vendor books a record.
Decide from the vendor's own data first, and where it says nothing, from a setting an admin of the
plugin fills, carrying the row's `changed_by` and `changed_at` as `edge.supplied`; never from what
a symbol looks like. A money market fund stays a fund. SnapTrade's
[cash links](set-a-plugins-settings.md#snaptrade-cash-links) are an
example.

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
`not_presented`, with why; every other case needs a producer. `meridian plugin check --verified`
fails a custody plugin with no such test (`role-suite`), and `--run-tests` runs it. From the CLI
release after 0.1.36 the rule is held only under `--verified`; CLI 0.1.36 and earlier hold every
custody plugin to it. A `dgm` plugin passes its own suite the same way: see
[Write a `dgm` against its suite](write-a-dgm.md#hold-it-to-the-suite).
