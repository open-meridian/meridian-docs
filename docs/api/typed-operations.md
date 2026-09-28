# Typed operations

A plugin reaches the Open Meridian bus through its **typed operations** and nothing else. Each operation is one step of a workflow that a plugin role may take. The plugin calls a typed method, and its sidecar does the rest:

1. It builds the domain message.
2. It stamps the fields only the sidecar knows truthfully.
3. It checks the grant.
4. It sends the message.

A plugin never names a topic.

The operations are generated, not written by hand. One generator reads the contract's matrix and domain protos and emits three things that must agree:

- the plugin-facing gRPC service, `meridian.plugin.v1.PluginOperations`;
- the sidecar's side of it;
- the Python methods on [`Plugin`](python-sdk.md#plugin).

This page lists every operation in this release. There is no order-routing or execution operation.

## Summary

| Python method | gRPC rpc | Workflow step | Kind | Role | Returns |
|---|---|---|---|---|---|
| [`report_sync_status`](#report_sync_status) | `ReportSyncStatus` | W2.1 Observe the brokerage sync state | event | `custody` | `Published` |
| [`record_holdings_statement`](#record_holdings_statement) | `RecordHoldingsStatement` | W2.2 Open a holdings statement | command | `custody` | `RecordHoldingsStatementResult` |
| [`record_holding`](#record_holding) | `RecordHolding` | W2.3 Publish each holding | command | `custody` | `RecordHoldingResult` |
| [`resolve_identifier`](#resolve_identifier) | `ResolveIdentifier` | W3.1 Resolve an identifier set | query | `custody` | `ResolveIdentifierResult` |
| [`report_missing_instrument`](#report_missing_instrument) | `ReportMissingInstrument` | W3.2 Report that a resolution missed | event | `custody` | `Published` |

**Role** is the plugin role that publishes the step, from the contract's matrix. A plugin can call an operation only if it holds that role, approved when it was launched. Otherwise the call raises `NotGranted`. See [Plugins, roles and grants](../concepts/plugins.md) and [Plugin manifest](plugin-manifest.md).

**Kind** says what comes back:

- An **event** returns `Published`, the message's identifier on the bus.
- A **command** or a **query** returns the answer of whatever serves it.

W2 is holdings ingestion from a brokerage. It is read-only throughout: nothing in it places an order. W3 is instrument resolution. The tutorial [Record a holdings statement](../tutorials/record-a-holdings-statement.md) walks through W2.

## Conventions

### Calling

Every operation is an `async` method on the `Plugin` that `meridian.connect()` returns, and takes keyword arguments only. The return types are the generated protobuf messages in `meridian.plugin.v1.operations_pb2`.

```python
import meridian

async with await meridian.connect() as plugin:
    published = await plugin.report_sync_status(
        source="snaptrade", external_account_id="acct-1", connection_healthy=True,
    )
```

### Amounts

!!! important "Amounts are `Decimal` in Python and exact scaled integers on the wire"
    An amount parameter takes a `decimal.Decimal`. The SDK multiplies it by 10^8 and sends the result as an `int64`: `quantity` crosses as `quantity_scaled_1e8`. Nothing on either side is a float.

    An amount is **refused rather than rounded**, in the plugin's process, before anything is sent:

    | Given | Raised |
    |---|---|
    | Anything but a `Decimal`, such as a `float` or an `int` | `TypeError: quantity is a Decimal, not float` |
    | `NaN` or infinity | `ValueError: quantity is not a finite amount` |
    | More than eight decimal places | `ValueError: quantity has more than eight decimal places; it is refused rather than rounded` |
    | Outside what an `int64` holds at 10^8 | `ValueError: quantity is too large to carry` |

    ```python
    from decimal import Decimal

    Decimal("12.5")          # sent as 1_250_000_000
    Decimal("0.00000001")    # sent as 1
    Decimal("0.000000001")   # ValueError
    ```

### Times and dates

A parameter ending `_ns` is a time in nanoseconds, as an `int`. `time.time_ns()` gives one. `as_of_date` is an ISO 8601 date string, such as `"2026-09-25"`.

!!! note
    The contract names the unit of `_ns` fields but not their epoch. The examples on this page assume the Unix epoch, which is what `time.time_ns()` returns.

### Defaults

Every parameter except the two amounts has a default in Python: the empty string, `0`, `False`, an empty sequence, or `None`. A default is what the wire carries when the field is unset. It does not mean the operation succeeds without the parameter. The **Required** column below says which parameters are needed, and who refuses a call without them.

### What the sidecar sets

Some fields describe the publisher rather than the event, and only the sidecar knows them truthfully. They are not parameters:

| Field | Set by the sidecar from |
|---|---|
| `account_id`, on `ReportSyncStatus` and `RecordHolding` | The link a deployment admin made from the plugin's `external_account_id` to an account. Refused when there is none. |
| `publisher_instance_id`, on `ReportMissingInstrument` | The instance the plugin was launched as. |

The sidecar also puts the plugin's own instance in place of `{instance}` in a topic, so a plugin can speak only as itself.

### Acting for a person

The two commands, `record_holdings_statement` and `record_holding`, take `acting_for`. Pass the `Meridian-Caller` header of the page request you are serving; with [`CallerMiddleware`](python-sdk.md#callermiddleware) that is `request.state.caller.header`.

- **Unset:** the plugin acts as itself.
- **Set:** the sidecar checks the assertion, admits the command only when that person may write the account it names, and stamps the person on it. For a command that names no account, the person must be able to write something through the plugin.

A person narrows what a plugin may do and never widens it.

## Errors { #errors }

A refusal is the call's gRPC status, chosen by what the caller should do about it. The SDK raises it as one of its own exceptions:

| Raised | Sidecar status | Means | Your next move |
|---|---|---|---|
| `NotGranted` | `PERMISSION_DENIED` | None of the plugin's roles grants this operation; or the account is outside the plugin's write scope; or the person in `acting_for` may not write it. | Stop. It is configuration: a role, a permission or a link, which a person changes. |
| `CallFailed`, `kind="refused"` | `FAILED_PRECONDITION` | An `external_account_id` nobody has linked to an account; or the sidecar considers the plugin not registered, or already left. | Report it. A deployment admin links the account, and the next statement records it. |
| `CallFailed`, `kind="invalid"` | `INVALID_ARGUMENT` | A required field is empty, such as `external_account_id`. | Fix the call. |
| `CallFailed`, `kind="no handler"` | `UNAVAILABLE` | Nothing serves the topic right now. | Retry later. |
| `CallFailed`, `kind="timeout"` | `DEADLINE_EXCEEDED` | What serves it did not answer in time. | Retry. |
| `CallFailed`, `kind="handler error"` | `ABORTED` | What serves it answered with a refusal. `detail` is its reason. | Report it. |
| `CallFailed`, `kind="not vouched for"` | `UNAUTHENTICATED` | The `acting_for` assertion was not accepted: expired, replayed, for another instance, or the sidecar holds none of the dashboard's keys. | Ask the person to reload the page. |
| `NotRegistered` | none (raised by the SDK) | The plugin has called `leave()`. | Don't use it after leaving. |
| `TypeError`, `ValueError` | none (raised by the SDK) | An amount that is not a `Decimal`, or that would have to be rounded. | Fix the call. |
| `grpc.aio.AioRpcError` | any other, such as `INTERNAL` | Raised unchanged. | |

On `NotGranted` and `CallFailed`, `topic` holds the operation's name, such as `"RecordHolding"`. On a development deployment, a grant or write-scope refusal also appears as a [`refused` event](plugin-dev-events.md).

!!! note
    `NotGranted` and `CallFailed` use an attribute called `topic`, but for typed operations it holds the operation's name, not a bus topic.

## `report_sync_status` { #report_sync_status }

Reports how fresh a connected account's data is, as the rail (the brokerage aggregator) reports it. It is published so an operator can tell stale data from absent data. Those look identical on a holdings screen and mean different things.

```python
async def report_sync_status(
    self, *, source: str = "", last_synced_at_ns: int = 0, connection_healthy: bool = False,
    status_detail: str = "", observed_at_ns: int = 0, external_account_id: str = "",
) -> Published
```

| | |
|---|---|
| gRPC | `rpc ReportSyncStatus(ReportSyncStatusParams) returns (Published)` |
| Workflow step | W2.1, Observe the brokerage sync state |
| Kind | event, on `platform.custody.{instance}.event.sync-status` |
| Role | `custody` |
| Heard by | the dashboard |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `source` | `str` | no | The rail's namespace, such as `"snaptrade"`. |
| `last_synced_at_ns` | `int` | no | When the rail last synced this account from the institution. |
| `connection_healthy` | `bool` | no | Whether the rail considers the connection healthy now. `False` with a recent `last_synced_at_ns` means the data is good but the connection has since broken. |
| `status_detail` | `str` | no | The rail's text when the connection is unhealthy. Diagnostic only; nothing branches on it. |
| `observed_at_ns` | `int` | no | When the plugin observed this. |
| `external_account_id` | `str` | yes, by the sidecar | The account as the rail knows it. The sidecar translates it to an account through its link, and refuses it when empty (`invalid`) or not linked (`refused`). |

**Returns** `Published`:

| Field | Type | Meaning |
|---|---|---|
| `message_id` | `str` | The message's identifier on the bus. |

**Errors:** `invalid` for an empty `external_account_id`; `refused` for one not linked; `NotGranted` without the `custody` role.

```python
import time

await plugin.report_sync_status(
    source="snaptrade",
    external_account_id="acct-1",
    connection_healthy=True,
    last_synced_at_ns=last_sync_ns,
    observed_at_ns=time.time_ns(),
)
```

## `record_holdings_statement` { #record_holdings_statement }

Opens one statement: one read of one rail, at one moment. Every holding row then attaches to it.

It carries two dates, and they are not the same thing:

- `as_of_date` is the date the positions reflect.
- `read_at_ns` is when the plugin fetched them.

A statement read this morning may be as of yesterday's close.

```python
async def record_holdings_statement(
    self, *, source: str = "", external_statement_id: str = "", as_of_date: str = "",
    read_at_ns: int = 0, expected_rows: int = 0, acting_for: str | None = None,
) -> RecordHoldingsStatementResult
```

| | |
|---|---|
| gRPC | `rpc RecordHoldingsStatement(RecordHoldingsStatementParams) returns (RecordHoldingsStatementResult)` |
| Workflow step | W2.2, Open a holdings statement |
| Kind | command, on `platform.street.command.record-statement` |
| Role | `custody` |
| Served by | the street store: what custodians say is held |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `source` | `str` | no | The rail's namespace, such as `"snaptrade"`. |
| `external_statement_id` | `str` | no | The rail's own identifier for this statement, where it has one. Used to recognise a redelivery of the same statement. |
| `as_of_date` | `str` | no | The ISO 8601 date the positions are as of. |
| `read_at_ns` | `int` | no | When the plugin read them. |
| `expected_rows` | `int` | yes, by the workflow | How many holding rows will follow. It is the only thing that marks the end of a statement. The street store closes the statement when this many rows have landed. A statement whose rows never all arrive stays open rather than publishing counts that are wrong. Hold the whole list before recording any of it. |
| `acting_for` | `str` or `None` | no | The `Meridian-Caller` header of the person this is sent for. See [Acting for a person](#acting-for-a-person). |

**Returns** `RecordHoldingsStatementResult`:

| Field | Type | Meaning |
|---|---|---|
| `statement_id` | `str` | Assigned by the deployment. Every row references it. |
| `already_recorded` | `bool` | `True` when this statement had already been recorded and the existing one is returned. Redelivery is a no-op, not a duplicate. |

**Errors:** `no handler`, `timeout` or `handler error` from the street store. With `acting_for`: `not vouched for`, or `NotGranted` when the person may write nothing through the plugin. `NotGranted` without the `custody` role.

```python
import time

statement = await plugin.record_holdings_statement(
    source="snaptrade",
    external_statement_id="stmt-2026-09-25",
    as_of_date="2026-09-25",
    read_at_ns=time.time_ns(),
    expected_rows=len(rows),
)
```

## `record_holding` { #record_holding }

Records one holding, for one account, at one instrument, against an open statement.

Set exactly one of `instrument_id` and `unresolved_identifiers`:

- `instrument_id` when the plugin resolved the instrument ([`resolve_identifier`](#resolve_identifier));
- `unresolved_identifiers` when it could not.

A row that could not be resolved is still recorded. A dropped holding would be invisible.

```python
async def record_holding(
    self, *, statement_id: str = "", instrument_id: str = "",
    unresolved_identifiers: Sequence[Identifier] = (), quantity: Decimal, market_value: Decimal,
    currency: str = "", external_account_id: str = "", acting_for: str | None = None,
) -> RecordHoldingResult
```

| | |
|---|---|
| gRPC | `rpc RecordHolding(RecordHoldingParams) returns (RecordHoldingResult)` |
| Workflow step | W2.3, Publish each holding |
| Kind | command, on `platform.street.command.record-holding` |
| Role | `custody` |
| Served by | the street store |

| Name | Type | Required | Meaning | On the wire |
|---|---|---|---|---|
| `statement_id` | `str` | yes, by the workflow | The `statement_id` that `record_holdings_statement` returned. | `statement_id` |
| `instrument_id` | `str` | one of these two | The instrument, when resolution succeeded. | `instrument_id` |
| `unresolved_identifiers` | sequence of `Identifier` | one of these two | Everything the plugin held, when resolution did not succeed, so an operator can see exactly what could not be accounted for. | `unresolved_identifiers` |
| `quantity` | `Decimal` | yes, by Python | Signed: negative is a short position. At most eight decimal places. | `quantity_scaled_1e8`, `int64` |
| `market_value` | `Decimal` | yes, by Python | The rail's valuation of the holding, recorded as reported and not recomputed. At most eight decimal places. | `market_value_scaled_1e8`, `int64` |
| `currency` | `str` | no | ISO 4217 code for `market_value`. | `currency` |
| `external_account_id` | `str` | yes, by the sidecar | The account as the rail knows it. The sidecar translates it through its link, and refuses it when empty or not linked. | `external_account_id` |
| `acting_for` | `str` or `None` | no | The `Meridian-Caller` header of the person this is sent for. | `acting_for` |

!!! note
    The contract says "never both, and never neither" for `instrument_id` and `unresolved_identifiers`. Neither the SDK nor the sidecar's generated code checks this before sending. Whether the street store refuses a row that breaks the rule is not visible in the plugin-facing code.

**Returns** `RecordHoldingResult`:

| Field | Type | Meaning |
|---|---|---|
| `holding_id` | `str` | The recorded row. |
| `resolved` | `bool` | `True` when the row carried an instrument and updated a custodial position. `False` for an unresolved row, which updates nothing until the deployment knows what it holds. |

**Errors:**

- `TypeError` or `ValueError` for an amount.
- `invalid` for an empty `external_account_id`, and `refused` for one not linked. The unlinked account is reported to the deployment admin, and the next statement after it is linked records it.
- `NotGranted` when the linked account is outside the plugin's write scope, or when the person in `acting_for` may not write it.
- `not vouched for` for an `acting_for` that is not accepted.
- `no handler`, `timeout` or `handler error` from the street store.

```python
from decimal import Decimal
import meridian

result = await plugin.record_holding(
    statement_id=statement.statement_id,
    instrument_id=instrument_id,
    quantity=Decimal("150"),
    market_value=Decimal("34218.75"),
    currency="USD",
    external_account_id="acct-1",
)

# An instrument that did not resolve is still recorded:
await plugin.record_holding(
    statement_id=statement.statement_id,
    unresolved_identifiers=[meridian.Identifier(scheme="symbol", value="XYZQ", source="snaptrade")],
    quantity=Decimal("10"),
    market_value=Decimal("12.30"),
    currency="USD",
    external_account_id="acct-1",
)
```

## `resolve_identifier` { #resolve_identifier }

Reverse resolution: asks which instrument a set of identifiers maps to, as of a date. The strongest identifier is matched first: a global identifier, then a symbol qualified by venue and currency.

A miss comes in two kinds, and ambiguity is one of them. When more than one instrument matches, the result is a miss rather than a pick.

```python
async def resolve_identifier(
    self, *, identifiers: Sequence[Identifier] = (), as_of_ns: int = 0,
    exchange_mic: str = "", currency: str = "",
) -> ResolveIdentifierResult
```

| | |
|---|---|
| gRPC | `rpc ResolveIdentifier(ResolveIdentifierParams) returns (ResolveIdentifierResult)` |
| Workflow step | W3.1, Resolve an identifier set |
| Kind | query, on `platform.reference.query.resolve-identifier` |
| Role | `custody` |
| Served by | the instrument store, the deployment's replica of the security master |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `identifiers` | sequence of `Identifier` | yes, by the contract | At least one. Matched strongest first. |
| `as_of_ns` | `int` | no | The reference time: the date the mapping is being asked about. An identifier maps to different instruments over time. |
| `exchange_mic` | `str` | no | Narrows a symbol match. Empty means unconstrained. |
| `currency` | `str` | no | Narrows a symbol match. |

**Returns** `ResolveIdentifierResult`:

| Field | Type | Meaning |
|---|---|---|
| `found` | `bool` | Whether exactly one instrument matched. |
| `instrument_id` | `str` | The instrument, when `found`. |
| `miss_reason` | `MissReason` | Set only when `found` is `False`: `MISS_REASON_NOT_FOUND` or `MISS_REASON_AMBIGUOUS`. |

**Errors:** `no handler`, `timeout` or `handler error` from the instrument store. `NotGranted` without the `custody` role.

```python
import time
import meridian

held = [
    meridian.Identifier(scheme="isin", value="US0378331005"),
    meridian.Identifier(scheme="symbol", value="AAPL", source="snaptrade"),
]
answer = await plugin.resolve_identifier(identifiers=held, as_of_ns=time.time_ns())
if answer.found:
    instrument_id = answer.instrument_id
else:
    reason = answer.miss_reason  # then report_missing_instrument, and carry on
```

## `report_missing_instrument` { #report_missing_instrument }

Reports that a resolution missed. **A fact, not a request.** The plugin reports what it held and carries on with the next holding. It does not ask for an instrument to be created, does not wait for one, and could not create one. The deployment and the platform decide what the instrument is, and an administrator completes it.

```python
async def report_missing_instrument(
    self, *, source: str = "", asset_class: str = "", identifiers: Sequence[Identifier] = (),
    as_of_ns: int = 0, reason: MissReason | None = None, observed_at_ns: int = 0,
) -> Published
```

| | |
|---|---|
| gRPC | `rpc ReportMissingInstrument(ReportMissingInstrumentParams) returns (Published)` |
| Workflow step | W3.2, Report that a resolution missed |
| Kind | event, on `platform.reference.event.instrument-missing` |
| Role | `custody` |
| Heard by | the instrument store, per the matrix. In W3.3 the conductor acts on the miss, asking the platform whether it already knows the instrument. |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `source` | `str` | no | The namespace the miss occurred in, such as `"snaptrade"`. |
| `asset_class` | `str` | no | The instrument's asset class. |
| `identifiers` | sequence of `Identifier` | no | Everything the plugin held at the miss. Enough to look it up against a global scheme, or to create a stub carrying them. |
| `as_of_ns` | `int` | no | The reference time of the missed resolution. The reaction targets the mapping effective then, not now. |
| `reason` | `MissReason` or `None` | no | The `miss_reason` that `resolve_identifier` returned. `None` leaves it unset, which reads as `MISS_REASON_UNSPECIFIED`. |
| `observed_at_ns` | `int` | no | When the plugin observed the miss. |

The sidecar sets `publisher_instance_id`.

**Returns** `Published`, with `message_id`, the message's identifier on the bus.

**Errors:** `NotGranted` without the `custody` role.

```python
import time

await plugin.report_missing_instrument(
    source="snaptrade",
    asset_class="equity",
    identifiers=held,
    as_of_ns=as_of_ns,
    reason=answer.miss_reason,
    observed_at_ns=time.time_ns(),
)
```

## The gRPC service

For reference, the plugin-facing service in `meridian/plugin/v1/operations.proto`, which the sidecar serves on loopback:

```protobuf
service PluginOperations {
  rpc ReportSyncStatus(ReportSyncStatusParams) returns (Published);
  rpc RecordHoldingsStatement(RecordHoldingsStatementParams) returns (RecordHoldingsStatementResult);
  rpc RecordHolding(RecordHoldingParams) returns (RecordHoldingResult);
  rpc ResolveIdentifier(ResolveIdentifierParams) returns (ResolveIdentifierResult);
  rpc ReportMissingInstrument(ReportMissingInstrumentParams) returns (Published);
}
```

Each `…Params` message keeps the field numbers of the domain message it stands for and drops the fields the sidecar stamps, so its encoding is the domain message's. `acting_for` is field 1000 on the two commands, a `meridian.v1.CallerAssertion`. The SDK decodes it from the base64url `Meridian-Caller` header you pass. `Identifier` and `MissReason` are plugin-facing mirrors of the domain types.
