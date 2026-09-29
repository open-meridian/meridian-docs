# Record a holdings statement

In this tutorial you build a small **custody** plugin. It records a holdings statement, one read of
one source at one moment, and a holding in it, against one of your firm's accounts. On the way you
set up everything a plugin needs before a deployment lets it write: a role, an account, and a link
from the source's name for that account to yours, made on an admin page the plugin serves.

!!! warning "What this tutorial cannot show yet"
    Read this first. The tutorial runs end to end, but three things are not built yet:

    - **You cannot read the result back.** No dashboard page and no SDK operation lists statements or
      custodial positions yet. You confirm the recording from the replies your plugin logs.
    - **The data is made up.** So that you need no broker account, this plugin calls no broker. It
      reports two invented accounts and records one invented holding.
    - **Nothing here trades.** Holdings are read-only records of what a custodian says you hold.
      Order routing and execution are not built.

Allow 30 minutes.

## What you need

- A deployment installed with `meridian up --development`, and you are a deployment admin on it.
  See [Install a deployment](../getting-started/installation.md).
- The `meridian` CLI, 0.1.14 or later, so that `meridian plugin new` builds on SDK 0.6, and Docker
  on this machine.
- To have done [Change your plugin's page, live](change-the-page-live.md), or be comfortable with
  `meridian plugin dev`.

The examples use `http://meridian.localhost`, the deployment on this machine. For another, give
its address to `meridian connect`.

## How it fits together

A custody plugin follows workflow W2, holdings ingestion, and links its accounts by W6.4. It uses
seven of the SDK's [typed operations](../api/typed-operations.md), all granted by the `custody`
role:

| Step | SDK call | What it does |
|---|---|---|
| W2.8 | `report_external_accounts` | Says which accounts the source reaches, as the source names them |
| W6.4 | `read_accounts_for_linking` | Reads the firm's accounts, for a deployment admin on the plugin's page |
| W6.4 | `link_external_account` | Links one of the source's accounts to one of the firm's, for that admin |
| W2.1 | `report_sync_status` | Says how fresh the source's data is for one external account |
| W3.1 | `resolve_identifier` | Asks which instrument an identifier means |
| W2.2 | `record_holdings_statement` | Opens one statement and says how many rows will follow |
| W2.3 | `record_holding` | Records one row: one account, one instrument, a side, a quantity and a value |

The deployment's street store closes the statement when as many rows have arrived as it said would
follow.

Two rules decide whether a row is accepted:

1. **The external account must be linked.** The plugin names an account as the source knows it. A
   deployment admin links that to one of the firm's accounts, on an admin page the plugin serves,
   and the plugin sends the link acting for them. A row for an unlinked account is refused.
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
cannot choose its own. See [Plugins, roles and grants](../concepts/plugins.md).

## 3. Launch it live

The plugin must be running, and must have reported its accounts, before an admin can link them. In
your first terminal:

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

Every save from now on is a new revision, `r2`, `r3` and on. To read what one logged, pass
`--since` the revision before it: for `r4`, `--since 3`.

## 4. Make an account to link to

Open the dashboard, sign in, and choose **Admin** at the top right. On the **Accounts** tab, choose
**New account**, name it `Demo brokerage account`, and choose **Create**. See
[Give people access](../how-to/administer-access.md) for more on the tab.

That is all the plugin needs from the Admin portal. You do not group the account or grant a
permission on it: the link you make in step 8 is the plugin's right to write it.

## 5. Report the source's accounts

A custody plugin says which accounts its source reaches before it records anything for them (W2.8).
Only an account it reported can be linked. Create a new file:

```python title="src/holdings_demo/source.py"
"""A made-up source: the accounts it reaches, as a broker would name them."""

from __future__ import annotations

import logging

import meridian

log = logging.getLogger("holdings_demo")

SOURCE = "demo"  # the source's name, like "snaptrade"

# Every account the source reaches: its own identifier, name and type for each.
ACCOUNTS = (
    meridian.ExternalAccount(
        external_account_id="DEMO-ACCT-1", name="Demo brokerage", venue_account_type="Individual"
    ),
    meridian.ExternalAccount(
        external_account_id="DEMO-ACCT-2", name="Demo retirement", venue_account_type="IRA"
    ),
)


async def report_accounts(plugin: meridian.Plugin) -> None:
    # W2.8: before recording anything, say which accounts the source reaches.
    await plugin.report_external_accounts(accounts=ACCOUNTS)
    log.info("reported %s", ", ".join(a.external_account_id for a in ACCOUNTS))
```

`DEMO-ACCT-1` and `DEMO-ACCT-2` are the names the source uses for the accounts, as a broker would.
The name and type are the source's own words, shown to the admin who links them.

## 6. Serve an Accounts page

Linking is done on the plugin's own admin page, because only the plugin knows what its accounts
are. Replace `src/holdings_demo/page.py`, the scaffold's page, with this one:

```python title="src/holdings_demo/page.py"
"""The plugin's Accounts page, for deployment admins only: link each account
the source reaches to one of the deployment's accounts (W6.4)."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import html
import http.server
import secrets
import threading
from collections.abc import Sequence
from typing import Any
from urllib.parse import parse_qs

import meridian
from meridian.plugin.v1 import operations_pb2 as ops

from .source import ACCOUNTS as REPORTED

TITLE = "Holdings demo"
KIT = "/.meridian/ui/0.1.0/"  # the plugin UI kit, which the dashboard serves
ACCOUNTS = "/admin/accounts"
ADMIN_PAGES = (meridian.Page(ACCOUNTS, "Accounts"),)

# A secret only this process knows, for the forms' tokens.
_SECRET = secrets.token_bytes(32)


def form_token(caller: meridian.Caller) -> str:
    return hmac.new(_SECRET, caller.subject.encode(), hashlib.sha256).hexdigest()


def render(
    caller: meridian.Caller,
    offered: Sequence[ops.AccountRecord],
    notice: str = "",
    bad: bool = False,
) -> str:
    e = html.escape
    choices = "".join(
        f'<option value="{e(a.account_id)}">{e(a.name)}</option>'
        for a in offered
        if a.state != ops.ACCOUNT_STATE_CLOSED
    )
    hidden = f'<input type="hidden" name="token" value="{form_token(caller)}">'
    rows = "".join(
        f"<tr><td><code>{e(a.external_account_id)}</code><br>{e(a.name)}</td><td>"
        f'<form method="post" action="{ACCOUNTS}" class="inline">{hidden}'
        f'<input type="hidden" name="external_account_id" value="{e(a.external_account_id)}">'
        f'<select name="account_id" required><option value="">Choose an account</option>'
        f"{choices}</select> <button>Link</button></form></td><td>"
        f'<form method="post" action="{ACCOUNTS}" class="inline">{hidden}'
        f'<input type="hidden" name="external_account_id" value="{e(a.external_account_id)}">'
        f'<input name="new_account_name" value="{e(a.name)}" required> '
        '<button class="primary">Create and link</button></form></td></tr>'
        for a in REPORTED
    )
    tone = "bad" if bad else "good"
    said = f'<div class="notice {tone}" role="status">{e(notice)}</div>' if notice else ""
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>Accounts</title><link rel="stylesheet" href="{KIT}meridian.css">'
        f'<script src="{KIT}meridian.js"></script></head><body><main class="page">'
        '<header class="page-head"><div><h1>Accounts</h1>'
        "<p>Link each account the source reaches to one of yours.</p></div></header>"
        f'{said}<section class="panel"><table><thead><tr><th>At the source</th>'
        "<th>Link to an existing account</th><th>Or to a new one</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></section></main></body></html>"
    )


def serve(plugin: meridian.Plugin, loop: asyncio.AbstractEventLoop, port: int) -> Any:
    """Serve the page on 127.0.0.1:`port`, in a thread; operations run on `loop`."""

    def on_loop(work: Any) -> Any:
        return asyncio.run_coroutine_threadsafe(work, loop).result(timeout=15)

    class Page(http.server.BaseHTTPRequestHandler):
        def _admin(self) -> meridian.Caller | None:
            """The caller, when this is the Accounts page and they are a deployment admin."""
            presented = self.headers.get_all("Meridian-Caller") or []
            caller = meridian.Caller.from_header(presented[0]) if len(presented) == 1 else None
            if self.path.partition("?")[0] != ACCOUNTS:
                self._send(404, "No such page.")
            elif caller is None or not caller.deployment_admin:
                self._send(403, "This page is for deployment admins.")
            else:
                return caller
            return None

        def _send(self, status: int, body: str) -> None:
            data = body.encode()
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _show(self, caller: meridian.Caller, notice: str = "", bad: bool = False) -> None:
            try:
                # The deployment's accounts, read for the admin viewing the page.
                read = on_loop(plugin.read_accounts_for_linking(acting_for=caller.header))
                offered = read.accounts
            except meridian.MeridianError as failed:
                offered, notice, bad = [], f"Refused: {failed}", True
            self._send(200, render(caller, offered, notice, bad))

        def do_GET(self) -> None:  # noqa: N802
            caller = self._admin()
            if caller is not None:
                self._show(caller)

        def do_POST(self) -> None:  # noqa: N802
            body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
            form = {name: values[0] for name, values in parse_qs(body.decode()).items()}
            caller = self._admin()
            if caller is None:
                return
            token = form.get("token", "").encode()
            if not hmac.compare_digest(token, form_token(caller).encode()):
                self._send(403, "This form is out of date. Reload the page.")
                return
            external = form.get("external_account_id", "")
            account_id = form.get("account_id", "")
            new_name = form.get("new_account_name", "")
            if not (account_id or new_name):  # neither would remove the link
                self._show(caller, "Choose an account, or name a new one.", bad=True)
                return
            try:
                # Sent for the admin: the sidecar checks they are a deployment
                # admin, and that this plugin reported the account.
                on_loop(
                    plugin.link_external_account(
                        external_account_id=external,
                        account_id=account_id,
                        new_account_name="" if account_id else new_name,
                        acting_for=caller.header,
                    )
                )
                self._show(caller, f"Linked {external}.")
            except meridian.MeridianError as refused:
                self._show(caller, f"Refused: {refused}", bad=True)

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), Page)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server
```

What it does:

- **It declares one admin page**, `ADMIN_PAGES`. The dashboard shows it as a tab in the plugin's
  admin view, and frames its path.
- **It serves it only to a deployment admin**, whose verified `Meridian-Caller` header says
  `deployment_admin`. Anybody else gets 403, and any other path 404, so the plugin no longer has a
  page for other people.
- **It reads the firm's accounts, and sends each link, acting for the admin**: `acting_for` is their
  header, handed back. The sidecar admits both only for a deployment admin, and a link only for an
  account this plugin reported.
- **Each link names an existing account or a new account's name.** A new one is created and linked
  in one step. A link naming neither removes it, so the page refuses an empty form rather than send
  one.
- **Every form carries a token**, made from the admin's identity and a secret only this process
  holds. The plugin's page has its own sign-in cookie, so without the token a page elsewhere could
  make an admin's browser post the form. Each save restarts the process with a new secret, so reload
  the page before linking after a save.
- **It is built on the plugin UI kit**, as the scaffold's page was: the kit's stylesheet, script and
  classes, and no colour of its own. See the plugin's `AGENTS.md`.

A plugin cannot read back what its accounts are linked to, so the page does not say which are
linked.

!!! note "A new account's custodian and type"
    From SDK 0.6.1, `link_external_account` also takes `new_account_custodian`, `new_account_type`,
    `new_account_owner` and `new_account_note`, which a real page pre-fills from what the source
    reported, for the admin to change. The scaffold from `meridian plugin new` 0.1.14 pins SDK
    0.6.0, so this page leaves them out. A dependency is part of a version: it changes with a new
    version, not with a save.

## 7. Declare the page and report on start

Open `src/holdings_demo/__main__.py`. Import the new names next to the page import:

```python title="src/holdings_demo/__main__.py"
from .page import ADMIN_PAGES, TITLE, serve
from .source import report_accounts
```

Declare the admin page, and that the plugin names accounts by a source's identifiers, which an
admin links. Change the `connect` call to:

```python title="src/holdings_demo/__main__.py"
    async with await meridian.connect(
        interface=meridian.Interface(port=port, title=TITLE, admin_pages=ADMIN_PAGES),
        reads_external_accounts=True,
    ) as plugin:
```

Then report the accounts just after the plugin reports itself healthy:

```python title="src/holdings_demo/__main__.py"
        await plugin.report(healthy=True, detail="started")
        await report_accounts(plugin)
        await stopped.wait()
```

Save. The first terminal shows a new revision for each file you saved. Wait for `ready` on the
last one, then read what it logged. If it was `r4`:

```bash
meridian plugin logs --instance holdings-demo --since 3
```

```text
… INFO holdings_demo: registered as holdings-demo, roles custody
… INFO holdings_demo: may publish …; may subscribe …
… INFO holdings_demo: serving its page on 127.0.0.1:8000
… INFO holdings_demo: reported DEMO-ACCT-1, DEMO-ACCT-2
```

## 8. Link DEMO-ACCT-1

In the dashboard, choose **Admin**, open the **Plugins** tab, and choose `holdings-demo`. Its view
has the tabs every plugin has, **Overview**, **Settings** and **Access**, then the plugin's own:
**Accounts**, the page you wrote. Open it.

It lists `DEMO-ACCT-1` and `DEMO-ACCT-2`. On the `DEMO-ACCT-1` row, under **Link to an existing
account**, choose `Demo brokerage account`, then **Link**. The page says:

```text
Linked DEMO-ACCT-1.
```

Leave `DEMO-ACCT-2` unlinked for now.

If the page says `This form is out of date`, the plugin restarted since you opened it: reload it and
link again. If it says `Refused:`, the reason is the sidecar's own.

## 9. Write the recording code

Create a new file:

```python title="src/holdings_demo/statement.py"
"""Record one made-up holdings statement, the way a custody plugin would."""

from __future__ import annotations

import logging
import time
import uuid
from decimal import Decimal

import meridian

from .source import SOURCE

log = logging.getLogger("holdings_demo")

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

!!! note "Why a fresh statement id each run"
    Each save restarts the plugin, so this records a new statement each time. A real connector uses
    the source's own statement id, so a statement delivered twice comes back with
    `already_recorded` set, instead of being recorded twice.

## 10. Call it on start

Open `src/holdings_demo/__main__.py` again. Import the new function:

```python title="src/holdings_demo/__main__.py"
from .page import ADMIN_PAGES, TITLE, serve
from .source import report_accounts
from .statement import record_demo_statement
```

Then record the statement just after reporting the accounts:

```python title="src/holdings_demo/__main__.py"
        await plugin.report(healthy=True, detail="started")
        await report_accounts(plugin)
        await record_demo_statement(plugin)
        await stopped.wait()
```

Save, and wait for `ready` on the last revision.

## 11. Check the result

Read what the last revision logged. If it was `r6`:

```bash
meridian plugin logs --instance holdings-demo --since 5
```

Expected output:

```text
… INFO holdings_demo: registered as holdings-demo, roles custody
… INFO holdings_demo: may publish …; may subscribe …
… INFO holdings_demo: serving its page on 127.0.0.1:8000
… INFO holdings_demo: reported DEMO-ACCT-1, DEMO-ACCT-2
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

## 12. See the rules work

Change the external account in `statement.py` to the one you left unlinked:

```python title="src/holdings_demo/statement.py"
EXTERNAL_ACCOUNT = "DEMO-ACCT-2"
```

Save, wait for `ready`, and read the logs after that revision. The last line now reads:

```text
… WARNING holdings_demo: not recorded: RecordHolding: refused: external account DEMO-ACCT-2 is not linked to an account; a deployment admin links it on the plugin's admin page (W6.4), and the next statement records it
```

The statement opened, but its one row was refused, so nothing is recorded for `DEMO-ACCT-2`. The
sync status before it was not refused: the dashboard shows it beside the unlinked account, so an
admin can tell whether it is worth linking.

Now link it the other way. Reload the plugin's **Accounts** tab. On the `DEMO-ACCT-2` row, keep the
name `Demo retirement` under **Or to a new one**, and choose **Create and link**. The deployment
creates the account and links it in one step.

The next statement records it. Make any change to `statement.py`, a blank line will do, save, and
read the logs after that revision: the last line is `recorded holding …` again.

A row for a closed account is refused too, as outside the plugin's write scope, and that refusal
also shows as a `refused` event from `meridian plugin events`.

!!! tip "If a save still reports the old state"
    If a save made straight after you make a link still reports the old state, save again.

## 13. Clean up

Press Ctrl-C in the first terminal, then:

```bash
meridian plugin stop holdings-demo
```

The accounts and the links stay. Close the accounts on the Admin portal's **Accounts** tab if you
do not want them. This page offers no way to remove a link: a page does it by sending
`link_external_account` naming neither account.

## What you learned

- A plugin writes only through its role's typed operations, and only on accounts in its write
  scope.
- A custody plugin reports the accounts its source reaches, and links them on its own admin page,
  acting for the deployment admin viewing it. The page is served to deployment admins only, and
  each form carries a token.
- An external account must be linked to one of the firm's accounts before rows for it are accepted,
  and the link is the plugin's right to write that account.
- A statement says how many rows follow; an unresolved row is recorded, never dropped.
- Refusals come back as `MeridianError` with the deployment's own reason.

## Next steps

- [Python SDK](../api/python-sdk.md) and [Typed operations](../api/typed-operations.md): every
  parameter of these calls.
- [Release a plugin version](../how-to/release-a-plugin.md): turn it into a version.
