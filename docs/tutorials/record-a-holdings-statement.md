# Record a holdings statement

In this tutorial you turn the plugin `meridian plugin new` makes into a small **custody** plugin. It
records a holdings statement, one read of one source at one moment, and a holding in it, against
one of your firm's accounts. On the way you set up everything a plugin needs before a deployment
lets it write: a role, an account, and a link from the source's name for that account to yours,
made on the plugin's own **Setup** page under Manage.

!!! warning "What this tutorial cannot show yet"
    Read this first. The tutorial runs end to end, but three things are not built yet:

    - **You cannot read the result back here.** No dashboard page lists statements or custodial
      positions yet, and the SDK's reads of them, `list_statements` and
      `list_custodial_positions`, are an `operations` plugin's, not a custody plugin's. You confirm
      the recording from the replies your plugin logs.
    - **The data is made up.** So that you need no broker account, this plugin calls no broker. It
      reports two invented accounts and records one invented holding.
    - **Nothing here trades.** Holdings are read-only records of what a custodian says you hold.
      Order routing and execution are not built.

Allow 30 minutes.

## What you need

- A deployment installed with `meridian up --development`, and you are a deployment admin on it.
  See [Install a deployment](../getting-started/installation.md).
- The `meridian` CLI, 0.1.36 (`meridian --version`; `meridian upgrade` updates it), and Docker on
  this machine. From CLI 0.1.36, `meridian plugin new` builds on SDK 0.21.0 (contract v16), and
  writes the **Setup** page that links accounts, which this tutorial uses; the deployment's sidecar
  must accept contract v16.
- To have done [Change your plugin's page, live](change-the-page-live.md), or be comfortable with
  `meridian plugin dev`.

The examples use `https://meridian.localhost`, the deployment on this machine. For another, give
its address to `meridian connect`.

## How it fits together

A custody plugin follows workflow W2, holdings ingestion, and links its accounts by W6.4. It uses
seven of the SDK's [typed operations](../api/typed-operations.md), all granted by the `custody`
role. The scaffold already makes the first three; you write the other four:

| Step | SDK call | What it does |
|---|---|---|
| W2.8 | `report_external_accounts` | Says which accounts the source reaches, as the source names them |
| W6.4 | `read_accounts_for_linking` | Reads the firm's accounts, their identities alone, for the admin viewing the plugin's Setup page under Manage |
| W6.4 | `link_external_account` | Links one of the source's accounts to one of the firm's, for that admin |
| W2.1 | `report_sync_status` | Says how fresh the source's data is for one external account |
| W3.1 | `resolve_identifier` | Asks which instrument an identifier means |
| W2.2 | `record_holdings_statement` | Opens one statement for one external account, with its figures, and says how many rows will follow |
| W2.3 | `record_holding` | Records one row: one account, one instrument, a side, a quantity and a value |

The deployment's street store closes the statement when as many rows have arrived as it said would
follow.

Two rules decide whether a statement or a row is accepted:

1. **The external account must be linked.** The plugin names an account as the source knows it. An
   admin of the plugin links that to one of the firm's accounts, on a page the plugin serves under
   Manage, and the plugin sends the link acting for them. A statement or a row for an unlinked
   account is refused. Link, then record.
2. **The account must be in the plugin's write scope.** The link puts it there: the `custody` role
   lets the plugin write to the street store, and the link gives it the one account, for as long as
   the link stands. No permission is needed for that. A permission is what lets people use a plugin
   on accounts.

See [Accounts](../concepts/accounts.md) and [Instruments](../concepts/instruments.md).

## 1. Make the plugin

```bash
meridian connect
meridian plugin new holdings-demo
cd holdings-demo
```

## 2. Ask for the custody role

Open `pyproject.toml` and set the roles:

```toml title="pyproject.toml"
[tool.meridian]
roles = ["custody"]
interface = true
```

Roles come from the deployment's fixed list, and each role's grants are fixed with it. The plugin
cannot choose its own. A role is approved at launch, so set it before the first one: a save never
adds a role to a running instance. See [Plugins, roles and grants](../concepts/plugins.md).

## 3. Launch it live

The plugin must be running, and must have reported its accounts, before an admin can link them. In
your first terminal:

```bash
meridian plugin dev --instance holdings-demo
```

The first time, it builds and uploads the plugin, which takes a minute or two. Approve the role
when asked:

```text
holdings-demo 0.1.0 asks for
  roles: custody
Launch it live as holdings-demo, with these? [y/N] y
Launched holdings-demo: holdings-demo 0.1.0.
Its page, if it serves one: https://meridian.localhost/plugins/holdings-demo
Watching . for holdings-demo. Ctrl-C stops watching; the instance keeps running.
r1 sent (10 files, 0 deleted)
r1 synced (10 sent, 0 deleted)
r1 restarted
r1 ready
```

Leave it running. In a second terminal, check what it registered as:

```bash
meridian plugin logs --instance holdings-demo
```

```text
… INFO holdings_demo: registered as holdings-demo, roles custody
… INFO holdings_demo: may publish …; may subscribe nothing
… INFO holdings_demo: reported 1 external account(s) to link
… INFO holdings_demo: serving its pages on 127.0.0.1:8000
```

The `may publish` list is what the `custody` role grants, among it
`platform.street.command.record-statement` and `platform.street.command.record-holding`. With it,
the scaffold reports the one external account it reaches, `reference-1`: a plugin holding no role
that may report accounts reports none.

Every save from now on is a new revision, `r2`, `r3` and on. To read what one logged, pass
`--since` the revision before it: for `r4`, `--since 3`.

## 4. Make an account to link to

Open the dashboard, sign in, and choose the gear at the top right, **Settings**. On the
**Accounts** tab, choose **+ Add**, name it `Demo brokerage account`, and choose **Create**.
See [Give people access](../how-to/administer-access.md) for more on the tab.

That is all the plugin needs from Settings. You do not group the account or grant a
permission on it: the link you make in step 6 is the plugin's right to write it.

## 5. Report the source's accounts

A custody plugin says which accounts its source reaches before it records anything for them (W2.8).
Only an account it reported can be linked. The scaffold reports `REACHES`, in
`src/holdings_demo/page.py`, at start. Replace its one account with the two a broker would name:

```python title="src/holdings_demo/page.py"
REACHES = [
    meridian.ExternalAccount(
        external_account_id="DEMO-ACCT-1", name="Demo brokerage", venue_account_type="Individual"
    ),
    meridian.ExternalAccount(
        external_account_id="DEMO-ACCT-2", name="Demo retirement", venue_account_type="IRA"
    ),
]
```

`DEMO-ACCT-1` and `DEMO-ACCT-2` are the names the source uses for the accounts, as a broker would.
The name and type are the source's own words, shown to the admin who links them.

Save, wait for `ready`, and read what that revision logged. If it was `r2`:

```bash
meridian plugin logs --instance holdings-demo --since 1
```

```text
… INFO holdings_demo: registered as holdings-demo, roles custody
… INFO holdings_demo: may publish …; may subscribe nothing
… INFO holdings_demo: reported 2 external account(s) to link
… INFO holdings_demo: serving its pages on 127.0.0.1:8000
```

The scaffold's tests, in `tests/test_page.py`, link its old account, `reference-1`, named
`Reference account`. Move them to the first of yours, so they keep passing: change `"reference-1"`
to `"DEMO-ACCT-1"` in `LINKED`, in each `external_account_id` a test posts or checks, and in
`"Linked reference-1."`, and change `Reference account` to `Demo brokerage`. Leave
`meridian.Identity("reference-1", …)`, and the `<code>reference-1</code>` the Setup test looks for:
that is the instance the tests' stand-in sidecar says the plugin was launched as. The tests are
never sent to the instance, so this save makes no revision. Run them:

```bash
pip install -e . pytest
meridian plugin check --run-tests
```

`tests-pass` passes. One rule fails, `role-suite`: a plugin holding `custody` runs the custody
suite in its tests, each case mapped to its own exchange with its vendor. This plugin converts no
vendor's data, so it has nothing to map, and nothing in this tutorial needs the check to pass:
`plugin dev` does not run it. A real custody plugin passes it; see
[Pass the role's suite](../how-to/keep-what-the-edge-converts.md#pass-the-roles-suite).

## 6. Link DEMO-ACCT-1

On the dashboard's home, `holdings-demo` is listed with **Manage**: as a deployment admin you are an
admin of every plugin, through **All plugins (admin)**. Choose **Manage**. The plugin's area opens
on its **Summary**; open the tab after **Summary** and **Settings**, its one page at `admin`,
**Setup**. See [Manage, Open and View](../concepts/plugins.md#manage-open-and-view).

Under **External accounts** it lists `DEMO-ACCT-1` and `DEMO-ACCT-2`, each **Not linked**. On the
`DEMO-ACCT-1` row, choose **Link…**, type `Demo` in **An existing account**, choose
`Demo brokerage account`, then **Link**. The page says:

```text
Linked DEMO-ACCT-1.
```

and the row shows it **Linked** to `Demo brokerage account`. Leave `DEMO-ACCT-2` unlinked for now.

What the scaffold's Setup page, `setup` and `link` in `page.py`, does:

- **It is declared at `admin`**: `@pages.page("/setup", "Setup", levels="admin")`, and its form's
  route, `/link`, at `admin` too. The dashboard shows it under **Manage** alone, `Pages` answers
  403 to a session at any other level before the view runs, and it shows no account's data: the
  accounts' identities and links are configuration.
- **It reads the firm's accounts, and sends each link, acting for the admin**: `acting_for` is
  their header, handed back. The sidecar admits both only in a session opened by Manage, answers
  the accounts' identities alone, and admits a link only for an account this plugin reported.
- **It reads its links, never keeps them**: each row's link comes from the plugin's account scope,
  `account_scope()`, as the sidecar has it now.
- **It draws them with the kit's `om-account-map`**, which searches, filters and pages thousands of
  accounts, posting plain forms that carry the page's CSRF token. The plugin's page has its own
  sign-in cookie, so without the token a page elsewhere could make an admin's browser post the
  form; `Pages` refuses a form without it before the view runs. See
  [Build a plugin's page](../how-to/build-a-plugin-page.md#to-link-external-accounts-om-account-map).
- **The link is also a tool**: the route declares its inputs as one record, `LinkAccount`, so an
  agent you delegated to can link through the deployment's MCP, at `admin`, as you would here.

If the page says `This form has expired or did not come from this plugin's page`, the plugin
restarted since you opened it, with a new secret: reload it and link again. If it says
`Refused:`, the reason is the sidecar's own.

## 7. Write the recording code

Create a new file:

```python title="src/holdings_demo/statement.py"
"""Record one made-up holdings statement, the way a custody plugin would."""

from __future__ import annotations

import logging
import time
import uuid
from decimal import Decimal

import meridian

log = logging.getLogger("holdings_demo")

SOURCE = "demo"  # the source's name, like "snaptrade"
CUSTODIAN = "Demo Securities"  # where the source says the account is held
EXTERNAL_ACCOUNT = "DEMO-ACCT-1"  # the account as the source names it


async def record_demo_statement(plugin: meridian.Plugin) -> None:
    now = time.time_ns()
    try:
        # W2.1: how fresh this source's data is for the account.
        await plugin.report_sync_status(
            source=SOURCE,
            external_account_id=EXTERNAL_ACCOUNT,
            connection_healthy=True,
            last_synced_at_ns=now,
            observed_at_ns=now,
        )

        # W3.1: which instrument this identifier means. When nothing matches,
        # the deployment mints its own record for it, and answers that; only
        # an ambiguous match is a miss.
        symbol = meridian.Identifier(scheme="symbol", value="ACME", source=SOURCE)
        resolved = await plugin.resolve_identifier(identifiers=[symbol], as_of_ns=now)
        if resolved.found:
            log.info("ACME is %s (minted: %s)", resolved.instrument_id, resolved.minted)

        # W2.2: open one statement for the account, saying how many rows will
        # follow, with its figures as the source reported them.
        opened = await plugin.record_holdings_statement(
            source=SOURCE,
            external_statement_id=f"demo-{uuid.uuid4()}",
            external_account_id=EXTERNAL_ACCOUNT,
            institution=CUSTODIAN,
            as_of_date=time.strftime("%Y-%m-%d", time.gmtime()),
            read_at_ns=now,
            expected_rows=1,
            figures=[
                meridian.StatementFigures(
                    segment="",  # the account as a whole
                    buying_power=meridian.Money(Decimal("1000.00"), "USD"),
                ),
            ],
        )
        log.info(
            "opened statement %s (already recorded: %s)",
            opened.statement_id,
            opened.already_recorded,
        )

        # W2.3: one row. Resolved, it names the instrument. Ambiguous, it
        # carries what we held, and is recorded rather than dropped.
        row = await plugin.record_holding(
            statement_id=opened.statement_id,
            instrument_id=resolved.instrument_id if resolved.found else "",
            unresolved_identifiers=[] if resolved.found else [symbol],
            side=meridian.HoldingSide.HOLDING_SIDE_LONG,
            quantity=Decimal("12.5"),
            market_value=meridian.Money(Decimal("2812.50"), "USD"),
            external_account_id=EXTERNAL_ACCOUNT,
        )
        log.info("recorded holding %s (resolved: %s)", row.holding_id, row.resolved)
    except meridian.MeridianError as failed:
        log.warning("not recorded: %s", failed)
```

Amounts are `Decimal`, never `float`, and a value is a `meridian.Money`, an amount and its currency.
The SDK refuses a `float`, or more than 18 decimal places, rather than round it. A holding states
its side, long here.

The statement names the account it was read for, as its row does, and the institution holding it.
Its figures are a set per margin segment, each naming its segment as the source does; the one set
here names none, so it is the account's as a whole. Every figure is as the source reported it: a
source that reports no buying power sends none, which is not zero. See
[`record_holdings_statement`](../api/typed-operations.md#record_holdings_statement).

!!! note "Why a fresh statement id each run"
    Each save restarts the plugin, so this records a new statement each time. A real connector uses
    the source's own statement id, so a statement delivered twice comes back with
    `already_recorded` set, instead of being recorded twice.

!!! note "Changes in SDK 0.22.0"
    From SDK 0.22.0 a `Money` also names its currency's cash instrument, and a date field takes a
    `datetime.date` as well as its ISO 8601 text. `Money(amount, "USD")` and the text date above
    keep working unchanged.

## 8. Call it on start

Open `src/holdings_demo/__main__.py`. Import the new function next to the page import:

```python title="src/holdings_demo/__main__.py"
from .page import REACHES, TITLE, pages, reports
from .statement import record_demo_statement
```

Then record the statement just after the plugin reports itself healthy, which is after it has
reported its accounts:

```python title="src/holdings_demo/__main__.py"
        await plugin.report(healthy=True, detail="started")
        await record_demo_statement(plugin)
        await stopped.wait()
```

Save, and wait for `ready` on the last revision.

## 9. Check the result

Read what the last revision logged. If it was `r4`:

```bash
meridian plugin logs --instance holdings-demo --since 3
```

Expected output:

```text
… INFO holdings_demo: registered as holdings-demo, roles custody
… INFO holdings_demo: may publish …; may subscribe nothing
… INFO holdings_demo: reported 2 external account(s) to link
… INFO holdings_demo: serving its pages on 127.0.0.1:8000
… INFO holdings_demo: ACME is LCL-… (minted: True)
… INFO holdings_demo: opened statement STMT-… (already recorded: False)
… INFO holdings_demo: recorded holding HLD-… (resolved: True)
```

What happened:

- The statement was opened against `Demo brokerage account`, which `DEMO-ACCT-1` is linked to, and
  given an id by the deployment.
- The row was recorded against the same account.
- The deployment knew no instrument for the symbol `ACME`, so it **minted** its own record for it,
  an identifier beginning `LCL-`, and answered that, with `minted: True`. A later resolve of the
  same identifiers matches that record, and says `minted: False`: from the next save on, and on any
  later run of this tutorial on the same deployment. An `LCL-` record is the deployment's own, a
  record like any other; a deployment admin completes what it lacks, such as its asset class, on
  the dashboard's **Instruments** page.
- `resolved: True` because the row names an instrument, and so it updates a custodial position
  under it.
- Had more than one instrument matched `ACME`, the answer would have been a miss, not a pick. The
  row would then carry the identifier it held instead, be recorded as unresolved, with
  `resolved: False`, and update no position. See
  [`resolve_identifier`](../api/typed-operations.md#resolve_identifier).
- One row arrived of one expected, so the street store closed the statement.

## 10. See the rules work

Change the external account in `statement.py` to the one you left unlinked:

```python title="src/holdings_demo/statement.py"
EXTERNAL_ACCOUNT = "DEMO-ACCT-2"
```

Save, wait for `ready`, and read the logs after that revision. The last line now reads:

```text
… WARNING holdings_demo: not recorded: RecordHoldingsStatement: refused: external account DEMO-ACCT-2 is not linked to an account; a deployment admin links it on the plugin's admin page (W6.4), and the next statement records it
```

The statement names `DEMO-ACCT-2`, so it was refused before its row was sent, and nothing is
recorded for `DEMO-ACCT-2`. A row naming it would be refused the same way. The sync status before
it was not refused: the dashboard shows it beside the unlinked account, so an admin can tell
whether it is worth linking.

!!! note "Telling this refusal apart"
    The words are for you, reading the log, and may change at any release: don't match them. This
    refusal raises `meridian.NotLinked`, chosen by a code the sidecar sends with it, so a plugin
    can catch that alone and offer the account for linking. It is a `CallFailed`, so the
    `except meridian.MeridianError` above still catches it. See
    [An unlinked external account](../api/typed-operations.md#an-unlinked-external-account).

Linking `DEMO-ACCT-2` to `Demo brokerage account` is refused: that account has `DEMO-ACCT-1`
linked already, and an account has one external account. Try it on **Setup**, and the page says
so, beginning `Refused:`. Two external accounts at one custodian are two accounts, each with its
own statements. See [Accounts](../concepts/accounts.md#external-accounts).

So give it its own. On the **Accounts** tab of Settings, add a second account, `Demo retirement
account`. Reload the plugin's **Setup** tab, under Manage, and link `DEMO-ACCT-2` to it as you
linked `DEMO-ACCT-1`.

!!! note "Creating the account from the plugin's page"
    `link_external_account` can also create the account and link it in one step, named with
    `new_account_name` and given the custodian and type the source reported. Only a deployment
    admin may name a new account, which `caller.deployment_admin` says, and the sidecar refuses one
    from anybody else. The scaffold's Setup page offers linking to existing accounts alone: its
    `om-account-map` says `no-new-account`, and its `LinkAccount` takes no new account's name. See
    [Build a plugin's page](../how-to/build-a-plugin-page.md#to-link-external-accounts-om-account-map).

The next statement records it. Make any change to `statement.py`, a blank line will do, save, and
read the logs after that revision: the last line is `recorded holding …` again, and the resolve
before it says `minted: False`.

A statement or a row for a closed account is refused too, as outside the plugin's write scope,
and that refusal also shows as a `refused` event from `meridian plugin events`.

!!! tip "If a save still reports the old state"
    If a save made straight after you make a link still reports the old state, save again.

## 11. Clean up

Press Ctrl-C in the first terminal, then:

```bash
meridian plugin stop holdings-demo
```

The accounts and the links stay. To remove a link, choose **Change…** on its row on **Setup**,
then **Unlink**, before you stop the plugin. Close the accounts on the **Accounts** tab of
Settings if you do not want them.

## What you learned

- A plugin writes only through its role's typed operations, and only on accounts in its write
  scope.
- A custody plugin reports the accounts its source reaches, and an admin links them on its own
  page at `admin`, which the plugin serves under Manage, acting for the admin viewing it. The
  scaffold's Setup page is that page: it shows no account's data, reads its links from the
  plugin's account scope, and each form carries the page's CSRF token.
- An external account must be linked to one of the firm's accounts before a statement or rows for
  it are accepted, and the link is the plugin's right to write that account. An account has one
  external account.
- A statement names its external account, states its figures per margin segment as the source
  reported them, and says how many rows follow. An instrument nobody knows is answered with a
  record the deployment mints, and an ambiguous one is recorded unresolved; a row is never dropped.
- Refusals come back as `MeridianError` with the deployment's own reason.

## Next steps

- [Python SDK](../api/python-sdk.md) and [Typed operations](../api/typed-operations.md): every
  parameter of these calls.
- [Keep what your custody plugin converts](../how-to/keep-what-the-edge-converts.md): the raw
  record behind every row, and the custody suite a real custody plugin passes.
- [Prove your plugin against a released runtime](../how-to/prove-a-plugin-against-a-released-runtime.md):
  link an account through the Setup page and compare the street store with what you expect, in CI.
- [Release a plugin version](../how-to/release-a-plugin.md): turn it into a version.
