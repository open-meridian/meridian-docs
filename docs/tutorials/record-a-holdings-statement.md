# Record a holdings statement

In this tutorial you build a small **custody** plugin. It records a holdings statement, one read of
one source at one moment, and a holding in it, against one of your firm's accounts. On the way you
set up everything a plugin needs before a deployment lets it write: a role, an account, and a link
from the source's name for that account to yours, made on a page the plugin serves under Manage.

!!! warning "What this tutorial cannot show yet"
    Read this first. The tutorial runs end to end, but three things are not built yet:

    - **You cannot read the result back.** No dashboard page lists statements or custodial positions
      yet, and the SDK's reads of them, `list_statements` and `list_custodial_positions`, are an
      `operations` plugin's, not a custody plugin's. You confirm the recording from the replies your
      plugin logs.
    - **The data is made up.** So that you need no broker account, this plugin calls no broker. It
      reports two invented accounts and records one invented holding.
    - **Nothing here trades.** Holdings are read-only records of what a custodian says you hold.
      Order routing and execution are not built.

Allow 30 minutes.

## What you need

- A deployment installed with `meridian up --development`, and you are a deployment admin on it.
  See [Install a deployment](../getting-started/installation.md).
- The `meridian` CLI, 0.1.24 or later, and Docker on this machine. From CLI 0.1.24,
  `meridian plugin new` builds on SDK 0.12.0 or later, 0.20.0 from CLI 0.1.35 and 0.21.0 from the release after it: its `meridian.Pages`, which this tutorial's page is
  built on, and a statement that names its external account, as this tutorial's does.
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
| W6.4 | `read_accounts_for_linking` | Reads the firm's accounts, their identities alone, for the admin viewing the plugin's page under Manage |
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
   account is refused.
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
… INFO holdings_demo: serving its pages on 127.0.0.1:8000
```

The `may publish` list is what the `custody` role grants.

Every save from now on is a new revision, `r2`, `r3` and on. To read what one logged, pass
`--since` the revision before it: for `r4`, `--since 3`.

## 4. Make an account to link to

Open the dashboard, sign in, and choose the gear at the top right, **Settings**. On the
**Accounts** tab, choose **+ Add**, name it `Demo brokerage account`, and choose **Create**.
See [Give people access](../how-to/administer-access.md) for more on the tab.

That is all the plugin needs from Settings. You do not group the account or grant a
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
CUSTODIAN = "Demo Securities"  # where the source says the accounts are held

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
The name and type are the source's own words, shown to the admin who links them, and so is the
custodian.

## 6. Serve an Accounts page

Linking is done on one of the plugin's own pages, at `admin`, because only the plugin knows what its
accounts are. A page at `admin` is shown and served under **Manage** alone, and shows no account's
data: the accounts' identities and links are configuration. Replace `src/holdings_demo/page.py`, the
scaffold's pages, with this one:

```python title="src/holdings_demo/page.py"
"""The plugin's Accounts page, under Manage: link each account the source
reaches to one of the deployment's accounts (W6.4)."""

from __future__ import annotations

from pathlib import Path

import meridian
from meridian.plugin.v1 import operations_pb2 as ops

from .source import ACCOUNTS as REPORTED
from .source import CUSTODIAN

TITLE = "Holdings demo"
ACCOUNTS = "/admin/accounts"

pages = meridian.Pages(TITLE, templates=Path(__file__).parent / "templates")


@pages.page(ACCOUNTS, "Accounts", levels="admin")
async def accounts(request: meridian.Request) -> str:
    return await show(request)


@pages.route(ACCOUNTS, levels="admin", methods=["POST"])
async def link(request: meridian.Request) -> str:
    caller, form = request.caller, request.form
    external = form.get("external_account_id", "")
    account_id = form.get("account_id", "")
    # Only a deployment admin names a new account; the sidecar refuses anybody else.
    new_name = form.get("new_account_name", "") if caller.deployment_admin else ""
    if not (account_id or new_name):  # neither would remove the link
        return await show(request, "Choose an account, or name a new one.", bad=True)
    try:
        # Sent for the admin: the sidecar checks this is a Manage session,
        # and that this plugin reported the account.
        await request.plugin.link_external_account(
            external_account_id=external,
            account_id=account_id,
            new_account_name="" if account_id else new_name,
            # Pre-filled from the source, and ignored with no new name.
            new_account_custodian=form.get("new_account_custodian", ""),
            new_account_type=form.get("new_account_type", ""),
            acting_for=caller.header,
        )
    except meridian.MeridianError as refused:
        return await show(request, f"Refused: {refused}", bad=True)
    return await show(request, f"Linked {external}.")


async def show(request: meridian.Request, notice: str = "", bad: bool = False) -> str:
    try:
        # The deployment's accounts, their identities alone, read for the admin.
        read = await request.plugin.read_accounts_for_linking(acting_for=request.caller.header)
        offered = [a for a in read.accounts if a.state != ops.ACCOUNT_STATE_CLOSED]
    except meridian.MeridianError as failed:
        offered, notice, bad = [], f"Refused: {failed}", True
    return pages.render(
        "link.html",
        reported=REPORTED,
        offered=offered,
        custodian=CUSTODIAN,
        notice=notice,
        tone="bad" if bad else "good",
    )
```

And give it its template, in the scaffold's `templates/` directory:

```html+jinja title="src/holdings_demo/templates/link.html"
{% extends "meridian/base.html" %}
{% block content %}
<p class="muted">Link each account the source reaches to one of yours.</p>
{% if notice %}
<div class="notice {{ tone }}" role="status">{{ notice }}</div>
{% endif %}
<section class="panel">
  <table>
    <thead><tr>
      <th>At the source</th><th>Link to an existing account</th>
      {% if caller.deployment_admin %}<th>Or to a new one</th>{% endif %}
    </tr></thead>
    <tbody>
    {% for a in reported %}
      <tr>
        <td><code>{{ a.external_account_id }}</code><br>{{ a.name }}</td>
        <td>
          <form method="post" action="/admin/accounts" class="inline">{{ csrf_input }}
            <input type="hidden" name="external_account_id" value="{{ a.external_account_id }}">
            <select name="account_id" required aria-label="Account">
              <option value="">Choose an account</option>
              {% for o in offered %}<option value="{{ o.account_id }}">{{ o.name }}</option>{% endfor %}
            </select>
            <button>Link</button>
          </form>
        </td>
        {% if caller.deployment_admin %}
        <td>
          <form method="post" action="/admin/accounts" class="inline">{{ csrf_input }}
            <input type="hidden" name="external_account_id" value="{{ a.external_account_id }}">
            <input name="new_account_name" value="{{ a.name }}" required aria-label="Name">
            <input name="new_account_custodian" value="{{ custodian }}" aria-label="Custodian">
            <input name="new_account_type" value="{{ a.venue_account_type }}" aria-label="Type">
            <button class="primary">Create and link</button>
          </form>
        </td>
        {% endif %}
      </tr>
    {% endfor %}
    </tbody>
  </table>
</section>
{% endblock %}
```

The scaffold's own templates, `setup.html` and `accounts.html`, are no longer used. Remove them:

```bash
rm src/holdings_demo/templates/setup.html src/holdings_demo/templates/accounts.html
```

What it does:

- **It declares one page, at `admin`**: `@pages.page(ACCOUNTS, "Accounts", levels="admin")`. The
  dashboard shows it as a tab of the plugin's area under **Manage**, and `Pages` answers 403 to a
  session at any other level before the view runs. Its form posts to the same path, declared with
  `@pages.route` at `admin` too.
- **It reads the firm's accounts, and sends each link, acting for the admin**: `acting_for` is their
  header, handed back. The sidecar admits both only in a session opened by Manage, answers the
  accounts' identities alone, and admits a link only for an account this plugin reported.
- **Each link names an existing account or a new account's name.** A new one is created and linked
  in one step, with the custodian and type the source reported, which the admin may change first.
  Only a deployment admin may name a new account, so the page offers that column to one alone,
  as `caller.deployment_admin` says, and the sidecar refuses one from anybody else. A link naming
  neither removes it, so the page refuses an empty form rather than send one.
- **Every form carries the page's CSRF token**, `{{ csrf_input }}`. The plugin's page has its own
  sign-in cookie, so without the token a page elsewhere could make an admin's browser post the
  form; `Pages` refuses a form without it before the view runs. Each save restarts the process with
  a new secret, so reload the page before linking after a save.
- **It is built on the plugin UI kit**: the template extends the kit's base template,
  `meridian/base.html`, which links the kit and draws the heading, and the page uses the kit's
  classes and no colour of its own. See the plugin's `AGENTS.md`.

This page keeps to plain forms, so that every step is in view, and it does not say which accounts
are linked.

!!! note "What a real page does instead"
    From SDK 0.7.0 a plugin reads its own links, `AccountScope.links` from `account_scope()`: each
    external account it links, the account it is linked to, and that account's name, at start and
    on every change. The kit's `om-account-map` draws each external account as linked or not, from
    those links, with the link, create and unlink forms, and needs no script; from kit 0.5.0 it
    searches, filters, groups and pages thousands of accounts, and suggests matches. See
    [Build a plugin's page](../how-to/build-a-plugin-page.md#to-link-external-accounts-om-account-map).

!!! note "The scaffold's tests"
    `meridian plugin new` also wrote `tests/test_page.py`, which tests the scaffold's pages. This page
    replaces them, so those tests now fail under `meridian plugin check --run-tests` and the
    scaffold's CI workflow. Nothing in this tutorial runs them. Replace them as you replace the
    pages, as the file itself says, with `meridian.testing.PageClient`: at least the page under
    each level, and `assert_no_account_data` under Manage. See
    [`meridian.testing`](../api/python-sdk.md#testing).

## 7. Declare that it reads external accounts, and report them on start

Open `src/holdings_demo/__main__.py`. The scaffold already declares its pages, with
`Interface(..., pages=pages)`, and serves them with `pages.serve`, so the new page is declared and
served as it is. Import the new function next to the page import:

```python title="src/holdings_demo/__main__.py"
from .page import TITLE, pages
from .source import report_accounts
```

Declare that the plugin names accounts by a source's identifiers, which an admin links. Change the
`connect` call to:

```python title="src/holdings_demo/__main__.py"
    async with await meridian.connect(
        interface=meridian.Interface(port=port, title=TITLE, pages=pages),
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
last one, then read what it logged. If it was `r6`:

```bash
meridian plugin logs --instance holdings-demo --since 5
```

```text
… INFO holdings_demo: registered as holdings-demo, roles custody
… INFO holdings_demo: may publish …; may subscribe …
… INFO holdings_demo: serving its pages on 127.0.0.1:8000
… INFO holdings_demo: reported DEMO-ACCT-1, DEMO-ACCT-2
```

## 8. Link DEMO-ACCT-1

On the dashboard's home, `holdings-demo` is listed with **Manage**: as a deployment admin you are an
admin of every plugin, through **All plugins (admin)**. Choose **Manage**. The plugin's area opens
on its **Summary**; open the tab after **Summary** and **Settings**, its one page at `admin`,
**Accounts**, the page you wrote. See
[Manage, Open and View](../concepts/plugins.md#manage-open-and-view).

It lists `DEMO-ACCT-1` and `DEMO-ACCT-2`. On the `DEMO-ACCT-1` row, under **Link to an existing
account**, choose `Demo brokerage account`, then **Link**. The page says:

```text
Linked DEMO-ACCT-1.
```

Leave `DEMO-ACCT-2` unlinked for now.

If the page says `This form has expired or did not come from this plugin's page`, the plugin
restarted since you opened it: reload it and link again. If it says `Refused:`, the reason is the
sidecar's own.

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

from .source import CUSTODIAN, SOURCE

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

        # W3.1: which instrument this identifier means. When nothing matches,
        # the deployment answers its placeholder for it; only an ambiguous
        # match is a miss.
        symbol = meridian.Identifier(scheme="symbol", value="ACME", source=SOURCE)
        resolved = await plugin.resolve_identifier(identifiers=[symbol], as_of_ns=now)
        if resolved.found:
            log.info(
                "ACME is %s (placeholder: %s)", resolved.instrument_id, resolved.placeholder
            )

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

        # W2.3: one row. Resolved, it names the instrument or the placeholder.
        # Ambiguous, it carries what we held, and is recorded rather than
        # dropped.
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

## 10. Call it on start

Open `src/holdings_demo/__main__.py` again. Import the new function:

```python title="src/holdings_demo/__main__.py"
from .page import TITLE, pages
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

Read what the last revision logged. If it was `r8`:

```bash
meridian plugin logs --instance holdings-demo --since 7
```

Expected output:

```text
… INFO holdings_demo: registered as holdings-demo, roles custody
… INFO holdings_demo: may publish …; may subscribe …
… INFO holdings_demo: serving its pages on 127.0.0.1:8000
… INFO holdings_demo: reported DEMO-ACCT-1, DEMO-ACCT-2
… INFO holdings_demo: ACME is LCL-… (placeholder: True)
… INFO holdings_demo: opened statement STMT-… (already recorded: False)
… INFO holdings_demo: recorded holding HLD-… (resolved: True)
```

What happened:

- The statement was opened against `Demo brokerage account`, which `DEMO-ACCT-1` is linked to, and
  given an id by the deployment.
- The row was recorded against the same account.
- The deployment knows no instrument for the symbol `ACME`, so it answered its **placeholder** for
  it: an identifier beginning `LCL-`, made the first time anyone asked about `ACME` from this source
  and answered every time after. The deployment reports the miss to the platform itself; the plugin
  has nothing more to do.
- `resolved: True` because the row names an instrument, the placeholder, and so it updates a
  custodial position under it. When the platform's `INS-` identifier replaces the placeholder, the
  position moves onto it.
- Had more than one instrument matched `ACME`, the answer would have been a miss, not a pick. The
  row would then carry the identifier it held instead, be recorded as unresolved, with
  `resolved: False`, and update no position. See
  [`resolve_identifier`](../api/typed-operations.md#resolve_identifier).
- One row arrived of one expected, so the street store closed the statement.

## 12. See the rules work

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
    The words are for you, reading the log, and may change at any release: don't match them. From
    SDK 0.7.0 this refusal raises `meridian.NotLinked`, chosen by a code the sidecar sends with it,
    so a plugin can catch that alone and offer the account for linking. It is a `CallFailed`, so the
    `except meridian.MeridianError` above still catches it. See
    [An unlinked external account](../api/typed-operations.md#an-unlinked-external-account).

Now link it the other way. Reload the plugin's **Accounts** tab, under Manage. On the `DEMO-ACCT-2`
row, keep the name `Demo retirement`, the custodian `Demo Securities` and the type `IRA` under **Or
to a new one**, and choose **Create and link**. The column is there because you are a deployment
admin; a plugin admin who is not one links to existing accounts only. The deployment creates the account and links it in one step.
The **Accounts** tab of Settings shows it with that custodian and type.

Linking `DEMO-ACCT-2` to `Demo brokerage account` instead is refused: that account has
`DEMO-ACCT-1` linked already, and an account has one external account. Two external accounts at
one custodian are two accounts, each with its own statements. See
[Accounts](../concepts/accounts.md#external-accounts).

The next statement records it. Make any change to `statement.py`, a blank line will do, save, and
read the logs after that revision: the last line is `recorded holding …` again.

A statement or a row for a closed account is refused too, as outside the plugin's write scope,
and that refusal also shows as a `refused` event from `meridian plugin events`.

!!! tip "If a save still reports the old state"
    If a save made straight after you make a link still reports the old state, save again.

## 13. Clean up

Press Ctrl-C in the first terminal, then:

```bash
meridian plugin stop holdings-demo
```

The accounts and the links stay. Close the accounts on the **Accounts** tab of Settings if you
do not want them. This page offers no way to remove a link: a page does it by sending
`link_external_account` naming neither account.

## What you learned

- A plugin writes only through its role's typed operations, and only on accounts in its write
  scope.
- A custody plugin reports the accounts its source reaches, and links them on its own page at
  `admin`, acting for the admin viewing it under Manage. The page is declared at `admin`, so it is
  served under Manage alone, shows no account's data, and each form carries the page's CSRF token.
- An external account must be linked to one of the firm's accounts before a statement or rows for
  it are accepted, and the link is the plugin's right to write that account. An account has one
  external account.
- A statement names its external account, states its figures per margin segment as the source
  reported them, and says how many rows follow. An instrument nobody knows is answered with the
  deployment's placeholder, and an ambiguous one is recorded unresolved; a row is never dropped.
- Refusals come back as `MeridianError` with the deployment's own reason.

## Next steps

- [Python SDK](../api/python-sdk.md) and [Typed operations](../api/typed-operations.md): every
  parameter of these calls.
- [Prove your plugin against a released runtime](../how-to/prove-a-plugin-against-a-released-runtime.md):
  link an account through this page and compare the street store with what you expect, in CI.
- [Release a plugin version](../how-to/release-a-plugin.md): turn it into a version.
