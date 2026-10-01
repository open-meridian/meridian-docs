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

This page lists every operation in SDK 0.12.0, which adds the two reads, `list_custodial_positions` and `list_statements`, to those of 0.7.0, and a statement's external account and figures per margin segment and a holding's cost and lots to the two commands that record holdings. There is no order-routing or execution operation.

## Summary

| Python method | gRPC rpc | Workflow step | Kind | Role | Returns |
|---|---|---|---|---|---|
| [`report_external_accounts`](#report_external_accounts) | `ReportExternalAccounts` | W2.8 Report the accounts a connection reaches | event | `custody` | `Published` |
| [`report_sync_status`](#report_sync_status) | `ReportSyncStatus` | W2.1 Observe the brokerage sync state | event | `custody` | `Published` |
| [`record_holdings_statement`](#record_holdings_statement) | `RecordHoldingsStatement` | W2.2 Open a holdings statement | command | `custody` | `RecordHoldingsStatementResult` |
| [`record_holding`](#record_holding) | `RecordHolding` | W2.3 Publish each holding | command | `custody` | `RecordHoldingResult` |
| [`list_custodial_positions`](#list_custodial_positions) | `ListCustodialPositions` | W2.7 Read custodial positions | query | `operations` | `ListCustodialPositionsResult` |
| [`list_statements`](#list_statements) | `ListStatements` | W2.9 Read completed statements | query | `operations` | `ListStatementsResult` |
| [`resolve_identifier`](#resolve_identifier) | `ResolveIdentifier` | W3.1 Resolve an identifier set | query | `custody` | `ResolveIdentifierResult` |
| [`report_missing_instrument`](#report_missing_instrument) | `ReportMissingInstrument` | W3.2 Report that a resolution missed | event | `custody` | `Published` |
| [`read_accounts_for_linking`](#read_accounts_for_linking) | `ReadAccountsForLinking` | W6.4 Link a plugin's external account | query | `custody` | `ReadAccountsForLinkingResult` |
| [`link_external_account`](#link_external_account) | `LinkExternalAccount` | W6.4 Link a plugin's external account | command | `custody` | `LinkExternalAccountResult` |

**Role** is the plugin role that publishes the step, or asks the query, from the contract's matrix. A plugin can call an operation only if it holds that role, approved when it was launched. Otherwise the call raises `NotGranted`. See [Plugins, roles and grants](../concepts/plugins.md) and [Plugin manifest](plugin-manifest.md).

**Kind** says what comes back:

- An **event** returns `Published`, the message's identifier on the bus.
- A **command** or a **query** returns the answer of whatever serves it.

W2 is holdings ingestion from a brokerage. It is read-only throughout: nothing in it places an order. A `custody` plugin records what the custodian says is held, and an `operations` plugin reads it, within its read scope, and hears it change with [`receive`](python-sdk.md#receive), the stream of what a plugin's roles hear (W4.3, `rpc Receive`). W3 is instrument resolution. W6.4 is linking the accounts a source reaches to the firm's own, which a plugin does on its own page at `admin`, for the admin of the plugin viewing it under Manage. The tutorial [Record a holdings statement](../tutorials/record-a-holdings-statement.md) walks through W2 and W6.4.

## Conventions

### Calling

Every operation is an `async` method on the `Plugin` that `meridian.connect()` returns, and takes keyword arguments only. The return types are the generated protobuf messages in `meridian.plugin.v1.operations_pb2`. Each parameter crosses the wire under its own name.

```python
import meridian

async with await meridian.connect() as plugin:
    published = await plugin.report_sync_status(
        source="snaptrade", external_account_id="acct-1", connection_healthy=True,
    )
```

### Numbers and amounts

!!! important "Numbers are `Decimal` in Python, and exact integers that carry their own scale on the wire"
    A quantity takes a `decimal.Decimal` or an `int`. An amount of currency takes a [`meridian.Money`](#money): an amount and its ISO 4217 currency code, together, so an amount is never separated from its currency.

    On the wire a number is its integer, in two 64-bit halves, and the scale it was stated with. `Decimal("1.50")` crosses as 150 at scale 2 and reads back as `1.50`. Nothing on either side is a float, and nothing normalises the scale.

    A number is **refused rather than rounded**, in the plugin's process, before anything is sent:

    | Given | Raised |
    |---|---|
    | A `float`, a `bool`, or anything but a `Decimal` or an `int` | `TypeError: quantity is a Decimal or an int, not float` |
    | `NaN` or infinity | `ValueError: quantity is not a finite number` |
    | More than 18 decimal places | `ValueError: quantity has 19 decimal places; at most 18 cross the wire, and it is refused rather than rounded` |
    | More than 38 digits | `ValueError: quantity has more than 38 digits; it is refused rather than rounded` |
    | For an amount, anything but a `meridian.Money` | `TypeError: market_value is a meridian.Money, not Decimal` |
    | A `Money` whose `currency_code` is not a `str` | `TypeError: market_value's currency_code is a str, not NoneType` |

    ```python
    from decimal import Decimal
    import meridian

    Decimal("12.5")                    # sent as 125 at scale 1
    Decimal("0.000000000000000001")    # sent as 1 at scale 18
    Decimal("0.0000000000000000001")   # ValueError: 19 decimal places
    meridian.Money(Decimal("34218.75"), "USD")
    ```

The sidecar holds a plugin that builds its params by hand to the same bounds, and refuses one outside them as `invalid`, naming the field.

Convert what the venue sent to the platform's convention before calling: amounts in the currency's major unit, and quantities in the instrument's own units. A plugin that read cents converts them. Keep what the venue sent, as sent, in the plugin's own logs. A float the venue sent becomes `Decimal(repr(value))`, its shortest round-trip form, never `Decimal(value)`, its binary expansion.

`meridian.as_decimal` and `meridian.as_money` read a number, or an amount, back off the wire exactly as it was stated.

### Enums { #enums }

A parameter whose type is an enum, such as [`AssetClass`](#assetclass) or [`HoldingSide`](#holdingside), takes the value (`meridian.AssetClass.ASSET_CLASS_EQUITY`), its name as a string (`"ASSET_CLASS_EQUITY"`), or that name without the enum's prefix in lower case (`"equity"`). `None` or `""` leaves it unset. Anything else, a different case or a value the enum does not define, raises `ValueError` naming the parameter and the values it takes, before anything is sent. The sidecar refuses a number the enum does not define with `invalid`, for a plugin that builds its params by hand.

### Times and dates

A parameter ending `_ns` is a time in nanoseconds, as an `int`. `time.time_ns()` gives one. `as_of_date` is an ISO 8601 date string, such as `"2026-09-25"`.

!!! note
    The contract names the unit of `_ns` fields but not their epoch. The examples on this page assume the Unix epoch, which is what `time.time_ns()` returns.

### Defaults

Every parameter except `quantity` has a default in Python: the empty string, `0`, `False`, an empty sequence, or `None`. A default is what the wire carries when the field is unset. It does not mean the operation succeeds without the parameter. The **Required** column below says which parameters are needed, and who refuses a call without them.

### What the sidecar sets

Some fields describe the publisher rather than the event, and only the sidecar knows them truthfully. They are not parameters:

| Field | On | Set by the sidecar from |
|---|---|---|
| `account_id` | `RecordHoldingsStatement`, `RecordHolding` | The link an admin of the plugin made from the plugin's `external_account_id` to an account. Refused when there is none, as [`NotLinked`](#an-unlinked-external-account). On a statement from 0.12.0. |
| `account_id` | `ReportSyncStatus` | The same link, or empty when there is none. Never refused. |
| `publisher_instance_id` | `ReportMissingInstrument` | The instance the plugin was launched as. |
| `placeholder_instrument_id` | `ReportMissingInstrument` | Nothing: always empty from a plugin. Only the instrument store sets it. |
| `plugin_instance_id` | `LinkExternalAccount` | The instance the plugin was launched as. |

The sidecar also puts the plugin's own instance in place of `{instance}` in a topic, so a plugin can speak only as itself.

### Reads are within the read scope { #reads }

From 0.12.0. The sidecar stamps the plugin's [read scope](../concepts/accounts.md#how-accounts-bound-a-plugin) on every read, and the store answers only within it: a read naming an account outside it is refused with `NotGranted`, one naming none answers every account in it, and a plugin whose read scope is empty reads nothing. A plugin reads its whole scope as itself, and serves each person from it with `caller.read`. What it hears with [`receive`](python-sdk.md#receive) is held to the same scope.

Each read answers a page, the next page's `cursor` in `next_cursor`, empty on the last, and `as_of`, the [`Watermark`](#watermark) it was read at. Given a watermark as `since`, a read answers only what changed after it. `receive` reads this way to seed and to catch up, so a plugin hearing a row seldom reads it itself.

### Acting for a person

Four operations take `acting_for`: the two commands that record holdings, and the two that link accounts. Pass the `Meridian-Caller` header of the page request you are serving: in a view on [`meridian.Pages`](python-sdk.md#pages), `request.caller.header`; with [`CallerMiddleware`](python-sdk.md#callermiddleware), `request.state.caller.header`.

For `record_holdings_statement` and `record_holding`, it is optional:

- **Unset:** the plugin acts as itself.
- **Set:** the sidecar checks the assertion, admits the command only in a session opened by **Open**, at `write`, and only when that person may write the account it names, and stamps the person on it. For a command that names no account, the person must be able to write something through the plugin. A command sent for a person in a session opened by Manage or View is refused with `NotGranted`, naming the session.

A person narrows what a plugin may do and never widens it.

For `read_accounts_for_linking` and `link_external_account`, it is required. They touch the deployment's configuration, which a plugin reaches only acting for an admin of the plugin in a session opened by **Manage**, at `admin`, and never as itself. Without an assertion, or with one from a session at any other level, the sidecar refuses the call with `NotGranted`. They are the only reads and commands the sidecar admits for a person in a Manage session: that session reaches no account's data.

## Errors { #errors }

A refusal is the call's gRPC status, chosen by what the caller should do about it. The SDK raises it as one of its own exceptions:

| Raised | Sidecar status | Means | Your next move |
|---|---|---|---|
| `NotGranted` | `PERMISSION_DENIED` | None of the plugin's roles grants this operation; or the account is outside the plugin's write scope, or, for a read, its read scope; or the person in `acting_for` may not write it, or sent it from a session not opened by Open; or an operation on the deployment's configuration without the assertion of an admin of the plugin under Manage; or a new account named by somebody who is not a deployment admin; or a link for an external account this plugin did not report. | Stop. It is configuration: a role, a permission, a link or an admin, which a person changes. |
| `NotLinked`, `kind="refused"` | `FAILED_PRECONDITION`, with the code `REFUSAL_REASON_EXTERNAL_ACCOUNT_NOT_LINKED` | An `external_account_id` nobody has linked to an account. See [An unlinked external account](#an-unlinked-external-account). | Offer it for linking, and stop this statement. An admin of the plugin links the account, and the next statement records it. |
| `CallFailed`, `kind="refused"` | `FAILED_PRECONDITION`, with no code | The sidecar considers the plugin not registered, or already left. | Connect again. |
| `CallFailed`, `kind="invalid"` | `INVALID_ARGUMENT` | A required field is empty, such as `external_account_id`; or a number outside what the wire carries, in params built by hand. | Fix the call. |
| `CallFailed`, `kind="no handler"` | `UNAVAILABLE` | Nothing serves the topic right now. | Retry later. |
| `CallFailed`, `kind="timeout"` | `DEADLINE_EXCEEDED` | What serves it did not answer in time. | Retry. |
| `CallFailed`, `kind="handler error"` | `ABORTED` | What serves it answered with a refusal. `detail` is its reason. | Report it. |
| `CallFailed`, `kind="not vouched for"` | `UNAUTHENTICATED` | The `acting_for` assertion was not accepted: expired, replayed, for another instance, or the sidecar holds none of the dashboard's keys. | Ask the person to reload the page. |
| `NotRegistered` | none (raised by the SDK) | The plugin has called `leave()`. | Don't use it after leaving. |
| `TypeError`, `ValueError` | none (raised by the SDK) | A number that is not a `Decimal` or an `int`, an amount that is not a `Money`, or a number that would have to be rounded; from 0.12.0, a statement whose figures the sidecar would refuse. | Fix the call. |
| `grpc.aio.AioRpcError` | any other, such as `INTERNAL` | Raised unchanged. | |

On `NotGranted` and `CallFailed`, `topic` holds the operation's name, such as `"RecordHolding"`. The exception's text is the operation's name, then the kind, then the sidecar's own words. For a row naming an external account nobody has linked:

```text
RecordHolding: refused: external account acct-1 is not linked to an account; a deployment admin links it on the plugin's admin page (W6.4), and the next statement records it
```

Match on the exception's class, and on `kind`, never on these words: they are for a person reading a log, and may be reworded at any release.

!!! note
    `NotGranted` and `CallFailed` use an attribute called `topic`, but for typed operations it holds the operation's name, not a bus topic.

### An unlinked external account { #an-unlinked-external-account }

A row naming an external account that nobody has linked is refused, and nothing is recorded for it. From SDK 0.7.0 that refusal carries a code, so a plugin can tell it apart from the other refusal with the same status, a plugin that is not registered.

The sidecar sends the code beside the status: a `meridian.v1.Refusal`, encoded, in the call's trailing metadata `meridian-refusal-bin`. Its `reason` comes from the refusal catalogue, the `RefusalReason` enum in `meridian/v1/sidecar.proto`:

| Reason | Number | Status | Sent when |
|---|---|---|---|
| `REFUSAL_REASON_UNSPECIFIED` | 0 | | Never sent. A refusal the status already says everything about carries no code. |
| `REFUSAL_REASON_EXTERNAL_ACCOUNT_NOT_LINKED` | 1 | `FAILED_PRECONDITION` | The operation named an external account nobody has linked to an account. Nothing was recorded, and the next statement after a link records it. |

A reason is never reused for another cause, and a retired one's number stays reserved. [`record_holding`](#record_holding) can be refused this way, and from 0.12.0 [`record_holdings_statement`](#record_holdings_statement), which names its external account too; `report_sync_status` for an unlinked account is not refused.

The SDK reads the code and raises **`meridian.NotLinked`**. It is a `CallFailed` whose `kind` is `"refused"`, as this refusal always was, so a plugin that caught `CallFailed` still catches it. It is raised by the code alone: a refusal that carries no code is a plain `CallFailed`, whatever its words say. A sidecar from before the catalogue sends none, so on such a deployment the same refusal arrives as `CallFailed` with `kind="refused"`, which catching `CallFailed` still covers.

Catch `NotLinked`. Do not match the text of the exception:

```python
try:
    await plugin.record_holding(..., external_account_id="acct-3")
except meridian.NotLinked:
    ...  # offer acct-3 for linking; stop this statement
```

To know before sending, read the plugin's links from [`account_scope()`](python-sdk.md#account_scope): `scope.link_of("acct-3")` is `None` while it is unlinked. The link can still be removed between reading and sending, so catch `NotLinked` all the same.

A plugin written in another language reads the same trailer: decode the `Refusal` from `meridian-refusal-bin` and compare its `reason`.

### Refusals on a development deployment

On a development deployment, a refusal by the sidecar itself, for a grant, the write scope, the deployment's configuration, an external account the plugin did not report, or a number out of range, also appears as a [`refused` event](plugin-dev-events.md).

## `report_external_accounts` { #report_external_accounts }

Reports every external account the plugin's connection reaches, as the source presents them. A custody plugin sends it before it records anything, and again whenever the list changes. One connection can reach several accounts, and an admin can link only an account the plugin reported.

It is the whole list each time. An account missing from it is one the connection no longer reaches.

```python
async def report_external_accounts(
    self, *, accounts: Sequence[ExternalAccount] = (),
) -> Published
```

| | |
|---|---|
| gRPC | `rpc ReportExternalAccounts(ReportExternalAccountsParams) returns (Published)` |
| Workflow step | W2.8, Report the accounts a connection reaches |
| Kind | event, on `platform.custody.{instance}.event.external-accounts` |
| Role | `custody` |
| Heard by | the dashboard, which counts the unlinked ones on the plugin's health |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `accounts` | sequence of [`ExternalAccount`](#externalaccount) | no | Every account the connection reaches. |

The sidecar keeps the list as the accounts a link from this plugin may name.

**Returns** `Published`, with `message_id`, the message's identifier on the bus.

**Errors:** `NotGranted` without the `custody` role.

```python
import meridian

await plugin.report_external_accounts(
    accounts=[
        meridian.ExternalAccount(
            external_account_id="acct-1", name="Individual brokerage", venue_account_type="Individual"
        ),
        meridian.ExternalAccount(
            external_account_id="acct-2", name="Rollover IRA", venue_account_type="IRA"
        ),
    ],
)
```

## `report_sync_status` { #report_sync_status }

Reports how fresh a connected account's data is, as the rail (the brokerage aggregator) reports it, and why when it is not current. It is published so an operator can tell stale data from absent data, and knows whose fix it is. Those look identical on a holdings screen and mean different things.

```python
async def report_sync_status(
    self, *, source: str = "", last_synced_at_ns: int = 0, connection_healthy: bool = False,
    status_detail: str = "", observed_at_ns: int = 0, external_account_id: str = "",
    state: SyncState | str | None = None, holdings_as_of_ns: int = 0, history_as_of_ns: int = 0,
) -> Published
```

| | |
|---|---|
| gRPC | `rpc ReportSyncStatus(ReportSyncStatusParams) returns (Published)` |
| Workflow step | W2.1, Observe the brokerage sync state |
| Kind | event, on `platform.custody.{instance}.event.sync-status` |
| Role | `custody` |
| Heard by | the dashboard, which shows it on the **Overview** tab of the plugin's view in Settings |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `source` | `str` | no | The rail's namespace, such as `"snaptrade"`. |
| `last_synced_at_ns` | `int` | no | When the rail last synced this account from the institution. Not when the data is as of: see the two `_as_of_ns` fields. |
| `connection_healthy` | `bool` | no | Whether the rail considers the connection healthy now. `False` with a recent `last_synced_at_ns` means the data is good but the connection has since broken. `state` says why. |
| `status_detail` | `str` | no | The rail's text, for whatever `state` does not say. Diagnostic only; nothing branches on it. |
| `observed_at_ns` | `int` | no | When the plugin observed this. |
| `external_account_id` | `str` | yes, by the sidecar | The account as the rail knows it. The sidecar refuses it when empty (`invalid`). It is not refused when unlinked: the dashboard shows the status beside the unlinked account, so an admin can tell whether it is worth linking. |
| `state` | [`SyncState`](#syncstate) or `None` | no | Whether the data is current, and if not, why. `None` leaves it unset, which reads as `SYNC_STATE_UNSPECIFIED`, shown as what `connection_healthy` says. |
| `holdings_as_of_ns` | `int` | no | When the holdings the rail serves are as of. `0` where the rail does not say. |
| `history_as_of_ns` | `int` | no | When the history (transactions) is as of. Apart from holdings, because a connection can have one current and the other not. |

**Returns** `Published`, with `message_id`, the message's identifier on the bus.

**Errors:** `invalid` for an empty `external_account_id`; `NotGranted` without the `custody` role.

```python
import time
import meridian

await plugin.report_sync_status(
    source="snaptrade",
    external_account_id="acct-1",
    connection_healthy=True,
    state=meridian.SyncState.SYNC_STATE_CURRENT,
    last_synced_at_ns=last_sync_ns,
    holdings_as_of_ns=last_sync_ns,
    observed_at_ns=time.time_ns(),
)
```

## `record_holdings_statement` { #record_holdings_statement }

Opens one statement: the plugin's snapshot of one account, at one moment. Every holding row then attaches to it.

From 0.12.0 the statement names that account, as the source knows it, and the sidecar records it against the account the external account is linked to, as it does a row. A statement is one account's: a row naming another account is refused.

It carries two dates, and they are not the same thing:

- `as_of_date` is the date the positions reflect.
- `read_at_ns` is when the plugin fetched them.

A statement read this morning may be as of yesterday's close.

```python
async def record_holdings_statement(
    self, *, source: str = "", external_statement_id: str = "", as_of_date: str = "",
    read_at_ns: int = 0, expected_rows: int = 0, buying_power: Money | None = None,
    margin_requirement: Money | None = None, maintenance_excess: Money | None = None,
    currency_assumed: bool = False, external_account_id: str = "",
    figures: Sequence[StatementFigures] = (), institution: str = "",
    acting_for: str | None = None,
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
| `external_statement_id` | `str` | no | The plugin's identifier for this snapshot, made from the account it read and when it read it, so the same read sent twice has the same one. Used to recognise a redelivery of the same statement. |
| `as_of_date` | `str` | no | The ISO 8601 date the positions are as of. |
| `read_at_ns` | `int` | no | When the plugin read them. |
| `expected_rows` | `int` | yes, by the workflow | How many holding rows will follow. It is the only thing that marks the end of a statement. The street store closes the statement when this many rows have landed. A statement whose rows never all arrive stays open rather than publishing counts that are wrong. Hold the whole list before recording any of it. |
| `external_account_id` | `str` | yes, by the sidecar | The account as the rail knows it, the one the statement's rows name. The sidecar translates it through its link, and refuses it when empty or not linked. From 0.12.0. |
| `institution` | `str` | no | The institution holding the external account, as the plugin names it: the brokerage behind an aggregator, as SnapTrade names it, or the venue itself for a plugin that reads the venue directly. Empty where the source does not say. From 0.12.0. |
| `figures` | sequence of [`StatementFigures`](#statementfigures) | no | The account's figures, one set per margin segment the venue reports, each naming its segment as the venue does; the set with no segment is the account's as a whole. No two sets name the same segment. Every figure is as the venue reported it, and never derived from the holdings. From 0.12.0. |
| `currency_assumed` | `bool` | no | `True` when the venue stated no currency for these figures, and the one given is the plugin's own assumption. Of every set in `figures`. |
| `buying_power`, `margin_requirement`, `maintenance_excess` | [`Money`](#money) or `None` | no | Superseded by `figures` from 0.12.0. Sent alone, they are read as the set with no segment; sent beside `figures`, they are refused. [`meridian plugin migrate`](cli.md#plugin-migrate) rewrites them into `figures`. |
| `acting_for` | `str` or `None` | no | The `Meridian-Caller` header of the person this is sent for. See [Acting for a person](#acting-for-a-person). |

A brokerage's own total account value goes in `net_liquidation`, in the set with no segment, as the brokerage reports it: never a sum the plugin makes of the holdings.

**Returns** `RecordHoldingsStatementResult`:

| Field | Type | Meaning |
|---|---|---|
| `statement_id` | `str` | Assigned by the deployment. Every row references it. |
| `already_recorded` | `bool` | `True` when this statement had already been recorded and the existing one is returned. Redelivery is a no-op, not a duplicate. |

**Errors:**

- `TypeError` or `ValueError` for an amount or a number, one inside `figures` named by its path (`figures[0].collateral[1].haircut`).
- `ValueError`, before anything is sent, for two sets naming one segment, a collateral balance neither posted nor received, or a flat figure beside `figures`, in the sidecar's words: the sidecar refuses each as `invalid` too.
- `invalid` for an empty `external_account_id`, and [`NotLinked`](#an-unlinked-external-account) for one not linked.
- `NotGranted` when the linked account is outside the plugin's write scope, or when the person in `acting_for` may not write it.
- `not vouched for` for an `acting_for` that is not accepted.
- `handler error` from the street store for a statement it refuses, with its reason, such as a collateral balance naming both or neither of an instrument and identifiers. `no handler` or `timeout` from the street store.
- `NotGranted` without the `custody` role.

```python
import time
from decimal import Decimal
import meridian

statement = await plugin.record_holdings_statement(
    source="snaptrade",
    external_statement_id="acct-1@2026-09-25T13:30:00Z",
    external_account_id="acct-1",
    institution="Interactive Brokers",
    as_of_date="2026-09-25",
    read_at_ns=time.time_ns(),
    expected_rows=len(rows),
    figures=[
        meridian.StatementFigures(
            segment="",
            buying_power=meridian.Money(Decimal("25000.00"), "USD"),
            net_liquidation=meridian.Money(Decimal("93550.00"), "USD"),
        ),
    ],
)
```

A plugin built on SDK 0.11.0 or earlier names no external account, and sends its figures flat. While the sidecar accepts its contract version, it admits such a statement with no account, which takes its rows' account when the first lands, and reads the flat figures as the set with no segment.

## `record_holding` { #record_holding }

Records one holding, for one account, at one instrument, on one side, against an open statement.

Set exactly one of `instrument_id` and `unresolved_identifiers`:

- `instrument_id` when [`resolve_identifier`](#resolve_identifier) found it: an instrument, or the deployment's placeholder for an identifier set nothing matched;
- `unresolved_identifiers` when it did not, because more than one instrument matched.

A row that could not be resolved is still recorded. A dropped holding would be invisible.

Cash is a holding like any other: of the currency's cash instrument, which the identifier scheme `iso4217` names (`scheme="iso4217", value="USD"`), with the cash the venue reports in that currency as its quantity.

```python
async def record_holding(
    self, *, statement_id: str = "", instrument_id: str = "",
    unresolved_identifiers: Sequence[Identifier] = (), quantity: Decimal | int,
    market_value: Money | None = None, external_account_id: str = "",
    side: HoldingSide | str | None = None, settle_date_quantity: Decimal | int | None = None,
    currency_assumed: bool = False, also_counted_in_cash: bool = False,
    cost_basis: Money | None = None, lots: Sequence[ReportedLot] = (),
    margin_requirement: Money | None = None, average_cost: Money | None = None,
    acting_for: str | None = None,
) -> RecordHoldingResult
```

| | |
|---|---|
| gRPC | `rpc RecordHolding(RecordHoldingParams) returns (RecordHoldingResult)` |
| Workflow step | W2.3, Publish each holding |
| Kind | command, on `platform.street.command.record-holding` |
| Role | `custody` |
| Served by | the street store |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `statement_id` | `str` | yes, by the street store | The `statement_id` that `record_holdings_statement` returned. |
| `instrument_id` | `str` | one of these two, by the street store | The instrument, or the deployment's placeholder, when resolution found one. |
| `unresolved_identifiers` | sequence of `Identifier` | one of these two, by the street store | Everything the plugin held, when resolution was ambiguous, so an operator can see exactly what could not be accounted for. |
| `quantity` | `Decimal` or `int` | yes, by Python | The trade-date quantity: what is held counting every trade executed, settled or not. Signed to match `side`: negative is short. At most 18 decimal places. |
| `market_value` | [`Money`](#money) or `None` | no | The rail's valuation of the holding, in its currency, recorded as reported and not recomputed. `None` where the venue reported none, which is not a value of zero. |
| `external_account_id` | `str` | yes, by the sidecar | The account as the rail knows it. The sidecar translates it through its link, and refuses it when empty or not linked. |
| `side` | [`HoldingSide`](#holdingside) or `None` | yes, by the street store | Long or short, stated rather than read off the sign. `None` leaves it unset, and the street store refuses the row. A venue that reports an account's long and short of one instrument apart sends two rows, one on each side. |
| `settle_date_quantity` | `Decimal`, `int` or `None` | no | The settle-date quantity: what is held counting only settled trades, where the venue reports it. For cash, the settled cash. |
| `currency_assumed` | `bool` | no | `True` when the venue stated no currency, and the one given is the plugin's own assumption: the market value's currency, and for cash the currency whose cash instrument the row names. |
| `also_counted_in_cash` | `bool` | no | `True` when this position's value is also included in the account's cash holding as the venue reports it, as SnapTrade does with a money-market fund. The street store keeps both as reported. |
| `cost_basis` | [`Money`](#money) or `None` | no | The holding's total cost, as the venue reports it. From 0.12.0. |
| `average_cost` | [`Money`](#money) or `None` | no | The venue's average cost per unit, in the venue's own unit: SnapTrade's is per share, even for an option whose quantity counts contracts. Never multiplied out by the quantity or a multiplier into a cost basis, nor a cost basis divided into it: give whichever the venue reports, or both. From 0.12.0. |
| `lots` | sequence of [`ReportedLot`](#reportedlot) | no | The holding's lots as the venue lists them. None is not one lot, and lots whose quantities do not sum to the holding's are recorded as reported. From 0.12.0. |
| `margin_requirement` | [`Money`](#money) or `None` | no | The margin requirement on the holding, as the venue reports it. From 0.12.0. |
| `acting_for` | `str` or `None` | no | The `Meridian-Caller` header of the person this is sent for. |

**Returns** `RecordHoldingResult`:

| Field | Type | Meaning |
|---|---|---|
| `holding_id` | `str` | The recorded row. |
| `resolved` | `bool` | `True` when the row carried an instrument and updated a custodial position. `False` for an unresolved row, which updates nothing until the deployment knows what it holds. |

**Errors:**

- `TypeError` or `ValueError` for a number or an amount, one inside `lots` named by its path (`lots[0].cost`).
- `invalid` for an empty `external_account_id`, and [`NotLinked`](#an-unlinked-external-account), a `CallFailed` of kind `refused`, for one not linked. The sidecar counts the unlinked account in its report of the plugin, and the next statement after it is linked records it.
- `NotGranted` when the linked account is outside the plugin's write scope, as a closed account is, or when the person in `acting_for` may not write it.
- `not vouched for` for an `acting_for` that is not accepted.
- `handler error` from the street store for a row it refuses, with its reason. It refuses a row that states no side, a quantity whose sign contradicts its side, both or neither of `instrument_id` and `unresolved_identifiers`, a statement it has not opened, or, from 0.12.0, an account other than its statement's.
- `no handler` or `timeout` from the street store.

```python
from decimal import Decimal
import meridian

result = await plugin.record_holding(
    statement_id=statement.statement_id,
    instrument_id=instrument_id,
    side=meridian.HoldingSide.HOLDING_SIDE_LONG,
    quantity=Decimal("150"),
    market_value=meridian.Money(Decimal("34218.75"), "USD"),
    external_account_id="acct-1",
    cost_basis=meridian.Money(Decimal("21000.00"), "USD"),
    lots=[
        meridian.ReportedLot(quantity=Decimal("100"), cost=meridian.Money(Decimal("13500.00"), "USD"),
                             acquired_date="2025-03-14"),
        meridian.ReportedLot(quantity=Decimal("50"), cost=meridian.Money(Decimal("7500.00"), "USD"),
                             acquired_date="2026-01-08"),
    ],
)

# An instrument that resolved ambiguously is still recorded. A short row's
# quantity is negative, and a venue that reported no value sends none:
await plugin.record_holding(
    statement_id=statement.statement_id,
    unresolved_identifiers=[meridian.Identifier(scheme="symbol", value="XYZQ", source="snaptrade")],
    side=meridian.HoldingSide.HOLDING_SIDE_SHORT,
    quantity=Decimal("-10"),
    external_account_id="acct-1",
)
```

## `list_custodial_positions` { #list_custodial_positions }

From 0.12.0. Reads what the custodian says the accounts in the plugin's read scope hold, and, beside it, the holdings that could not be named, so one read answers both what is held and what could not be accounted for. See [Reads are within the read scope](#reads).

```python
async def list_custodial_positions(
    self, *, account_id: str = "", include_unresolved: bool = False, page_size: int = 0,
    cursor: str = "", since: Watermark | None = None,
) -> ListCustodialPositionsResult
```

| | |
|---|---|
| gRPC | `rpc ListCustodialPositions(ListCustodialPositionsParams) returns (ListCustodialPositionsResult)` |
| Workflow step | W2.7, Read custodial positions |
| Kind | query, on `platform.street.query.list-custodial-positions` |
| Role | `operations` |
| Served by | the street store |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `account_id` | `str` | no | One account, which must be in the plugin's read scope. Empty for every account in it. |
| `include_unresolved` | `bool` | no | Also answer the holdings that never resolved, with the first page only, so a read across pages sees each once. |
| `page_size` | `int` | no | How many to a page: 100 when `0`, and never more than 500. |
| `cursor` | `str` | no | The previous page's `next_cursor`, or empty for the first. |
| `since` | [`Watermark`](#watermark) or `None` | no | Only the positions whose last change is after it, removed ones included. |

**Returns** `ListCustodialPositionsResult`:

| Field | Type | Meaning |
|---|---|---|
| `positions` | sequence of [`CustodialPosition`](#custodialposition) | The positions on the page. A removed one is answered only to a read given `since`. |
| `unresolved` | sequence of [`UnresolvedHolding`](#unresolvedholding) | With `include_unresolved`, on the first page. |
| `next_cursor` | `str` | The next page's cursor, empty on the last. |
| `as_of` | [`Watermark`](#watermark) | The point in the store's record the page was read at. |

**Errors:** `NotGranted` for an `account_id` outside the read scope, and without the `operations` role. `no handler`, `timeout` or `handler error` from the street store.

```python
page = await plugin.list_custodial_positions(include_unresolved=True)
for position in page.positions:
    quantity = meridian.as_decimal(position.quantity)
```

## `list_statements` { #list_statements }

From 0.12.0. Reads the completed statements of the accounts in the plugin's read scope, each as the street store announced it when its last row landed. A statement's figures are on it and on no position, so this is how a plugin reads them without having heard the statement. An open statement is not listed: until all its rows have landed, it is not the custodian's whole word on the account. See [Reads are within the read scope](#reads).

```python
async def list_statements(
    self, *, account_id: str = "", as_of_date: str = "", since: Watermark | None = None,
    page_size: int = 0, cursor: str = "",
) -> ListStatementsResult
```

| | |
|---|---|
| gRPC | `rpc ListStatements(ListStatementsParams) returns (ListStatementsResult)` |
| Workflow step | W2.9, Read completed statements |
| Kind | query, on `platform.street.query.list-statements` |
| Role | `operations` |
| Served by | the street store |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `account_id` | `str` | no | One account, which must be in the plugin's read scope. Empty for every account in it. |
| `as_of_date` | `str` | no | Only statements as of this ISO 8601 date. Empty for any. |
| `since` | [`Watermark`](#watermark) or `None` | no | Only the statements completed after it. |
| `page_size` | `int` | no | How many to a page: 100 when `0`, and never more than 500. |
| `cursor` | `str` | no | The previous page's `next_cursor`, or empty for the first. |

**Returns** `ListStatementsResult`:

| Field | Type | Meaning |
|---|---|---|
| `statements` | sequence of [`StatementRecordedEvent`](#statementrecordedevent) | The completed statements on the page. |
| `next_cursor` | `str` | The next page's cursor, empty on the last. |
| `as_of` | [`Watermark`](#watermark) | The point in the store's record the page was read at. |

**Errors:** `NotGranted` for an `account_id` outside the read scope, and without the `operations` role. `no handler`, `timeout` or `handler error` from the street store.

```python
page = await plugin.list_statements(account_id="ACC-…")
for statement in page.statements:
    for figures in statement.figures:
        if figures.HasField("net_liquidation"):
            value = meridian.as_money(figures.net_liquidation)
```

## `resolve_identifier` { #resolve_identifier }

Reverse resolution: asks which instrument a set of identifiers maps to, as of a date. The strongest identifier is matched first: a global identifier, then a symbol qualified by venue and currency.

There are two outcomes other than a match:

- **Nothing matched.** The instrument store answers the deployment's placeholder for the set, an `LCL-` identifier, minting it the first time the set is asked about. `found` is `True` and `placeholder` is `True`. Record the holding against it: the platform's `INS-` identifier replaces it later, and the instrument store reports the miss itself.
- **More than one matched.** The result is a miss rather than a pick: `found` is `False` and `miss_reason` is `MISS_REASON_AMBIGUOUS`. Record the holding with `unresolved_identifiers`, and [report the miss](#report_missing_instrument).

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
| `identifiers` | sequence of `Identifier` | yes, by the contract | At least one. Matched strongest first. An empty set is a miss, `MISS_REASON_NOT_FOUND`, with no placeholder. |
| `as_of_ns` | `int` | no | The reference time: the date the mapping is being asked about. An identifier maps to different instruments over time. |
| `exchange_mic` | `str` | no | Narrows a symbol match. Empty means unconstrained. |
| `currency` | `str` | no | Narrows a symbol match. |

**Returns** `ResolveIdentifierResult`:

| Field | Type | Meaning |
|---|---|---|
| `found` | `bool` | Whether `instrument_id` holds an answer: exactly one instrument matched, or the placeholder stands in. |
| `instrument_id` | `str` | The instrument, or the placeholder, when `found`. |
| `placeholder` | `bool` | `True` when nothing matched and `instrument_id` is the deployment's `LCL-` placeholder for the set. |
| `miss_reason` | `MissReason` | Set only when `found` is `False`: `MISS_REASON_AMBIGUOUS`, or `MISS_REASON_NOT_FOUND` for an empty set. |

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
    instrument_id = answer.instrument_id  # an instrument, or the deployment's placeholder
else:
    reason = answer.miss_reason  # ambiguous: record the row unresolved, report the miss, carry on
```

## `report_missing_instrument` { #report_missing_instrument }

Reports that a resolution missed. **A fact, not a request.** The plugin reports what it held and carries on with the next holding. It does not ask for an instrument to be created, does not wait for one, and could not create one. The deployment and the platform decide what the instrument is, and an administrator completes it.

A plugin reports only an ambiguous miss. When nothing matched, `resolve_identifier` answered a placeholder, and the instrument store has already reported that miss, carrying it.

```python
async def report_missing_instrument(
    self, *, source: str = "", asset_class: AssetClass | str | None = None,
    identifiers: Sequence[Identifier] = (), as_of_ns: int = 0,
    reason: MissReason | str | None = None, observed_at_ns: int = 0,
) -> Published
```

| | |
|---|---|
| gRPC | `rpc ReportMissingInstrument(ReportMissingInstrumentParams) returns (Published)` |
| Workflow step | W3.2, Report that a resolution missed |
| Kind | event, on `platform.reference.event.instrument-missing` |
| Role | `custody` |
| Heard by | the conductor, which asks the platform whether it already knows the instrument (W3.3) |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `source` | `str` | no | The namespace the miss occurred in, such as `"snaptrade"`. |
| `asset_class` | [`AssetClass`](#assetclass), `str` or `None` | no | The instrument's asset class, such as `"equity"`, when the plugin knows it. `None` leaves it unset, and the stub the platform mints has no class until an administrator completes it. An ETF is `"fund"` and an option `"derivative"`. |
| `identifiers` | sequence of `Identifier` | no | Everything the plugin held at the miss. Enough to look it up against a global scheme, or to create a stub carrying them. |
| `as_of_ns` | `int` | no | The reference time of the missed resolution. The reaction targets the mapping effective then, not now. |
| `reason` | `MissReason` or `None` | no | The `miss_reason` that `resolve_identifier` returned. `None` leaves it unset, which reads as `MISS_REASON_UNSPECIFIED`. |
| `observed_at_ns` | `int` | no | When the plugin observed the miss. |

The sidecar sets `publisher_instance_id`, and leaves `placeholder_instrument_id` empty.

**Returns** `Published`, with `message_id`, the message's identifier on the bus.

**Errors:** `ValueError` for an asset class or a reason the enum does not define, such as `"EQUITY"` or `"etf"`. `NotGranted` without the `custody` role.

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

## `read_accounts_for_linking` { #read_accounts_for_linking }

Reads the deployment's accounts, so the plugin's own page at `admin` can offer the ones an external account may be linked to. It is read only for an admin of the plugin, the one viewing the page under Manage, and is answered every account's identity: a plugin admin is account agnostic, and links to any existing account.

```python
async def read_accounts_for_linking(
    self, *, acting_for: str | None = None,
) -> ReadAccountsForLinkingResult
```

| | |
|---|---|
| gRPC | `rpc ReadAccountsForLinking(ReadAccountsForLinkingParams) returns (ReadAccountsForLinkingResult)` |
| Workflow step | W6.4, Link a plugin's external account |
| Kind | query, on `platform.config.query.accounts` |
| Role | `custody` |
| Served by | the conductor |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `acting_for` | `str` or `None` | yes, by the sidecar | The `Meridian-Caller` header of the admin viewing the page, in a session opened by Manage. See [Acting for a person](#acting-for-a-person). |

**Returns** `ReadAccountsForLinkingResult`:

| Field | Type | Meaning |
|---|---|---|
| `accounts` | sequence of [`AccountRecord`](#accountrecord) | Every account in the deployment, open and closed: each one's identifier, name, state, custodian, type, owner and note. No holdings. |

Offer only open accounts. A link to a closed account is refused.

**Errors:** `NotGranted` without an `acting_for`, or with one from a session not opened by Manage. `not vouched for` for an `acting_for` that is not accepted. `no handler`, `timeout` or `handler error` from the conductor. `NotGranted` without the `custody` role.

```python
from meridian.plugin.v1 import operations_pb2 as ops

read = await plugin.read_accounts_for_linking(acting_for=request.state.caller.header)
offered = [a for a in read.accounts if a.state != ops.ACCOUNT_STATE_CLOSED]
```

## `link_external_account` { #link_external_account }

Links an external account the plugin reported to one of the firm's accounts, or removes its link. The plugin sends it from its own page at `admin`, for the admin of the plugin viewing it under Manage.

Name one of these, never both:

- `account_id`, to link to an existing account;
- `new_account_name`, to create an account and link to it in one step, so nothing is left half-done. Only a deployment admin names a new account.

Name neither to remove the link.

An account has one external account: a link naming an account that another external account is already linked to, through this plugin or any other, is refused. Two external accounts at one custodian link to two accounts. See [Accounts](../concepts/accounts.md#external-accounts).

The link is also the plugin's right to that account. The `custody` role grants the street store; the link grants the one account, which is in the plugin's read and write scope while the link stands, with no permission needed. A closed account stays readable through the link, and is not writable. Removing the link removes both.

```python
async def link_external_account(
    self, *, external_account_id: str = "", account_id: str = "", new_account_name: str = "",
    new_account_custodian: str = "", new_account_type: str = "", new_account_owner: str = "",
    new_account_note: str = "", acting_for: str | None = None,
) -> LinkExternalAccountResult
```

| | |
|---|---|
| gRPC | `rpc LinkExternalAccount(LinkExternalAccountParams) returns (LinkExternalAccountResult)` |
| Workflow step | W6.4, Link a plugin's external account |
| Kind | command, on `platform.config.command.link-external-account` |
| Role | `custody` |
| Served by | the conductor, which records the admin as the one who made the link |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `external_account_id` | `str` | yes, by the sidecar | The account as the source knows it. It must be one this plugin reported with `report_external_accounts`, or, to remove a link, one it already links. |
| `account_id` | `str` | one of these two, or neither | An existing, open account to link to. |
| `new_account_name` | `str` | one of these two, or neither | A new account's name, for the conductor to create and link in one step. Only for a deployment admin. |
| `new_account_custodian` | `str` | no | The new account's custodian, such as `"Fidelity"`. At most 200 characters. |
| `new_account_type` | `str` | no | The new account's type, such as `"Roth IRA"`. At most 200 characters. |
| `new_account_owner` | `str` | no | One ownership or grouping label for the new account. At most 200 characters. |
| `new_account_note` | `str` | no | Anything else worth knowing about the new account. At most 2,000 characters. |
| `acting_for` | `str` or `None` | yes, by the sidecar | The `Meridian-Caller` header of the admin viewing the page, in a session opened by Manage. |

The four `new_account_*` attributes are free text, which a page may pre-fill from what the source reported, for the admin to change. They are ignored unless `new_account_name` is given: an existing account is edited only on the **Accounts** tab of the dashboard's Settings.

**Returns** `LinkExternalAccountResult`:

| Field | Type | Meaning |
|---|---|---|
| `plugin_instance_id` | `str` | The plugin the link belongs to. |
| `external_account_id` | `str` | The external account. |
| `account_id` | `str` | The account it is linked to: the new account's identifier when one was created, and empty when the link was removed. |

**Errors:**

- `NotGranted` without an `acting_for`, or with one from a session not opened by Manage; for a `new_account_name` from an admin who is not a deployment admin; or for an external account this plugin did not report, an empty one included.
- `not vouched for` for an `acting_for` that is not accepted.
- `handler error` from the conductor for a link it refuses, with its reason: both `account_id` and `new_account_name`, an account that does not exist or is closed, an account that already has an external account linked, or an attribute that is too long.
- `no handler` or `timeout` from the conductor.
- `NotGranted` without the `custody` role.

```python
caller = request.state.caller

# Link to an existing account:
await plugin.link_external_account(
    external_account_id="acct-1", account_id="ACC-…", acting_for=caller.header,
)

# Or create one and link it, pre-filled from what the source reported:
await plugin.link_external_account(
    external_account_id="acct-2",
    new_account_name="Rollover IRA",
    new_account_custodian="Fidelity",
    new_account_type="IRA",
    acting_for=caller.header,
)

# Remove a link:
await plugin.link_external_account(external_account_id="acct-2", acting_for=caller.header)
```

## Types { #types }

The plugin-facing types these operations take and return. [`Identifier`](python-sdk.md#identifier) and [`MissReason`](python-sdk.md#missreason) are described with the Python SDK. `Money`, `StatementFigures`, `ReportedCollateral` and `ReportedLot` are the SDK's frozen dataclasses, exported from `meridian`, which take their numbers as `Decimal` and their amounts as `Money`, and are converted and refused as a call's own parameters are. Every other type below is a generated protobuf message or enum in `meridian.plugin.v1.operations_pb2`, and `AssetClass`, `CollateralDirection`, `ExternalAccount`, `HoldingSide` and `SyncState` are also exported from `meridian`. What a read answers is all generated messages, `StatementFigures` among them: read a number or an amount off one with [`as_decimal` and `as_money`](#numbers-and-amounts).

### `Money` { #money }

An amount of currency, `meridian.Money(amount, currency_code)`: a frozen dataclass.

| Field | Type | Meaning |
|---|---|---|
| `amount` | `Decimal` or `int` | In the currency's major unit. |
| `currency_code` | `str` | ISO 4217, such as `"USD"`. |

### `ExternalAccount` { #externalaccount }

One account a connection reaches, as the custodian presents it.

| Field | Type | Meaning |
|---|---|---|
| `external_account_id` | `str` | Stable: the plugin makes it so where the venue does not. It is the `external_account_id` the account's rows name. A handle the venue wants on each call stays inside the plugin. |
| `name` | `str` | The custodian's own name for it, as a person there would recognise it. |
| `venue_account_type` | `str` | The venue's own word for the kind of account, verbatim and for display only. |

### `AssetClass` { #assetclass }

The kind of claim holding an instrument gives. A closed list: a class joins it by a ruling, never because a venue sent one. In a string, a value is spelled as its name without `ASSET_CLASS_`, in lower case.

| Value | Number | Meaning |
|---|---|---|
| `ASSET_CLASS_UNSPECIFIED` | 0 | Not known. Only a stub minted from a deployment's miss may have no class; activating it requires one. |
| `ASSET_CLASS_EQUITY` | 1 | `equity`: a share of ownership. |
| `ASSET_CLASS_DEBT` | 2 | `debt`: somebody owes the holder, as with a bond. |
| `ASSET_CLASS_FUND` | 3 | `fund`: a share of a pool, such as an ETF or a mutual fund. |
| `ASSET_CLASS_DERIVATIVE` | 4 | `derivative`: a contract whose value comes from something else, such as an option or a future. |
| `ASSET_CLASS_CRYPTO_ASSET` | 5 | `crypto_asset`. |
| `ASSET_CLASS_EVENT_CONTRACT` | 6 | `event_contract`: pays on whether an event happens. |
| `ASSET_CLASS_CASH` | 7 | `cash`: a holding of a currency's cash instrument. |

What kind of instrument within a class (an ETF within fund, an option within derivative) is its instrument type, which the contract does not carry yet.

### `HoldingSide` { #holdingside }

Which side of an instrument a holding is on.

| Value | Number | Meaning |
|---|---|---|
| `HOLDING_SIDE_UNSPECIFIED` | 0 | Not said. Refused by the street store. |
| `HOLDING_SIDE_LONG` | 1 | Long. The quantity is zero or more. |
| `HOLDING_SIDE_SHORT` | 2 | Short. The quantity is zero or less. |

### `SyncState` { #syncstate }

Why a connection's data is, or is not, current. Each asks something different of a person.

| Value | Number | Meaning |
|---|---|---|
| `SYNC_STATE_UNSPECIFIED` | 0 | Not said. Shown as what `connection_healthy` says. |
| `SYNC_STATE_CURRENT` | 1 | Current. Nothing to do. |
| `SYNC_STATE_STALE` | 2 | Still serving, but older than it should be; `holdings_as_of_ns` says since when. Usually the rail's to recover. |
| `SYNC_STATE_NEEDS_SIGN_IN` | 3 | A person must sign in again at the venue before it serves anything new. |
| `SYNC_STATE_DISABLED` | 4 | The connection is disabled and serves only what it last read. Somebody re-enables it. |
| `SYNC_STATE_DELAYED_BY_DESIGN` | 5 | Late on purpose, such as by a business day. Expected; nothing to do. |
| `SYNC_STATE_HOLDINGS_UNAVAILABLE` | 6 | The venue does not provide holdings through this connection. Waiting changes nothing. |

### `StatementFigures` { #statementfigures }

A statement's figures for one margin segment, `meridian.StatementFigures(...)`, keyword only. Each is as the venue reported it and `None` where it reported none, which is not zero; none is derived. From 0.12.0.

| Field | Type | Meaning |
|---|---|---|
| `segment` | `str` | The segment as the venue names it, verbatim, such as Interactive Brokers' `"securities"` and `"commodities"`, or an FCM's class. Empty, the default, for the account as a whole. |
| `buying_power` | [`Money`](#money) or `None` | The buying power. |
| `margin_requirement` | [`Money`](#money) or `None` | The margin requirement. |
| `maintenance_excess` | [`Money`](#money) or `None` | The maintenance excess. Negative is a deficit. |
| `initial_margin` | [`Money`](#money) or `None` | The initial margin. |
| `variation_margin` | [`Money`](#money) or `None` | The variation margin. |
| `net_liquidation` | [`Money`](#money) or `None` | A brokerage's own total account value, as it reports it. Never a sum of the holdings. |
| `collateral` | sequence of [`ReportedCollateral`](#reportedcollateral) | The collateral held under this segment. |

### `ReportedCollateral` { #reportedcollateral }

One collateral balance under a margin segment, `meridian.ReportedCollateral(...)`, keyword only, each field as the venue reports it and unset where it does not. A balance moves nothing: posted collateral the custodian also lists as a holding is a holding row as well, and collateral received under a security interest is never a holding. From 0.12.0.

| Field | Type | Meaning |
|---|---|---|
| `direction` | [`CollateralDirection`](#collateraldirection), `str` or `None` | Posted by the account or received by it. Refused when not said. |
| `instrument_id` | `str` | The instrument, resolved as a holding's is: an instrument, the deployment's placeholder, or the currency's cash instrument for cash. |
| `unresolved_identifiers` | sequence of `Identifier` | The identifiers the plugin held, when the resolve was ambiguous. Exactly one of these two. |
| `quantity` | `Decimal` or `int` | The quantity. Required. |
| `value` | [`Money`](#money) or `None` | Its value. |
| `haircut` | `Decimal`, `int` or `None` | A fraction of the value: `Decimal("0.15")` is 15%, a venue's percentage written as its fraction. |
| `value_after_haircut` | [`Money`](#money) or `None` | Its value after the haircut. |
| `held_at` | `str` | Where it is held, as the venue names it: the FCM, the dealer, a third-party custodian. Empty where it does not say. |

### `CollateralDirection` { #collateraldirection }

| Value | Number | Meaning |
|---|---|---|
| `COLLATERAL_DIRECTION_UNSPECIFIED` | 0 | Not said. Refused: collateral is posted or received. |
| `COLLATERAL_DIRECTION_POSTED` | 1 | `posted`: posted by the account. |
| `COLLATERAL_DIRECTION_RECEIVED` | 2 | `received`: received by it. |

### `ReportedLot` { #reportedlot }

One lot of a holding, as the custodian lists it, `meridian.ReportedLot(...)`, keyword only. From 0.12.0.

| Field | Type | Meaning |
|---|---|---|
| `quantity` | `Decimal` or `int` | Signed as the holding's quantity: a short holding's lots are short, their quantities negative. Required. |
| `cost` | [`Money`](#money) or `None` | The lot's total cost, with its sign as the venue reports it, never flipped to match. `None` where not reported. |
| `acquired_date` | `str` | When it was acquired, an ISO 8601 date. Empty where not reported. |

### `CustodialPosition` { #custodialposition }

What the custodian says an account holds of an instrument, on one side. It is the custodian's belief, read from its statements, and not what the deployment calculates from its own activity.

| Field | Type | Meaning |
|---|---|---|
| `account_id` | `str` | The account. |
| `instrument_id` | `str` | An instrument, or the deployment's `LCL-` placeholder awaiting identity, which the platform's `INS-` identifier replaces when it arrives. |
| `side` | [`HoldingSide`](#holdingside) | Long or short. |
| `quantity` | `Decimal` message | The trade-date quantity, signed to match `side`. |
| `settle_date_quantity` | `Decimal` message | The settle-date quantity, where the custodian reported one. |
| `market_value` | `Money` message | Unset where the custodian reported no value, which is not zero. |
| `also_counted_in_cash` | `bool` | Its value is also in the account's cash holding as the custodian reports it. |
| `cost_basis`, `average_cost`, `lots`, `margin_requirement` | as on [`record_holding`](#record_holding) | As the custodian reported them on the row that last stated the position, unset or empty where it reported none. |
| `last_statement_id`, `as_of_date`, `updated_at_ns` | `str`, `str`, `int` | The statement that last stated it, and when. |
| `last_change` | `JournalRef` | Where its last change sits in the store's record, which [`receive`](python-sdk.md#receive) reads to catch up. A handler is handed none. |
| `removed` | `bool` | Removed, as when a placeholder's replacement moved it: answered only to a read given `since`, and heard once. |

### `UnresolvedHolding` { #unresolvedholding }

A holding the deployment received but could not name.

| Field | Type | Meaning |
|---|---|---|
| `holding_id` | `str` | The recorded row. |
| `account_id` | `str` | The account. |
| `identifiers` | sequence of `Identifier` | What the plugin held. |
| `quantity` | `Decimal` message | Signed, as the row stated it: negative is a short row. |
| `market_value` | `Money` message | Unset where the custodian reported no value. |
| `source`, `as_of_date` | `str` | As on its statement. |
| `escalated` | `bool` | Whether the miss has already been raised, so nobody having looked at it is told apart from its being with an administrator. |

### `StatementRecordedEvent` { #statementrecordedevent }

A completed statement, as the street store announced it when its last row landed. The `statement_recorded` handler of [`receive`](python-sdk.md#receive) is handed one, and [`list_statements`](#list_statements) answers them.

| Field | Type | Meaning |
|---|---|---|
| `statement_id` | `str` | The statement. |
| `account_id` | `str` | The account it is of: its external account's, or, from a plugin built before contract v7, its rows'. |
| `external_account_id`, `institution` | `str` | As the statement named them. Empty from a plugin built before contract v7. |
| `source`, `as_of_date` | `str` | As the statement named them. |
| `rows_received`, `rows_resolved`, `rows_unresolved` | `int` | Its counts. The unresolved count is the one an operator watches. |
| `figures` | sequence of `StatementFigures` | Its figures as recorded, one set per segment. |
| `currency_assumed` | `bool` | As the statement said. |
| `recorded_at_ns` | `int` | When it was completed. |
| `journal`, `cause` | `JournalRef`, `ChangeCause` | Where its completion sits in the store's record, and who caused it. A handler is handed `cause` as [`Heard.cause`](python-sdk.md#heard), and no `journal`. |

### `Watermark` { #watermark }

A point in a store's record: `partitions`, each a `partition` and its `sequence`. A read answers the one it was read at, as `as_of`, and takes one, as `since`, to answer what changed after it. A plugin passes back what a read answered, and reads nothing into it.

### `AccountRecord` { #accountrecord }

One of the firm's accounts. See [Accounts](../concepts/accounts.md).

| Field | Type | Meaning |
|---|---|---|
| `account_id` | `str` | `ACC-` followed by 26 letters and digits. |
| `name` | `str` | The account's name. |
| `state` | `AccountState` | `ACCOUNT_STATE_OPEN` or `ACCOUNT_STATE_CLOSED`. Closed, not deleted. |
| `created_at_ns` | `int` | When it was created. |
| `custodian` | `str` | Where it is held. Free text; may be empty. |
| `account_type` | `str` | What it is. Free text; may be empty. |
| `owner` | `str` | One ownership or grouping label. Free text; may be empty. |
| `note` | `str` | Anything else. Free text; may be empty. |

## The gRPC service

For reference, the plugin-facing service in `meridian/plugin/v1/operations.proto`, which the sidecar serves on loopback:

```protobuf
service PluginOperations {
  rpc ReportExternalAccounts(ReportExternalAccountsParams) returns (Published);
  rpc ReportSyncStatus(ReportSyncStatusParams) returns (Published);
  rpc RecordHoldingsStatement(RecordHoldingsStatementParams) returns (RecordHoldingsStatementResult);
  rpc RecordHolding(RecordHoldingParams) returns (RecordHoldingResult);
  rpc ListCustodialPositions(ListCustodialPositionsParams) returns (ListCustodialPositionsResult);
  rpc ListStatements(ListStatementsParams) returns (ListStatementsResult);
  rpc ResolveIdentifier(ResolveIdentifierParams) returns (ResolveIdentifierResult);
  rpc ReportMissingInstrument(ReportMissingInstrumentParams) returns (Published);
  rpc LinkExternalAccount(LinkExternalAccountParams) returns (LinkExternalAccountResult);
  rpc ReadAccountsForLinking(ReadAccountsForLinkingParams) returns (ReadAccountsForLinkingResult);
  rpc Receive(ReceiveRequest) returns (stream Delivery);
}
```

Each `…Params` message keeps the field numbers of the domain message it stands for and drops the fields the sidecar stamps, so its encoding is the domain message's. `acting_for` is field 1000 on the four operations that take it, a `meridian.v1.CallerAssertion`. The SDK decodes it from the base64url `Meridian-Caller` header you pass. A number is a `Decimal` message, `high` and `low` halves of a 128-bit integer and a `scale` of 0 to 18, and an amount a `Money` message, a `Decimal` and a `currency_code`. `Identifier`, `MissReason` and the other types are plugin-facing mirrors of the domain types. `Receive`, from 0.12.0, is a stream: each item a `Delivery`, a row's message beside what is known of it, or a `Lost` where the sidecar dropped deliveries. The SDK's [`receive`](python-sdk.md#receive) reads it, and catches up from the store where it missed something.
