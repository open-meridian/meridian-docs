# Plugins, roles and grants

Everything a firm builds on Open Meridian is a **plugin**: a connector to a
broker, an analytics page, a bot, a tool a trader had an AI agent write. This
page explains what a plugin is, what it may do, how that is decided, and how
people reach it.

To write one, start with [Your first plugin](../getting-started/first-plugin.md).

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
| `custody` | Custodian, prime broker and broker positions, and reconciliation |
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

Nothing else is a role. The deployment's own components — the conductor, the
dashboard, the street and instrument stores, first-run and the launcher — are
not roles, and no plugin may declare one. In particular there is no `admin`
role: administering a deployment is the dashboard's, and no plugin can
administer the deployment it was installed into.

!!! note "Most roles hold nothing yet"
    A role holds exactly the topics a workflow in Open Meridian's contract
    names it for. Today that is `custody`, for holdings ingestion: recording a
    statement and its holdings, reporting sync status, resolving an instrument
    and reporting a missing one. The other twelve are reserved names that hold
    no topics until their workflows are built — order routing and execution
    among them, which are on the roadmap. A plugin holding only such roles, or
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

## Tags: dividing a plugin among people

A **tag** is a plugin's own name for a part of itself that people may be
given. Tags carry no topics and grant nothing on the bus. They exist so that a
deployment admin can give different people different parts of one plugin, at
`read` or `write`.

For example, a compliance plugin might declare `compliance` and `reporting`
tags. A compliance officer is given `compliance` at write and `reporting` at
read; a trader is given `compliance` at read, to see whether an order was
approved. How that is granted is described in [Access](access.md).

Roles are chosen from Open Meridian's list; tags are the plugin's to name.

## Declaring them

A plugin declares its roles and tags in its own `pyproject.toml`, where
`meridian plugin new` puts them:

```toml
[tool.meridian]
roles = []          # a set, from the thirteen above
tags = []           # its parts, for people
interface = true    # it serves a page
```

`meridian plugin upload` refuses a role outside the list, or a component's
name, before anything is sent. The full format is in
[the plugin manifest reference](../api/plugin-manifest.md).

## The catalogue: each deployment's own registry

Every deployment has its own **registry**, inside it, holding the plugins
uploaded to that deployment and nothing that reaches any other.

A deployment admin uploads a plugin with `meridian plugin upload`, signed in
from a terminal. The CLI builds the image on the developer's machine and sends
it through the dashboard, layer by layer; layers the registry already has are
skipped, and the shared base image for each SDK version is held once for every
plugin built on it. The metadata — roles, tags, whether it serves a page — is
recorded with the version.

**A recorded version is never replaced.** Uploading a name and version that is
already recorded is refused. To change a plugin, raise its version.

## Launching, and approval

Uploading a plugin runs nothing. Running it is a separate act, **launching**,
and launching is where its roles and tags are approved.

`meridian plugin launch <name> <version> --instance <id>` shows the roles and
tags the version asks for, and runs it only once the deployment admin approves
them. The conductor checks the launch against its catalogue, records it with
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

A person opens a plugin from the dashboard's home, which lists the plugins
they hold access on. The dashboard hands the browser a one-time code, which
the plugin's host exchanges for a session of its own, ending when the
dashboard session it came from ends. On every request after that:

1. The dashboard checks the person's access against the records as they are
   now.
2. It signs an assertion: who the person is, and what they hold on this plugin
   — for each tag, the accounts they may read and the accounts they may write
   — for this instance only, valid for 60 seconds.
3. The plugin's sidecar verifies the assertion and hands the plugin the
   verified claims. A request that fails verification never reaches the
   plugin, and anything the request carried claiming to be the caller is
   removed.

The plugin can refuse more than it was handed; it has no way to permit more.
A deployment admin can open the page of any running plugin, but opening is not
access: the assertion still carries only what they hold on that plugin.

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
