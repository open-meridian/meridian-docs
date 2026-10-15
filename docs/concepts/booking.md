# Booking

From contract v24 a fill does not stop at the order. The `oms` **books**
the order's executions to the accounts they were for: one allocation per
account, each with its quantity, average price, fees and settlement date.
The book checks that the allocations add up to the executions exactly,
moves each account's positions and lots, and then the booking is handed
off to `operations` for its post-trade life.

Booking is its own act and its own record, pointing at the order. The
order's executions and their positions are what the venue did; the booking
says whose they are.

!!! note "TODO: contract v24, built, not released"
    Booking is in core for contract v24, to be released in chart
    `0.1.CHART24` with open-meridian 0.28.0 (TODO: the date). Every
    operation on this page is `preview`: it may change in a later contract
    version, with a migration. Core proves booking end to end with stand-in
    plugins only: its order-path test books a block order across two
    funds. No released plugin holds the `oms` role yet (TODO: confirm at
    release).

## Who does what

- **`portfolio`** sets each order's allocation instruction: the accounts,
  each with its amount or weight, and its sleeve where the account has
  sleeves. It may amend the instruction later, with a reason, for what is
  not booked yet. **`operations`** sets a client's instruction where the
  firm is the client's custodian.
- **The `oms`** books the executions, hands the booking off, closes a
  client's booking the firm does not settle, cancels a booking before its
  hand-off, and records a cross between two sleeves.
- **`operations`** owns each allocation after the hand-off, and corrects a
  booking by replacing it.
- **`compliance`** raises alerts of its own and acknowledges the book's
  error-account alerts, for a person, with a reason.
- **`connectivity` and `confirmation`** report a prime broker's answer to
  a give-up.
- **The book** checks that a booking ties out, moves positions and lots,
  raises and clears its own alerts, and mints every ID.

**Core records; it does not police.** The book checks that what is
allocated equals what was executed, and nothing else. Whether a block's
members were treated fairly, or whether allocated equals ordered, is a
`compliance` plugin's rule. Nothing on this page is presented as meeting
any market's or regulator's rule.

## The allocation instruction

An order carries its allocation instruction from the moment it is
proposed (see [Proposing an order](the-order-lifecycle.md#proposing-an-order)).
`SetAllocationInstruction` changes it afterwards, with a reason. Each line
names an account, its amount or weight, and its sleeve, the order's own
sleeve by default.

An amendment is refused (`REFUSAL_REASON_ORDER_STATE`) where it would take
an account below what that account's live bookings on the order already
allocate. So booking one trade date at a time, and an increase with its
allocation, both still amend the instruction for what is not booked yet.

## Booking an order's executions

`BookOrder` books an explicit list of executions, all on one order: the
same instrument, side, trade date and settlement date. Any subset of the
unbooked executions may be booked, so a booking can be made during the day,
and a late fill stays visibly unbooked. A child order's executions are
booked as its parent's.

Each allocation carries:

- the account, and its sleeve;
- the quantity, the average price and the gross amount;
- the fees, each by kind, each marked **capitalised** or not;
- the net amount, which the book derives;
- the intended settlement date;
- whether it states an average price;
- the lots the receiving account relieves, where it names them;
- on an error account, the cause and the reason.

The book checks exactly, with no tolerance:

- the quantities sum to the executions booked;
- the gross amounts sum to the executions' gross, any rounding residual on
  one named allocation;
- each fee kind sums to the executions' fees of that kind.

A booking that does not tie out is refused,
`REFUSAL_REASON_BOOKING_UNBALANCED`. An account the instruction does not
name, and which is not an error account, is refused,
`REFUSAL_REASON_ACCOUNT_NOT_INSTRUCTED`. An execution unmatched, answered
DK, superseded, or already in a live booking is refused,
`REFUSAL_REASON_ORDER_STATE`, naming it.

The book mints a booking ID, `BKG-` followed by a ULID, and an allocation
ID for each allocation, `ALC-` followed by a ULID, even for a single
account. The street echoes the allocation ID back.

### What booking does to lots

A fill's lots are provisional until they are booked. Booking closes the
fill-time lots in the order's account, with no realised result, and opens
one lot per allocation, acquired on the trade date, at the allocation's
average price plus its capitalised fees. A single-account order is booked
the same way, so each account's basis is what its confirmation states.

Every fee stays its own cash line, so cash does not change when a fee is
capitalised. Whether a capitalised fee enters a lot's cost is the `oms`'s
policy; core sets no default.

**Lot relief is per receiving account.** On a sale each account relieves
its own lots, by the instruction line's method or the account's
[lot relief](accounts.md#in-the-book), or the specific lots an allocation
names. The book records when each designation was made and refuses
nothing for lateness: which rule applies is the `oms`'s policy and
`reporting`'s to check.

### Cash

From contract v24 an account's **base currency** is a balance, and every
other currency opens lots:

- a fill or an opening position in the account's base currency moves its
  balance, a signed amount, never a short lot;
- a fill or an opening position in any other currency opens lots, each
  with its cost in the base currency and its acquisition date, as any
  position's lots;
- a change of base currency moves no position and re-states no lot. It
  applies from then on: lots already open in the new base currency stay
  open until relieved, and none opens in it after the change.

The book converts nothing with the base currency. Until contract v24 no
cash position had lots. See
[What the book requires](the-book-of-record.md#what-the-book-requires).

## The block order

A **block** gathers several members' orders into one order worked at the
venue. It is proposed in an account marked as an **allocation account**,
naming its members (`block_member_order_ids`). Its executions move the
allocation account.

Booking the block allocates its executions to the members' accounts. Each
allocation moves its account, and moves the allocation account by the
opposite amount, so the allocation account is flat once the block is
booked. A member's filled quantity is its allocation's, and a correction
moves it with it.

A deployment admin marks an account as an allocation account on its
**Edit** (see [In the book](accounts.md#in-the-book)). Reconciliation then
knows the account has no statement.

## The error account

An overfill's excess, or a trade a client will not take, goes to an
**error account**. A booking may allocate to an account marked as one
without the instruction naming it, with no cap. Each such allocation
carries its reason and its cause:

- **overfill**, more was filled than ordered;
- **client reneged**, the client would not take the trade;
- **wrong accept**, a venue-originated fill accepted to the wrong order;
- **booking error**;
- **other**, with text saying what.

Each one raises an alert (see [Alerts](#alerts)), so none passes
unreviewed. An overfill booked to the error account clears the order's
does-not-tie-out flag.

The mark is a deployment admin's, on the account's **Edit**. Unmarking is
recorded and never refused; past allocations keep their flag. The mark and
its alert are the control; this makes no regulatory claim.

**A wrong accept** is put right by booking. There is no unaccept: the
execution stays on the order it was accepted to. `portfolio` adds the
right account to the instruction, and the `oms` books to it, or books the
fill to the error account with the cause **wrong accept**.

## The hand-off

`HandOffBooking` hands a booked booking to `operations`, or, with `close`,
closes a client's booking the firm does not settle, handing its
error-account allocations to the firm's `operations` in the same act.
`BookOrder` may ask for the hand-off in the same call (`hand_off`).

**The check at the hand-off**: executed equals allocated, in quantity,
gross and each fee kind, the error account included. Executions can move
after booking, by a bust, a correction, a late fill or a fee reported
later. A booking that no longer ties out is **held** with the reason, and
raises a held-booking alert, until the `oms` books it again so it does.
An allocation account left with a balance after booking holds the booking
the same way.

A booking's states, derived from its journal as an order's status is:

- **Booked**: booked, not yet handed off.
- **Held**: the check at the hand-off failed; the reason is kept.
- **Handed off**: `operations` owns each allocation from here.
- **Closed**: a client's booking the firm does not settle.
- **Cancelled**: cancelled before the hand-off, so the executions can be
  booked again.

Each transition is a row of the one
[transition table](the-order-lifecycle.md#the-transition-table), keyed
`b1` onward.

## Corrections

`CorrectBooking` carries the booking's whole new allocation set and a
reason; the book works out the movement lines from the difference and
journals them as their own entry. There are two kinds:

- **Cancel**, the `oms`'s, before the hand-off or closing. The booking ends
  cancelled, and the executions may be booked again.
- **Replace**, `operations`', after it, with the date the correction takes
  effect, the trade date by default. The booking keeps its state and makes
  a new version.

A client reneging after the hand-off is a replace that moves the whole
allocation to the error account, with the cause **client reneged**. A bust
after the hand-off keeps the booking's state: `operations` hears it and
corrects the booking by a replace. A correction never moves the order
backwards.

## Sleeves

An allocation may name a sleeve of its account. Three more rules:

- **A sleeve cross** (`RecordSleeveCross`) moves a position between two
  sleeves of one account, at `portfolio`'s decision, recorded by the `oms`:
  the instrument, the two sleeves, the quantity, the cross price and its
  source, who decided and why. Where it stands in for two opposite orders,
  it names them (`order_ids`), and each order counts it as filled. It mints
  no execution, since nothing traded, and the account's quantity and cash
  do not change. The book mints its ID, `SXC-` followed by a ULID.
- **Two layers.** For tax, each lot moves between the sleeves keeping its
  cost and acquisition date, a partial cross splitting the lot. For
  performance, each moved lot takes the cross price as its cost, and the
  giving sleeve realises its performance result there. No tax computation
  reads the performance layer.
- **A street sale from one sleeve** relieves lots within that sleeve.

## Give-ups

When a trade is given up to a prime broker, the prime accepts or rejects
it. A `connectivity` or `confirmation` plugin reports the answer with
`ReportGiveUp`: accepted or rejected, the prime's reference and a reason,
naming the execution and, where one is booked, its allocation. Each answer
is its own record, kept on the execution and on the allocation.

A rejection moves no position: the fund still owns the trade, which stays
with the executing broker as its settlement counterparty, shown to
`operations`. A report naming nothing the book holds is kept as an
unplaced fact.

## Alerts

An **alert** is a record in the account's partition that asks a person to
look. Its state is **raised**, **acknowledged** or **cleared**, and nothing
is deleted. It names what it is about: an order, a booking, an allocation
or a position. There are three kinds:

- **Error-account booking**: raised by the book for each allocation to an
  error account. `compliance` acknowledges it, for a person, with a
  reason.
- **Booking held**: raised by the book when a booking is held, to the
  `oms` and `operations`, due by the affirmation deadline. It clears itself
  when the booking is handed off or closed. A person's acknowledgement is
  recorded and never clears it.
- **Compliance**: raised by a `compliance` plugin, with `RaiseAlert`.

**The deadline** is the `operations` plugin's declaration,
`affirmation_deadline`, a time of day in the deployment's time zone. The
alert carries the moment it is due by; whether it is overdue is a reader's
comparison against the deployment's clock.

An alert's reason and acknowledgement are text written by people, and
reach an agent as data, never instructions.

## Reading bookings and alerts

- **`ListBookings`** lists the bookings in a plugin's read scope, as of a
  sequence or changed since a watermark, filtered by account and state,
  each with its allocations, paged. `oms`, `operations`, `compliance`,
  `portfolio` and `reporting` read it, and hear **BookingUpdated**.
- **`ListAlerts`** lists the alerts the same way, filtered by state and
  kind. `compliance`, `reporting`, the `oms` and `operations` read it, and
  hear **AlertChanged**.

A plugin that offers these acts on its pages offers each to agents as a
tool too, under MCP parity: `set_allocation_instruction`, `book_order`,
`hand_off_booking`, `correct_booking`, `list_bookings`, `raise_alert`,
`acknowledge_alert` and `list_alerts`.

## What is recorded

Every booking act is journalled in the partition of the order's account.
Each allocation's movement in another account is a child entry in that
account's own partition, naming the booking. A booking's entries are
`booking-booked`, `booking-held`, `booking-handed-off`, `booking-closed`,
`booking-cancelled`, `booking-corrected` and `allocation-moved`. Every
correction is its own record.

The same instrument is compared through the replacement: a booking's
executions on an `LCL-` record that has since resolved to an `INS-` record
are one instrument (see [One ID per instrument](one-id.md)).

## Refusals

- **`REFUSAL_REASON_BOOKING_UNBALANCED`**: allocations that do not sum
  exactly to the executions booked, in quantity, gross or a fee kind.
- **`REFUSAL_REASON_ACCOUNT_NOT_INSTRUCTED`**: an allocation to an account
  the instruction does not name and that is not an error account.
- **`REFUSAL_REASON_ORDER_STATE`**: an execution unmatched, answered DK,
  superseded or already booked; a hand-off of a booking handed off, closed
  or cancelled; a correction of the wrong kind for the booking's state or
  the actor; an amendment touching what is booked already; a sleeve cross
  naming an order that has ended.
- **`REFUSAL_REASON_REASON_REQUIRED`**: an error-account allocation, a
  correction, an amendment, a sleeve cross or an acknowledgement with no
  reason.
- **`REFUSAL_REASON_ACTOR_REQUIRED`**: no person or service account behind
  the act.
- **`INVALID_ARGUMENT`**, naming the field: an error-account allocation
  with the cause other and no text; a sleeve cross naming an order of
  another account or instrument, or two orders of one side.

## Not in v24

- **Confirming an allocation with a client** (`confirmation`), and matching
  a trade's confirmation to a booking.
- **RFQs**, non-order transactions and settlement; an allocation's settled
  quantity and dates.
- **Period close**, and an event contract's payout.

## Related

- [The order lifecycle](the-order-lifecycle.md): how an order reaches a
  venue, and how fills move positions before they are booked.
- [The book of record](the-book-of-record.md): positions, lots and
  reconciliation.
- [Accounts](accounts.md#in-the-book): the error and allocation account
  marks, and the base currency.
