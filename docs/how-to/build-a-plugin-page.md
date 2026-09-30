# Build a plugin's page

A plugin's page is built on the **plugin UI kit**, which the dashboard serves on the plugin's own
host. Linking it gives the page the platform's look, each person's colour scheme and market-direction
convention, and web components for what trading pages need. This guide covers linking the kit,
which version answers, linking external accounts with `om-account-map`, grids that read well on a
phone, and how a page behaves inside the dashboard's frame.

The kit is framework-free: CSS and custom elements, used the same way from plain HTML, React, Vue
or Svelte, from a plugin in any language. Every class, component, attribute and event is listed in
the kit's own reference, the
[meridian-ui README](https://github.com/open-meridian/meridian-ui#readme). The page
`meridian plugin new` writes is already built on it.

## To link the kit

The dashboard serves the kit at `/.meridian/ui/<version>/` on every plugin host, so it is on the
page's own origin. Link its stylesheet and script in `<head>`, and draw the page inside
`<main class="page">`:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Accounts</title>
  <link rel="stylesheet" href="/.meridian/ui/0.3.0/meridian.css">
  <script src="/.meridian/ui/0.3.0/meridian.js"></script>
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

**A 0.x release only adds.** Nothing in the kit is removed or renamed within 0.x, so a page built
against an earlier 0.x keeps working on a later one.

**The dashboard serves the newest 0.x kit to any 0.x request.** A page that links
`/.meridian/ui/0.1.0/` is answered with the newest 0.x kit the deployment carries, not with 0.1.0,
and not with nothing. So the version in a page's path says what it was built against, and the
deployment decides what it gets: a brand change reaches every page at once, and no plugin is
rebuilt for it. The rule is specified in meridian-design's `spec/plugin-pages-share-one-kit.md`,
Q2, and stated in the kit's README under
[Versions](https://github.com/open-meridian/meridian-ui#linking-the-kit).

It also means a deployment older than the kit a page was built against answers with the kit it
has. A component that kit does not know stays an unknown element and shows what the page put inside
it, so put inside each component what a browser should show without the kit, as the examples below
do.

## To link external accounts: `om-account-map`

A plugin that reads accounts at a source, and names them by that source's identifiers, has a
deployment admin link each of them to one of the firm's accounts, on the plugin's own admin page.
`om-account-map` is that page's content: each external account beside the account it is linked to,
or the forms to link it. It needs kit 0.3.0 and SDK 0.7.0, and no script on the page.

Serve the page only to a deployment admin, whose `Caller.deployment_admin` is `True`, and declare
it as one of the plugin's [admin pages](../api/python-sdk.md#interface). See
[Accounts](../concepts/accounts.md#external-accounts) for what a link is.

### Give it its data

The map takes three lists, as JSON inside the element:

```html
<om-account-map action="/admin/accounts" token-name="token" token="3f9c…" empty="No accounts yet.">
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
| `accounts` | The firm's accounts, from [`read_accounts_for_linking`](../api/typed-operations.md#read_accounts_for_linking), acting for the admin viewing the page: `account_id`, `name`, `custodian`, `account_type`, and `open` (default `true`). Only open accounts are offered. `null` says they could not be read. |
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
`intent`, and names its fields as `link_external_account` takes them:

| `intent` | Fields | Shown as |
|---|---|---|
| `link` | `external_account_id`, `account_id` | A picker of the open accounts, and **Link** |
| `create` | `external_account_id`, `new_account_name`, `new_account_custodian`, `new_account_type` | A new account's name (the external account's to start), its custodian and type pre-filled, and **Create and link** |
| `unlink` | `external_account_id` | **Unlink**, on a linked account |

The server checks the token, then does what `intent` says, acting for the admin, and answers with
the page again:

```python
caller = request.state.caller  # from CallerMiddleware; a deployment admin
external = form["external_account_id"]
if form["intent"] == "link":
    await plugin.link_external_account(
        external_account_id=external, account_id=form["account_id"], acting_for=caller.header,
    )
elif form["intent"] == "create":
    await plugin.link_external_account(
        external_account_id=external,
        new_account_name=form["new_account_name"],
        new_account_custodian=form.get("new_account_custodian", ""),
        new_account_type=form.get("new_account_type", ""),
        acting_for=caller.header,
    )
elif form["intent"] == "unlink":
    await plugin.link_external_account(external_account_id=external, acting_for=caller.header)
```

The token matters: the plugin's page has a sign-in cookie of its own, so without one a page
elsewhere could make an admin's browser post the form. Make it from the admin's identity and a
secret only the plugin's process holds, as
[Record a holdings statement](../tutorials/record-a-holdings-statement.md#6-serve-an-accounts-page)
does.

The change reaches `AccountScope.links` with the next delivery of the account scope, which the link
itself causes. Say what was done in a `.notice` on the page you answer with, rather than guess the
new state.

A page with script of its own may listen for the map's `om-link` event, which carries the same
fields, and cancel it to send the link itself.

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
- **A choice is drawn as the dashboard draws one**: `fieldset.choice` holding `label.option`
  radio buttons, each with a line of hint.
- **`om-moment` shows when figures are as of**, to read rather than to choose:
  `<om-moment label="Last read" value="2026-09-29T12:04:00Z">`. It shows the moment to the minute
  in UTC, or in the reader's own time zone with `zone="local"`, and "Not yet" for a value it cannot
  read, never a guess.

## Inside the dashboard's frame

The dashboard shows a plugin's admin pages as tabs in its admin view of the instance, each page in
a frame. The frame stays, because it keeps the plugin's script on the plugin's own origin, away from
the admin's dashboard session. From kit 0.2.0 it is **seamless**: it has no border and no scrollbar
of its own, it is as tall as the page's content, and the dashboard's heading and tab row are the only
ones.

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

## Related

- [Plugins, roles and grants](../concepts/plugins.md#a-plugins-page): how a person reaches a page,
  and what the plugin learns about them.
- [Record a holdings statement](../tutorials/record-a-holdings-statement.md): a custody plugin with
  an admin page for linking accounts.
- [Python SDK](../api/python-sdk.md): `Interface`, `Page`, `Caller` and `CallerMiddleware`.
