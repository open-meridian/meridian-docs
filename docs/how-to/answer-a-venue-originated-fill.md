# Answer a venue-originated fill

A **venue-originated fill** is one the venue reports on no order the book
sent: an order someone placed in the broker's own app, or a liquidation.
From contract v23 the connectivity plugin that hears it reports it, and the
book holds it **unmatched**, moving no position, until a trader at the
`ems` linked to that connectivity plugin answers it: **accept** it to an
order, or answer it **DK** (don't know). This page is for that trader, and
for whoever writes the `ems` or connectivity plugin. What the book does is
on [The order lifecycle](../concepts/the-order-lifecycle.md#venue-originated-fills).

!!! note "Contract v23"
    The accept and the DK are in core and open-meridian 0.27.0, released
    2026-10-14 in chart 0.1.303. Core proves them with a stand-in `ems`
    page (its **Unmatched fills**) against a simulated venue that takes
    FIX's acknowledgements; no broker is reached. Their operations are
    `preview`. No `ems` plugin offering these acts is released yet: an
    `ems` is yours to build. The connectivity plugins that report
    venue-originated fills are Alpaca 0.8.0, Tradier 0.7.0 and SnapTrade
    0.17.0, released 2026-10-14, each tested against a simulated brokerage
    only; none of their brokers takes an acknowledgement, so a DK tells
    the broker nothing.

## Where they show

On the **`ems` plugin's page**, for the accounts it may read, and flagged on
the **operations plugins' pages**. In core's stand-in, **Unmatched fills**
lists them one line each (the execution, account, instrument, side,
quantity, venue order and trade date), with **Accept** and **DK** on each
line. An unmatched fill waits with no time limit. The dashboard shows none.
A busted fill leaves the list; a corrected one is listed once, as its
correction.

Until it is answered, the custodian's statement will differ from the book,
and the operations plugin shows a break, the unmatched fill its candidate
cause.

## Answer it

You need `write` on the `ems` plugin's `ems` role, and the fill's account
in your write access.

| You know the fill as | Do | What the book records |
|---|---|---|
| Part of an order the book holds | **Accept**, choosing the order | The fills linked to a placement created at filled under that order; the position moved as of the fills' trade date |
| Yours, with no order in the book | **Accept** to a new order, choosing its sleeve, with a note | A new order at filled, made from the fills, marked as entered after the trade by you; its placement at filled |
| Not yours, or wrong | **DK**, with a reason | The fill closed, never moving a position |

- **Several prints of one venue order** are accepted together: they must
  share their account, instrument, side, connectivity plugin and trade
  date. Fills of two trade dates are accepted separately.
- **An existing order** is one your `ems` may place against: released,
  working or filled, not cancelled, expired or refused, and not claimed by
  another. A sell fill matches the order's sell, a buy a buy.
- **Past the order's quantity** is refused: accept to a new order instead,
  or have the portfolio manager increase the order first.
- **A DK's reason** is one of: unknown instrument, wrong side, quantity
  exceeds order, no matching order, price exceeds limit, calculation
  difference, or other, which needs text.
- **Once answered, a fill stays answered.** A wrong accept is put right as
  any wrong fill is, by a bust, or by booking's corrections in a later
  release.

**Whether the venue is told** depends on what it takes, as its connectivity
plugin's catalogue says. Where it takes a FIX acknowledgement, the
connectivity plugin sends it: accepted, or "don't know" with your reason.
Where it takes none, as at SnapTrade, Alpaca and Tradier, the page says
**the venue is not told** before you DK.

**After an accept** the break clears on the next statement. **After a DK**
it stays, for a person at the operations plugin to resolve. A later fill of
the same venue order goes on the accepted placement; after a DK it arrives
unmatched again, the earlier DK shown beside it.

### Through an agent

The `ems` plugin's acts are tools under its instance's name, at `write` on
`ems`: `accept_execution`, `dk_execution`, and the page's read,
`read_unmatched_fills`. As with any act, the deployment admin and the
plugin's admin set whether your agent may make an answer, only prepare it,
or not reach it (see [Prepared changes](../concepts/prepared-changes.md)).
The `ems`'s service account may answer fills itself, at the levels its
admin sets; core never answers one on its own.

## Refusals

| Refused | When |
|---|---|
| `REFUSAL_REASON_EXECUTION_STATE` | The fill is answered already, or superseded by a bust or a correction |
| `REFUSAL_REASON_EXECUTIONS_DIFFER` | The fills differ in account, instrument, side, connectivity plugin or trade date, or a fill's side is the order's opposite |
| `REFUSAL_REASON_QUANTITY_EXCEEDS_ORDER` | The accept would take the order past its ordered quantity |
| `REFUSAL_REASON_ORDER_STATE` | The order has ended |
| `REFUSAL_REASON_CLAIMED` | Another holds the order's claim |
| `REFUSAL_REASON_ACTOR_REQUIRED` | No person or service account behind the answer |
| Invalid, naming the field | A fill named twice (`execution_ids[i]`); a DK with reason other and no `text` |

## In a plugin

From open-meridian 0.27.0. **A connectivity plugin** reports the fill with
[`report_execution`](../api/typed-operations.md#report_execution), naming no
placement, and hears what became of it:

```python
await plugin.report_execution(
    venue_account_code="X12345", instrument_id=aapl, side="buy",
    venue_order_id="V-9921", venue_client_order_id="app-77",
    venue_execution_id="F-1", quantity=Decimal("5"), price=Money(Decimal("227.10"), "USD"),
    trade_time_ns=at, trade_date="2026-10-13", settlement_date="2026-10-14",
    kind="venue_reported", raw_record=plugin.raw_record(key),
)

async def answered(heard: meridian.Heard) -> None:
    execution = heard.message.execution      # its state matched or dont_know
    ...                                      # send BN or Q, where the catalogue says the venue takes it

await plugin.receive(execution_recorded=answered, placement_updated=on_placement)
```

Its catalogue says what the venue takes
(`VenueCatalogue(execution_acknowledgement="bn")`, `"dont_know_trade"` or
`"none"`; nothing reads as none). After an accept it reports later fills,
and a charge it reported on no placement, again on the placement the
accept created.

**An `ems` plugin** lists the unmatched fills in its scope and answers them,
acting for the person, or as its service account:

```python
listed = await plugin.list_orders(execution_state="unmatched")
await plugin.accept_execution(execution_ids=[e1, e2], order_id=order_id,
                              note="Placed by the PM in the broker's app.",
                              acting_for=request.caller.header)
await plugin.accept_execution(execution_ids=[e3], new_order=ops.NewOrderFromExecutions(sleeve="core"),
                              note="Liquidation by the broker.", acting_for=request.caller.header)
await plugin.dont_know_execution(execution_ids=[e4], reason="other", text="Not our account's order.",
                                 acting_for=request.caller.header)
```

The suites hold it: `connectivity`'s `reports-a-fill-on-no-placement`,
`reports-a-later-fill-on-the-accepted-placement` and
`re-reports-a-charge-on-the-accepted-placement`, each about
`venue-originated fills`, which a plugin whose venue never originates a
fill marks not presented, with why; `ems`'s `accepts-a-fill-to-an-order`,
`accepts-a-fill-to-a-new-order`, `answers-a-fill-dk-with-a-reason` and
`accept-past-ordered-refused`; `operations`'
`names-an-unmatched-fill-as-a-breaks-cause`; and `compliance`'s
`hears-an-order-created-at-accept`.

## Related

- [The order lifecycle: venue-originated fills](../concepts/the-order-lifecycle.md#venue-originated-fills).
- [Route orders through a connectivity plugin](route-orders-through-a-connectivity-plugin.md):
  the link and the venue account map an unmatched fill's account is stamped
  by.
- [Using an operations plugin](using-an-operations-plugin.md): the break an
  unmatched fill explains.
- [The order path in the Python SDK](../api/python-sdk.md#the-order-path).
