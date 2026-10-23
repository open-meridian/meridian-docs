# Net FX orders

This page is for the author of an `oms` plugin that nets opposite FX orders
on one pair and one value date: it proposes the net order, records the
offset as internal crosses, and books the result. What a net is, and why,
is in [FX netting](../concepts/fx-netting.md).

You need SDK 0.32.0 or later, a deployment on contract 27 (chart 0.1.309 or
later), an [allocation account](../concepts/accounts.md#in-the-book) in the
`oms`'s write scope, and the members' accounts in it too.

## Propose the net

Name the members, released FX orders of one pair and one value date, of
both sides, in `net_member_order_ids`. The book works out the net's pair,
side and quantity from them: leave them out, or state them as the book
would, since a stated value that differs is refused, naming it.

```python
reply = await plugin.propose_order(
    account_id="ACC-ALLOC",                      # the allocation account
    net_member_order_ids=["ORD-...", "ORD-...", "ORD-..."],
    order_type="market",
    time_in_force="day",
    acting_for=request.caller.header,
)
net = reply.order                                  # released on creation
```

Each member is linked to the net, its link `net`, naming the net as its
parent. The net is released at once and goes to market as any order, by
an `ems`. A member not released, or already in a live block or net, is
refused `REFUSAL_REASON_ORDER_STATE`; a member of another pair or value
date is refused `invalid`, naming `net_member_order_ids[i]`; members that
offset exactly, leaving nothing to place, are refused `invalid`, naming
`net_member_order_ids`.

**The value date.** Each member's `value_date` is the date `portfolio`
stated when it proposed the order, or empty for spot: the pair's spot date
on the trade date the order opened.

## Record the offset

Record what the members cross between them as internal crosses on the
net, one for each member's side of the offset, each naming that member's
account. A cross goes to no venue and names no placement. Say which
convention set its rate:

```python
await plugin.report_execution(
    order_id=net.order_id,
    account_id="ACC-FUND-A",
    kind="internal_cross",
    cross_rate_source="net_street_rate",           # or "mid_at_netting"
    side="buy",
    quantity=Decimal("2000000"),
    price=Money(Decimal("1.0842"), "USD"),            # the quote currency
    trade_time_ns=crossed_at_ns,
    trade_date="2026-10-22",
    settlement_date=net.value_date,
    acting_for=request.caller.header,
)
```

With `net_street_rate`, every member crosses at the net's street rate,
known once the net is filled. With `mid_at_netting`, it crosses at the mid
when the net was made; name the quote's dataset in the cross's raw record.
A cross on an order that is not a net, one with no `cross_rate_source`,
one naming a placement, or one with no side, is refused `invalid`, naming
the field.

## Book it

Book the net as a block is booked: `book_order` books its street
executions and its crosses to the members' accounts, and the allocation
account nets to zero. Each member's filled quantity is its allocation's.
See [Booking](../concepts/booking.md).

## Related

- [FX netting](../concepts/fx-netting.md).
- [`propose_order`](../api/typed-operations.md#propose_order) and
  [`report_execution`](../api/typed-operations.md#report_execution).
- [Booking](../concepts/booking.md#the-block-order).
