# Using an operations plugin

An **operations plugin** (the role `operations`) keeps the firm's own
[book of record](../concepts/the-book-of-record.md): it takes each account's
opening balance from a person, reconciles the book against the custodian's
statements, and records each difference as a break for a person to work.
Every operations plugin has the same first-use path, the same pages in the
same order, and the same "not set up yet" states. This page is that path,
valid for every operations plugin. Today there is one, the sample
operations plugin (plugin-sample-operations), so where this page names
something only it has, it says so.

!!! note "Contract v20"
    The common part is in open-meridian 0.24.0 (contract v20), the kit
    0.12.0 and core's **Setting up**, released 2026-10-12 in chart
    0.1.298. The sample operations plugin 0.10.0, released 2026-10-12,
    is built on open-meridian 0.24.0 and runs on chart 0.1.298 or
    later. It takes the common part, gives its Breaks and Reconciliations
    pages tools of their own, and makes every act preparable, its opening
    balance among them. The sample operations plugin 0.9.1 is built on
    contract v18.

## The first-use path

| # | Step | Whose | Where |
|---|---|---|---|
| 1 | **Choose its settings** | the plugin's admin | the plugin's **Settings**, under Manage |
| 2 | **Have access and a street source** | a deployment admin | access: a group holding `write` on the plugin over accounts; and a custody plugin running with a linked account among them. See [Give people access](administer-access.md) and [Using a custody plugin](using-a-custody-plugin.md). |
| 3 | **Confirm opening balances** | a person with `write` | the plugin's **Opening balances** page: every account in its scope has an opening balance in the book |
| 4 | **Reconcile** | the plugin, or a person with `write` | the plugin's **Reconciliations** page |
| 5 | **Work the breaks** | a person with `write` | the plugin's **Breaks** page: daily work, not a setup step |

From contract v20 core's **Setting up**, on the
plugin's **Summary**, judges the first two from its own records: every
required setting set, and a group holding `write` on the plugin over an
account group, linking to the plugin's **Access** tab, or, to anyone but a
deployment admin, "Ask a deployment admin to have access and a street
source". The rest are the pages' own to say. See
[Using a data plugin](using-a-data-plugin.md#setting-up-on-the-summary) for
how the part reads.

## Its settings

The sample's, offered to every operations plugin by the SDK's role
template: **Reconcile** (`reconcile`), each automation its own switch, off
until turned on (the sample operations plugin keeps it on by default, so an
upgrade changes nothing; an admin may turn it off); **A break is due** (`due_business_days`); and **Reconcile
against a statement no older than** (`street_fresh_within_hours`). Then the
plugin's own.

## Its pages

Under **Open** and **View**, the page you return to daily first:

- **Breaks** (`read_breaks`): each difference between the book and the
  street, with **Handle**, **Resolve** and **Close**. Before any: "No breaks
  yet: nothing is reconciled until each account's opening balance is
  confirmed, under Opening balances".
- **Reconciliations** (`read_reconciliations`): each reconciliation run,
  and **Reconcile now**.
- **Opening balances** (`read_opening_balances`; `confirm_opening_balance`):
  each account in the plugin's scope awaiting an opening balance, confirmed
  with **Confirm**. With none in scope: "Nothing to confirm: no account is
  in this plugin's scope yet; a deployment admin grants it".

From contract v20 an opening balance can be
[prepared](../concepts/prepared-changes.md): an agent prepares it through
the deployment's MCP, checked by `check_opening_draft`, or a person with
**Prepare** beside **Confirm**, and a person makes it on **Opening
balances**, where the page opens started from the prepared draft, marked
"prepared by" with the reason. Where the act's second pair of eyes is on,
the page offers Prepare alone, and someone other than whoever prepared it
confirms it.

## Its figures

**Open breaks**, **Overdue breaks**, **Awaiting an opening balance**,
**Street missing** (only when any) and **Last reconciliation**: the
sample's, now every operations plugin's.

## Related

- [The book of record](../concepts/the-book-of-record.md).
- [The custodian's activity](../concepts/the-custodians-activity.md):
  what explains a break.
- [Prepared changes](../concepts/prepared-changes.md).
