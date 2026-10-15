# The order lifecycle

An order reaches a venue through the
[book of record](the-book-of-record.md), and what the venue does comes back
into it. Plugins **ask and report**; the book **decides, journals and
publishes**. No plugin sets an order's state: it asks for a change (a
command), which the book may refuse with a reason and which then changes
nothing, or it reports a fact from the venue, which the book never refuses
for the state it arrives in. An order's status is derived from its journal,
one entry at a time, and stored nowhere as a fact.

!!! note "Tested against simulated venues"
    The order path's operations are `preview`: they may change in a later
    contract version, with a migration (see
    [The order path](../api/python-sdk.md#the-order-path)). Core proves the
    path end to end against a simulated venue only, which takes the FIX
    acknowledgements, with stand-in plugins for each role; no broker,
    brokerage, paper account or trading API is reached by those tests. The
    connectivity plugins a deployment can launch, SnapTrade, Alpaca and
    Tradier, are each tested against a simulated brokerage only (see
    [Trading through SnapTrade](../how-to/using-a-custody-plugin.md#trading-through-snaptrade)).

!!! note "TODO: contract v24, built, not released"
    Contract v24 adds, in core and open-meridian 0.28.0, to be released in
    chart `0.1.CHART24` (TODO: the date): [booking](booking.md), by which
    the `oms` books an order's executions to its accounts, with the block
    order, the error account, the hand-off, corrections, sleeve crosses,
    give-ups and alerts; and [orders on local records](#orders-on-local-records),
    a deployment setting. Every operation it adds is `preview`. Core proves
    booking against a simulated venue and stand-in plugins only.

## Who does what

The duties are kept apart by role, whichever plugins hold them. In one
plugin holding several roles they stay apart in the records, and
[access per role](access.md#access-per-role) refuses a person the role they
do not hold: a person with `write` on a plugin's `portfolio` role and not on
its `oms` role cannot release an order through it. **`portfolio` and the
`oms` own orders, the `ems` owns placements, and the connectivity plugin
owns fills.**

| Role or component | Does | Never |
|---|---|---|
| [`portfolio`](roles.md#portfolio) | Proposes orders, with their allocation instruction, sleeve and the fields its decision owns; amends and withdraws its own proposals; increases or reduces an order's quantity | Releases or places |
| [`oms`](roles.md#oms) | Releases or rejects proposed orders; sets time in force, execution instructions, the lot-relief method and capacity; claims, holds and pauses; records a telephoned or outside order; enters manual and done-away fills; aligns an order that does not tie out, with a reason; acknowledges late facts | Changes an order's instrument, account or side |
| [`ems`](roles.md#ems) | Claims, holds and pauses; proposes [child orders](#child-orders) under a released order; creates placements, each at one of the connectivity plugins linked to it, with the venue account code it mapped the account to; asks for their changes; enters manual fills; accepts a [venue-originated fill](#venue-originated-fills) to an order or answers it DK | Changes an ordered quantity |
| [`connectivity`](roles.md#connectivity) | The venue: sends the placements naming its instance, in the venue's vocabulary; reports acknowledgements, rejections, restatements, fills, busts, finality, charges and unknown outcomes in the contract's meanings, each with the raw record it keeps in its own storage; reports a fill on no placement and a venue's value-date roll, and tells its venue an accept or a DK where the venue takes it; records locates; publishes its venue's catalogue | Records an order or creates a placement; links accounts of its own: it reaches accounts only through its one `ems` |
| [`compliance`](roles.md#compliance) | Records checks and verdicts on an order version or a placement; requires approval by its policy; overrides a block for a person its policy allows; checks a short order's locate | Sets an order's state |
| [`operations`](roles.md#operations) | Hears executions and unplaced facts; acknowledges late facts; reconciles the book with the street, a traded position no longer a break | Moves a date in the book |
| [`reporting`](roles.md#reporting) | Reads orders, executions, their history and the fields recorded for reporting, and publishes outward | Anything on the order path |
| The book (`bor`) | Decides every transition, mints identifiers, holds the release gate, records the trading instructions and account attributes, expires orders by the deployment's clock, journals everything, and moves the trade-date position by reported fills, an unmatched fill only once accepted | Polices: limits, credit, restricted lists and which orders need approval are plugins' |
| The dashboard | Sets the [trading instructions](#trading-instructions) and whether an account's releases wait for compliance; makes a connectivity plugin available and links it to an `ems` | Decides an order |
| The conductor | Keeps each connectivity plugin's link to its `ems`, the `ems`'s map of accounts to venue account codes, and the venue's catalogue | |

**Core records; it does not police.** The book enforces four things: the
transition table, the equality of what is ordered and what is allocated at
release, a placement reaching only a connectivity plugin linked to the
placing `ems` and made available to whoever it acts for, and an account
within the scope of the plugin and person acting. Everything else -- limits,
credit, a restricted list, which orders need approval, how a plugin honours
a pause -- is a plugin's, and the book records what it did. Nothing on this
page is presented as meeting any market's or regulator's rule: a firm
decides what its controls must be, and which plugins provide them.

## An order's states and conditions

An order is in exactly one of **seven states**:

| State | Means |
|---|---|
| **Proposed** | Proposed, not yet released for working. Awaiting a check or an approval, it stays here. |
| **Refused** | Ended at proposal: a `compliance` verdict of refuse, or rejected by the `oms` asked to work it. |
| **Released** | Released for working, with nothing committed at a venue or in a child order. |
| **Working** | Released, with quantity committed at a live placement or child order, or filled in part. |
| **Filled** | Reported filled has reached the ordered quantity. |
| **Cancelled** | Ended by a cancel, or a withdrawal of a proposal. |
| **Expired** | Ended by its time in force, by the deployment's clock. |

Beside its state an order holds any of **nine conditions**, each with its
reason and the actor that set it: **change requested**, **approval
required**, **awaiting check**, **claimed**, **held**, **paused**,
**outcome unknown**, **does not tie out** (an overfill or a restatement)
and **late fact**.

A **placement** -- the part of an order sent to one connectivity plugin --
is in one of eight states, **queued**, **sent**, **working**, **done for
day**, **filled**, **cancelled**, **expired** or **rejected**, with the
conditions **change requested**, **outcome unknown**, **suspended** and
**awaiting trigger**.

### Status is derived from the journal

An order's status and every quantity on it are derived from its entries,
never stored: refused, cancelled or expired if an entry ended it; filled if
reported filled reaches the ordered quantity; working if released with
quantity committed or filled; released if released; proposed otherwise.

The quantities are **ordered**, **reported filled**, **final filled**,
**awaiting acceptance**, **committed**, **idle** and **leaves**. Committed
counts the open quantity at live placements and at live child orders. Idle
may go negative: over-commitment is shown, never refused. Several
placements may be live at once, at one venue or several.

## The transition table

The states, the conditions and every transition between them are one table,
in the contract before any code. It is published by meridian-schema as
`boundaries/transitions.json`; core's book is generated from it, and the
Python SDK carries it as `meridian/transitions.json`, so a plugin written by
one vendor and another written by a second agree on what "working" means
without talking to each other.

A command the table does not allow is refused with its reason code,
`REFUSAL_REASON_ORDER_STATE` where the order's state does not allow it, and
changes nothing. **A venue's fact is never refused for its state**: it is
accepted, recorded and flagged, a fill after a cancel took effect setting
**late fact** and leaving the order cancelled.

| Row | From | What happens | Caused by | To |
|---|---|---|---|---|
| 1 | proposed | A release, through the gate, its allocation equal to its ordered quantity | `oms` | released |
| 2 | proposed | Approval required by policy, then a person's approval | `compliance`, `oms` | released |
| 3 | proposed | A verdict of warn or block, then a person's override of a block, with a reason | `compliance` | released |
| 4 | proposed | A verdict of refuse, or a rejection by the `oms` asked to work it | `compliance`, `oms` | refused |
| 5 | released | A recall, with nothing committed or filled | `oms` | proposed |
| 6 | released | A placement or a child order commits quantity | `ems` | working |
| 7 | working | Every placement ends unfilled | the book | released |
| 8 | released, working | Placements created and ended; over-commitment shown, never refused | `ems` | unchanged |
| 9 | working | A pause or resume of working, for a person | `ems`, `oms` | unchanged |
| 10 | released, working | Fills: partly filled or filled, derived from the quantities | the book | working, filled |
| 11 | working | Fills while a cancel is pending; change requested stays | `connectivity` | working, filled |
| 12 | cancelled | A fill after the cancel took effect: accepted, late fact set | `connectivity` | cancelled |
| 13 | working | Fills while a replace is pending | `connectivity` | working, filled |
| 14 | released, working | A cancel or replace rejected by the venue: the request ends refused | `connectivity` | unchanged |
| 15 | released, working | A second change while the first is pending, tracked | `ems`, `oms` | unchanged |
| 16 | released, working | A cancel of an unacknowledged placement, or one crossing the acknowledgement | `ems`, `oms` | unchanged |
| 17 | filled | A bust (a superseding fact) | `connectivity` | working |
| 18 | filled | An increase, applied: `portfolio`'s, its allocation amended in the same act; the `oms`'s only to align | `portfolio`, `oms` | working |
| 19 | working | A reduction, applied: `portfolio`'s; the `oms`'s only to align | `portfolio`, `oms` | filled |
| 20 | working | A placement done for day, then restated; its quantity stays committed | `connectivity` | unchanged |
| 21 | released, working | An immediate-or-cancel or fill-or-kill placement unfilled: the order cancelled if its own time in force is one of these, back to idle otherwise | `connectivity` | cancelled, released, working |
| 22 | released, working | A venue-initiated cancel, replace, quantity cut, cancel at close or restatement; past the order's intent, late fact and does not tie out | `connectivity` | unchanged |
| 23a | none | An order the book did not create: telephoned or placed outside, recorded by the `oms` for a user and never through the gate | `oms` | released, working, filled |
| 23b | none | A client's order received at a broker, proposed into the client's account | `portfolio` | proposed |
| 24 | working | A placement held at the venue, then triggered | `connectivity` | unchanged |
| 25 | any | A duplicate identifier or a possible resend: a repeat answered as the first, a key reused for another command refused, a resent fact recognised | any | unchanged |
| 26 | released, working | A placement sent, its outcome unknown; resolved by a status reply or a fact, never treated as rejected | `connectivity` | unchanged |
| 27 | released, working | A manual fill, or a fill from inventory, entered for a person | `ems`, `oms` | working, filled |
| 28 | any | A trade done away, recorded against the order | `oms`, `connectivity` | unchanged |
| 29 | any | A bust or correction after a cancel or a done for day (a superseding fact) | `connectivity` | unchanged |
| 30 | any | Finality moves: matched, included, final, or failed; a failed execution reopens the order if it no longer reaches ordered | `connectivity` | unchanged |
| 31 | working, filled | An overfill: accepted, does not tie out until a justified alignment | the book | filled |
| 32 | any | Booking (a later revision): the order's state unchanged | `oms`, `operations` | unchanged |
| i1 | proposed | A withdrawal | `oms`, `portfolio` | cancelled |
| i2 | none | A child order proposed under a released parent: released on creation, within the parent, not through the gate | `ems`, `oms` | released |
| i3 | released, working | An order cancel: each live placement and child order asked to cancel; cancelled when none is live | `oms`, `ems` | cancelled |
| i4 | released, working | The order's time in force ends, by the deployment's clock; live placements asked to cancel first | the book | expired |
| i5 | any | A trading instruction set: recorded and broadcast; no order changes state, nothing refused or cancelled for it | the dashboard | unchanged |
| i6 | released, working | A cancel under a stop: each working plugin's cancel, its cause the stop's entry; a connectivity plugin's cancel at the venue reported at once | `oms`, `ems`, `connectivity` | cancelled |
| i7 | proposed | A day order never released: its day ends, by the deployment's clock, awaiting a check or an approval included | the book | expired |

The table holds an execution's rows beside the order's
(see [Venue-originated fills](#venue-originated-fills)):

| Row | From | What happens | Caused by | To |
|---|---|---|---|---|
| e1 | none | A fill on a placement the book holds, or entered manual or done away against an order | `connectivity`, `ems`, `oms` | matched |
| e2 | none | A fill on no order and no placement, its venue account code mapped: moving nothing | `connectivity` | unmatched |
| e3 | unmatched | An accept, to an existing order or a new one: the placement created at filled, the position moved as of the trade date | `ems` | matched |
| e4 | unmatched | A DK, with its reason: closed, never moving a position | `ems` | DK |
| e5 | unmatched | A correction: the correcting fill unmatched in its place | `connectivity` | unmatched |
| e6 | unmatched | A bust: closed with nothing to answer, left out of the unmatched list | `connectivity` | unchanged |
| e7 | DK | A later fill of the same venue order, unmatched on its own | `connectivity` | unchanged |
| e8 | matched | A bust or correction: the position reversed by its own entry | `connectivity` | unchanged |

Each row also names the reason codes a command meeting it may be refused
with; see [Refusals](#refusals). The table changes only by a contract
revision, with its migration.

## Proposing an order

`portfolio` proposes an order into an account; the `oms` proposes too. An
order names its instrument by the deployment's instrument ID, its account
and its side (buy, sell, sell short, or sell short exempt, a short naming
the [locate](#locates) it relies on). **Its instrument, account and side are
its identity and never change**: a different one is a new order.

- **Exactly one of a quantity or a cash quantity.** An order states a unit
  `quantity` or a `cash_quantity`, never both and never neither; either
  mistake is refused `INVALID_ARGUMENT`, naming both fields. An order of 0
  quantity is refused, naming `quantity`.
- **Its type and limit**, and on a currency pair its dealt currency, a cash
  instrument, and its **quote currency**
  (`quote_currency`): the pair's second currency as it is quoted, USD for
  EUR/USD, by its cash instrument's ID, so a market order, which states no
  price, still names both currencies. The dealt currency still says which
  of the two the quantity is in, and a limit or stop is in the quote
  currency. A quote currency naming the order's own instrument is refused
  `INVALID_ARGUMENT` naming `quote_currency`, and a limit or stop priced in
  another currency naming `limit_price` or `stop_price`, as is a change's
  limit (`change.limit_price`). Optionally legs, each an instrument, a side and a ratio; a
  stop price, an expiry date or time where its type or time in force needs
  one; and the standard execution instructions (not held, do not reduce, do
  not increase, reduce only, a self-match prevention instruction).
- **Its allocation instruction**: the accounts and amounts or weights it is
  for. With none, the whole is in the order's own account.
- **Its sleeve**, a part of the account the order is for, empty for the
  account's unsleeved part.
- **Who decided it**, where that differs from who entered it. Who entered
  it is stamped from the actor; who executed it is the placement's and the
  entered execution's.
- **Fields recorded for reporting**, each set by the plugin that knows it:
  the customer's and firm's identifiers, when it was received with the
  precision the plugin's clock achieves, the quote at the time it was
  received (bid, ask, their sizes, the time it was taken, and whether it is
  the consolidated best bid and offer or one named venue's), the parties'
  LEIs where given, and the orders a firm's order represents. Core stores
  them and reports nothing; a `reporting` plugin reads them and publishes
  outward.
- **References kept for a later revision**, carried empty: an axe's
  source and counterparty on the order, and on a placement the RFQ and the
  axe it answers (`rfq_id`, `axe_id`). A plugin may send them; they mean
  nothing until the RFQ revision defines them.

A proposal names an idempotency key, so a resend is applied once. An
incomplete instrument record, or a required field missing, is refused
`REFUSAL_REASON_INCOMPLETE`, naming each field.

**Proposing is an act a person, an agent or a service account takes through
a plugin.** The deployment admin's ceiling, the plugin admin's level per
act, the second pair of eyes and a service account's setting decide whether
it is made or prepared (see [Agents and service accounts](#agents-and-service-accounts)).
A prepared proposal is a [prepared change](prepared-changes.md) and nothing
in the book until a person makes it; made, the order's entry names the
prepared change it came from.

## Child orders

An `ems` working a strategy in house, a time-weighted or volume-weighted
slicing for instance, slices a released order into **child orders** (the
`oms` may too). Each child is proposed naming its parent, a split link
(`OrderLink`, kind `split`, with the `parent_order_id`).

- **In its parent's account, with its parent's instrument and side.** A
  child naming another instrument or side is refused `INVALID_ARGUMENT`,
  naming the field.
- **Released on creation, within its parent.** It does not pass the release
  gate or wait for compliance again: the parent passed them. A child under
  an order that is not released (still proposed, or ended) is refused
  `REFUSAL_REASON_ORDER_STATE`.
- **No allocation instruction of its own.** Its parent's governs.
- **It commits its parent's quantity** while it is live, as a placement
  does, so the parent's committed and idle count it.
- **Its executions are its parent's.** A fill on a child's placement is
  recorded once, on the child, and counts toward the parent's reported and
  final filled; the position moves once.
- **A child may have children**, quantities rolling up the chain to the
  top.
- **Cancelling or expiring a parent** asks each live child, and each live
  placement, to cancel first.

## The release gate, and waiting for compliance

The `oms` releases a proposed order, for a person or its role's service
account. The book checks, in this order, and refuses with the first that
fails:

1. **The allocation equals the ordered quantity**
   (`REFUSAL_REASON_ALLOCATION_UNBALANCED`).
2. **No block stands without an override** (`REFUSAL_REASON_CHECK_BLOCKS`).
3. **Approval, if required, has been given** (`REFUSAL_REASON_APPROVAL_REQUIRED`).
4. **The order's state allows it** (`REFUSAL_REASON_ORDER_STATE`).

And, where the account **waits for compliance**, every `compliance` plugin
covering the account must have recorded a verdict on this version of the
order. Until then the release refuses nothing: the order stays proposed,
**awaiting check**, with no bound but its own time in force.

**An account waits for compliance by default.** Every account does, each
recorded by its own entry. A deployment admin changes it per account on the
**Accounts** tab (see [Set trading instructions and whether releases wait](../how-to/set-trading-instructions.md#whether-an-accounts-releases-wait-for-compliance)).
A deployment with no `compliance` plugin therefore releases nothing until a
deployment admin turns waiting off for the account, by design.

**A day order never released expires at its day's end**, by the
deployment's clock, its awaiting check or approval ending with it (row i7).
A good-till-cancelled order never released never comes due.

**The book's approval is not the second pair of eyes.** Approval required
is the order's own condition in the book, set by a `compliance` or `oms`
plugin's policy and given by a person. The
[second pair of eyes](prepared-changes.md#a-second-pair-of-eyes) is the
dashboard's gate on who makes an act, before any command exists. A firm may
use either or both; neither is read from the other.

## Placements, and the connectivity plugins an ems may use

An `ems` creates a **placement** for part of a released order at one of the
connectivity plugins linked to it: its quantity, limit, time in force, the
venue account code it maps the order's account to on that plugin, a strategy
to work at the venue where there is one, its destination (a
[venue ID](venues.md)) and route type. The placement reaches **that
connectivity plugin alone**: no other instance of the role hears it.

**Each connectivity plugin is linked to exactly one `ems`**; an `ems`,
usually a desk, may have many. Three decisions, in three places, make a
connectivity plugin usable (see
[Route orders through a connectivity plugin](../how-to/route-orders-through-a-connectivity-plugin.md)):

- **A deployment admin makes it available**, or withdraws it.
- **The `ems`'s admin links an available one to their `ems`**, and chooses
  who may route through it: people, service accounts and user groups. A
  connectivity plugin already linked to another `ems` is refused
  (`REFUSAL_REASON_CONNECTIVITY_LINKED`).
- **The `ems`'s admin maps each account** to the venue account code it
  trades under at that connectivity plugin, on the `ems`'s own page, within
  the accounts a deployment admin granted the `ems`.

A placement at a connectivity plugin not linked to the placing `ems`, or not
made available to the person or service account it acts for, is refused
`REFUSAL_REASON_CONNECTIVITY_NOT_ALLOWED`, and **the refusal is recorded**,
where every other refusal changes nothing: an entry on the order names the
`ems`, the connectivity plugin asked for, the actor and the reason, heard by
the `ems` and `compliance`.

**Who checks it.** When a person opens an `ems`'s page, or an agent or a
service account calls one of its acts, the dashboard works out the
connectivity plugins that user may route through for that `ems`, from the
links and the user groups the person is in, and puts only those instances
in the claims the plugin receives (`Caller.connectivity_instance_ids`). The
plugin learns which connectivity plugins the user may choose, **never the
user's groups**. The `ems`'s sidecar checks each placement against that set,
whatever the page drew, and the book refuses on its verdict.

**Unlinking or withdrawing** leaves the placements already made as they
are; a new placement through it is refused. A connectivity plugin linked to
no `ems`, or withdrawn, reaches no account and hears nothing.

**The venue's catalogue.** A connectivity plugin publishes, per venue
account code its `ems` mapped, what its venue offers: order types with
their time-in-force values, the broker's strategies with their parameters
(described on the model of FIXatdl, so a broker's published definitions can
be imported rather than keyed again), and eligibility for the instruments
it states (fractionable, shortable, borrow status, an options level). The
`ems` and the `oms` read it and build a typed order from it; the
connectivity plugin constructs the venue's own message, so an `ems` never
meets a venue's wire format. What is not listed is rejected `unsupported` if
sent, by the venue's plugin, never refused by core. It also
says which acknowledgement the venue takes of an accepted or DK'd
venue-originated fill (`execution_acknowledgement`; see
[What the venue is told](#what-the-venue-is-told)), unspecified reading as
none.

### Cancelling or replacing a placement

The `ems` or the `oms` asks to cancel or replace a placement, the change
naming its kind and, for a replace, the new quantity, limit and time in
force. **The placement carries its own change requests**
(`change_requests`), each with that change and its outcome (pending,
applied or rejected), so its connectivity plugin, hearing the placement,
tells a cancel from a replace by the kind and reads a replace's new terms
from it, never from a condition's reason. Several may be outstanding at
once. An order's own change requests stay on the order.

## What the venue reports

A connectivity plugin reports what the venue did, each report naming the
raw record it was converted from, kept in the plugin's own storage (see
[The archive](the-archive.md)):

- **A placement's progress:** sent, acknowledged (with the venue's order
  ID and the routing time), replaced, done for day, restated with its
  reason, suspended, triggered, cancelled, expired, or rejected with its
  reason: **unsupported** (what the plugin or the venue does not offer for
  this account), **venue rejected** (the catch-all, with the venue's
  reason as reported only where no contract reason maps) or **held by
  pre-trade check** (the plugin's own check held it back).
- **Outcome unknown**, never a rejection: the connection was lost, the
  request went unanswered, or the venue's status maps to nothing (with the
  status as reported). The quantity stays committed, and the plugin
  resolves it by asking the venue, never by resending.
- **An execution:** its quantity, price, trade time and trade date, the
  venue's execution ID (or one derived the same way every time), its kind
  (venue reported, manual, done away, inferred) and source (primary or drop
  copy, deduplicated on the venue's identifiers), its finality, its fees (a
  rebate negative), the counterparty where known, its **settlement date**,
  and the fields recorded for reporting. A bust or correction names the
  execution it supersedes, with the date it takes effect; nothing is
  edited. A fee's kind is exchange, cancel, network,
  **financing** (`FEE_KIND_FINANCING`, a rolling position's cost or
  credit of carrying it to the next value date) or **commission**
  (`FEE_KIND_COMMISSION`, the broker's, which FIX keeps apart from its
  other fees).
- **A charge** with no fill, a venue's cancel fee, moving cash and counting
  toward no quantity; also a rolling position's financing
  at a roll, on the placement whose fill opened it.

**It reports on the `ems`'s placements, and on nothing of its own.** A
connectivity plugin records no order and creates no placement: its
`RecordOrder` or `CreatePlacement` is refused by its sidecar,
`PERMISSION_DENIED`, as any operation its role does not hold. A telephoned
or outside order is the `oms`'s to record, for a person or its service
account (row 23a). A fill the venue reports on no placement the `ems`
made, such as a liquidation or an order placed in the broker's own app, is
reported as such and waits for the `ems`'s answer: see
[Venue-originated fills](#venue-originated-fills).

**The settlement date is the venue's, or worked out in core.** The date the
venue states is kept as stated. Where it states none, or where the plugin
also asks, the plugin asks core for the date from the
[settlement calendars](settlement-calendars.md) and carries the computed
date with its basis, the rule and each calendar with their versions, beside
the stated one. The pending lines take the stated date, else the computed
one. A fill with no settlement date is refused, naming `settlement_date`:
the book never guesses one.

**A fact the book cannot place is kept, never dropped.** A well-formed fact
naming no placement the book holds, or a venue account code the `ems`
mapped to no account, is kept as an **unplaced fact** with its reason,
heard by `operations`, and placed by its own entry when a later record
claims it. The connectivity plugin's admin view counts the facts kept with
no account, **Unplaced facts**, beside its own figures.

## Fills move the book's positions

Reported fills move the account's trade-date position at once:

- **A buy** covers a short first, then opens a lot at the fill's price and
  quantity, acquired on its trade date.
- **A sale** relieves lots by the order's lot-relief method, or the lots it
  names, or the account's default (see [In the book](accounts.md#in-the-book)).
- **The security and the cash** are pending to the settlement date, the
  stated one else the computed one; fees are their own cash lines.
- **A bust or a correction** reverses what its superseded execution moved,
  by its own entry, so positions and fills never disagree.
- **The sleeve** an order names is carried by its executions, and by the
  positions, lots and pending lines they move; reconciliation compares the
  account as the sum of its sleeves.
- **An unmatched fill moves nothing** until the `ems` accepts it, and one
  answered DK never does (see
  [Venue-originated fills](#venue-originated-fills)).
- **A venue's value-date roll** moves pending lines to the next value date,
  the trade-date position unchanged (see
  [A venue's value-date roll](#a-venues-value-date-roll)).

`operations` reconciles the next statement against the book, so a
traded position is not a break. A fill's lots are
provisional until the `oms` books the executions to their accounts, and a
fill in a currency other than the account's base currency opens lots: see
[Booking](booking.md).

## Venue-originated fills

**A fill the venue originates** -- an order placed in
the broker's own app, a liquidation -- reaches the book through the
connectivity plugin that hears it, and waits there until the `ems` answers
it. Positions move only when it is accepted.

1. **The connectivity plugin reports only the fill**, and any fee on it, on
   no order and no placement: its instrument (`instrument_id`), side
   (`side`) and the venue's order ID (`venue_order_id`, FIX 37), each
   required on such a fill and refused `INVALID_ARGUMENT`, naming the
   field, without it, and the venue's client order ID
   (`venue_client_order_id`, FIX 11) where the venue sent one. A venue's
   open orders are not recorded. The sidecar stamps the account from the
   `ems`'s map; an unmapped code is kept as an
   [unplaced fact](#what-the-venue-reports).
2. **The book holds it unmatched.** It mints an `EXE-` ID and records an
   execution with no order and no placement, its state **unmatched**. The
   linked `ems` hears it, and the `ems`'s and the operations plugins' pages
   flag it, with no time limit. The dashboard shows no unmatched fill.
3. **The `ems` answers it**, for a person or as its role's
   [service account](service-accounts.md), at the levels its admin sets:
   it **accepts** it to an order, or answers it **DK** (don't know). Core
   never answers on its own. See
   [Answer a venue-originated fill](../how-to/answer-a-venue-originated-fill.md).

An execution's state is derived from the journal, never stored:

| State | Means |
|---|---|
| **Matched** (`EXECUTION_STATE_MATCHED`) | On a placement: every fill on a placement the `ems` made, and an unmatched fill once accepted |
| **Unmatched** (`EXECUTION_STATE_UNMATCHED`) | Reported on no placement, its account mapped, waiting for the `ems`'s answer |
| **DK** (`EXECUTION_STATE_DONT_KNOW`) | Answered DK: recorded and closed, never moving a position |

### Accept

`AcceptExecution` links 1 to 500 unmatched fills to an order, with a note.
The fills share one account, instrument, side, connectivity plugin and
trade date, since the placement it creates has one of each; a liquidation
arriving in many prints is accepted in one act.

- **To an existing order** (`matched_order.order_id`) the accepting `ems`
  may place against: released, working or filled, never ended, and not
  claimed by another. A buy fill matches a buy order; any sell matches the
  order's sell, the venue's marking kept on the execution. An accept that
  would take the order's filled quantity past its ordered quantity is
  refused: accept to a new order instead, or have `portfolio` increase the
  order first.
- **To a new order** (`matched_order.new_order`, its `sleeve` and `note`),
  made from the fills: their account, instrument, side, trade date and
  venue order ID, ordered quantity equal to the accepted quantity, order
  type market, time in force day, no limit. It is recorded **filled**,
  never through the release gate, its origin
  `ORDER_ORIGIN_ACCEPTED_EXECUTION`, so it says it was entered after the
  trade, by whom and when. The note is kept on the accept's entry.

The book then creates the `ems`'s placement at **filled**, at the
connectivity plugin that reported the fills, with the fills' venue account
code, venue order ID and place of execution, its routing time left 0, and
links the fills to it. **The trade-date position moves as of the fills'
trade date**, by an entry recorded at the accept, so a point-in-time read
from before the accept shows no position, and past reconciliations stay
true to what was known. `compliance` hears the order and the executions and
may record a check after the trade; a block on a filled order gates nothing,
but stands until a person overrides it with a reason.

### DK

`DontKnowExecution` answers 1 to 500 unmatched fills DK with a reason from
a closed list mirroring FIX's DKReason (127), and text, required with
**other** as FIX requires Text (58). The execution keeps both (`dk_reason`,
`dk_text`). "DK", not "reject": a reject is a venue's, or an approval's.

| Reason | |
|---|---|
| `DK_REASON_UNKNOWN_INSTRUMENT` | Unknown instrument |
| `DK_REASON_WRONG_SIDE` | Wrong side |
| `DK_REASON_QUANTITY_EXCEEDS_ORDER` | Quantity exceeds order |
| `DK_REASON_NO_MATCHING_ORDER` | No matching order |
| `DK_REASON_PRICE_EXCEEDS_LIMIT` | Price exceeds limit |
| `DK_REASON_CALCULATION_DIFFERENCE` | Calculation difference |
| `DK_REASON_OTHER` | Other, with its text |

### What the venue is told

The connectivity plugin hears its fill accepted or answered DK
(`ExecutionRecorded`, directed to the instance that reported it, and on an
accept the placement created) and tells its venue where the venue takes it,
as its [venue catalogue](#placements-and-the-connectivity-plugins-an-ems-may-use)
says (`execution_acknowledgement`):

| The catalogue says | On an accept | On a DK |
|---|---|---|
| `EXECUTION_ACKNOWLEDGEMENT_BN` | FIX ExecutionAcknowledgement (35=BN), ExecAckStatus (1036) Accepted | The same message, ExecAckStatus "Don't know / Rejected", with its DKReason (127) |
| `EXECUTION_ACKNOWLEDGEMENT_DONT_KNOW_TRADE` | Nothing: DontKnowTrade has no accept | DontKnowTrade (35=Q) |
| `EXECUTION_ACKNOWLEDGEMENT_NONE`, or nothing | Nothing | Nothing: the `ems`'s page says "the venue is not told" before the DK |

No record is kept per acknowledgement sent: FIX sends no reply to it.

### After the answer

- **Later fills** of the same venue order: after an accept, on the placement
  the accept created, as on any placement. On an order and placement the
  accept made, the ordered and placed quantities follow, so they stay
  filled and tie out; on an existing order, quantity past ordered is an
  overfill, **does not tie out**, which the `oms` aligns. After a DK, a
  later fill arrives unmatched and is answered on its own, the earlier DK
  shown beside it.
- **A bust** of an unmatched fill closes it with nothing to answer: it stays
  unmatched, superseded by the bust, and leaves the unmatched list and
  counts. **A correction** stays unmatched, the correcting fill listed in
  its place. An accept or a DK naming the superseded fill is refused. After
  an accept, a bust reverses the position by its own entry, as any bust
  does; a wrong accept is fixed so.
- **A fee on the fill** rides on it and moves cash only on accept. A charge
  on no placement is kept unplaced (`UNPLACED_REASON_UNKNOWN_PLACEMENT`,
  "a placement the book does not hold, or none"); the connectivity plugin
  reports it again on the placement the accept created, which places it.
  After a DK it stays unplaced, for `operations`.
- **Reconciliation.** Until the accept, the custodian's change shows as a
  break. `operations` may name the unmatched fill its candidate cause
  (`BREAK_CAUSE_CATEGORY_UNBOOKED_TRADE`, with the fill's journal entry in
  `book_entry`); after an accept the break clears on the next statement,
  after a DK it stays for a person. The listing filters by an execution's
  state (`execution_state`), so the `ems`'s and operations' counts read
  only the unmatched fills.

The execution's transitions, rows `e1` to `e8`, are in the
[transition table](#the-transition-table) beside the order's.

## A venue's value-date roll

A retail FX broker never settles a spot position: at its
daily roll, 17:00 New York, it moves the position's value date to the next
spot, and charges or credits the financing separately. The connectivity
plugin reports the roll (`ReportValueDateRoll`): the venue account code,
the pair's two cash instruments, the value date left
(`from_value_date`), the new value date and its basis as the date read
gives them for the roll's moment (`to_value_date`, `value_date_basis`, from
[settlement calendars](settlement-calendars.md), never a date the plugin
works out), the moment (`rolled_at_ns`), the `CHG-` IDs of the financing
charges it reported first (`charge_ids`, each `FEE_KIND_FINANCING`), and
its raw record.

- **One entry per roll**, of kind `value-date-rolled`, moves the account's
  pending lines in the pair's two cash instruments that this plugin's fills
  or rolls on the code put on the old date to the new one, each sleeve's
  own. The trade, its executions and its lots are untouched, and so is the
  trade-date position. No transition: the book never moves a date by
  itself; the venue moved it.
- **Kept unplaced, never refused or dropped:** a roll on a venue account code
  no `ems` mapped (`UNPLACED_REASON_UNMAPPED_VENUE_ACCOUNT`), and one that
  finds nothing pending to move (`UNPLACED_REASON_NOTHING_PENDING`), kept in
  the account's partition so `operations` hears the mismatch. A malformed
  roll is refused `INVALID_ARGUMENT`, naming the field: a pair that is not
  two cash instruments (`pair`), a missing date or basis, or a new date not
  after the old.
- **A bust or correction after a roll** reverses the fill's pending lines at
  their current value date, followed through the rolls since.
- **A fill booked after its trade was rolled** -- reported late, or a
  venue-originated fill accepted days later -- pends to the value date it
  was recorded with. The connectivity plugin reports a **catch-up roll**
  for it, from that date to the current one, the date read's answer as for
  any roll; until then the custodian's difference is a break.

A connectivity plugin whose venue settles its trades never reports a roll.

## Trading instructions

A **trading instruction** is **active**, **pause** or **stop**, set on a
target with a reason:

| Set by | On |
|---|---|
| A deployment admin | An account, **All accounts**, a plugin, a person or a service account |
| A plugin's admin | Their plugin, or a person, a service account or an account within it, naming the plugin |

The level it was set at is stamped by the dashboard from the setter's
access, never entered. **The most restrictive in force governs**, stop over
pause over active, so a plugin's admin narrows a deployment admin's
instruction and never lifts it; an instruction is lifted only at the level
that set it. **A user group is not a target yet**: an instruction naming
one is refused `INVALID_ARGUMENT`, naming `target.user_group_id`, until a
later revision resolves a group's people.

**The book refuses and cancels nothing for an instruction.** It records it,
broadcasts it to every `oms`, `ems`, connectivity, `portfolio` and
`compliance` plugin whatever their accounts, and journals any order sent
anyway with the instruction in force. **Each plugin honours it**, as its
development provides: on a pause it sends no new orders; on a stop it sends
none and cancels its working orders. A connectivity plugin cancels at the
venue at once, without waiting for the book, and reports each cancel as a
fact, its actor the venue and its cause the stop's entry, so no level or
setting stands between a stop and the venue.

Set them on the **Trading instructions** page or through
`dashboard__set_trading_instruction`: see
[Set trading instructions](../how-to/set-trading-instructions.md).

## Orders on local records

An order may name an instrument whose record is still a
deployment's local `LCL-` record, one the platform has not answered for
(see [One ID per instrument](one-id.md)), while the deployment's setting
**Allow orders on local records** is on, as it is by default. The order is
marked "local record: not priced".

Off, a proposal naming a local record and an accept of a venue-originated
fill on one are refused, `REFUSAL_REASON_LOCAL_RECORD_NOT_ALLOWED`, from
the change on. Orders already working continue, as do their placements and
child orders; a trading instruction stops them. An order the `oms` records
for a telephoned or outside order is recorded whatever the setting. A
plugin that proposes or accepts reads the setting
(`ReadLocalRecordOrders`) so it can tell a person before sending. A
deployment admin sets it on the **Trading instructions** page (see
[Allow orders on local records](../how-to/set-trading-instructions.md#allow-orders-on-local-records)).

## A command naming a record by its ID

Releasing, checking, approving, claiming, placing, changing, reporting on
or acknowledging names an order, a placement, a change request or a locate
by its ID, not its account. The sidecar stamps such a command with the
sending plugin's write scope, narrowed to the person's write access where
it acts for one; the book finds the record's account and refuses a command
whose account is outside them, `PERMISSION_DENIED` with no reason code,
changing nothing. A connectivity plugin's scope is the accounts its `ems`
mapped venue account codes to on it, while it is available and linked.

## Locates

A fund's connectivity plugin records a **locate** it requested of its prime
broker -- the instrument, the quantity asked, the venue account code --
often before any order, and then the prime's answer on the same record: the
quantity approved, the rate, the expiry and the prime's ID. `compliance` or
the `oms` records each use of it: a **reservation** for an order, its
**give back** on a cancel or at the day's end, or its **consumption** by
fills, the remaining quantity derived. When a locate is used up is that
plugin's logic: core keeps the records for either way, and refuses nothing
for a short order without one. A use of an expired locate is refused
`REFUSAL_REASON_ORDER_STATE`.

## Agents and service accounts

Every order-path act a plugin offers a person -- propose, release, place,
cancel, override -- is one of that plugin's acts like any other, with a
check tool so it can be prepared. The book has no level of its own: what
agents may do with each act, and its second pair of eyes, are set by the
deployment admin and the plugin's admin (see
[What agents may do](prepared-changes.md#what-agents-may-do)).

An automated strategy, or an `ems` placing on its own, acts as its role's
[service account](service-accounts.md), through the plugin's own acts, the
levels and the gate applying. Its call names the
**algorithm** it runs, one its plugin's version declares (`algorithm_id`):
the sidecar checks it and stamps it on every command the act sends, so none
can name another, and the book records it on the entry's service account
actor, where a `reporting` plugin reads which algorithm decided or
executed. A person's act names none. There is no agent actor: an agent's
call is the person's act.

## What is recorded

Every entry names its typed actor -- a person, a service account (with its
owner and the algorithm its call named), the venue through the connectivity
plugin reporting it, or the system (the book's own act, such as an expiry) --
the instance that sent it, the time on the message, the times the book
received and committed it, and the sequence of the trading instructions in
force, so a replay decides the same way. A command
is answered only after its entry commits, and applied once, on its message
or its idempotency key; a venue fact repeated with the same venue
identifiers is applied once.

Each change is published with the whole new record: an order's to the
`oms`, `ems`, `compliance`, `portfolio`, `operations` and `reporting`
plugins within their read scopes; a placement's to the `ems`, `oms` and
`compliance`, and to its connectivity plugin alone of its role; executions
to the order's hearers and to the connectivity plugin
that reported each, and an unmatched one to the `ems` linked to it;
unplaced facts to `operations`. A plugin catches up
after a gap by reading the records changed since the watermark it last
saw; `compliance`, `reporting`, `operations` and the `oms` read an order's
whole history from its first entry.

## Refusals

| Code | When |
|---|---|
| `REFUSAL_REASON_ORDER_STATE` | The order's or placement's state does not allow the command; a child under an order that is not released; an `oms` quantity change that is not an alignment, or any `ems` quantity change; a use of an expired locate |
| `REFUSAL_REASON_ALLOCATION_UNBALANCED` | A release whose allocation does not sum to the ordered quantity |
| `REFUSAL_REASON_CHECK_BLOCKS` | A release with a block standing and no override |
| `REFUSAL_REASON_APPROVAL_REQUIRED` | A release where approval is required and not given |
| `REFUSAL_REASON_CLAIMED` | A change to an order's placements or child orders by other than the instance holding its claim; an accept onto an order another claims |
| `REFUSAL_REASON_QUANTITY_EXCEEDS_ORDER` | An accept whose quantity, added to what the order has filled, passes its ordered quantity |
| `REFUSAL_REASON_EXECUTION_STATE` | An accept or a DK naming an execution answered already, or superseded by a bust or a correction |
| `REFUSAL_REASON_EXECUTIONS_DIFFER` | An accept naming fills of more than one account, instrument, side, connectivity plugin or trade date, or a fill whose side is the order's opposite |
| `REFUSAL_REASON_CONNECTIVITY_NOT_ALLOWED` | A placement at a connectivity plugin not linked to the placing `ems`, or not made available to whoever it acts for; recorded. Also an `ems`'s mapping at a connectivity plugin not linked to it |
| `REFUSAL_REASON_CONNECTIVITY_LINKED` | A connectivity plugin linked to a second `ems` |
| `REFUSAL_REASON_ACCOUNT_NOT_LINKABLE` | An `ems`'s mapping naming an account not granted to it (`FAILED_PRECONDITION`) |
| `REFUSAL_REASON_IDENTIFIER_IN_USE` | An identifier already used for another record |
| `REFUSAL_REASON_ACTOR_REQUIRED` | A command other than a fact report with no person or service account behind it, an accept or a DK among them; an approval or override with no person |
| `REFUSAL_REASON_REASON_REQUIRED` | A justified act, an override or an instruction, with no reason |
| `REFUSAL_REASON_LOCAL_RECORD_NOT_ALLOWED` | A proposal naming a local record, or an accept of a fill on one, while orders on local records are off |
| `REFUSAL_REASON_BOOKING_UNBALANCED`, `REFUSAL_REASON_ACCOUNT_NOT_INSTRUCTED` | A booking that does not tie out, or allocates to an account its instruction does not name; see [Booking](booking.md#refusals) |
| `REFUSAL_REASON_INCOMPLETE` | A proposal missing a required field, each named; an order recorded naming an instrument whose record is incomplete |
| `INVALID_ARGUMENT`, naming fields | Both or neither of `quantity` and `cash_quantity`; a child naming another instrument or side; a fill with no `settlement_date`; an instruction on `target.user_group_id`; an algorithm the version does not declare (`algorithm_id`); a fill on no placement without `instrument_id`, `side` or `venue_order_id`; an execution named twice in one accept (`execution_ids[i]`); a DK with reason other and no `text`; a quote currency naming the order's own instrument (`quote_currency`), or a limit or stop priced in another currency (`limit_price`, `stop_price`, `change.limit_price`); a roll whose `pair` is not two cash instruments, or with no date or basis |
| `PERMISSION_DENIED`, no code | A command naming a record whose account is outside the plugin's write scope or the person's write access; a connectivity plugin's `RecordOrder` or `CreatePlacement`, refused by its sidecar |

In the Python SDK a coded refusal is a `CommandRefused` carrying its code,
an `INVALID_ARGUMENT` a `CallFailed` of kind `"invalid"` naming the fields,
and a `PERMISSION_DENIED` a `NotGranted` (see
[Exceptions](../api/python-sdk.md#exceptions)).

## Not built yet { #not-built-yet }

- **RFQs and axes**: their references are carried empty on the order and
  the placement until the RFQ revision (slice C); an order of 0 quantity, a
  pass, is refused until then.
- **Confirming an allocation with a client**, non-order transactions and
  settlement: see [Booking](booking.md#not-built-yet).
- **Other named links** between orders -- street orders, two-way quotes,
  alternatives, baskets -- wait for their slices. The split link and the
  block are the ones there are.
- **A trading instruction on a user group**, until groups are resolved to
  their people.
- **Derivative terms** on an execution, which come with the instrument
  templates for options and futures.
- **The fast tiers**: every order-path act is acknowledged after its entry
  commits, on disk.

## Related

- [Route orders through a connectivity plugin](../how-to/route-orders-through-a-connectivity-plugin.md):
  make one available, link it to an `ems`, choose who may route and map
  the accounts.
- [Answer a venue-originated fill](../how-to/answer-a-venue-originated-fill.md):
  accept it to an order, or answer it DK.
- [Booking](booking.md): an order's executions booked to
  its accounts.
- [Set trading instructions and whether releases wait](../how-to/set-trading-instructions.md).
- [Settlement calendars](settlement-calendars.md): how a settlement date
  is worked out when the venue states none.
- [The book of record](the-book-of-record.md): positions, lots and
  reconciliation.
- [The order path in the Python SDK](../api/python-sdk.md#the-order-path)
  and [its typed operations](../api/typed-operations.md#the-order-path).
