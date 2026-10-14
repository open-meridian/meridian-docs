# Route orders through a connectivity plugin

From contract v22 an `ems` places orders at a venue through a **connectivity
plugin**, a plugin holding the `connectivity` role, which sends what it is
given in the venue's vocabulary and reports back what the venue did.
`portfolio` and the `oms` own orders, the `ems` owns placements, and the
connectivity plugin owns the fills it reports on them. Each
connectivity plugin is linked to **one** `ems`, usually a desk, and reaches
only the accounts that `ems` mapped on it. Three people set it up, each in
their own place:

| # | Step | Whose | Where |
|---|---|---|---|
| 1 | **Make the connectivity plugin available** | a deployment admin | the connectivity plugin's **Access** tab, **Its ems** |
| 2 | **Grant the `ems` the accounts it may map** | a deployment admin | the `ems`'s **Accounts** tab |
| 3 | **Link it to the `ems`, and choose who may route through it** | an admin of the `ems` | the `ems`'s **Access** tab, **Its connectivity plugins** |
| 4 | **Map each account to its venue account code** | an admin of the `ems` | the `ems`'s own page |
| 5 | **Give the desk access** to the roles they work | a deployment admin | Settings, as for any plugin |

Until steps 1, 3 and 4 are done, a placement through it is refused and the
refusal recorded, and the connectivity plugin reaches no account and hears
nothing. See [The order lifecycle](../concepts/the-order-lifecycle.md#placements-and-the-connectivity-plugins-an-ems-may-use)
for why it is set up this way.

!!! note "Contract v22"
    The link, the map and the checks are in core for contract v22, released
    2026-10-13 in chart 0.1.301. Core proves them against a simulated
    venue only.

The first connectivity plugin a deployment can launch is SnapTrade 0.16.0,
released 2026-10-13, which holds `connectivity` beside `custody`. It is
tested against a simulated brokerage only. Its connections are read-only
until an admin of its `connectivity` role enables trading on each, with
**Enable trading** on its **Connections** page (the `enable_trading` tool):
see [Trading through SnapTrade](using-a-custody-plugin.md#trading-through-snaptrade).
Until then every order placed through it on that connection is rejected
`unsupported`.

!!! note "Contract v23"
    Alpaca 0.8.0 and Tradier 0.7.0, released 2026-10-14 on open-meridian
    0.27.0 (contract v23) for chart 0.1.303 or later, hold `connectivity`
    beside `data` and `custody`, placing at Alpaca's Trading API and at
    Tradier, each tested against a simulated brokerage only, trading
    enabled per account by an admin of the `connectivity` role. They and
    SnapTrade 0.17.0, released the same day, report fills of orders placed
    in the broker's own app as
    [venue-originated fills](answer-a-venue-originated-fill.md).

## Before you start

- **Both plugins are launched**: the connectivity plugin and the `ems`
  (often one plugin holding `oms` and `ems`). A plugin's roles are its
  manifest's, approved when it is launched; see
  [Plugins, roles and grants](../concepts/plugins.md).
- **Someone administers the `ems`'s role**: `admin` on the plugin's `ems`
  role (see [To make someone a plugin's admin](administer-access.md#to-make-someone-a-plugins-admin)).

## 1. Make it available

1. Open the connectivity plugin's admin view (Settings, **Plugins**, the
   plugin), then its **Access** tab. Its part **Its ems** shows one line:
   **Available** (Yes or No), **Linked to** (the `ems`, or none) and **Who
   may route**.
2. Choose **Make available**, say **Why**, and confirm.

At the upgrade to contract v22 no connectivity plugin is available or
linked, each recorded so. To withdraw one, choose **Withdraw**: it then
reaches no account, and the placements already made stay as they are.

## 2. Grant the `ems` its accounts

An `ems` maps only the accounts a deployment admin granted it, nothing by
default, as a plugin that links external accounts is granted. On the
`ems`'s **Accounts** tab, **Accounts it may link to**, grant each account
the desk trades for, with a note saying why (see
[To grant a plugin accounts to link](administer-access.md#to-grant-a-plugin-accounts-to-link)).
For an `ems` a grant lets its admins map the account; it gives nobody
anything to read or write. A connectivity plugin takes no grant: it links
no accounts of its own.

## 3. Link it, and choose who may route

An admin of the `ems` links it from the `ems`'s own admin view, and needs no
admin on the connectivity plugin:

1. Open the `ems`'s admin view (Settings, **Plugins**, the `ems`), then its
   **Access** tab. Its part **Its connectivity plugins** lists each one
   linked to it, with **Edit**, and each a deployment admin made available
   that is linked to none, with **Link**.
2. Choose **Link** on the connectivity plugin's row. The dialog is headed
   **Link** the plugin's name **to** the `ems`.
3. Under **Who may route through it**, choose the people, service accounts
   and user groups who may place through it. The picker is searchable.
4. Say **Why**, and choose **Save**.

**Edit** on a linked plugin's row changes who may route, or, with **None
(unlink)** under **The ems**, unlinks it. A plugin's admin view opens only
for its own admins and deployment admins, so someone who also administers
the connectivity plugin may do the same from its **Access** tab, **Its
ems**, with **Edit link**, shown where the plugin is available or already
linked to an `ems` they administer. A connectivity plugin already linked to
another `ems` is refused (`REFUSAL_REASON_CONNECTIVITY_LINKED`): its
`ems`'s admin unlinks it first.

**Who may route is access**, so it is set at the page only: no tool sets
it. A placement for anyone not chosen is refused
`REFUSAL_REASON_CONNECTIVITY_NOT_ALLOWED`, and recorded on the order. The
plugin is told which connectivity plugins each person may choose, never
their user groups.

## 4. Map the accounts

On the `ems`'s own page, under Manage at `admin`, map each book account to
the **venue account code** it trades under at each of the `ems`'s
connectivity plugins. The `ems` plugin sends each mapping as acting for you,
and the deployment keeps the map, each change its own record. The `ems`
then sets the venue account code on each placement from it, and a fill,
charge or locate the connectivity plugin reports naming a code finds its
account by it. One naming a code not mapped is kept as an unplaced fact,
counted on the connectivity plugin's admin view.

- An account not granted to the `ems` is refused
  (`REFUSAL_REASON_ACCOUNT_NOT_LINKABLE`).
- A code already mapped on that connectivity plugin is refused.
- A connectivity plugin not linked to this `ems` is refused
  (`REFUSAL_REASON_CONNECTIVITY_NOT_ALLOWED`).

How the page looks is the `ems` plugin's. A plugin holding both `custody`
and `connectivity` may offer its custody links as suggestions; they are
never the map itself.

The `ems`'s **Access** tab shows the connectivity plugins linked to it
(**Available**, **Users**), with **Link** and **Edit** for its admins
only, and, read-only, its **Venue account map**, one line per mapping,
searchable: the connectivity plugin, the venue account code and the
account.

## 5. Give the desk access

People work orders through the plugins' own roles, granted as any role is:
`write` on the `oms` role to release, on the `ems` role to place, on
`portfolio` to propose, over the account groups they trade (see
[Give people access](administer-access.md)). Being chosen under **Who may
route through it** decides which connectivity plugins a person may place
at; it grants no access of its own.

Decide too whether each account's releases **wait for compliance**, true for
every account by default, and whether any trading instruction is in force:
see [Set trading instructions](set-trading-instructions.md).

## What the connectivity plugin does once linked

- **It works the `ems`'s placements.** It hears each placement naming its
  instance, sends it to the venue, and reports what the venue did: the
  acknowledgement, a rejection, each fill, bust and charge, each with the
  raw record it keeps. It hears the trading instructions too, and on a stop
  cancels at the venue at once.
- **It hears a cancel or a replace on the placement.** The placement
  carries its own change requests (`change_requests`), each with its kind,
  cancel or replace, a replace's new quantity, limit and time in force, and
  its outcome. The plugin acts on the kind, never on a condition's reason.
- **It records no order and creates no placement.** Those are the `oms`'s
  and the `ems`'s: a connectivity plugin's `RecordOrder` or
  `CreatePlacement` is refused by its sidecar (`PERMISSION_DENIED`). A
  telephoned or outside order is recorded by the `oms`, for a person.
- **It reports a venue-originated fill** from contract v23. A fill the
  venue reports on no placement the `ems` made -- a liquidation, say, or an
  order placed in the broker's own app -- is reported on no placement and
  waits in the book, unmatched, for the linked `ems` to accept it to an
  order or answer it DK, and its account is stamped by the same venue
  account map: see
  [Answer a venue-originated fill](answer-a-venue-originated-fill.md). In
  contract v22 it had no path into the book.
- **It reports a venue's value-date roll** from contract v23, where its
  venue rolls spot FX positions (see
  [A venue's value-date roll](../concepts/the-order-lifecycle.md#a-venues-value-date-roll)).

## Through an agent

[`dashboard__read_plugin_access`](../api/core-tools.md#dashboard__read_plugin_access)
answers, in `connectivity`, a connectivity plugin's link (`available`, the
`ems_instance_id`, its `users`) and an `ems`'s linked connectivity plugins
and its venue account map. Nothing is set through a tool: making a
connectivity plugin available, linking it and choosing who may route are a
person's, at the page.

## What is recorded

Each change to a connectivity plugin's availability or link, and each
mapping made or removed, is its own record: who, when, the instance, what
it was and what it became, and the note. A placement refused for its link
is an entry on the order naming the `ems`, the connectivity plugin asked
for, the actor and the reason.

## Related

- [The order lifecycle](../concepts/the-order-lifecycle.md): what the
  connectivity plugin, the `ems` and the book each do.
- [Answer a venue-originated fill](answer-a-venue-originated-fill.md).
- [Accounts](../concepts/accounts.md#accounts-a-plugin-may-link-to): grants.
- [Core's tools](../api/core-tools.md#dashboard__read_plugin_access).
