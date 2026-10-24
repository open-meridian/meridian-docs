# Place manually or by RFQ

This page is for the author of an `ems` plugin: it places a trade agreed by
phone as a manual placement, and works an order by asking dealers for
quotes and picking one. What each type means is in
[Placement types and RFQ quotes](../concepts/placement-types-and-rfq-quotes.md).

You need SDK 0.32.0 or later and a deployment on contract 27 (chart
0.1.309 or later).

## A manual placement

A trade agreed by phone or chat names no connectivity plugin. It names its
counterparty as its destination, and its evidence:

```python
reply = await plugin.create_placement(
    order_id=order_id,
    placement_type="manual",
    destination="VEN-...",                      # the counterparty
    counterparty_contact="J. Smith, FX desk",
    agreed_at_ns=agreed_at_ns,
    agreed_precision="second",
    quantity=Decimal("1000000"),
    acting_for=request.caller.header,
)
```

Then enter its fills as the `ems`'s manual executions, for the person, with
the counterparty's execution ID where it gave one:

```python
await plugin.report_execution(
    placement_id=reply.placement.placement_id,
    kind="manual",
    venue_execution_id="CP-4471",               # the counterparty's, if any
    quantity=Decimal("1000000"),
    price=Money(Decimal("1.0842"), "USD"),
    trade_time_ns=agreed_at_ns,
    trade_date="2026-10-22",
    settlement_date="2026-10-26",
    acting_for=request.caller.header,
)
```

## An RFQ placement

Place with `placement_type="rfq"` at a connectivity plugin whose venue
lists `rfq` for the account's code on its catalogue
([`read_venue_catalogue`](../api/typed-operations.md#read_venue_catalogue)).
The connectivity plugin asks its venue and records each dealer's quote on
the placement; the `ems` hears them on the placement
(`placement_updated`). Show the open quotes, best first, and let the
person pick:

```python
from meridian.roles import ems

quotes = ems.open_quotes(placement)              # best first for the firm's side
await plugin.pick_placement_quote(
    placement_id=placement.placement_id,
    quote_id=chosen.quote_id,                    # any open quote, not only the best
    reason="best all-in after the dealer's settlement terms",
    acting_for=request.caller.header,
)
```

The connectivity plugin accepts the pick at the venue and reports the fill
as on any placement. If the quote expires before the venue accepts it, the
pick is cleared: pick another. An agent's pick is refused on a connection
that is not demo while [the agents' guard](../concepts/the-agents-guard.md)
is on, as an agent's placement is.

The ems suite's `picks-a-quote-on-its-rfq-placement` holds the pick. It
carries no `about`, so every `ems` maps it to its own pick.

## In a connectivity plugin

On `meridian.roles.connectivity`'s `Trader`, the adapter states the types
its venue takes beside DMA, `placement_types(code)`, and where it takes
RFQs, `request_quotes`, `quotes` and `accept_quote`; the `Trader` does the
rest. See
[Placement types and RFQ quotes](../concepts/placement-types-and-rfq-quotes.md#for-a-plugins-author).

## Related

- [Placement types and RFQ quotes](../concepts/placement-types-and-rfq-quotes.md).
- [`create_placement`](../api/typed-operations.md#create_placement),
  [`report_placement_quote`](../api/typed-operations.md#report_placement_quote)
  and [`pick_placement_quote`](../api/typed-operations.md#pick_placement_quote).
- [Route orders through a connectivity plugin](route-orders-through-a-connectivity-plugin.md).
