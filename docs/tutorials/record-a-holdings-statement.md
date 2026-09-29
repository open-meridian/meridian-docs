# Record a holdings statement

In this tutorial you build a small **custody** plugin. It records a holdings statement, one read of
one source at one moment, and a holding in it, against one of your firm's accounts. On the way you
set up everything a plugin needs before a deployment lets it write: a role, an account, a permission
and an external account link.

!!! warning "What this tutorial cannot show yet"
    Read this first. The tutorial runs end to end, but three things are not built yet:

    - **You cannot read the result back.** No dashboard page and no SDK operation lists statements or
      custodial positions yet. You confirm the recording from the replies your plugin logs.
    - **The data is made up.** A deployment cannot yet hand a plugin its settings, such as a broker's
      API key, so this plugin does not call a real broker. It records one invented holding.
    - **Nothing here trades.** Holdings are read-only records of what a custodian says you hold.
      Order routing and execution are not built.

Allow 20 minutes.

## What you need

- A deployment installed with `meridian up --development`, and you are a deployment admin on it.
  See [Install a deployment](../getting-started/installation.md).
- The `meridian` CLI, 0.1.3 or later, and Docker on this machine.
- To have done [Change your plugin's page, live](change-the-page-live.md), or be comfortable with
  `meridian plugin dev`.

The examples use `http://meridian.localhost`, the deployment on this machine. For another, give
its address to `meridian connect`.

## How it fits together

A custody plugin follows workflow W2, holdings ingestion. It uses four of the SDK's
[typed operations](../api/typed-operations.md), all granted by the `custody` role:

| Step | SDK call | What it does |
|---|---|---|
| W2.1 | `report_sync_status` | Says how fresh the source's data is for one external account |
| W3.1 | `resolve_identifier` | Asks which instrument an identifier means |
| W2.2 | `record_holdings_statement` | Opens one statement and says how many rows will follow |
| W2.3 | `record_holding` | Records one row: one account, one instrument, a quantity and a value |

The deployment's street store closes the statement when as many rows have arrived as it said would
follow.

Two rules decide whether a row is accepted:

1. **The external account must be linked.** The plugin names an account as the source knows it. A
   deployment admin links that to one of the firm's accounts. An unlinked row is refused.
2. **The account must be in the plugin's write scope.** Some permission must give this plugin's
   `custody` part at `write` on an account group holding that account.

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
cannot choose its own. See [Plugins, roles and grants](../concepts/plugins.md).

## 3. Launch it live

The plugin must be running before an admin can grant it anything or link accounts to it. In your
first terminal:

```bash
meridian plugin dev --instance holdings-demo
```

Approve the role when asked:

```text
holdings-demo 0.1.0 asks for
  roles: custody
Launch it live as holdings-demo, with these? [y/N] y
Launched holdings-demo: holdings-demo 0.1.0.
Its page, if it serves one: http://meridian.localhost/plugins/holdings-demo
Watching . for holdings-demo. Ctrl-C stops watching; the instance keeps running.
r1 sent (8 files, 0 deleted)
r1 synced (8 sent, 0 deleted)
r1 restarted
r1 ready
```

Leave it running. In a second terminal, check what it registered as:

```bash
meridian plugin logs --instance holdings-demo
```

```text
… INFO holdings_demo: registered as holdings-demo, roles custody
… INFO holdings_demo: may publish …; may subscribe …
… INFO holdings_demo: serving its page on 127.0.0.1:8000
```

The `may publish` list is what the `custody` role grants.

## 4. Give the plugin an account to write

Do this on the dashboard's Administer page. Open the dashboard, sign in, and choose **administer
this deployment**. See [Give people access](../how-to/administer-access.md) for more on each tab.

1. **Accounts** tab: choose **New account**, name it `Demo brokerage account`, and choose
   **Create**.
2. **Account groups** tab: choose **New account group**, name it `Demo accounts`, tick
   `Demo brokerage account`, and choose **Create**.
3. **Access groups** tab: choose **New access group**, name it `Holdings demo`, and under
   **Entries, one per line** write:

    ```text
    holdings-demo write
    ```

    Choose **Create**. An entry is a plugin instance and a level, `read` or `write`, the same for
    every plugin.

4. **Permissions** tab: choose **Grant a permission**. Choose:
    - **User group:** `Deployment admins`, or a user group of your own.
    - **On accounts:** `Demo accounts`.
    - **Access:** `Holdings demo`.

    Choose **Grant**. The account is now in the plugin's write scope, and the people in that user
    group may use the plugin on it.

5. Link the external account `DEMO-ACCT-1` to `Demo brokerage account`.

    !!! warning "This step is being rewritten"
        The dashboard's External accounts tab has been removed: each plugin now links its own
        external accounts, from its own admin page, acting for the deployment admin viewing it
        (see [Accounts](../concepts/accounts.md)). The demo plugin in this tutorial has no such page
        yet, so this step cannot be completed as written. A version of the tutorial whose plugin
        reports `DEMO-ACCT-1` and links it from a small admin page, with
        `plugin.link_external_account(..., acting_for=caller.header)`, is on its way.

`DEMO-ACCT-1` is the name the plugin will use for the account, as a broker would.

## 5. Write the recording code

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

SOURCE = "demo"                    # the source's name, like "snaptrade"
EXTERNAL_ACCOUNT = "DEMO-ACCT-1"   # the account as the source names it


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

        # W3.1: which instrument this identifier means, if the deployment knows.
        symbol = meridian.Identifier(scheme="symbol", value="ACME", source=SOURCE)
        resolved = await plugin.resolve_identifier(identifiers=[symbol], as_of_ns=now)

        # W2.2: open one statement, saying how many rows will follow.
        opened = await plugin.record_holdings_statement(
            source=SOURCE,
            external_statement_id=f"demo-{uuid.uuid4()}",
            as_of_date=time.strftime("%Y-%m-%d", time.gmtime()),
            read_at_ns=now,
            expected_rows=1,
        )
        log.info(
            "opened statement %s (already recorded: %s)",
            opened.statement_id,
            opened.already_recorded,
        )

        # W2.3: one row. Resolved, it names the instrument. Unresolved, it
        # carries what we held, and is recorded rather than dropped.
        row = await plugin.record_holding(
            statement_id=opened.statement_id,
            instrument_id=resolved.instrument_id if resolved.found else "",
            unresolved_identifiers=[] if resolved.found else [symbol],
            quantity=Decimal("12.5"),
            market_value=Decimal("2812.50"),
            currency="USD",
            external_account_id=EXTERNAL_ACCOUNT,
        )
        log.info("recorded holding %s (resolved: %s)", row.holding_id, row.resolved)
    except meridian.MeridianError as failed:
        log.warning("not recorded: %s", failed)
```

Amounts are `Decimal`, never `float`. The SDK refuses more than eight decimal places rather than
round them.

!!! note "Why a fresh statement id each run"
    Each save restarts the plugin, so this records a new statement each time. A real connector uses
    the source's own statement id, so a statement delivered twice comes back with
    `already_recorded` set, instead of being recorded twice.

## 6. Call it on start

Open `src/holdings_demo/__main__.py`. Import the new function next to the page import:

```python title="src/holdings_demo/__main__.py"
from .page import TITLE, serve
from .statement import record_demo_statement
```

Declare that the plugin names accounts by a source's identifiers, which an admin links. Add
`reads_external_accounts=True` to the `connect` call:

```python title="src/holdings_demo/__main__.py"
    async with await meridian.connect(
        interface=meridian.Interface(port=port, title=TITLE),
        reads_external_accounts=True,
    ) as plugin:
```

Then call the new function just after the plugin reports itself healthy:

```python title="src/holdings_demo/__main__.py"
        await plugin.report(healthy=True, detail="started")
        await record_demo_statement(plugin)
        await stopped.wait()
```

Save both files. The first terminal shows a new revision, or two if you saved the files far apart:

```text
r2 sent (2 files, 0 deleted)
r2 synced (2 sent, 0 deleted)
r2 restarted
r2 ready
```

The steps below assume one revision, `r2`. If you got two, `r2` and `r3`, add one to each
`--since` number below.

## 7. Check the result

```bash
meridian plugin logs --instance holdings-demo --since 1
```

Expected output:

```text
… INFO holdings_demo: registered as holdings-demo, roles custody
… INFO holdings_demo: may publish …; may subscribe …
… INFO holdings_demo: serving its page on 127.0.0.1:8000
… INFO holdings_demo: opened statement STMT-… (already recorded: False)
… INFO holdings_demo: recorded holding … (resolved: False)
```

What happened:

- The statement was opened and given an id by the deployment.
- The row was recorded against `Demo brokerage account`, which `DEMO-ACCT-1` is linked to.
- `resolved: False` because the deployment does not know an instrument for the symbol `ACME`. The
  row is kept as **unresolved**, with the identifier the plugin held. It updates no position, since
  there is none until the deployment knows what is held.
- One row arrived of one expected, so the street store closed the statement.

## 8. See the rules work

Change the external account in `statement.py` to one that is not linked:

```python title="src/holdings_demo/statement.py"
EXTERNAL_ACCOUNT = "DEMO-ACCT-2"
```

Save, wait for `ready`, and read the logs after that revision:

```bash
meridian plugin logs --instance holdings-demo --since 2
```

The last line now reads something like:

```text
… WARNING holdings_demo: not recorded: ReportSyncStatus: refused: external account DEMO-ACCT-2 is not linked to an account; a deployment admin links it (W6.4), and the next statement records it
```

Nothing was recorded for `DEMO-ACCT-2`. Once it is linked, from the plugin's own admin page, the
next statement records it. A row for an account outside the plugin's write scope is refused the
same way, and also shows as a `refused` event from `meridian plugin events`.

Put `DEMO-ACCT-1` back when you are done.

!!! tip "If a save still reports the old state"
    If a save made straight after you change a link or a permission still reports the old state,
    save again.

## 9. Clean up

Press Ctrl-C in the first terminal, then:

```bash
meridian plugin stop holdings-demo
```

The account, groups, permission and link stay. Close the account on the **Accounts** tab and
withdraw the permission on the **Permissions** tab if you do not want them.

## What you learned

- A plugin writes only through its role's typed operations, and only on accounts in its write
  scope.
- An external account must be linked to one of the firm's accounts before rows for it are accepted.
- A statement says how many rows follow; an unresolved row is recorded, never dropped.
- Refusals come back as `MeridianError` with the deployment's own reason.

## Next steps

- [Python SDK](../api/python-sdk.md) and [Typed operations](../api/typed-operations.md): every
  parameter of these calls.
- [Release a plugin version](../how-to/release-a-plugin.md): turn it into a version.
