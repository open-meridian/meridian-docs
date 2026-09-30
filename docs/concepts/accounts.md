# Accounts

An **account** is one of the firm's own accounts, as the firm names it. It is a
record in the deployment, authored by a deployment admin, and it is the only
thing holdings, positions and statements are ever recorded against.

Brokers and custodians have accounts of their own, named their own way. Those
are **external accounts**, and a plugin that reads one ties it to one of the
firm's accounts rather than creating an account of its own. This page
explains both, and how accounts bound what a plugin may read and write.

## The firm's accounts

A deployment admin creates accounts on the **Accounts** tab of the dashboard's
**Settings**. Each has a name and an identifier, `ACC-` followed by 26
letters and digits, and may say more about itself, in free text:

| Attribute | What it says | For example |
|---|---|---|
| Custodian | Where it is held | `Fidelity` |
| Type | What it is | `Roth IRA` |
| Owner | One ownership or grouping label | `Fund I` |
| Note | Anything else | `Opened for the 2026 rollover` |

All four are optional and searchable, as the name is, so two accounts of the
same name at different custodians can be told apart. None of them decides
anything: who may reach an account is its account groups' and its links'
business, never its owner's.

**An account is closed, never deleted.** Closing keeps it and its history:

- a closed account stays readable, so everything ever recorded against it can
  still be seen;
- it is never writable, by anybody, whatever their permissions say;
- nothing new is recorded against it, and an external account cannot be
  linked to it.

Accounts are given to people through **account groups**: explicit lists of
accounts, which a permission names. There is no "all accounts" group and no
nesting. An account in no account group is visible to deployment admins and
to nobody else, and it is in no plugin's scope except through a link. See
[Access](access.md).

The platform never receives an account, its name, or anything recorded
against it.

## External accounts

A plugin that brings data from outside — a brokerage connector reading
holdings, say — sees the source's own name for each account. A deployment
admin links each external account to one of the firm's accounts, on the
plugin's own admin pages: the plugin offers the firm's accounts, and sends the
link acting for the admin. **A plugin creates an account only that way**, when
the admin names a new account to link to; it may pre-fill the new account's
custodian, type, owner and note from what the source reported, for the admin
to change.

The link is applied by the plugin's sidecar, on the way in. A holding naming a
linked external account is recorded against the firm's account. One naming an
external account nobody has linked is refused, with a code that says so, and
the sidecar lists the unlinked accounts in its report of the plugin, so a
deployment admin can see what needs linking. Nothing is recorded against a
guess. A sync status for an unlinked account is not refused: it is shown
beside the account, so an admin can tell whether it is worth linking.

A link can be made only for a plugin instance that has run and reported, since
until then what it carries is unknown.

**A plugin can read its own links.** Beside its account scope, the sidecar
hands the plugin each of its links: the external account, the firm's account
it is linked to, and that account's name as the deployment holds it now. The
plugin reads them as itself, acting for nobody, so a page can say which of its
accounts are linked, and to what, without an admin viewing it. They arrive
when the plugin starts and again whenever one changes, including when a linked
account is renamed or closed, so the plugin keeps no copy of its own. It sees
its own links and no other plugin's. In the Python SDK they are
`AccountScope.links`, from 0.7.0; see
[`account_scope()`](../api/python-sdk.md#account_scope).

## How accounts bound a plugin

A plugin does not declare which accounts it works on. Its reach is derived
from two things: the permissions that name it, and its own links.

| Scope | What it is |
|---|---|
| **Read scope** | Every account some person may read through this plugin, and every account one of its external accounts is linked to |
| **Write scope** | Every open account some person may write through this plugin, and every open account one of its external accounts is linked to |

A person's access to a plugin is `read` or `write`, the same for every
plugin, and `write` includes `read`. A permission gives it on the accounts of
an account group; see [Access](access.md).

**A link is the plugin's right to the account it names.** The plugin's role
grants it the store, such as the street store for `custody`, and the link
grants it the one account. While the link stands, that account is in the
plugin's read and write scope, with no permission needed, and in no other
plugin's by that link. Removing the link removes it.

**A closed account is read-only.** It stays in the read scope, through a
permission or a link, and is in nobody's write scope.

The conductor derives both scopes from the permissions and the links, and
delivers them to the plugin's sidecar. They change as permissions and links
change, within the same 30-second bound as everything else about access.

- **Reads are aggregate.** A plugin reads as itself, for its whole read scope
  at once; the sidecar stamps that scope on its queries and subscriptions, and
  the stores answer only for accounts in it. The plugin then shows each person
  only the accounts that person's assertion allows. A person narrows what a
  plugin shows them and never widens what the plugin holds.
- **Writes are checked per account.** A command naming an account outside the
  plugin's write scope is refused by the sidecar. A command sent for a person
  is also refused unless that person may write that account, and when it is
  admitted the person is recorded as having made it.

So an account nobody may reach through a plugin is one that plugin cannot read
or change at all.

## What is recorded against an account

Today, what custodians say is held, in the **street store**: statements,
holdings and custodial positions, as brokerage and custody plugins report
them. Three rules govern it.

- **A position is replaced, not accumulated.** A holding states a quantity as
  of a date; it is not a change to one. Adding holdings up would double
  anything that appeared in two statements.
- **A holding whose instrument does not resolve is recorded, and moves
  nothing.** It is kept as evidence that something was held, and shown beside
  the positions so the gap is visible. See [Instruments](instruments.md).
- **No floating point.** A quantity crosses the wire as an integer with the
  scale it was stated with, up to 18 decimal places, and sits in the store as
  an exact decimal at that scale, so there is no rounding to get wrong. An
  amount of money always carries its currency. In the Python SDK a quantity is
  a `Decimal` and an amount a `meridian.Money`, and a value that cannot be
  carried exactly is refused rather than rounded.

!!! note "Not built yet"
    The street store holds the custodian's view of what is held. The firm's
    own book of record, calculated from its own activity, does not exist yet,
    and neither does reconciling one against the other. Orders and executions
    against an account are on the roadmap.
