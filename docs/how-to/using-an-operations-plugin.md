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

The sample operations plugin takes the role's common part, gives its Breaks
and Reconciliations pages tools of their own, and makes every act
preparable, its opening balance among them. It can close cleared breaks
automatically as the operations role's
[service account](../concepts/service-accounts.md) (see
[Close cleared breaks automatically](#close-cleared-breaks-automatically)).
It reads the [order path](../concepts/the-order-lifecycle.md): a fill traded
after a statement's date is taken back out when the book is compared with
that statement, so a traded position is not a break, and a fill the book
records compares its account's latest statement again. A **Flags** tab
under Open and View (`read_flags`) lists, in the accounts you may read, each
order carrying a late fact and each venue's fact the book holds on no
order, with why; a late fact is acknowledged with a reason
(`acknowledge_flag`, under Open). Each run asks core whether every pending
fill's value date is a business day on its
[settlement calendars](../concepts/settlement-calendars.md), and where it is
not, offers that as a break's first candidate cause, linked to the check;
the book never moves the date. It reads [booking](../concepts/booking.md)
too: see [Bookings](#bookings).

The sample operations plugin records only on change. A custodian sending
the same statement again writes nothing: figures are recorded only where a
value moved, and a break is brought up to date only where its differences
or its candidate causes changed. A break found again unchanged keeps the
date it was first seen, so a correction proposed for it takes effect from
when the difference arose. Every change is still its own entry.

## The first-use path

| # | Step | Whose | Where |
|---|---|---|---|
| 1 | **Choose its settings** | the plugin's admin | the plugin's **Settings**, under Manage |
| 2 | **Have access and a street source** | a deployment admin | access: a group holding `write` on the plugin over accounts; and a custody plugin running with a linked account among them. See [Give people access](administer-access.md) and [Using a custody plugin](using-a-custody-plugin.md). |
| 3 | **Confirm opening balances** | a person with `write` | the plugin's **Opening balances** page: every account in its scope has an opening balance in the book |
| 4 | **Reconcile** | the plugin, or a person with `write` | the plugin's **Reconciliations** page |
| 5 | **Work the breaks** | a person with `write` | the plugin's **Breaks** page: daily work, not a setup step |

Core's **Setting up**, on the plugin's **Summary**, judges the first two from its own records: every
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

An opening balance can be
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
a justified act. A person closes them, in one action on **Breaks**; or,
with the sample operations plugin's setting **Close cleared breaks automatically** (`auto_close_cleared`,
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
| **Refused** | the role runs as no service account | "Closing them automatically waits for a service account: the operations role runs as none. A deployment admin grants one, and an admin of this plugin chooses it on its Access tab." A person closes them in one action |
| **Refused** | the account is disabled, removed or not granted | "Closing them automatically was refused: …", with the reason. Nothing is closed |
| **Failed** | the plugin's act refused, or the call failed | "Closing them automatically was refused by this plugin's act: …" or "Closing them automatically failed: …". Nothing is closed |

None of them fails the reconciliation.

## Unmatched fills and outcomes

What an operations plugin may offer as a break's cause includes two more
sources:

- **An unmatched fill.** A fill the venue originated waits in the book,
  unmatched, until the `ems` accepts it, so the custodian's change shows as
  a break meanwhile. An operations plugin flags unmatched fills
  (`list_orders(execution_state="unmatched")`) and names the one matching a
  break (account, instrument, quantity, trade date: its own logic) as its
  candidate cause, `BREAK_CAUSE_CATEGORY_UNBOOKED_TRADE` with the fill's
  journal entry. After an accept the break clears on the next statement;
  after a DK it stays for a person. A fee on a DK'd fill stays unplaced,
  for you. See [Answer a venue-originated fill](answer-a-venue-originated-fill.md).
- **An event contract's outcome.** A custodian's payout of a resolved
  contract is not in the book yet, so it shows as a break, which the
  plugin may explain with `BREAK_CAUSE_CATEGORY_CORPORATE_ACTION` and the
  outcome's row key as its event reference, reading the lake's outcomes
  (`list_outcomes`), the one thing an operations plugin reads from the lake.

The operations suite's `names-an-unmatched-fill-as-a-breaks-cause` and
`hears-and-reads-an-outcome` hold them. The sample operations plugin names
an unmatched fill: a security's quantity differing by exactly one such
fill, traded on or before the statement's date, is offered an unbooked
trade first, the fill's book entry linked. It holds no event contract, so
it marks `hears-and-reads-an-outcome` not presented.

## An unrecognized security

A statement line too thin for any instrument record, such as a code and a
quantity with nothing else, is kept in the street, outside the book (see
[One ID per instrument](../concepts/one-id.md#why-a-thinly-described-security-stays-unrecognised)).
It is never silent: the sample operations plugin reads it with the
statement and records it as a break of its own category, **Unrecognized
security** (`BREAK_CATEGORY_UNRECOGNIZED_SECURITY`), naming no position:
the street record, the identifiers it carries and the quantity it states,
its cause unknown, brought up to date while it persists. Once the source,
or a person, gives what an instrument record needs, the next statement
records the position on it.

## Bookings

Once the `oms` [books](../concepts/booking.md) an order's executions and
hands the booking off, `operations` owns each allocation. The sample
operations plugin:

- **Names an unsettled allocation as a break's cause.** Each run reads the
  bookings handed off (`list_bookings`); a quantity or settled quantity
  short by exactly an allocation to the account whose intended settlement
  date has come is offered a fail, the booking's book entry linked.
- **Compares again when a booking is handed off** (`booking_updated`), for
  each account it allocates to.
- **Lists each held booking on Flags.** A held booking's alert
  (`alert_changed`, read on start with `list_alerts`) is a flag, and turns
  the status dot amber until the book clears it. A booking's ID opens it
  and its parts.
- **Replaces a booking's parts**, once handed off: **Replace the parts**
  (`correct_booking`, checked by `check_correct_booking`), each part an
  account and its quantity at the booking's average price, with why, such
  as a client having reneged. At `write`.
- **Sets a client's allocation**, where the firm is the client's
  custodian: an order's view, **Set the client's allocation**
  (`set_allocation_instruction`, checked by
  `check_set_allocation_instruction`). At `write`.

## Its figures

**Open breaks**, **Overdue breaks**, **Awaiting an opening balance**,
**Street missing** (only when any) and **Last reconciliation**: the
same on every operations plugin.

## Related

- [The book of record](../concepts/the-book-of-record.md).
- [The custodian's activity](../concepts/the-custodians-activity.md):
  what explains a break.
- [Prepared changes](../concepts/prepared-changes.md).
- [Run a plugin's autonomous work as a service account](run-a-plugins-work-as-a-service-account.md).
