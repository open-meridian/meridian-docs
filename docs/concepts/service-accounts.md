# Service accounts

A **service account** is a user of the deployment that is not a person. A
plugin's autonomous work -- a scheduled sweep, a strategy, an agent inside
the plugin -- acts as one when it changes something with no person's request
to serve. A deployment admin creates it, names the person answerable for it
(its **owner**), grants it as anyone is granted, and sets it to **prepare
only** (the default) or **act**. A role's admin chooses which of the
accounts granted on that role the role's autonomous work **runs as**.

Whatever it asks, the deployment applies what it applies to a person's
agent: the account's grants and accounts, every level the admins set on the
act, the act's second pair of eyes, and the account's own setting. The
strictest wins. Allowed to make the act, it makes it, and the record names
the service account and its owner; held to preparing, it prepares it, and a
person makes it.

On the [order path](the-order-lifecycle.md) an automated strategy's orders
and an `ems`'s own placements are made as its role's service account,
through the plugin's own acts. Its call names the algorithm its work runs,
one the plugin's version declares (`algorithm_id`), which the book records
on the entry's service account actor. A service account may be among those
who may route through a connectivity plugin, and a
[trading instruction](the-order-lifecycle.md#trading-instructions) may
target it, as a person.

Work a plugin does with no person behind it runs as a service account,
never on a person's delegation: a delegation does not outlive its person.

## What it is, and is not

- **A user of the deployment.** It lives in the deployment's own records,
  whatever your identity provider. Its ID, `SA-` and a ULID, is its
  subject: a user group lists it in its logins by that ID, and its grants
  reach it as a person's do.
- **It never signs in.** It holds no password, key or token, and is never
  authenticated by your identity provider, your LDAP or the accounts the
  deployment holds. No client acts as one, and it never comes to the
  dashboard's `/mcp`.
- **It administers nothing.** Whatever it is granted, it is refused every
  admin route and every change to the deployment's configuration, and it
  reaches no core act: no `dashboard__` tool, no setting, and no prepared
  change's make, discard or share. A grant of `admin` gives it nothing.
- **Not the other things the words name.** Core also uses "service
  account" for the account the dashboard binds to your LDAP with, and for a
  Kubernetes pod's own account. Neither is a service account in the sense
  of this page.

## What vouches for it

No secret is held for a service account: not by it, the plugin, its owner
or the deployment, and none is handled to set one up. What vouches for each
call is the deployment's own record (the role's **Runs as** choice, the
account's state and its grants) and the plugin's sidecar, which asks the
dashboard as itself, for the instance it serves and no other.

Allowed to make an act, the dashboard mints the claims a person's call
gets: for that one call, addressed to that instance, single use, good for
at most 60 seconds, at `write` with the account's accounts on that role,
naming the act's tool, marked a service account and naming its owner. The
plugin's code is handed nothing longer-lived.

**Nothing to rotate.** Disabling or removing the account, withdrawing its
grant, or the role's admin choosing another refuses the next call; claims
already in flight live at most 60 seconds.

## How the levels bind it

A service account reaches only acts: the plugin's own declared acts on the
role it runs for, admitted by the dashboard as a person's agent's call is.
The levels that apply are those of
[Prepared changes](prepared-changes.md#what-agents-may-do): the strictest
of the deployment's ceiling for the act, the plugin admin's level, any
stricter level for an access group reaching the account, and its own
setting.

| The act's level (strictest that applies) | Second pair of eyes | Account set to **act** | Account set to **prepare only** |
|---|---|---|---|
| May make | off | makes it | prepares it |
| May make | on | prepares it; a person other than its owner makes it | prepares it |
| Prepare only | either | prepares it | prepares it |
| May not | either | refused by name | refused by name |
| An act with no check tool, at may make | (none possible) | makes it | refused: it cannot be prepared |

**Prepare only means never making that act**, by any route: not directly,
not by making a prepared change. No service account makes, discards or
shares a prepared change at all, whatever its setting.

**No setting for service accounts as a class.** To let people's agents make
an act and keep every service account to preparing it, put the service
accounts in a user group of their own and set a stricter level for the
access group it holds (see
[What agents may do](prepared-changes.md#what-agents-may-do)).

## Who does what

Nothing is permitted by default: a new service account is granted nothing,
and a role runs as nobody until its admin chooses.

| Who | Does | Never |
|---|---|---|
| **A deployment admin** | creates a service account with its name, purpose, owner and setting; changes any of them; disables, re-enables and removes it; grants it per role, `read` or `write` over account groups, by its ID in a user group's logins; sets the ceiling and core's acts' levels | grants it the deployment admin's capabilities |
| **A role's admin** | chooses which service account the role's autonomous work runs as, among those granted on that role, at a level no higher than its grant; sets the plugin's acts' levels and second pair of eyes | creates, grants or changes a service account, or chooses one not granted on the role |
| **Its owner** | sees what it did; is told when it is disabled or removed and when its prepared changes lapse; disables it | re-enables, changes or grants it |
| **The plugin** | offers its autonomous work as acts a person could take, each naming its check tool so it can be prepared | chooses which account its work runs as, or whether it makes or prepares |

One account may serve several roles, each chosen by that role's admin and
granted on each. An act needs `write`: a role run at `read` reaches no act.

## Its owner

The owner is a person the deployment knows, required, and never another
service account. They answer for it:

- **They see what it did:** every act it made, every change it prepared and
  every refusal, by name and outcome. The contents -- a prepared change's
  arguments -- only within their own read access: owning an automation never
  opens accounts the owner may not read. Where a prepared change names an
  account they may not read, its contents are withheld from them.
- **They are shown its prepared changes**, beside everyone who may make
  them. Under a second pair of eyes they never make what it prepared, as
  the person behind an agent never makes what their agent prepared; with
  the gate off they may, like anyone who may make the act.
- **They are told**, in their Inbox, when it is disabled or removed and by
  whom, and when each of its prepared changes lapses with it. Not of a
  disable they made themselves.
- **They may disable it** at once, and nothing more.

## Its prepared changes

A change a service account prepared goes to **everyone who may make it at
once**, its owner always shown it: there is no person whose own it is. In
the Inbox and on the change's page its preparer is the account and its
owner, such as *The sweep, a service account owned by Cat Ruiz*. The first who makes, changes or discards it
settles it for all. It lapses after the lapse period, as any prepared change
does, or when the account is disabled or removed; it is never made by
lapsing. See [Prepared changes](prepared-changes.md).

## Disabling and removing

**Disabling** refuses its next call, lapses its waiting prepared changes,
each its own record saying why, and tells its owner. A deployment admin or
its owner disables it; only a deployment admin re-enables it.

**Removing** takes it out of use for good: it is never re-enabled, and it
stays listed, marked removed. Every record it left is kept. Its waiting
prepared changes lapse, as on disabling.

No lifetime is fixed: it holds no credential to steal, its owner sees its
rows and refusals, and either admin or its owner can stop it.

A role's **Runs as** choice stands when its account is disabled, removed or
no longer granted, and the Access tab shows it so; every call is refused
until the grant returns or the role's admin chooses again.

## What is recorded

Each change is its own record, naming who made it, when, and why:

| Change | Recorded |
|---|---|
| A service account created, its name, purpose, owner or setting changed, disabled, re-enabled or removed | one record each in the dashboard's records, saying the part changed and its value, such as `setting: act` |
| A role's **Runs as** chosen, changed or cleared, and its level | one record each, scoped to the plugin's role (`instance:role`) |
| Its user groups and grants | as every grant is recorded |
| A call it made | the act's own record in its store, naming the service account, its owner when it acted, and the instance; in the book, the entry's actor is the service account (see [The book of record](the-book-of-record.md)) |
| A call, made, prepared or refused | the call's record: the account, the act, the outcome and why refused, never the arguments; its last use and last refusal on its row |
| A change it prepared | the prepared change, its preparer the service account, every step its own record |

What a plugin did as itself, a finding such as a break, stays recorded as
the plugin's instance, which is what it was.

What a service account's setting and the levels do is what they say: it
prepares this act, or it makes it, or it is refused. Nothing here describes
them as meeting any supervisory or regulatory rule: whether they serve one
is for the firm to judge.

## What the plugin is told

A refusal names the field it is about, as every refusal does:

| Refused | Field | Why |
|---|---|---|
| The role runs as no service account | `role` | its admin has not chosen one on the plugin's Access tab |
| The account is disabled or removed, or no longer held | `role` | until a deployment admin re-enables it or the role's admin chooses another |
| The account holds less than `write` on the role, or the role runs it at `read` | `role` | a deployment admin grants it; the role's admin chooses the level |
| The act is at May not | `tool_name` | naming who set it |
| An act with no check tool, for an account set to prepare only | `tool_name` | it cannot be prepared |
| A tool that is not one of the role's acts: a read, another role's act, a core tool | `tool_name` | a service account reaches its plugin's own acts on the role it runs for |
| A role the instance was not launched with | `role` | |
| A reason missing, past 4,000 characters, or not plain text (a control, zero-width or bidirectional override character) | `reason` | the reason is untrusted text, as a prepared change's is |
| Arguments that are not a JSON object, or over 1 MiB | `arguments_json` | the act's typed record of inputs, an empty object when it takes none |
| The act's check refuses it | the check's own fields | nothing is kept |

How a plugin calls and reads these is in
[A service account runs the plugin's autonomous work](../api/python-sdk.md#runs_as).

## Where you see it

- **Settings, Service accounts** (a deployment admin): one line each,
  name, owner, setting, state, the roles it runs for (**Runs for**), last
  used and last refusal, with **What it did**, **Edit**, **Disable**,
  **Re-enable** and **Remove**.
- **Service accounts**, `/service-accounts`, reached from your home when
  you own one: your own accounts' lines, with **Disable**.
- **An account's page**, `/service-accounts/<SA-…>`, **What it did**: **Its
  calls** (when, the act, the outcome, why refused), **Its prepared
  changes** and **Its record**, every change made to it.
- **A plugin's Access tab**, **Runs as**: what each role runs as and at
  which level, or nobody.
- **The Inbox**: an owner's notices, and the changes it prepared.
- **Through an agent**:
  [`dashboard__list_service_accounts`](../api/core-tools.md#dashboard__list_service_accounts)
  reads the rows, and
  [`dashboard__read_plugin_access`](../api/core-tools.md#dashboard__read_plugin_access)
  each role's `runs_as`. No tool creates, changes, grants, disables or
  removes a service account, or chooses what a role runs as: who acts is who
  holds access, which no tool changes.

## Related

- [Run a plugin's autonomous work as a service account](../how-to/run-a-plugins-work-as-a-service-account.md):
  the steps.
- [Prepared changes](prepared-changes.md): the levels, the second pair of
  eyes and lapse.
- [Access](access.md): grants, per role.
- [A service account runs the plugin's autonomous work](../api/python-sdk.md#runs_as):
  `meridian.runs_as`.
