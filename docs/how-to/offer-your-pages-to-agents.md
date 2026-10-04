# Offer your plugin's pages to agents

A deployment serves one MCP surface, at its dashboard's `/mcp`. A person
connects an agent to it -- Claude, or any MCP client -- and the agent works the
deployment as that person, on a delegation they made: only what they hold,
only what they ticked, recorded as them through that client. Your plugin
offers its tools there without writing any: the SDK derives a tool from each
route that declares its inputs as one typed record.

This needs open-meridian 0.17.0 (contract v12) and a runtime serving v12.

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

## Routes you cannot offer

Declare why: `tool=False, why="a file the person chooses"`. `meridian plugin
check` fails a route that changes something with no record and no reason
(`tools-cover-routes`), and a verified plugin may keep none from agents
(`meridian plugin check --verified`). `@pages.tool(replaces="/path")` stands in
for a derived tool where you want a different one.

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
that claim at the tool's own route alone.

## Beside core's own tools

The surface lists core's tools beside your plugin's, named `dashboard__...`:
the Instruments tools, to a deployment admin, and from contract v13 seven
ticket and inbox tools, to any delegation that reaches a level on any plugin.
An agent that meets a problem with your plugin can file a ticket about your
instance with `dashboard__file_ticket`, as its person; a person on your page
files through your plugin, with
[`plugin.file_ticket`](../api/python-sdk.md#file_ticket). The tools, and who
sees a ticket, are in [Tickets and the inbox](../concepts/tickets-and-the-inbox.md#through-an-agent).

## What a person sees

When they connect an agent, the consent page lists under each plugin and
level the tools that row reaches, reads and acts apart; they tick rows,
never single tools. Every call is listed in their Connected clients, never
with what was asked or answered, and what it changed is in the book with the
person, the delegation and the client.
