# Plugins, roles and grants

Everything a firm builds on Open Meridian is a **plugin**: a connector to a
broker, an analytics page, a bot, a tool a trader had an AI agent write. This
page explains what a plugin is, what it may do, how that is decided, and how
people reach it.

To write one, start with [Your first plugin](../getting-started/first-plugin.md).
To choose its roles, see [Roles](roles.md).

## A plugin is a small program beside its sidecar

A plugin runs in a pod of its own, beside a **sidecar** that Open Meridian
provides. The sidecar listens on the pod's loopback address, and the plugin
talks to it and to nothing else.

- It never learns the bus's address, and never holds a broker credential.
  The credential is mounted into the sidecar's container, not the plugin's.
- It never discovers another plugin. Plugins that work together do it over
  the bus, each through its own sidecar.
- It cannot forge who it is. The sidecar stamps the plugin's identity, the
  time and each message's identifier onto everything the plugin sends.

This is what makes a plugin small. Access control, transport, correlation and
health are the sidecar's, implemented once, so a plugin author writes against
one local surface and gets all of them. That surface is the contract in
meridian-schema; the operations a plugin's roles may take are listed in
[Typed operations](../api/typed-operations.md), and in Python the
[SDK](../api/python-sdk.md) wraps them.

Admission fails closed: nothing a plugin sends is admitted before the sidecar
has loaded what it is allowed to do. The plugin is told its grants when it
registers, so a plugin missing a grant fails at start, where somebody is
looking, rather than at its first refused message.

### Plugins hold no state

A plugin is ephemeral. It may be stopped, restarted or moved to another node at
any moment, and it keeps nothing that has to survive that: no local database,
no file it expects to find again. What it needs, it reads from the deployment
when it starts. What must last — holdings, statements, instruments,
configuration — lives in the deployment's own stores.

## Roles: what a plugin is for

A **role** says what a plugin is for, and it is the only thing that decides
what the plugin may publish and subscribe to on the bus. Roles come from a
fixed list of thirteen, and a plugin declares a *set* of them. An order and
execution management system is `oms` and `ems`; a fully automated trading
system might be `signal`, `portfolio`, `oms` and `ems`. A plugin holding
several roles still has one sidecar and one credential, and holds the union of
their grants.

| Role | What a plugin with it is for |
|---|---|
| `ccm` | Broker and venue connectivity |
| `compliance` | Pre- and post-trade compliance rules |
| `custody` | Custodian, prime broker and broker statements, positions and cash, into the street store; reconciling them with the book is `operations`' |
| `dgm` | External data ingress |
| `ems` | Execution management |
| `match` | Confirmation with external matching services |
| `oms` | Order management, including tax-lot selection |
| `operations` | The post-trade pipeline: matching, servicing, reconciliation, settlement |
| `portfolio` | Portfolio construction |
| `reporting` | Reporting, analytics and valuation |
| `servicing` | Non-trading transactions: corporate actions, lifecycle events, coupons |
| `settlement` | External settlement rails |
| `signal` | Signal generation |

Each role's entry, with its persona, its duties, what it leaves to which other
role and what it holds today, is on [Roles](roles.md), with the principles a
plugin must fit and the method that maps an idea for a plugin to the least
roles it needs. Because nobody can change a role's grants, an idea that needs
a grant no role has is reshaped to fit, never given one.

Nothing else is a role. The deployment's own components — the conductor, the
dashboard, the street and instrument stores, the book, first-run and the launcher — are
not roles, and no plugin may declare one. In particular there is no `admin`
role: administering a deployment is the dashboard's, and no plugin can
administer the deployment it was installed into. The `admin` level below is a
person's, on a plugin, and has nothing to do with roles.

!!! note "Most roles hold nothing yet"
    A role holds exactly the topics a workflow in Open Meridian's contract
    names it for. Today six do. `custody` is for holdings ingestion: recording
    a statement and its holdings, reporting sync status, resolving an
    instrument and reporting a missing one. `operations`, from contract v7,
    reads the statements and custodial positions custody plugins record, and
    hears them change, within its read scope; from contract v8 it writes the
    [book of record](the-book-of-record.md). `portfolio`, `reporting`,
    `compliance` and `oms`, from contract v8, read the book and hear it
    change. The other seven are reserved
    names that hold no topics until their workflows are built — order routing
    and execution among them, which are on the roadmap. A plugin holding only such roles, or
    naming no role at all, is admitted with no topics rather than refused. It
    can still serve a page.

### Grants are generated, never written

Nobody writes a plugin's grants. Open Meridian's contract lists, for every
topic on the bus, which roles and components publish it and which subscribe.
A role's grants are derived from that list, and so are the broker's
permissions. There is no grant file for a deployment to edit or forget to
mount, and no second policy that could disagree with the first.

This is also why a role is never a code path. The sidecar enforces a role's
grants and nothing in the runtime behaves differently because of it.

## Who may use a plugin: admin, read or write

Roles decide what a plugin may do on the bus. Who may use it is decided
separately, by the deployment, and it is the same three levels for every
plugin:

- **`admin`**: the person configures the plugin, its settings and its own
  pages at `admin`, and sees no account's data.
- **`read`**: the plugin may show the person what it reads, cut to the
  accounts they may read.
- **`write`**, which includes `read`: the plugin may also act for the person,
  sending commands for them, on the accounts they may write.

A person may hold `admin` and, beside it, `read` or `write`. A deployment
admin grants these in the deployment's access groups: an entry names a plugin
and a level. How that is granted is described in [Access](access.md).

A plugin names no parts of itself for people. Earlier versions let a plugin
declare **tags** for that; they were retired, so that every plugin is
administered the same way and nobody meets a new vocabulary with each one.

## Declaring them

A plugin declares its roles in its own `pyproject.toml`, where
`meridian plugin new` puts them:

```toml
[tool.meridian]
roles = []          # a set, from the thirteen above
interface = true    # it serves a page
```

`meridian plugin upload` refuses a role outside the list, or a component's
name, before anything is sent. From CLI 0.1.14 it also refuses a
`[tool.meridian]` that declares `tags`, even an empty list. The full format is in
[the plugin manifest reference](../api/plugin-manifest.md).

## The catalogue: each deployment's own registry

Every deployment has its own **registry**, inside it, holding the plugins
uploaded to that deployment and nothing that reaches any other.

A deployment admin uploads a plugin with `meridian plugin upload`, signed in
from a terminal. The CLI builds the image on the developer's machine and sends
it through the dashboard, layer by layer; layers the registry already has are
skipped, and the shared base image for each SDK version is held once for every
plugin built on it. The metadata — roles, whether it serves a page — is
recorded with the version.

**A recorded version is never replaced.** Uploading a name and version that is
already recorded is refused. To change a plugin, raise its version.

## Launching, and approval

Uploading a plugin runs nothing. Running it is a separate act, **launching**,
and launching is where its roles are approved.

`meridian plugin launch <name> <version> --instance <id>` shows the roles the
version asks for, and runs it only once the deployment admin approves them. The conductor checks the launch against its catalogue, records it with
who approved it, and only then asks the launcher to start it. The launcher
creates one Deployment in the chart's plugin shape, from an image in the
deployment's own registry, and nothing else.

Each launch is an **instance**, with an identifier chosen at launch. One
plugin may be launched more than once — `snaptrade-1` and `snaptrade-2` from
one image — and each instance has its own pod, its own broker credential and
its own page. `meridian plugin stop <instance>` is launching's inverse.

!!! note "Launching from the dashboard"
    Today a plugin is uploaded, launched and stopped from the CLI; see
    [the CLI reference](../api/cli.md). A page in the dashboard offering the
    same launch to an administrator is specified and not built yet.

## A plugin's page

A plugin that declares `interface = true` serves a page. Each instance's page
has an origin of its own:

```text
https://<instance>.plugins.<dashboard host>/
```

A separate origin per instance is what stops a plugin's script from acting as
the person on the dashboard, or on another plugin's page. It is why a
deployment needs a wildcard name, `*.plugins.<host>`, and why its address must
be a name rather than an IP address. On a laptop, any name under `.localhost`
works with nothing set up.

A person opens a plugin from the dashboard's home, at one of the levels they
hold (see [Manage, Open and View](#manage-open-and-view)). The dashboard hands
the browser a one-time code, which the plugin's host exchanges for a session
of its own, carrying that level and ending when the dashboard session it came
from ends. On every request after that:

1. The dashboard checks the person's access against the records as they are
   now, and that they still hold the session's level.
2. It signs an assertion: who the person is, the session's level, and what
   that level reaches on this plugin — none of their accounts under `admin`,
   the accounts they may read and the accounts they may write under `write`,
   the accounts they may read under `read` — for this instance only, valid
   for 60 seconds.
3. The plugin's sidecar verifies the assertion and hands the plugin the
   verified claims. A request that fails verification never reaches the
   plugin, and anything the request carried claiming to be the caller is
   removed.

The plugin can refuse more than it was handed; it has no way to permit more.
Being a deployment admin opens no plugin: the home offers a plugin only at a
level the person holds on it.

### Manage, Open and View

The dashboard's home, **Your plugins**, lists every plugin the person holds a
level on, `admin` included, with a button for each level held:

| Button | Level | What it opens |
|---|---|---|
| **Manage** | `admin` | Its **Summary** and **Settings**, and the plugin's pages at `admin`: its configuration, such as connections and account links. No account's data |
| **Open** | `write` | Its pages at `write`, acting on the accounts the person may write |
| **View** | `read` | Its pages at `read`, read-only. A writer is offered View too |

A button opens the plugin's **area**, at `/plugins/<instance>?level=admin`,
`write` or `read`: one head, and one tab row holding the pages the plugin
declared at that level, in the order declared, with the page asked for in a
seamless frame below. A plugin that declares no page at `write` or `read` has
one there, its `/`.

The head is the same on every tab and at every level. On the left are the
house, back to the home, the plugin's name and its status dot. On the right
are the page's actions, such as a Refresh drawn as a circular arrow, then the
**Manage** | **Open** | **View** switch of the levels the person holds, by
which they move between them, as on the home; the switch is always the
rightmost, so an action never moves it. Under Manage the dot is the plugin's
health on the dashboard's own tabs and on any page that tells none; at Open
and View it is the page's. On a phone the head stays one row: the switch is a
menu naming the session's level and listing the levels held, and a long name
is cut with an ellipsis. See
[Inside the dashboard's frame](../how-to/build-a-plugin-page.md#inside-the-dashboards-frame).

Under Manage the dashboard draws two tabs of its own before the plugin's, and
Manage opens on the first:

- **Summary**: the plugin's status, which is core's to say (its health and
  why, the version running and the contract it registered with), then the
  figures the plugin reports about its own work, each a tile, such as
  SnapTrade's Connections, Accounts reached and Last read. A figure is a
  count, a decimal, a text or a time, with an optional as-of, a state (ok,
  warn or error) as the tile's mark and a why as its note. A plugin reports at
  most 8, on its heartbeat; a list past any bound is refused, never cut. A
  figure names no account and carries none of an account's data. See
  [Figures](../api/python-sdk.md#figures).
- **Settings**: the plugin's settings form, the same as in the dashboard's
  admin view of it.

So a plugin builds no summary page of its own. The health a plugin reports
stands, with its why, until it reports again: one that says it is not healthy
stays so on Summary until it says it is.

From a terminal, `meridian plugin open --level manage`, `open` or `view` does
the same; without `--level` it opens at the first level held, Manage before
Open before View. See [`meridian plugin open`](../api/cli.md#meridian-plugin-open).

Each session carries one level, so Manage, Open and View are separate
sessions, and a person moves between them by the buttons. A page serves only
the levels it is declared with: a page at `write` and `read` asked for in a
Manage session is refused.

A page looks like the rest of Open Meridian because it is built on the
**plugin UI kit**, which the dashboard serves on the plugin's own host at
`/.meridian/ui/<version>/`, answering any 0.x version with the newest 0.x
kit it carries. The kit brings the brand's type and spacing, each person's
colour scheme, and components such as a data grid and the map a plugin links
its external accounts with. Every page sits in the area in a seamless frame:
the page keeps its own origin, and the frame has no border or scrollbar of
its own and is as tall as the page. See
[Build a plugin's page](../how-to/build-a-plugin-page.md).

What every plugin has, whatever its pages, is in the dashboard's admin view of
it, at `/admin/plugins/<instance>`: **Overview** (its health, what its
settings still need and its external accounts' sync state), **Settings** (its
form, for its admins) and **Access** (who holds which level on it). Its own
pages are not there: they are in its area, reached from the home, its
configuration pages under Manage.

### Reads and writes on behalf of people

A plugin reads **as itself**, for every account anyone may read through it —
its *read scope* — and shows each person only the accounts their assertion
allows. That per-person cut is the plugin's to get right; core bounds it to
the plugin's scope, so a mistake can show a person another user's accounts on
the same plugin, never an account outside it.

Writes do not rest on the plugin. A command a plugin sends for a person
carries that person's assertion, and the sidecar admits it only when the
person may write the account it names and the account is in the plugin's
*write scope*. The person is stamped on the change, so it is recorded as
theirs. The plugin's own grants remain the ceiling throughout. Scopes are
explained in [Accounts](accounts.md).
