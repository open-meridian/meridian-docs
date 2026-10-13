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

!!! note "Contract v21"
    The sample operations plugin 0.11.0, released 2026-10-12, is built on
    open-meridian 0.25.0 (contract v21) and runs on chart 0.1.299 or
    later. It closes cleared breaks automatically as the operations role's
    [service account](../concepts/service-accounts.md) (see
    [Close cleared breaks automatically](#close-cleared-breaks-automatically)).

!!! note "Contract v22"
    The sample operations plugin 0.12.0, released 2026-10-13, is built on
    open-meridian 0.26.0 (contract v22) and runs on chart 0.1.301 or
    later. It reads the [order path](../concepts/the-order-lifecycle.md):
    a fill traded after a statement's date is taken back out when the book
    is compared with that statement, so a traded position is not a break,
    and a fill the book records compares its account's latest statement
    again. A **Flags** tab under Open and View (`read_flags`) lists, in the
    accounts you may read, each order carrying a late fact and each venue's
    fact the book holds on no order, with why; a late fact is acknowledged
    with a reason (`acknowledge_flag`, under Open). Each run asks core
    whether every pending fill's value date is a business day on its
    [settlement calendars](../concepts/settlement-calendars.md), and where
    it is not, offers that as a break's first candidate cause, linked to
    the check; the book never moves the date. It passes every case of the operations suite.

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

## Close cleared breaks automatically

A break whose difference has gone at the next reconciliation is not closed
by silence: it is closed as cleared, citing the statement where it cleared,
a justified act. Until contract v21 a person closes them, in one action on
**Breaks**. From the sample operations plugin 0.11.0 (contract v21), with
its setting **Close cleared breaks automatically** (`auto_close_cleared`,
off by default) turned on, each reconciliation that
finds cleared breaks calls the plugin's own act `close_cleared_breaks`,
checked by `check_close_cleared_breaks`, as the
[service account](../concepts/service-accounts.md) the `operations` role
runs as, after the run's figures. The plugin chooses no account and holds
no credential:

1. A deployment admin creates a service account, owned by a person, and
   grants it `write` on the plugin's `operations` role over the accounts it
   reconciles.
2. An admin of the plugin's `operations` role chooses it on the plugin's
   **Access** tab, under **Runs as**.

See [Run a plugin's autonomous work as a service account](run-a-plugins-work-as-a-service-account.md).
What each run's call came to is said on **Breaks**, beside the cleared
breaks, and in the plugin's log:

| Came to | When | What Breaks says, and what happens |
|---|---|---|
| **Made** | the account is set to **act**, and every level lets agents make the act with no second pair of eyes | "Closed N cleared break(s) automatically, as the service account the operations role runs as." The breaks are closed as cleared; the book's entry names the service account and its owner, and Breaks names the closer "service account SA-… owned by …" |
| **Prepared** | otherwise, the default | "Closing them automatically was prepared (PC-…) for a person who may close them to make." The prepared change waits in the Inbox of everyone who may close those breaks, and the account's owner, its reason naming how many cleared breaks of which account and the statement's date that found no difference for them; the breaks stay open until a person makes it. It is not prepared again for the same statement and breaks until a person asks, with **Reconcile now**, or the plugin restarts |
| **Refused** | the role runs as no service account | "Closing them automatically waits for a service account: the operations role runs as none. A deployment admin grants one, and an admin of this plugin chooses it on its Access tab." A person closes them, as before, in one action |
| **Refused** | the account is disabled, removed or not granted | "Closing them automatically was refused: …", with the reason. Nothing is closed |
| **Failed** | the plugin's act refused, or the call failed | "Closing them automatically was refused by this plugin's act: …" or "Closing them automatically failed: …". Nothing is closed |

None of them fails the reconciliation.

## Its figures

**Open breaks**, **Overdue breaks**, **Awaiting an opening balance**,
**Street missing** (only when any) and **Last reconciliation**: the
sample's, now every operations plugin's.

## Related

- [The book of record](../concepts/the-book-of-record.md).
- [The custodian's activity](../concepts/the-custodians-activity.md):
  what explains a break.
- [Prepared changes](../concepts/prepared-changes.md).
- [Run a plugin's autonomous work as a service account](run-a-plugins-work-as-a-service-account.md).
