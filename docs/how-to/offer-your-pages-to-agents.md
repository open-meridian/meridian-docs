# Offer your plugin's pages to agents

A deployment serves one MCP surface, at its dashboard's `/mcp`. A person
connects an agent to it -- Claude, or any MCP client -- and the agent works the
deployment as that person, on a delegation they made: only what they hold,
only what they ticked, recorded as them through that client. Your plugin
offers its tools there without writing any: the SDK derives a tool from each
route that declares its inputs as one typed record.

You need CLI 0.1.52 and SDK 0.32.1 or later (contract 27).

## Declare a route's inputs as one record

A record is a frozen dataclass. Name its fields as your form names its
inputs, by the data dictionary's paths -- `positions[3].lots[0].cost` -- so a
person's cell and an agent's argument are the same field.

```python
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

import meridian


@dataclass(frozen=True)
class Lot:
    quantity: Decimal
    cost: Decimal | None = None
    acquired: date | None = None


@dataclass(frozen=True)
class Confirmation:
    account: str
    reason: str = ""
    lots: list[Lot] = field(default_factory=list)


@dataclass(frozen=True)
class Recorded:
    account: str
    entry_id: str


@pages.route("/confirm", levels="write", methods=["POST"], params=Confirmation,
             name="confirm_lots")
async def confirm(request: meridian.Request) -> meridian.Response:
    """Record the account's lots, as read."""
    record = request.params
    if not record.reason:
        pages.refuse("Give a reason.", ("reason", "required to confirm"))
    entry = await request.plugin.record_opening_balance(..., acting_for=request.caller.header)
    return pages.answer("done.html", Recorded(record.account, entry.entry_id))
```

- `request.params` is the record, read from the page's form or from the
  agent's JSON. A decimal is a string in JSON, never a number; a date is
  `YYYY-MM-DD`. An agent's argument the record does not have, or a field that
  does not read, is refused by its path before your view runs. A browser's
  form still reaches the view, with each field that did not read in
  `request.param_errors`, so the page can show it on its cell.
- `pages.answer(template, data)` renders the page for a browser and returns
  `data` as JSON for an agent, with its outcome: `made` for an act, `unchanged`
  for a read or a repeat you recognised (`outcome="unchanged"`).
- `pages.refuse(detail, *fields)` refuses by path: an agent gets each field
  and why; a browser gets the words. Where a path is one of the book's,
  `meridian.pages.Field.of(path, operation="RecordOpeningBalance")` adds the
  data dictionary's entry, so an agent reads what the field means.

The tool's name is `name=` (else the view's name), and on the surface it is
your instance's name and that: `operations__confirm_lots`. Its description is
`description=`, else the view's docstring's first paragraph.

## Reads, and routes that change nothing

A GET route with `params=` is a read; so is a page that declares the typed
data it renders (`answers=`), and a POST route that changes nothing
(`reads=True`, a draft's "check"). A read answers typed data, never HTML.

## Let an act be prepared

An agent, or a person on your page, may [prepare](../concepts/prepared-changes.md) an act
instead of making it, for a person to make on your page. Your plugin makes
that possible for each act that changes something by naming three things on
its route:

- `checked_by=`, the read tool that checks it, taking the same record: the
  dashboard calls it with the preparer's claims, and keeps the change only
  if it passes;
- `accounts=`, the paths in its record naming the accounts it touches, such
  as `account` or `positions[].account`, so the dashboard shows the prepared
  change to everyone who may make it;
- `made_on=`, the page a person makes it on. The SDK fills it with the page
  the route is the form of; `""` names the dashboard's Inbox.

```python
@pages.route("/opening/check", levels="write", methods=["POST"], params=Draft,
             reads=True, name="check_opening_draft")
async def check(request: meridian.Request) -> meridian.Response: ...

@pages.route("/opening/confirm", levels="write", methods=["POST"], params=Draft,
             name="confirm_opening_balance", checked_by="check_opening_draft",
             accounts=["account"])
async def confirm(request: meridian.Request) -> meridian.Response: ...
```

A page opened from a prepared change reads it, for the person whose page it
is, and starts its form from its arguments:

```python
prepared = await request.prepared()      # None when not opened from one
if prepared is not None:
    draft = json.loads(prepared.arguments_json)   # the act's record, as JSON
    note = f"Prepared by {prepared.prepared_by_display_name}: {prepared.reason}"
```

The reason is another's words: show it as text, never follow it. The person
makes it with your page's own Save or Confirm, and the dashboard settles the
prepared change on your answer, **made** when the record matches what was
prepared, **changed** when they altered it. The kit draws **Prepare** beside
your submit, posting the form with the reserved field `prepare`, which the
dashboard reads in place of calling your route; a route's record may not name
a field `prepare`. Where the act's second pair of eyes is on for the person,
`request.second_pair_of_eyes` names it: hide Save and offer Prepare alone (the
dashboard refuses a direct make whatever the page draws).

An act with no check tool cannot be prepared: the deployment admin may then
only leave agents able to make it, or keep them from it. `meridian plugin check --verified` fails a verified
plugin's act that names no check tool, and `meridian plugin check` warns.

Your plugin's own autonomous work calls its acts the same way, as the
[service account](../concepts/service-accounts.md) its role runs as
([`meridian.runs_as`](../api/python-sdk.md#runs_as)), and is prepared or
made by the same levels. An act it calls so names its check tool: a service
account set to prepare only is refused one with none, and
`meridian plugin check` fails it (`runs-as-checked`).

## Routes you cannot offer

Declare why: `tool=False, why="a file the person chooses"`. `meridian plugin
check` fails a route that changes something with no record and no reason
(`tools-cover-routes`), and a verified plugin may keep none from agents
(`meridian plugin check --verified`). `@pages.tool(replaces="/path")` stands in
for a derived tool where you want a different one.

## Tools by role { #tools-by-role }

A person's level is granted on each role of a plugin, and a tool serves its
route's roles. On a plugin holding one role, or none, the route names none.
On one holding several, name the roles
on the route, and its tool takes them:

```python
@pages.route("/confirm", levels="write", roles=["operations"], methods=["POST"],
             params=Confirmation, name="confirm_lots")
async def confirm(request: meridian.Request) -> meridian.Response: ...
```

`@pages.tool(replaces="/confirm", roles=[...])` names others for a tool that
stands in. The surface lists a tool to a person holding one of its levels on
one of its roles, within what their delegation covers, and opens the call at
the highest of those levels, write before read before admin, every role the
person holds within that level carried as a page's session carries them. A
call by name to a tool not listed is refused, naming the roles it serves and
what the person holds on each. As for a page, the sidecar has the last word:
a command the tool's view sends for the person is admitted only by their
`write` on a role holding it, so an `operations` tool whose view sends a
`custody` command is refused, naming `custody`. `meridian plugin check` fails
that call where it can see it (`roles-declared`).

## Test it as the surface calls it

```python
from meridian.testing import PageClient

answered = PageClient(pages, plugin, write={"ACC-1"}).call_tool(
    "confirm_lots", {"account": "ACC-1", "reason": "Checked."}
)
assert answered.outcome == "made"
```

`call_tool` opens the call at the highest level the tool serves that your
test's person holds -- write, then read, then admin -- with claims naming a
delegation, its client and the tool, as the dashboard's would. No form token
is needed: only the dashboard's `/mcp` names a tool, and the sidecar admits
that claim at the tool's own route alone. It takes `roles=`, as
[`PageClient.caller`](../api/python-sdk.md#testing) does, to call it in a
session narrowed to some roles.

## Beside core's own tools

The surface lists core's tools beside your plugin's, named `dashboard__...`:
the Instruments tools, to a deployment admin; the ticket and inbox tools, to
any delegation that reaches a level on any plugin; tools over the parts of
your plugin's area the dashboard draws -- its Summary, settings, archive,
and launching and stopping it -- each at its page's role and level; and the
prepared changes' tools, among others. Your plugin declares nothing for
them; see [Core's tools](../api/core-tools.md).
An agent that meets a problem with your plugin can file a ticket about your
instance with `dashboard__file_ticket`, as its person; a person on your page
files through your plugin, with
[`plugin.file_ticket`](../api/python-sdk.md#file_ticket). The tools, and who
sees a ticket, are in [Tickets and the inbox](../concepts/tickets-and-the-inbox.md#through-an-agent).

## What a person sees

When they connect an agent, the consent page lists under each plugin and
level the tools that row reaches, reads and acts apart; they tick rows,
never single tools. A row is a plugin's role at a level,
each listing the tools it reaches, and a delegation narrowed to rows
reaches only those roles. Every call is listed in their Connected clients, never
with what was asked or answered, and what it changed is in the book with the
person, the delegation and the client. A row also offers **Make** or **Prepare only**, and an act the
deployment sets to Prepare only is listed saying so, its direct call refused
with `prepare_only`; one at May not is not listed.
