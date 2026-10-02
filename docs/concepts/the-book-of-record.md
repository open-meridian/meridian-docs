# The book of record

There are two beliefs about what an account holds: the firm's and the
custodian's. The custodian's arrives in the **street store**, as custody
plugins report it. From contract v8 a deployment also keeps the firm's own:
the **book of record**, a core component, `bor`, with its own store. An
account enters the book once, with an opening balance a person answers for;
after that the book changes only by its own entries; and an `operations`
plugin reconciles it with the street on every statement, recording each
difference as a break.

The rule is short. **The street is what custodians say. The book is verified
against it, and never overwritten by it.** No statement is ever applied to the
book.

## The edge, the street and the book

What is held is recorded in three places, by three owners, and no one of them
is a copy of another.

| | What it holds | Who writes it |
|---|---|---|
| **The edge** | A plugin's raw records, as it received them from outside: a vendor's responses, a statement as sent | The edge plugin alone, in storage of its own. Core never reads it, and no other plugin does |
| **The street** | The custodian's view, as reported: statements, holdings and custodial positions, each statement's figures, and what of each holding is available and what cannot move | Custody plugins, through the street store. See [Record a holdings statement](../tutorials/record-a-holdings-statement.md) |
| **The book** | The firm's view: positions, lots, pending settlements, encumbrances, breaks, figures and each account's attributes, every change a journalled entry | An `operations` plugin, through the book; the dashboard sets an account's attributes |

A custody plugin converts what its vendor sends into the street's terms at
the edge, and may keep the raw records to debug a difference between what the
vendor said and what it recorded: the SnapTrade plugin keeps its raw
responses for a stated time and shows them on its own **Raw responses** tab.
The deployment giving an edge plugin storage of its own for them is specified
and not built yet, so such a plugin keeps them where its pod lets it, for as
long as the pod lasts.

The book and the street share no key, join or transaction. A break, or an
opening balance, names the street record it came from by value: the
statement, the custodial position's change, the custodian's as-of date.

## What the book holds

Every quantity is an exact decimal, and every amount carries its currency. A
value a source did not state is unset, never zero.

| Record | What it is |
|---|---|
| **Position** | An instrument and a side in one account. Its trade-date quantity is its settled quantity, plus what is pending on each value date, plus what its source did not say was settled or pending, by construction. Its settled quantity is unknown, never zero, while any of it is not stated. A position held under a placeholder instrument is flagged. |
| **Lot** | The book's own record of how a position was acquired: its open and original quantity, its cost and currency, its acquisition date, and where it came from. A position's open lots sum to its trade-date quantity; cash has none. |
| **Pending settlement** | Quantity pending on a value date, which may be years out, with whether it is failing and its new expected date where the source reports a fail. |
| **Encumbrance** | What of a position cannot move, as the latest statement states it: its kind (pledged, posted, on loan, blocked, restricted, in transit, or other with the source's own code), its quantity, to whom and where, and the margin agreement where the source names one. An attribute of the position, never a movement: its quantities do not change. |
| **Free quantity** | Derived, never reported: the settled quantity less the encumbrances. Unset while the settled quantity is unknown. It is what is free to trade. |
| **Break** | A difference between the book and the street, open, resolved or closed. See [Breaks](#breaks). |
| **Figures** | The account's figures for a business date, one set per margin agreement, as the street recorded them, with the collateral held under it and the custodian's own value and margin requirement for each position, labelled as the custodian's. A series, never a figure the book computed. |
| **Attributes** | The account's base currency, its default method of relieving lots when a sale names none, and its standing opening balance. |

The book records; it does not police. It computes no margin, no projection, no
scenario and no return, and converts nothing with the base currency. Plugins
that read it derive those, joined to reference and market data.

### Every change is an entry

The book is an append-only **journal**, partitioned by account. An entry is
never updated or deleted: a correction is a later entry naming what it
corrects. Every entry that moves a position is a set of movement lines, and a
position is its account's opening balance plus every entry's lines since.
Each entry records its kind (`opening-balance`, `adjustment`, `reversal`,
`break-recorded` and others, an open list), its cause, who made it, the plugin
instance that sent it, when it was sent, received and committed, and the
business date it stands for. Every record an entry changes is numbered from
the account's partition, with no holes, so a reader that misses one can tell.

The positions, breaks and figures a plugin reads are projections of the
journal, and `meridian-bor rebuild` makes them again from the journal alone.

## How an account enters the book

An account enters once, with an **opening balance**: as of a business date,
what it holds, position by position, with each position's trade-date
quantity, its settled quantity where the source states it, its pending
settlements and its lots, as the custodian or the prior system reports them.
It names its source, the date the source's figures are as of, whether they
are trade-date or settled, and the street records it was composed from. An
account holding nothing enters with an empty balance.

An opening balance is the fact every later break inherits, so **a person
confirms it**. An `operations` plugin composes it, typically from the
account's first completed statement, and shows it on its own page; a person
granted `write` on the account through the plugin confirms it there, with a
reason, and the book records that person as having made it. The book refuses:

- an opening balance with no person (`REFUSAL_REASON_ACTOR_REQUIRED`) or no
  reason (`REFUSAL_REASON_REASON_REQUIRED`);
- a second one for an account that has one standing
  (`REFUSAL_REASON_OPENING_BALANCE_RECORDED`);
- lots that do not sum to their position (`REFUSAL_REASON_LOTS_UNBALANCED`).

A holding the street records under a placeholder enters under that
placeholder, flagged, and does not hold the confirmation up; when the
instrument is identified, the book moves what it holds under the placeholder
onto the instrument, as an entry of its own. An error in an opening balance is
corrected by an adjustment with its reason, or, while no later entry moves the
account's positions, by reversing it and recording a new one naming the
reversed one.

## Reconciling each statement

On every completed statement after the opening balance, an `operations`
plugin compares the book with the street, account by account and margin
agreement by agreement: trade-date and settled quantities, cost and lots,
settled against pending, a position on one side only, and what cannot move.
When and how it compares is the plugin's behaviour; what it records is the
book's. From each statement it records:

- each difference, as a **break**;
- the account's **figures**, as the street recorded them;
- each position's **encumbrances**, as the statement states them.

These are findings, so the plugin may send them as itself, acting for nobody.
**Every difference is a break**: core has no tolerance, and a plugin may rank
or group breaks for its people but never drop one. A break that persists is
one break, brought up to date, not another each day. Until orders are booked
on the platform, every trade made away from it and every corporate action
shows as a break until it is resolved.

### Breaks

A break records the account, the position or account-level figure it
concerns, its category (trade-date quantity, settled quantity, cost or lots,
settled against pending, on the book's side only, on the street's side only,
or a figure), each differing field with the book's value and the street's,
what was compared, and the business dates it was first and last seen. Its age
is derived from those dates, never stored.

The plugin's matching offers **candidate causes**: an unbooked trade,
settlement timing, a cost or price difference, a corporate action, a fail, a
custodian error, or unknown, each with the item found to cause it. A person
confirms one, and sets who owns the break, its escalation level and its due
date. Then a person ends it, with a reason, in one of three ways:

- **Resolved**, by the entry that corrects the book in the same act: an
  adjustment with its movement lines, or a reversal of an entry. The book moves
  only by that entry, which names the break, so a correction traces back to
  what caused it.
- **Closed** with an explanation, moving nothing: a custodian's error, say.
- **Closed as cleared**, citing the statement where the difference was gone,
  moving nothing: a settlement landing, or the custodian catching up.

A break is never closed by silence, and a statement never overwrites the book.

## Who reads the book

A plugin reads and hears the book only within its read scope, as it reads the
street; see [Accounts](accounts.md#how-accounts-bound-a-plugin).

| Record | Written by | Read and heard by |
|---|---|---|
| Positions | `operations` | `portfolio`, `reporting`, `compliance`, `oms`, `operations` |
| Breaks | `operations` | `operations`, `oms`, `compliance`, `portfolio`, `reporting` |
| Figures | `operations` | `operations`, `portfolio`, `compliance`, `reporting` |
| Attributes | the dashboard, for a deployment admin; the standing opening balance by the book, when `operations` records one | `portfolio`, `reporting`, `compliance`, `oms`, `operations`, and the dashboard |

A position is delivered whole, its lots and pending settlements included, so
a plugin that hears it needs no second read.

## The Books tab

A deployment admin sees the book on the **Books** tab of the dashboard's
**Settings**. It lists every open account, one row each, with:

| Column | What it shows |
|---|---|
| **Account** | The account's name and identifier |
| **Base currency** | The account's base currency in the book |
| **Lot relief** | The method a sale relieves lots by when it names none: first in, first out; last in, first out; highest cost; lowest cost; or average cost |
| **In the book since** | The date the account's opening balance stands for, or *Not yet* before it has one |

**Edit** on a row opens a dialog headed with the account's name, such as
**Main's book**. It
sets the **Base currency**, three capital letters, and **Lot relief, when a
sale names none**, and asks for a **Reason**. Each attribute you change is its
own entry in the account's journal, with your reason and you as the one who
made it; saving with nothing changed is refused, saying the book holds these
already. An account may have attributes before its opening balance. If the
book does not answer, the tab says so, and the rest of Settings is drawn
without it.

The tab shows no position, lot or break. The dashboard reads every account's
attributes and no account's data, as a deployment admin reaches no account's
data: positions and breaks are for the plugins that read them, shown on their
own pages to the people granted access to them.

## Related

- [Accounts](accounts.md): the accounts a book is kept for, and what bounds a
  plugin's reach.
- [Record a holdings statement](../tutorials/record-a-holdings-statement.md):
  how the custodian's view reaches the street store.
- [Prove your plugin against a released runtime](../how-to/prove-a-plugin-against-a-released-runtime.md#the-book-of-record):
  print the book from a plugin's e2e, and compare it with what you expect.
