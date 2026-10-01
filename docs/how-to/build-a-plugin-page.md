# Build a plugin's page

A plugin's page is built on the **plugin UI kit**, which the dashboard serves on the plugin's own
host. Linking it gives the page the platform's look, each person's colour scheme and market-direction
convention, and web components for what trading pages need. This guide covers declaring a plugin's
pages with the levels they serve, linking the kit, which version answers, linking external accounts
with `om-account-map` (at thousands of accounts too), grids that read well on a phone, and how a
page behaves inside the dashboard's frame, header actions and status included.

The kit is framework-free: CSS and custom elements, used the same way from plain HTML, React, Vue
or Svelte, from a plugin in any language. Every class, component, attribute and event is listed in
the kit's own reference, the
[meridian-ui README](https://github.com/open-meridian/meridian-ui#readme). The page
`meridian plugin new` writes is already built on it.

## To declare a page and the levels it serves

A plugin's pages are one list, each a path, a title and the levels it serves: `admin`, `write` or
`read`, one or several. A person opens the plugin by the dashboard's **Manage** (`admin`), **Open**
(`write`) or **View** (`read`), and the plugin's area shows, in one tab row, the pages whose levels
include the session's. See [Manage, Open and View](../concepts/plugins.md#manage-open-and-view).

Decide each page's levels by what it shows:

- **Configuration is a page at `admin`**: connections, account links, setup. Under Manage the
  session holds no account's data, so such a page shows none of what the plugin holds for an
  account, no holdings, rows or balances; external identities and links are configuration.
- **Daily work is a page at `write` and `read`**, one path for both. It shows every account the
  person may read (`caller.read`), and offers actions only under Open (`level == "write"`), on the
  accounts in `caller.write`.

In Python, from SDK 0.10.0, a page is a view function and a template, declared where the view is
with [`meridian.Pages`](../api/python-sdk.md#pages):

```python title="src/my_plugin/page.py"
from pathlib import Path

import meridian

pages = meridian.Pages("Holdings", templates=Path(__file__).parent / "templates")


@pages.page("/admin/accounts", "Account links", levels="admin")
async def account_links(request: meridian.Request) -> str:
    return pages.render("links.html", ...)  # identities and links, no account's data


@pages.page("/", "Statements", levels=["write", "read"])
async def statements(request: meridian.Request) -> str:
    rows = [...]  # every account in request.caller.read
    return pages.render("statements.html", rows=rows)


@pages.route("/refresh", levels="write", methods=["POST"])
async def refresh(request: meridian.Request) -> str: ...
```

`Pages` sends the list when the plugin registers (`Interface(pages=pages)`), and answers 403 to a
session at any other level before the view runs. Each template extends the kit's base template:

```html+jinja title="src/my_plugin/templates/statements.html"
{% extends "meridian/base.html" %}
{% block status %}<om-status data-om-header state="ok" label="Read"></om-status>{% endblock %}
{% block head_actions %}{% if level == "write" %}
  <form class="inline" method="post" action="/refresh">{{ csrf_input }}<button data-om-action="refresh">Refresh</button></form>
{% endif %}{% endblock %}
{% block content %}
  <om-grid row-key="id"><script type="application/json">{{ grid | tojson }}</script></om-grid>
{% endblock %}
```

`meridian/base.html` links the kit and draws the page's heading and tab row, which the kit drops when
the dashboard frames the page. Its blocks are `title`, `status`, `head_actions` and `content`, and
`caller` and `level` are always in the template's context. Every request but GET and HEAD must carry
the page's CSRF token, `{{ csrf_input }}` in a form or the `X-CSRF-Token` header from a script, or
it is refused before the view runs. See the [Python SDK](../api/python-sdk.md#templates).

Test each page under each level with `meridian.testing.PageClient`: `every_page()` renders each
under Manage, Open and View, and `assert_no_account_data(*held)`, given the account data the test
put in the plugin (holdings, quantities, values, balances), fails when a page at `admin` shows any of
it. An account's identity is not looked for, since a Manage page may list every account as a link
target. See [`meridian.testing`](../api/python-sdk.md#testing).

A plugin that serves its pages some other way, on an ASGI framework of its own, declares each as
`meridian.Page(path, title, levels=[...])` in `Interface(pages=...)`, and checks the session's level
itself with `page.serves(caller)`.

## To link the kit

The dashboard serves the kit at `/.meridian/ui/<version>/` on every plugin host, so it is on the
page's own origin. A page extending `meridian/base.html` links it already. Otherwise, link its
stylesheet and script in `<head>`, and draw the page inside `<main class="page">`:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Accounts</title>
  <link rel="stylesheet" href="/.meridian/ui/0.7.0/meridian.css">
  <script src="/.meridian/ui/0.7.0/meridian.js"></script>
</head>
<body>
  <main class="page">
    <header class="page-head">
      <div><h1>Accounts</h1><p>Link each account the source reaches to one of yours.</p></div>
    </header>
    <section class="panel padded">…</section>
  </main>
</body>
</html>
```

Three rules hold for every page, and `meridian plugin check` checks them (see the
[command line](../api/cli.md)):

- **Link the kit; never copy it.** A page that holds its own `meridian.css` misses every change to
  the brand.
- **Never a raw colour.** Every colour is a scheme property, such as `var(--ink)`, `var(--accent)`
  or `var(--buy)`. The person chooses the scheme and the mode, and a hex or a colour name is one no
  scheme can change and no contrast check has seen.
- **Nothing from another origin.** The kit's components reach only the page's own origin, and so
  does the page. The plugin's server proxies anything further.

The theme needs no code. The dashboard hands the page the person's scheme, mode and
market-direction convention, and the kit applies them.

## Kit versions

| Version | What it added |
|---|---|
| 0.1.0 | The brand's tokens and colour schemes, the platform's CSS classes, and `om-grid` (with its high-rate mode), `om-chart`, `om-asof`, `om-instrument-picker`, `om-live` and `om-panels` |
| 0.2.0 | The seamless frame: a page the dashboard frames drops its own heading and tab row, and the frame is sized to the page. See [Inside the dashboard's frame](#inside-the-dashboards-frame). |
| 0.3.0 | `om-account-map`; `om-moment`; the grid's declared JSON, rich cells and narrow layouts; list rows that wrap; option and field-row styles, and a select as tall as an input |
| 0.4.0 | Header actions: a framed page's head buttons, drawn by the dashboard in its own header. See [Header actions](#header-actions). |
| 0.5.0 | `om-account-map` at scale: a dense table with search, filters, grouping, pages, a chooser found by typing, suggestions, and several links in one form (`link-several`). See [At thousands of accounts](#at-thousands-of-accounts). |
| 0.6.0 | `om-status`, a status dot with its note on hover, focus or a tap; and in `om-account-map`, each account's optional `status` and `values`, a Status column and a filter by state |
| 0.7.0 | Header status: a framed page's head `om-status` marked `data-om-header`, drawn by the dashboard beside the plugin's name. See [Header status](#header-status). |

**A 0.x release only adds.** Nothing in the kit is removed or renamed within 0.x, so a page built
against an earlier 0.x keeps working on a later one.

**The dashboard serves the newest 0.x kit to any 0.x request.** A page that links
`/.meridian/ui/0.1.0/` is answered with the newest 0.x kit the deployment carries, not with 0.1.0,
and not with nothing. So the version in a page's path says what it was built against, and the
deployment decides what it gets: a brand change reaches every page at once, and no plugin is
rebuilt for it. The kit's README states the rule under
[Versions](https://github.com/open-meridian/meridian-ui#linking-the-kit).

It also means a deployment older than the kit a page was built against answers with the kit it
has. A component that kit does not know stays an unknown element and shows what the page put inside
it, so put inside each component what a browser should show without the kit, as the examples below
do.

## To link external accounts: `om-account-map`

A plugin that reads accounts at a source, and names them by that source's identifiers, has an admin
of the plugin link each of them to one of the firm's accounts, on one of the plugin's pages at
`admin`. `om-account-map` is that page's content: each external account beside the account it is
linked to, or the forms to link it. It needs kit 0.3.0 and SDK 0.7.0, and no script on the page.
From kit 0.5.0 it is built for hundreds or thousands of accounts; see
[At thousands of accounts](#at-thousands-of-accounts).

Declare the page at `admin`, so it is shown and served under Manage alone:
`@pages.page("/admin/accounts", "Account links", levels="admin")`. A plugin admin is account
agnostic: they link to any existing account, and the page shows identities and links, never an
account's holdings or values. Only a deployment admin may name a new account, which
`caller.deployment_admin` says; the sidecar refuses a new account from anybody else. From kit 0.6.0
an external account in the map may carry a `status` and `values`; on a page at `admin`, give it
neither, since they are an account's data. See
[Accounts](../concepts/accounts.md#external-accounts) for what a link is.

### Give it its data

The map takes three lists, as JSON inside the element:

```html
<om-account-map action="/admin/accounts" token-name="csrf" token="3f9c…" empty="No accounts yet.">
  <script type="application/json">{
    "external_accounts": [
      {"external_account_id": "DEMO-ACCT-1", "name": "Demo brokerage", "detail": "Demo Securities · Individual",
       "custodian": "Demo Securities", "account_type": "Individual"}],
    "accounts": [
      {"account_id": "ACC-01J9Z3Q4W7X8Y2K5M6N0P1R3S4", "name": "Demo brokerage account",
       "custodian": "", "account_type": "", "open": true}],
    "links": []
  }</script>
  <p>Without the kit, the page's own forms go here.</p>
</om-account-map>
```

| Data | Where it comes from |
|---|---|
| `external_accounts` | The accounts the plugin reported with [`report_external_accounts`](../api/typed-operations.md#report_external_accounts): `external_account_id` (required), `name`, `detail` (a line under the name), `custodian` and `account_type` (to pre-fill a new account), and `note` (a hint). |
| `accounts` | The firm's accounts, from [`read_accounts_for_linking`](../api/typed-operations.md#read_accounts_for_linking), acting for the admin viewing the page under Manage: `account_id`, `name`, `custodian`, `account_type`, and `open` (default `true`). Only open accounts are offered. `null` says they could not be read. |
| `links` | The plugin's links, exactly as [`AccountScope.links`](../api/python-sdk.md#accountscope) gives them: `external_account_id`, `account_id`, `account_name`. An external account in this list is linked, to that account; one not in it is not linked. |

The links are read, never guessed: the plugin holds the latest `AccountScope` from
`account_scope()` and puts its `links` here. In Python:

```python
import json

import meridian
from meridian.plugin.v1 import operations_pb2 as ops


def account_map_json(
    reported: list[meridian.ExternalAccount],
    accounts: list[ops.AccountRecord] | None,  # None when they could not be read
    scope: meridian.AccountScope,
) -> str:
    data = {
        "external_accounts": [
            {
                "external_account_id": a.external_account_id,
                "name": a.name,
                "detail": a.venue_account_type,
                "account_type": a.venue_account_type,
            }
            for a in reported
        ],
        "accounts": None if accounts is None else [
            {
                "account_id": a.account_id,
                "name": a.name,
                "custodian": a.custodian,
                "account_type": a.account_type,
                "open": a.state != ops.ACCOUNT_STATE_CLOSED,
            }
            for a in accounts
        ],
        "links": [
            {
                "external_account_id": link.external_account_id,
                "account_id": link.account_id,
                "account_name": link.account_name,
            }
            for link in scope.links
        ],
    }
    # The JSON must not close the element early.
    text = json.dumps(data)
    return text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
```

Write `<`, `>` and `&` inside the JSON's strings as `<`, `>` and `&`, as the last
line does, so that no account name can end the `<script>` early.

### Answer its forms

Each form the map draws is a plain `<form method="post">` to `action` (by default the page's own
address). Every form carries the page's token, in a hidden field named by `token-name`, and an
`intent`, and names its fields as `link_external_account` takes them. With `meridian.Pages`, the
token is the page's CSRF token: `token-name="csrf" token="{{ csrf_token }}"` in the template.

| `intent` | Fields | Shown as |
|---|---|---|
| `link` | `external_account_id`, `account_id` | A picker of the open accounts, and **Link** |
| `create` | `external_account_id`, `new_account_name`, `new_account_custodian`, `new_account_type` | A new account's name (the external account's to start), its custodian and type pre-filled, and **Create and link**. Only a deployment admin's is admitted |
| `unlink` | `external_account_id` | **Unlink**, on a linked account |

The server does what `intent` says, acting for the admin, and answers with the page again.
`Pages` has checked the level and the token before the view runs:

```python
@pages.route("/admin/accounts", levels="admin", methods=["POST"])
async def link(request: meridian.Request) -> str:
    caller, form, plugin = request.caller, request.form, request.plugin
    external = form["external_account_id"]
    if form["intent"] == "link":
        await plugin.link_external_account(
            external_account_id=external, account_id=form["account_id"], acting_for=caller.header,
        )
    elif form["intent"] == "create" and caller.deployment_admin:
        await plugin.link_external_account(
            external_account_id=external,
            new_account_name=form["new_account_name"],
            new_account_custodian=form.get("new_account_custodian", ""),
            new_account_type=form.get("new_account_type", ""),
            acting_for=caller.header,
        )
    elif form["intent"] == "unlink":
        await plugin.link_external_account(external_account_id=external, acting_for=caller.header)
    return ...  # the page again, saying what was done
```

The token matters: the plugin's page has a sign-in cookie of its own, so without one a page
elsewhere could make an admin's browser post the form. `Pages` makes it from the person, the
session's level and a secret only the plugin's process holds, and refuses a form without it. A page
served another way does the same itself.

The change reaches `AccountScope.links` with the next delivery of the account scope, which the link
itself causes. Say what was done in a `.notice` on the page you answer with, rather than guess the
new state.

A page with script of its own may listen for the map's `om-link` event, which carries the same
fields, and cancel it to send the link itself.

### At thousands of accounts

From kit 0.5.0 the map is a dense table, one row per external account, built for a deployment with
hundreds or thousands of them. The document holds one page of rows however many there are. Above
the table:

- **a search**, matching every word typed anywhere in the external account's name, ID, number,
  custodian, type, detail and connection, or in the account it is linked or suggested to;
- **Unlinked, Linked and All**, each with its count. The map opens on Unlinked while any account is
  unlinked, because that is the work;
- **Group by** connection or custodian, offered where the data has at least two;
- and under the table, **pages** of rows.

A row's **Link…** (**Change…** on a linked one, **Other…** beside a suggestion) opens its choices
under that row alone: an
existing open account, found by typing into a chooser, a new account named from the external one,
and on a linked account, **Unlink**.

Three attributes and three optional data fields shape it:

| Attribute | |
|---|---|
| `group-by` | `connection` or `custodian`: the grouping to start with. The person may change it. |
| `page-size` | Rows on a page, 50 by default. |
| `link-several` | The handler at `action` takes several links in one form (below), so the map offers **Link N suggested…**. |

| Field on an external account | |
|---|---|
| `number` | The source's account number, for matching and shown. Leave out a masked one, such as `****3003`. |
| `connection`, `connection_id` | The connection the account is reached through, to group by. |

An account in `accounts` may carry a `number` too.

**Suggestions.** Where an unlinked external account's name or number matches exactly one open
account (ignoring case, spacing and character width), the map suggests it in the row, saying why:
"same name", "same number" or "named by its number". The row's **Link** takes it, as the plain
`link` form. Nothing is suggested where two accounts match, where the account is linked to another
external account already, where two unlinked accounts would claim it, or where the firm's accounts
could not be read.

**Several links in one form.** With `link-several`, **Link N suggested…** opens a review of the
suggestions the search finds, each of which can be left out, and sends them in one form whose
`intent` is `link-several`. It carries the token once, then `external_account_id` and `account_id`
repeated, one pair per link, in order. The handler reads both as lists, refuses the whole form if
they differ in length, name an external account twice or hold an empty ID, and otherwise links each
pair as its own `link_external_account` call, so one refused leaves the others as they went. It
answers with the page, saying how each went. Allow for a body of a few thousand pairs, about a
hundred bytes each.

```python
from urllib.parse import parse_qs

form = parse_qs(request.body.decode())  # every value a list, in the order the page wrote them
if form.get("intent") == ["link-several"]:
    externals = form.get("external_account_id", [])
    accounts = form.get("account_id", [])
    if (
        not externals
        or len(externals) != len(accounts)
        or len(set(externals)) != len(externals)
        or not all(externals)
        or not all(accounts)
    ):
        ...  # answer 400 and send nothing
    for external, account_id in zip(externals, accounts):
        try:
            await request.plugin.link_external_account(
                external_account_id=external, account_id=account_id,
                acting_for=request.caller.header,
            )
        except meridian.MeridianError as refused:
            ...  # say which was not linked, and why, on the page you answer with
```

Offer `link-several` only once the handler takes it: a map without it never sends that intent, and
the one-pair `link` form stays for a suggestion taken alone. The SnapTrade plugin,
[meridian-snaptrade](https://github.com/open-meridian/meridian-snaptrade), links its accounts this
way. The kit's README lists every property, method and event of the map.

## To show records on a phone: `om-grid` with `narrow`

A grid that is wide on a desk is cramped on a phone, or in a narrow panel. With kit 0.3.0, `narrow`
chooses what a grid does where it is under 40rem wide. It is the grid's own width, so a grid in a
narrow panel counts as narrow too.

- **`narrow="cards"`**: each row becomes a card. The first column is the card's title, every other
  value sits under its column's name, and an empty cell is left out. Use it for records whose
  columns each matter, such as an account's sync state. Not in high-rate mode.
- **`narrow="priority"`**: the columns the page wants least hide first. A column's `priority` is
  `1` or none (never hidden), `2` (hidden under 32rem) or `3` (hidden under 48rem). The table stays
  a table, so figures still compare down a column. Use it for positions or quotes, and with
  high-rate mode.

Without `narrow`, a narrow grid scrolls sideways, as it did before 0.3.0.

The grid takes its columns and rows as JSON inside it, as the map does, so a page needs no script.
**Rich cells** say more than a value, each as plain JSON on the column:

| Column option | What it shows |
|---|---|
| `hint: "field"` | The row's `field`, under the value |
| `tone: {"field": "f"}` | The tone the row's field `f` names: for a badge `good`, `warn`, `bad`, `accent`, `info`, `violet`, `buy` or `sell`, and for other text `good`, `warn`, `bad`, `buy` or `sell`. Anything else is no tone |
| `blank: "text"` | What an empty value says, faintly |
| `strong: true` | The value in strong text, as a row's name |

```html
<om-grid row-key="id" narrow="cards" caption="Accounts">
  <script type="application/json">{
    "columns": [
      {"key": "account", "label": "Account", "hint": "where", "strong": true},
      {"key": "link", "label": "Link", "type": "badge", "tone": {"field": "link_tone"}},
      {"key": "holdings_as_of", "label": "Holdings as of", "blank": "not reported"}],
    "rows": [
      {"id": "DEMO-ACCT-1", "account": "Demo brokerage", "where": "Demo Securities · Individual",
       "link": "Linked", "link_tone": "good", "holdings_as_of": "2026-09-29 12:04 UTC"},
      {"id": "DEMO-ACCT-2", "account": "Demo retirement", "where": "Demo Securities · IRA",
       "link": "Not linked", "link_tone": "warn", "holdings_as_of": ""}]
  }</script>
  <div class="table-wrap"><table>…the same rows, for a browser without the kit…</table></div>
</om-grid>
```

Data set from script, through the grid's `columns` and `rows` properties, wins over the declared
JSON.

Kit 0.3.0 also fits the rest of a page to a phone, with nothing to do but use its classes:

- **List rows wrap.** In a `.list-row`, where the text and the row's buttons do not fit side by
  side, the buttons drop below the text.
- **A field and its button share a row**, level and the same height, in a `.field-row`; on a narrow
  row the button drops below.
- **A choice is drawn as options to pick from**: `fieldset.choice` holding `label.option` radio
  buttons, each with a line of hint, the chosen one marked.
- **`om-moment` shows when figures are as of**, to read rather than to choose:
  `<om-moment label="Last read" value="2026-09-29T12:04:00Z">`. It shows the moment to the minute
  in UTC, or in the reader's own time zone with `zone="local"`, and "Not yet" for a value it cannot
  read, never a guess.

## Inside the dashboard's frame

The dashboard shows every page of a plugin in the plugin's **area**, at `/plugins/<instance>`,
reached from the home by **Manage**, **Open** or **View**: the plugin's name, the session's level,
and one tab row holding the pages declared at that level, each page in a frame. The frame stays,
because it keeps the plugin's script on the plugin's own origin, away from the person's dashboard
session. From kit 0.2.0 it is **seamless**: it has no border and no scrollbar of its own, it is as
tall as the page's content, and the dashboard's heading and tab row are the only ones. It is the
same frame, on the same template, under each of the three buttons.

The dashboard tells the page it is framed, and the kit does the page's half with no code. A framed
page:

- **hides its own heading**, the `h1` of its `.page-head`. The rest of the head stays: the line
  under the heading, and the `.actions`. A head holding nothing but a heading goes whole;
- **hides its tab row**, a `.tabs` inside the head or straight after it. A `.tabs` further down is
  the page's content, and stays;
- **drops its own padding, centring and width limit**, and its background, so the dashboard's page
  colour shows through;
- **reports its height** to the dashboard whenever it changes, and the dashboard sizes the frame to
  it.

The same page opened on its own, in a window of its own, looks exactly as it would without a frame.

So draw the heading and tab row with the kit, in its shape, and the frame takes care of them:

```html
<main class="page">
  <header class="page-head">
    <div><h1>Connections</h1><p>Reading the source. Last read 12:04.</p></div>
    <div class="actions"><button class="primary">Connect</button></div>
  </header>
  <nav class="tabs">…</nav>   <!-- hidden when framed: the dashboard's tabs replace it -->
  …
</main>
```

!!! warning "Never size a page by the viewport's height"
    Don't use `vh`, or `height: 100%` on `html` or `body`, to size a page. Inside the frame the
    viewport is the frame, and the frame's height follows the page, so a page sized by it chases its
    own tail. Let the content decide the height.

### Header actions

From kit 0.4.0 a framed page can hand the buttons in its head to the dashboard, which draws them in
its own header, where its own buttons are. Mark each with `data-om-action` and an id, on a `button`
(or an `input type="submit"`) inside the head's `.actions`. Most often it is a plain form's submit
button:

```html
<header class="page-head">
  <div><h1>Connections</h1><p>Reading the source.</p></div>
  <div class="actions">
    <form method="post" action="/admin/read" class="inline">
      <input type="hidden" name="csrf" value="…"><button data-om-action="refresh">Refresh</button>
    </form>
  </div>
</header>
```

The page writes no script for it. Framed, the kit hides the marked buttons in the page and offers
them to the dashboard; pressing one in the dashboard's header presses the page's own, so the form
posts from the page, to the page's server, with its own token. The dashboard never sees the form or
its answer. Opened on its own, the page shows its buttons where they are.

- The id is lower-case letters, digits and hyphens, at most 32 characters. The label is the
  button's text, at most 40 characters.
- `class="primary"` or `class="danger"` is its tone, and a disabled button stays disabled.
- At most four are offered, each id once, in the page's order. A button the kit cannot offer (a bad
  or repeated id, a fifth, no label or a long one) stays in the page.
- A marked button anywhere but the head's `.actions` is the page's own, and stays.

### Header status

From kit 0.7.0 a framed page can hand the dashboard its status dot, which it draws beside the
plugin's name, so the dot takes no line of the page's. Mark an `om-status` in the head with
`data-om-header`; in a template on `meridian/base.html`, put it in the `status` block:

```html
<header class="page-head">
  <div><h1>Account links</h1>
    <p><om-status data-om-header state="ok" label="Read" at="2026-09-30T13:12:00Z" at-label="Last read">Read. Last read 2026-09-30 13:12 UTC.</om-status></p></div>
</header>
```

The first marked one in the head is offered; its `state` is `ok`, `busy`, `warn` or `error`. An
unmarked `om-status` stays in the page. Opened on its own, the page shows the dot where it is. A head
left with nothing to show, once the dashboard draws its heading, actions and status, is dropped
whole, so the page starts right under the dashboard's tabs.

The kit's README gives the messages between the page and the dashboard.

## Related

- [Plugins, roles and grants](../concepts/plugins.md#a-plugins-page): how a person reaches a page,
  and what the plugin learns about them.
- [Record a holdings statement](../tutorials/record-a-holdings-statement.md): a custody plugin with
  a page at `admin` for linking accounts.
- [Python SDK](../api/python-sdk.md): `Pages`, `Interface`, `Page`, `Caller` and
  `meridian.testing`.
