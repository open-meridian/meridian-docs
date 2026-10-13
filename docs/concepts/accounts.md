# Accounts

An **account** is one of the firm's own accounts, as the firm names it. It is a
record in the deployment, authored by a deployment admin, and it is the only
thing holdings, positions and statements are ever recorded against.

Brokers and custodians have accounts of their own, named their own way. Those
are **external accounts**, and a plugin that reads one ties it to one of the
firm's accounts rather than creating an account of its own. This page
explains both, and how accounts bound what a plugin may read and write.

!!! note "Contract v20"
    From contract v20 a deployment admin grants each plugin the accounts it
    may link to, nothing by default (see
    [Accounts a plugin may link to](#accounts-a-plugin-may-link-to)), and an
    account's attributes in the book sit on the account's own row (see
    [In the book](#in-the-book)), in place of the dashboard's Books tab.
    Released 2026-10-12 in chart 0.1.298.

!!! note "Contract v22"
    From contract v22 an account's attributes in the book also say whether
    its releases wait for compliance (see [In the book](#in-the-book)); a
    deployment admin grants an `ems` the accounts it may map to venue
    account codes; and a connectivity plugin reaches the accounts its `ems`
    mapped on it (see
    [Accounts a plugin may link to](#accounts-a-plugin-may-link-to)).
    Released 2026-10-13 in chart 0.1.301.

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

### In the book

From contract v20 the Accounts tab also shows each
account's attributes in the [book of record](the-book-of-record.md), one
book per deployment, so they sit with the account they belong to: its
**Base currency** and its **Lot relief**, the lots a sale relieves when it
names none, are columns of its row. An account's **Edit** has two
sections, each saved on its own:

- **Account**: its name, custodian, type, owner and note, as above.
- **In the book**: its base currency (an ISO 4217 code) and its lot relief
  (first in, first out; last in, first out; highest cost; lowest cost;
  average cost), and from contract v22 whether its
  **Releases** wait for compliance (**Wait for compliance** or **Do not
  wait**, shown in the row's **Compliance** column as **Waits** or **Does
  not wait**), each change saved to the book with a **Reason**, its own
  act, journalled in the account's partition. A new account waits; see
  [The release gate](the-order-lifecycle.md#the-release-gate-and-waiting-for-compliance). Beside the title it says
  since when the book holds the account, the date its opening balance
  stands for, or "not yet". That date is set only by the book, when a
  person confirms the opening balance, never here.

"In the book" is shown only for an account that exists: create the account
first, then edit it. Before v20 the same attributes were on a tab of their
own, **Books**.

**An account is closed, never deleted.** Closing keeps it and its history:

- a closed account stays readable, so everything ever recorded against it can
  still be seen;
- it is never writable, by anybody, whatever their permissions say;
- nothing new is recorded against it, and an external account cannot be
  linked to it.

Accounts are given to people through **account groups**: explicit lists of
accounts, which a permission names, with no nesting. One is built in, **All
accounts**, which holds every account, those opened later included. An
account no other group lists is reached only through a permission naming All
accounts, or by a plugin through a link; nobody reaches it by being an admin.
See [Access](access.md).

The platform never receives an account, its name, or anything recorded
against it.

## External accounts

A plugin that brings data from outside — a brokerage connector reading
holdings, say — sees the source's own name for each account. An admin of the
plugin links each external account to one of the firm's accounts, on the
plugin's own pages at `admin`, under Manage: the plugin offers the firm's
accounts, by their identities alone, and sends the link acting for the admin.
Before contract v20 a plugin admin could link to any existing account; from
v20 only to an account the deployment admin granted the plugin (below).
**A plugin creates an account only that way**, when a deployment admin
names a new account to link to; it may pre-fill the new account's
custodian, type, owner and note from what the source reported, for the
admin to change. From v20 an account made by linking is granted to the
plugin that made it.

**An account has one external account.** At most one external account is
linked to an account, through whichever plugin, and the account's statements
are that one's. So two custodians holding for one fund, such as a prime
broker and an FCM, or a margin account and a cash one, are two accounts, and
so are two external accounts at one custodian, kept for different purposes. A
link naming an account that already has an external account linked is
refused, naming that one, and nothing is linked: link the second to another
account, or a new one. Links made before this rule are kept, never removed,
and the conductor logs each account holding more than one, for a deployment
admin to separate.

The link is applied by the plugin's sidecar, on the way in. A statement or a
holding naming a linked external account is recorded against the firm's
account. One naming an external account nobody has linked is refused, with a
code that says so, and
the sidecar lists the unlinked accounts in its report of the plugin, so its
admins can see what needs linking. Nothing is recorded against a
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

### Accounts a plugin may link to

From contract v20 **the deployment admin grants each
plugin instance the accounts it may link to**, and its admins link its
external accounts only within them. The two decisions are layered: the
deployment admin decides which of the firm's accounts a custodian's data
may ever be tied to; the plugin's admin, who sees the custodian's own
accounts, chooses which of those each one is.

- **Nothing is granted by default.** A new plugin instance links to no
  account until a deployment admin grants it some, on the plugin's
  **Accounts** tab in the dashboard's admin view of the plugin
  (`/admin/plugins/<instance>?tab=accounts`): **Grant** an account, with a
  note saying why, or **Withdraw** one. Each grant and each withdrawal is
  its own record. The plugin's admins read the tab; only a deployment admin
  changes it.
- **A plugin sees only what it was granted.** When a plugin offers the
  firm's accounts for linking, it is answered the accounts granted to its
  instance, not the deployment's whole list.
- **A link outside the grant is refused**
  (`REFUSAL_REASON_ACCOUNT_NOT_LINKABLE`), and nothing is linked.
- **A grant is not access.** It lets the plugin's admins link to the
  account; it gives nobody anything to read or write. Who reads the
  account's statements through the plugin is still access, `read` or
  `write` on its role over an account group.
- **Withdrawing an account keeps its link.** A link made while the account
  was granted stands until someone removes it; the withdrawal stops new
  links.
- **A connectivity plugin needs no grant.** It links no external accounts:
  it reaches accounts only through the `ems` it serves, which names the
  venue's account. From contract v22 its read and
  write scope is the accounts its `ems` mapped venue account codes to on
  it, while it is available and linked, and nothing otherwise.
- **An `ems` is granted the accounts it may map**, from contract v22: on its **Accounts** tab, as a linking plugin is, nothing
  by default. Its admins map only those to venue account codes; a mapping
  naming another account is refused `REFUSAL_REASON_ACCOUNT_NOT_LINKABLE`.
  See [Route orders through a connectivity plugin](../how-to/route-orders-through-a-connectivity-plugin.md).
- **At the upgrade to contract v20**, each account a plugin already linked
  is granted to it, recorded as made then, so nothing that worked stops.

An agent reads the grant with
[`dashboard__read_linkable_accounts`](../api/core-tools.md#dashboard__read_linkable_accounts);
no tool sets it. In the Python SDK, a plugin's
`read_accounts_for_linking` answers the granted accounts, and a link naming
another raises `CommandRefused` with that reason.

## How accounts bound a plugin

A plugin does not declare which accounts it works on. Its reach is derived
from two things: the permissions that name it, and its own links.

| Scope | What it is |
|---|---|
| **Read scope** | Every account some person may read through this plugin, and every account one of its external accounts is linked to |
| **Write scope** | Every open account some person may write through this plugin, and every open account one of its external accounts is linked to |

A person's account access on a plugin, from contract v15 on each of its
roles, is `read` or `write`, the same for every plugin, and `write` includes
`read`. A
plugin's scopes are the union over its roles. A permission gives it on the accounts of
an account group; see [Access](access.md). `admin` on a plugin reaches no
account, and adds nothing to its scope.

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
  the stores answer only for accounts in it. A read naming an account outside
  it is refused, one naming none answers the whole scope, and a plugin whose
  read scope is empty reads and hears nothing. The plugin then shows each
  person only the accounts that person's assertion allows. A person narrows
  what a plugin shows them and never widens what the plugin holds.
- **Writes are checked per account.** A command naming an account outside the
  plugin's write scope is refused by the sidecar. A command sent for a person
  is also refused unless that person may write that account, and when it is
  admitted the person is recorded as having made it.

So an account nobody may reach through a plugin is one that plugin cannot read
or change at all.

## What is recorded against an account

Two beliefs about what it holds, kept apart on purpose: the custodian's and
the firm's.

What custodians say is held is in the **street store**: statements,
holdings and custodial positions, as brokerage and custody plugins report
them. A statement is one account's, with the account's figures, such as its
buying power and margin, a set per margin segment as the custodian reports
them; a holding may carry its cost and its lots, as reported, and nothing is
derived from them. An `operations` plugin reads these, and hears each change,
within its read scope. Three rules govern it.

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

What the firm says is held is in the **book of record**, from contract v8:
the account's positions, lots, pending settlements, what of each position
cannot move, breaks and figures, from an opening balance a person confirms and
the book's own entries since. An `operations` plugin writes it, and reconciles
it with the street on every statement, recording each difference as a break;
no statement is ever applied to it. See
[The book of record](the-book-of-record.md).

!!! note "Not built yet"
    Orders and executions against an account are on the roadmap. Until they
    are, every trade made away from the platform shows in the book as a break
    until it is resolved.
