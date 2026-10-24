# FX netting

An FX desk often holds opposite orders on the same pair for different
accounts: one fund buying euros, another selling them. **FX netting** joins
them into one **net order**, so only the difference goes to market and the
offset between the two sides is crossed internally, between the members'
accounts. In this release a net is **one pair and one value date**.

## The net order

The `oms` proposes a net order in an
[allocation account](accounts.md#in-the-book), naming its members of both
sides in `net_member_order_ids`
([`propose_order`](../api/typed-operations.md#propose_order)). The book
links each member to it, its link `ORDER_LINK_KIND_NET`, naming the net as
its parent.

- **Its quantity** is the members' buys less their sells, and its side the
  larger side's.
- **It is released on creation**, as a [block](booking.md#the-block-order)
  is, never through the gate again.
- **Only the net goes to market.** The `ems` places it as any released
  order.

**The members** must each be released, FX orders of one pair, the same
base currency's instrument and the same `quote_currency`, and of one value
date, and in no other live block or net.

**The value date.** An FX order states its `value_date`, the date it
settles on, as `portfolio` gives it (FIX SettlDate, 64). Empty is spot: the
pair's spot date on the trade date the order opened, worked out in core
(see [Settlement calendars](settlement-calendars.md)). Two empty value
dates are the same date only on one trade date.

**Refusals.**

| Refused | When |
|---|---|
| `REFUSAL_REASON_ORDER_STATE` | A member not released, or in another live block or net |
| `invalid`, naming `net_member_order_ids[i]` | A member of another pair or value date |
| `invalid`, naming `net_member_order_ids` | A net naming one side only, or members that offset exactly, leaving nothing to place |
| `invalid`, naming both | A net naming `block_member_order_ids` and `net_member_order_ids` |

## The offset, crossed internally

The offset between the sides is recorded by the `oms` as **internal
crosses**: executions of kind `EXECUTION_KIND_INTERNAL_CROSS` on the net
order, naming no placement and no venue, each booked to the members'
accounts as a two-account act with an entry in each.

**Its rate is the plugin's choice**, recorded with its source on every
cross (`cross_rate_source`,
[`report_execution`](../api/typed-operations.md#report_execution)). Core
supports both conventions the platforms use:

| `cross_rate_source` | The rate |
|---|---|
| `CROSS_RATE_SOURCE_NET_STREET_RATE` | The net's street rate, for every member: the platforms' allocate-back |
| `CROSS_RATE_SOURCE_MID_AT_NETTING` | The mid at the moment of netting, its dataset named in the raw record |

An internal cross on an order that is not a net, or one with no
`cross_rate_source`, is refused `invalid`, naming the field.

## Booking it

[Booking](booking.md) is the one there is: `BookOrder` books the net
order's street executions and its crosses to the members' accounts. The
allocation account nets to zero, as a block's does, and each member's
filled quantity is its allocation's. Whether netting is fair, whether one
fund always takes the cross, is a `compliance` plugin's rule; the book
checks only that the net balances.

## Not built yet

- **Cross-currency netting**, EUR/USD against USD/JPY, which needs
  triangulated amounts and a rule for the residual currency.
- **Funding FX from equity orders**: an `oms` may propose the FX orders
  itself.
- **Settlement netting**, one payment per currency per value date, which
  is settlement's, not the order path's.

## Related

- [Net FX orders](../how-to/net-fx-orders.md): an `oms` proposing a net
  and recording its crosses.
- [The order lifecycle](the-order-lifecycle.md): child orders, blocks and
  release.
- [Booking](booking.md): the block, allocation accounts and lots.
