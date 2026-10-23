# Placement types and RFQ quotes

A placement says where part of an order goes: a connectivity plugin, its
venue account code, a destination and a route. Its **placement type** says
how it is executed: electronically and directly, by a broker's algorithm,
worked by a broker's desk, by asking dealers for quotes, or agreed by phone
or chat with nothing sent at all. The `ems` sets it once, when it creates
the placement; the order keeps its own order type. See
[The order lifecycle](the-order-lifecycle.md#placements-and-the-connectivity-plugins-an-ems-may-use)
for placements in general.

## The five types

| Type | How it is executed | What the connectivity plugin sends |
|---|---|---|
| `dma` | Directly, electronically, with no broker intervention | An order, FIX HandlInst (21) `1` |
| `algo` | By the broker's algorithm, named in the placement's `strategy` | An order with its strategy, HandlInst `1` or `2` |
| `care` | Worked by a broker's desk | An order, HandlInst `3` with ExecInst (18) Not held |
| `rfq` | By asking dealers for quotes, then hitting the one picked | A quote request, then the picked quote hit as Previously quoted (OrdType `D`) with its QuoteID |
| `manual` | Agreed by phone or chat | Nothing: it reaches no connectivity plugin |

**Set once.** A placement's type never changes. Another style of execution
is another placement, as FIX fixes HandlInst for an order's life. A
placement with no type stated, made before contract 27 or by a plugin built
before it, is read as `dma`, and nothing is backfilled.

**Consistency.** The book refuses, `invalid`, naming the field:

- an `algo` placement with no `strategy`, and a `dma`, `care` or `manual`
  placement with one;
- any placement but `rfq` on an order of type request for quote. An `rfq`
  placement may be made on any order: asking dealers is a way of executing
  an order already there;
- a `manual` placement naming a connectivity plugin, and any other naming
  none.

**What a venue takes.** A connectivity plugin lists the placement types
each venue account code takes on its venue catalogue, beside its order
types. A placement of a type its catalogue does not list is rejected by
the connectivity plugin, `unsupported`, as an order type it does not take
is: core refuses nothing a venue cannot do. A reporting plugin reads each
placement's type from the orders it reads, and a regime's manual order
indicator is derived from `manual`, never stored twice.

## A manual placement

A trade agreed by phone or chat is placed as `manual`. It names no
connectivity plugin and no venue account code, and is delivered to none.
It names its counterparty as its `destination`, a `VEN-` ID, and carries
the trade's evidence, which is not street data:

- the person who agreed it, the actor the book records;
- `counterparty_contact`, the person or desk at the counterparty;
- `agreed_at_ns` and `agreed_precision`, when it was agreed, and how
  precisely that is known.

Its fills are the `ems`'s manual entries for a person
(`EXECUTION_KIND_MANUAL`, through
[`report_execution`](../api/typed-operations.md#report_execution)). A
manual fill may carry the counterparty's execution ID, as
`venue_execution_id`: where the counterparty's electronic report arrives
later on a care placement, it is matched on that ID and not counted twice,
as a drop copy is. A manual fill with none is reconciled by an `operations`
plugin against the confirmation. Whether a manual fill needs a second pair
of eyes is the firm's choice of
[gate](prepared-changes.md#a-second-pair-of-eyes).

**A care placement** goes to a broker through its connectivity plugin, and
its fills arrive electronically as on any placement. Its outcome-unknown
and done-for-day handling is the same as any placement's.

## RFQ placements { #rfq-placements }

An `rfq` placement asks dealers for quotes and executes on one the `ems`
picks. The firm is the **initiator**: this is the buy side's RFQ. The
dealers' quotes are trade details on the firm's placement, kept in the book
as its best-execution record and staying with the order to settlement.
Nothing copies them into the lake: [the street is post-trade](the-book-of-record.md),
and the quotes are the placement's own.

1. **The `ems` places**, type `rfq`, at a connectivity plugin whose venue
   lists `rfq` for the account's code.
2. **The connectivity plugin asks** its venue for quotes, and records each
   dealer's quote on the placement as it arrives
   ([`report_placement_quote`](../api/typed-operations.md#report_placement_quote)):
   the dealer by its `VEN-` ID, the dealer's quote ID as delivered, its
   side, price and quantity, when it was received and until when it stands,
   and its raw record. The book mints each quote a `PQT-` ID.
3. **The `ems` picks** one open quote
   ([`pick_placement_quote`](../api/typed-operations.md#pick_placement_quote)),
   for a person or as its service account, with a reason where the firm's
   policy asks one. It need not be the best: picking another is the trader's
   choice, recorded, never refused. The placement's `picked_quote_id` names
   it.
4. **The connectivity plugin accepts** the picked quote at the venue, and
   reports the fill as on any placement. Its cost against the quotes
   received is then the placement's own record.

Each quote moves through its outcomes, each its own entry: **open**, then
**picked**, then **accepted**; or **expired**, **withdrawn** by the dealer,
or **not picked**. An outcome never moves backwards. A quote that expires
after the pick and before the venue accepts it is recorded expired, the
pick is cleared, and the `ems` may pick another.

The book refuses, `REFUSAL_REASON_ORDER_STATE`: a quote on a placement that
is not `rfq` or not the reporting plugin's own; a pick of a quote not open,
or past its valid-until time; and a second pick while one stands. A pick on
another `ems`'s placement, and a quote reported on a placement outside the
plugin's scope, are refused `PERMISSION_DENIED`.

**Agents.** [The agents' guard](the-agents-guard.md) applies to a pick as
to a placement: an agent's pick, made through a delegation or by a service
account, is demo only where every connection the caller may route through
is demo, and is otherwise refused `REFUSAL_REASON_AGENT_LIVE_ORDER`, and
recorded.

**Compliance** reads the quotes and the pick on the placement, for best
execution.

## For a plugin's author

- **An `ems`** sets `placement_type` on
  [`create_placement`](../api/typed-operations.md#create_placement), and a
  manual placement's `counterparty_contact`, `agreed_at_ns` and
  `agreed_precision`. `meridian.roles.ems.open_quotes(placement)` answers an
  RFQ placement's open quotes, best first for the firm's side: a dealer's
  offer lowest first to a buyer, its bid highest first to a seller, ties by
  the time received. The ems suite's `picks-a-quote-on-its-rfq-placement`
  holds it.
- **A connectivity plugin** on `meridian.roles.connectivity`'s `Trader`
  states what its venue takes in its adapter: `placement_types(code)`, the
  types beside DMA; and where the venue takes RFQs, `request_quotes(code,
  asked)`, `quotes(code, request_id)`, each a `VenueQuote`, and
  `accept_quote(code, request_id, quote, asked)`. The `Trader` lists the
  types on the catalogue, rejects a type the account does not take with its
  reason, records each quote on the placement and accepts the pick. A
  read-only account takes none. The connectivity suite's
  `records-a-dealers-quote-on-an-rfq-placement` is `about: rfqs`: a plugin
  whose venue takes no RFQ marks it not presented, with why (see
  [A case not presented](../api/python-sdk.md#a-case-not-presented)).

## Not built yet

- **The sell side**: an RFQ received from a client, recorded in the lake,
  and the firm's response to it; and axes. A placement's `rfq_id` and
  `axe_id`, and an order's axe fields, are carried empty, and an order of
  quantity 0, a pass, is refused.

## Related

- [The order lifecycle](the-order-lifecycle.md): placements, the
  connectivity plugins an `ems` may use, and what the venue reports.
- [Execution costs](execution-costs.md): each fill's cost against the
  standard benchmarks, by placement.
- [The agents' guard](the-agents-guard.md).
- [Typed operations: contract 27's](../api/typed-operations.md#contract-v27s-operations).
