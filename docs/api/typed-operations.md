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

This page lists every operation in SDK 0.14.0, which declares contract v9. It has the operations of 0.13.0, which added the [book of record](../concepts/the-book-of-record.md)'s seven commands and four reads, and `resolve_instrument`, to those of 0.12.0, and what of a holding cannot move to the commands that record holdings. What 0.14.0 adds is the book's refusal of an entry missing what it requires, `REFUSAL_REASON_INCOMPLETE`, naming each missing field (see [What the book requires](#what-the-book-requires)). A plugin built on 0.12.0 or 0.13.0 keeps working, and the book refuses an incomplete entry from it all the same. There is no order-routing or execution operation.

From 0.19.0, contract v14, it also lists three operations of [the custodian's activity](../concepts/the-custodians-activity.md): [`record_activity`](#record_activity), by which a `custody` plugin reports each activity on an account as the custodian states it, and [`list_activities`](#list_activities) and [`list_sync_statuses`](#list_sync_statuses), by which an `operations` plugin reads it and each sync status the street keeps. Their rows are `preview` in v14. A sync status says from when the source can read the account's history ([`history_from`](#report_sync_status)), and a break's cause may link the activity that explains it ([`BreakCause`](#breakcause)).

## Summary

| Python method | gRPC rpc | Workflow step | Kind | Role | Returns |
|---|---|---|---|---|---|
| [`report_external_accounts`](#report_external_accounts) | `ReportExternalAccounts` | W2.8 Report the accounts a connection reaches | event | `custody` | `Published` |
| [`report_sync_status`](#report_sync_status) | `ReportSyncStatus` | W2.1 Observe the brokerage sync state | event | `custody` | `Published` |
| [`record_holdings_statement`](#record_holdings_statement) | `RecordHoldingsStatement` | W2.2 Open a holdings statement | command | `custody` | `RecordHoldingsStatementResult` |
| [`record_holding`](#record_holding) | `RecordHolding` | W2.3 Publish each holding | command | `custody` | `RecordHoldingResult` |
| [`list_custodial_positions`](#list_custodial_positions) | `ListCustodialPositions` | W2.7 Read custodial positions | query | `operations` | `ListCustodialPositionsResult` |
| [`list_statements`](#list_statements) | `ListStatements` | W2.9 Read completed statements | query | `operations` | `ListStatementsResult` |
| [`record_activity`](#record_activity) | `RecordActivity` | W2.10 Record an account's activity | command | `custody` | `RecordActivityResult` |
| [`list_activities`](#list_activities) | `ListActivities` | W2.11 List an account's activity | query | `operations` | `ListActivitiesResult` |
| [`list_sync_statuses`](#list_sync_statuses) | `ListSyncStatuses` | W2.14 Read an account's sync status | query | `operations` | `ListSyncStatusesResult` |
| [`resolve_identifier`](#resolve_identifier) | `ResolveIdentifier` | W3.1 Resolve an identifier set | query | `custody` | `ResolveIdentifierResult` |
| [`report_missing_instrument`](#report_missing_instrument) | `ReportMissingInstrument` | W3.2 Report that a resolution missed | event | `custody` | `Published` |
| [`read_accounts_for_linking`](#read_accounts_for_linking) | `ReadAccountsForLinking` | W6.4 Link a plugin's external account | query | `custody` | `ReadAccountsForLinkingResult` |
| [`link_external_account`](#link_external_account) | `LinkExternalAccount` | W6.4 Link a plugin's external account | command | `custody` | `LinkExternalAccountResult` |
| [`resolve_instrument`](#resolve_instrument) | `ResolveInstrument` | W3.6 Resolve an instrument for display | query | `portfolio`, `reporting`, `compliance`, `oms`, `operations` | `ResolveInstrumentResult` |
| [`record_opening_balance`](#record_opening_balance) | `RecordOpeningBalance` | W9.1 Record an account's opening balance | command | `operations` | `RecordOpeningBalanceResult` |
| [`record_break`](#record_break) | `RecordBreak` | W9.4 Record a break | command | `operations` | `RecordBreakResult` |
| [`record_account_figures`](#record_account_figures) | `RecordAccountFigures` | W9.5 Record the account's figures | command | `operations` | `RecordAccountFiguresResult` |
| [`record_encumbrances`](#record_encumbrances) | `RecordEncumbrances` | W9.15 Record a position's encumbrances | command | `operations` | `RecordEncumbrancesResult` |
| [`handle_break`](#handle_break) | `HandleBreak` | W9.6 Set a break's cause and handling | command | `operations` | `HandleBreakResult` |
| [`resolve_break`](#resolve_break) | `ResolveBreak` | W9.7 Resolve or close a break | command | `operations` | `ResolveBreakResult` |
| [`close_breaks_as_cleared`](#close_breaks_as_cleared) | `CloseBreaksAsCleared` | W9.7 Resolve or close a break | command | `operations` | `CloseBreaksAsClearedResult` |
| [`list_positions`](#list_positions) | `ListPositions` | W9.10 Read positions | query | `portfolio`, `reporting`, `compliance`, `oms`, `operations` | `ListPositionsResult` |
| [`list_breaks`](#list_breaks) | `ListBreaks` | W9.11 Read breaks | query | `operations`, `oms`, `compliance`, `portfolio`, `reporting` | `ListBreaksResult` |
| [`list_account_figures`](#list_account_figures) | `ListAccountFigures` | W9.12 Read the account's figures | query | `operations`, `portfolio`, `compliance`, `reporting` | `ListAccountFiguresResult` |
| [`list_account_attributes`](#list_account_attributes) | `ListAccountAttributes` | W9.14 Read an account's attributes | query | `portfolio`, `reporting`, `compliance`, `oms`, `operations` | `ListAccountAttributesResult` |

**Role** is the plugin role that publishes the step, or the roles that may ask the query, from the contract's matrix. A plugin can call an operation only if it holds one of them, approved when it was launched. Otherwise the call raises `NotGranted`. See [Plugins, roles and grants](../concepts/plugins.md) and [Plugin manifest](plugin-manifest.md).

**Kind** says what comes back:

- An **event** returns `Published`, the message's identifier on the bus.
- A **command** or a **query** returns the answer of whatever serves it.

W2 is holdings ingestion from a brokerage. It is read-only throughout: nothing in it places an order. A `custody` plugin records what the custodian says is held, and from 0.19.0 each activity on the account as the custodian states it, and an `operations` plugin reads it, within its read scope, and hears it change with [`receive`](python-sdk.md#receive), the stream of what a plugin's roles hear (W4.3, `rpc Receive`). W3 is instrument resolution. W6.4 is linking the accounts a source reaches to the firm's own, which a plugin does on its own page at `admin`, for the admin of the plugin viewing it under Manage. The tutorial [Record a holdings statement](../tutorials/record-a-holdings-statement.md) walks through W2 and W6.4.

W9, from 0.13.0, is the [book of record](../concepts/the-book-of-record.md): the firm's own record of what each account holds, which an `operations` plugin opens with an opening balance a person confirms, reconciles with the street on each statement, and corrects only by entries that resolve its breaks. `portfolio`, `reporting`, `compliance` and `oms` read it, and hear it change with `receive`. W3.6 is forward resolution, by which those roles join a book position to its instrument. From 0.14.0, contract v9, the book refuses an entry missing what tax tracking, valuation, confirmation or settlement need, and names each field it lacks.

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
| `account_id` | `RecordHoldingsStatement`, `RecordHolding`, `RecordActivity` | The link an admin of the plugin made from the plugin's `external_account_id` to an account. Refused when there is none, as [`NotLinked`](#an-unlinked-external-account). On a statement from 0.12.0; on an activity from 0.19.0. |
| `account_id` | `ReportSyncStatus` | The same link, or empty when there is none. Never refused. |
| `publisher_instance_id` | `ReportMissingInstrument` | The instance the plugin was launched as. |
| `placeholder_instrument_id` | `ReportMissingInstrument` | Nothing: always empty from a plugin. Only the instrument store sets it. |
| `plugin_instance_id` | `LinkExternalAccount` | The instance the plugin was launched as. |

The sidecar also puts the plugin's own instance in place of `{instance}` in a topic, so a plugin can speak only as itself.

### Reads are within the read scope { #reads }

From 0.12.0. The sidecar stamps the plugin's [read scope](../concepts/accounts.md#how-accounts-bound-a-plugin) on every read, and the store answers only within it: a read naming an account outside it is refused with `NotGranted`, one naming none answers every account in it, and a plugin whose read scope is empty reads nothing. A plugin reads its whole scope as itself, and serves each person from it with `caller.read`. What it hears with [`receive`](python-sdk.md#receive) is held to the same scope.

Each read answers a page, the next page's `cursor` in `next_cursor`, empty on the last, and `as_of`, the [`Watermark`](#watermark) it was read at. Given a watermark as `since`, a read answers only what changed after it. `receive` reads this way to seed and to catch up, so a plugin hearing a row seldom reads it itself.

### Acting for a person

Twelve operations take `acting_for`: the two commands that record holdings and, from 0.19.0, the one that records an activity; the seven commands of the book; and the two that link accounts. Pass the `Meridian-Caller` header of the page request you are serving: in a view on [`meridian.Pages`](python-sdk.md#pages), `request.caller.header`; with [`CallerMiddleware`](python-sdk.md#callermiddleware), `request.state.caller.header`.

For `record_holdings_statement`, `record_holding`, `record_activity` and the book's commands, the sidecar applies the same rule:

- **Unset:** the plugin acts as itself.
- **Set:** the sidecar checks the assertion, admits the command only in a session opened by **Open**, at `write`, and only when that person may write the account it names, and stamps the person on it. For a command that names no account, the person must be able to write something through the plugin. A command sent for a person in a session opened by Manage or View is refused with `NotGranted`, naming the session.

A person narrows what a plugin may do and never widens it.

Of the book's commands, the findings (`record_break`, `record_account_figures` and `record_encumbrances`) are a plugin's to send as itself. The rest are justified acts, which the book refuses without a person and a reason: see [The book's commands](#the-books-commands).

For `read_accounts_for_linking` and `link_external_account`, it is required. They touch the deployment's configuration, which a plugin reaches only acting for an admin of the plugin in a session opened by **Manage**, at `admin`, and never as itself. Without an assertion, or with one from a session at any other level, the sidecar refuses the call with `NotGranted`. They are the only reads and commands the sidecar admits for a person in a Manage session: that session reaches no account's data.

### The book's commands { #the-books-commands }

From 0.13.0. Every command of the book answers after its entry commits, with every record it changed: see [Book entry result](#book-entry-result).

- **A finding or a person's act.** A break, the figures and the encumbrances are findings, which the plugin may send as itself, acting for nobody. An opening balance, a break's cause and handling, its resolution and closing it as cleared are a person's: send them `acting_for` that person, with their `reason`, or the book refuses them with `REFUSAL_REASON_ACTOR_REQUIRED` or `REFUSAL_REASON_REASON_REQUIRED`. The book records the person, or the plugin's instance, as the entry's actor.
- **One arm of a oneof, by keyword.** Where a message holds one of several things, the method takes each as a keyword: a break's `position=` or `figure=`, a resolution's `adjustment=`, `reversal=`, `entries=` or `explanation=`, a basis adjustment's `cost_change=` or `stated_cost=`, a cause's item. Two at once raise `ValueError` naming the oneof, before anything is sent.
- **The book's own refusals** carry a code, and the SDK raises them as [`CommandRefused`](#the-books-refusals). From 0.14.0 an incomplete entry's refusal also names each field it lacks: see [What the book requires](#what-the-book-requires).

### Idempotency keys { #idempotency-keys }

Each of the book's commands takes an `idempotency_key`: the plugin's key for the command, derived from its source, unique per account. The same command again with the same key is answered with the first's reply and applies nothing, so a plugin restarted halfway, or a person retrying after a lost reply, records nothing twice. The sidecar mints each message's identifier, so a retry is a new message: the key is what makes it the same command. A different command under a key the account's book already holds is refused with `REFUSAL_REASON_IDEMPOTENCY_CONFLICT`, nothing applied. Empty sends none.

Derive a key from what the command is about, such as `opening/{account}/{statement}` for an opening balance composed from a statement, or `break/{account}/{statement}/{subject}/{category}` for a break found in it.

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
| `CommandRefused`, `kind="refused"` | `ABORTED`, with a code | From 0.13.0: the book refused the command with a code of its own, such as `REFUSAL_REASON_BREAK_STATE`; from 0.14.0, `REFUSAL_REASON_INCOMPLETE` with each missing field in `fields`. See [The book's refusals](#the-books-refusals). | Act on the code: read the book again and say what stands, or ask the person for what was missing, which `fields` names. Not retried. |
| `CallFailed`, `kind="handler error"` | `ABORTED`, with no code | What serves it answered with a refusal. `detail` is its reason. | Report it. |
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
| `REFUSAL_REASON_ACTOR_REQUIRED` … `REFUSAL_REASON_INCOMPLETE` | 2 to 11 | `ABORTED` | The book's refusals: 2 to 10 from 0.13.0, and 11 from 0.14.0. See [The book's refusals](#the-books-refusals). |

A reason is never reused for another cause, and a retired one's number stays reserved. [`record_holding`](#record_holding) can be refused this way, from 0.12.0 [`record_holdings_statement`](#record_holdings_statement), which names its external account too, and from 0.19.0 [`record_activity`](#record_activity); `report_sync_status` for an unlinked account is not refused.

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

### The book's refusals { #the-books-refusals }

From 0.13.0. The book of record refuses with a code, which the sidecar carries beside `ABORTED` in the same trailer, `meridian-refusal-bin`. The SDK raises **`meridian.CommandRefused`**: a `CallFailed` whose `kind` is `"refused"`, with `reason`, the code's number, and `reason_name`, its name. From 0.14.0 it also has `fields`, a tuple of each field the command left out, by its path in the call, read from the same `Refusal`'s `fields`; only `REFUSAL_REASON_INCOMPLETE` carries any, and every other refusal has none. Match the code and the paths, never the words.

| Reason | Number | Sent when |
|---|---|---|
| `REFUSAL_REASON_ACTOR_REQUIRED` | 2 | A person's act sent for nobody: an opening balance, a break's handling, its resolution or closing, or an account's attribute. |
| `REFUSAL_REASON_REASON_REQUIRED` | 3 | A justified act sent without its reason or explanation. |
| `REFUSAL_REASON_OPENING_BALANCE_RECORDED` | 4 | A second opening balance while one stands. |
| `REFUSAL_REASON_NO_OPENING_BALANCE` | 5 | A break, figures, encumbrances or an entry for an account with no opening balance. |
| `REFUSAL_REASON_BEFORE_OPENING_BALANCE` | 6 | An entry moving a position effective on or before the opening balance's date. |
| `REFUSAL_REASON_LOTS_UNBALANCED` | 7 | An opening position whose lots do not sum to its quantity, or an entry that would leave a position's open lots so. |
| `REFUSAL_REASON_BREAK_STATE` | 8 | Updating, handling, resolving or closing a break that is not open. |
| `REFUSAL_REASON_LATER_ENTRIES_STAND` | 9 | A reversal of an opening balance while a later entry moving the account's positions stands. |
| `REFUSAL_REASON_IDEMPOTENCY_CONFLICT` | 10 | A key the account's book holds for a different command. |
| `REFUSAL_REASON_INCOMPLETE` | 11 | From 0.14.0: an opening balance, or an adjustment opening a lot, missing a field the book requires, nothing applied. Each missing field is in `fields`. See [What the book requires](#what-the-book-requires). |

```python
try:
    await plugin.record_opening_balance(..., acting_for=caller.header)
except meridian.CommandRefused as refused:
    if refused.reason_name == "REFUSAL_REASON_OPENING_BALANCE_RECORDED":
        ...  # already recorded: read it back with list_account_attributes and say so
    elif refused.reason_name == "REFUSAL_REASON_INCOMPLETE":
        ...  # show the person what to supply: ("positions[0].settled_quantity", ...)
```

A plugin built on 0.13.0 meets the same refusal from a book at contract v9 as a `CommandRefused` whose `reason` is 11 and whose `reason_name` is `"11"`, since its SDK does not know the name, and it does not read the fields.

### What the book requires { #what-the-book-requires }

From 0.14.0, contract v9. The book refuses an entry missing what its downstream activities need, tax tracking, valuation, confirmation and settlement, with `REFUSAL_REASON_INCOMPLETE`, nothing applied, and names every missing field in `CommandRefused.fields` by its path in the call's parameters. The refusal applies to every plugin, whatever SDK it was built on. See [What the book requires](../concepts/the-book-of-record.md#what-the-book-requires) for why.

Of an opening balance ([`record_opening_balance`](#record_opening_balance)):

| Path | Missing when |
|---|---|
| `as_of_date` | Empty. |
| `sources` | No source at all, even for an account entering holding nothing. |
| `sources[n].name` | A source naming no custodian or system, on a balance holding positions. |
| `positions[n].instrument_id`, `positions[n].side`, `positions[n].trade_date_quantity` | Unset. |
| `positions[n].settled_quantity` | Unset. Where the source states none, a person supplies it. |
| `positions[n].pending[m].quantity`, `positions[n].pending[m].value_date` | Unset or empty: every pending quantity has its value date. |
| `positions[n].pending` | The settled quantity and the pending quantities do not account for the whole trade-date quantity: the rest, neither settled nor pending on a date, is pending nobody has given. |
| `positions[n].lots` | No lots, on a position whose instrument's record says it is not cash. |
| `positions[n].lots[m].quantity`, `positions[n].lots[m].terms.cost`, `positions[n].lots[m].terms.acquired_date` | Unset or empty: every lot carries its quantity, its cost in all, and its acquisition date. |

Of an adjustment ([`resolve_break`](#resolve_break)): `adjustment.lines[n].opens_lot.cost` and `adjustment.lines[n].opens_lot.acquired_date`, on a line that opens a lot without them.

The book reads whether an instrument is cash from its record: its asset class, or a currency identifier. Cash has no lots. Where the record cannot say, because the position is held under a placeholder, the record names no asset class and no currency identifier, or the instrument store does not answer in time, the book does not require its lots, for now, and still refuses any lot sent incomplete. An `operations` plugin flags such a position, and it does not hold the confirmation back.

A lot of unknown cost and the settlement bucket "not stated" are no longer admitted. They stay on the wire for what a book at contract v8 recorded: `BookPosition.not_stated_quantity` is zero on every position v9 records, and its `settled_quantity` is set.

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
    history_from: str = "",
) -> Published
```

| | |
|---|---|
| gRPC | `rpc ReportSyncStatus(ReportSyncStatusParams) returns (Published)` |
| Workflow step | W2.1, Observe the brokerage sync state |
| Kind | event, on `platform.custody.{instance}.event.sync-status` |
| Role | `custody` |
| Heard by | the dashboard, which shows it on the **Overview** tab of the plugin's view in Settings; from contract v14, the street store, which keeps each one for `operations` to read and hear (W2.13, see [`list_sync_statuses`](#list_sync_statuses)) |

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
| `history_from` | `str` | no | From 0.19.0. The first date, ISO 8601, the source can read the account's activity from: how far back a backfill of [`record_activity`](#record_activity) reaches, beside how fresh the history is. Empty where the source does not say. |

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
    history_from="2024-06-03",          # from 0.19.0: the first day of the history it can read
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
    security_interest: bool | None = None, acting_for: str | None = None,
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
| `currency_assumed` | `bool` | no | `True` when the venue stated no currency for these figures, and the one given is the plugin's own assumption. Of every set in `figures`. Deprecated in contract v11 for the figures' provenance ([keep what your custody plugin converts](../how-to/keep-what-the-edge-converts.md)). |
| `security_interest` | `bool` or `None` | no | `True` when the account servicer holds a lien or a right of set-off over the account, as the statement reports it; `None` where it does not say. Not an encumbrance: it reduces no holding's available quantity. From 0.13.0. |
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
    available_quantity: Decimal | int | None = None,
    not_available_quantity: Decimal | int | None = None,
    available_basis: AvailableBasis | str | None = None,
    encumbrances: Sequence[ReportedEncumbrance] = (), acting_for: str | None = None,
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
| `currency_assumed` | `bool` | no | `True` when the venue stated no currency, and the one given is the plugin's own assumption: the market value's currency, and for cash the currency whose cash instrument the row names. Deprecated in contract v11 for the row's provenance. |
| `also_counted_in_cash` | `bool` | no | `True` when this position's value is also included in the account's cash holding as the venue reports it. Deprecated in contract v11: the street counts each asset once, and a custody plugin sends the cash net of the fund ([keep what your custody plugin converts](../how-to/keep-what-the-edge-converts.md)). |
| `cost_basis` | [`Money`](#money) or `None` | no | The holding's total cost, as the venue reports it. From 0.12.0. |
| `average_cost` | [`Money`](#money) or `None` | no | The venue's average cost per unit, in the venue's own unit: SnapTrade's is per share, even for an option whose quantity counts contracts. Never multiplied out by the quantity or a multiplier into a cost basis, nor a cost basis divided into it: give whichever the venue reports, or both. From 0.12.0. |
| `lots` | sequence of [`ReportedLot`](#reportedlot) | no | The holding's lots as the venue lists them. None is not one lot, and lots whose quantities do not sum to the holding's are recorded as reported. From 0.12.0. |
| `margin_requirement` | [`Money`](#money) or `None` | no | The margin requirement on the holding, as the venue reports it. From 0.12.0. |
| `available_quantity`, `not_available_quantity` | `Decimal`, `int` or `None` | no | What of the holding is available and what is not, each as the source reports it, never derived from the other or from the quantity: available is never the quantity less what is encumbered. `None` where the source gives none. From 0.13.0. |
| `available_basis` | [`AvailableBasis`](#availablebasis), `str` or `None` | no | What the available quantity is on, as the source says. From 0.13.0. |
| `encumbrances` | sequence of [`ReportedEncumbrance`](#reportedencumbrance) | no | Each sub-balance the source reports as encumbered, one per kind, location and pledgee. Empty means none reported, not none held. From 0.13.0. |
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

## `record_activity` { #record_activity }

From 0.19.0, contract v14. Records one activity on an account as the custodian states it: a purchase, a sale, a reinvested dividend, a dividend or interest, a fee or a tax, a split or another corporate action, a transfer, a contribution, a withdrawal or a journal. It is evidence that explains a break, never a source: the street store keeps it as reported and derives no position, lot or figure from it, and nothing moves the book until a person confirms. See [The custodian's activity](../concepts/the-custodians-activity.md), and [Report the custodian's activity](../how-to/report-the-custodians-activity.md) for a custody plugin's side.

```python
async def record_activity(
    self, *, external_account_id: str = "", source: str = "",
    activity: CustodialActivity | None = None, acting_for: str | None = None,
) -> RecordActivityResult
```

| | |
|---|---|
| gRPC | `rpc RecordActivity(RecordActivityParams) returns (RecordActivityResult)` |
| Workflow step | W2.10, Record an account's activity |
| Kind | command, on `platform.street.command.record-activity` |
| Role | `custody` |
| Served by | the street store, which announces each new one as `ActivityRecorded` (W2.12) to `operations` |
| Stability | `preview` in contract v14 |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `external_account_id` | `str` | yes, by the sidecar | The account as the source knows it, which the sidecar translates to the account it is linked to. |
| `source` | `str` | yes, by the sidecar | The plugin's scheme for its source, as on a statement, such as `"snaptrade"`. |
| `activity` | [`CustodialActivity`](#custodialactivity) or `None` | yes, by the sidecar | The activity, as the custodian states it. |
| `acting_for` | `str` or `None` | no | Unset: the plugin reports as itself, as it does on every sync. See [Acting for a person](#acting-for-a-person). |

The street keeps an activity once, by its source, its account and its `external_activity_id`. Sent again under the same identifier, it is answered `already_recorded` with the first one's `activity_id`, recorded and announced once, so a retry, a restart or a backfill sent again records nothing twice. A custodian restating an activity under a new identifier is a new activity, reported, never merged: operations sees both, and a person decides which applies.

**Returns** `RecordActivityResult`:

| Field | Type | Meaning |
|---|---|---|
| `activity_id` | `str` | The street's identifier for the activity, such as `ACT-…`. |
| `already_recorded` | `bool` | `True` when it was recorded before, by its source, account and `external_activity_id`, and the first one is answered. |

**Errors:** [`NotLinked`](#an-unlinked-external-account) for an external account nobody has linked: nothing is recorded, and the plugin reports the account's activity once it is linked. `invalid` for an empty `external_account_id` or `source`, no `activity`, an empty `external_activity_id` or `trade_date`, no raw record, a `Money` with no amount, a kind the enum does not define, or a value outside its bounds (an `external_activity_id` of 1 to 200 characters, a `description` of at most 500, at most 32 provenance entries), naming the field. `NotGranted` without the `custody` role. `no handler`, `timeout` or `handler error` from the street store.

```python
from decimal import Decimal
import meridian

reply = await plugin.record_activity(
    external_account_id="acct-1",
    source="snaptrade",
    activity=meridian.CustodialActivity(
        external_activity_id=venue_activity["id"],       # the custodian's own identifier
        kind="reinvestment",
        instrument_id=instrument_id,                     # resolved at the edge, as a holding's is
        trade_date="2026-09-30",
        settlement_date="2026-09-30",
        units=Decimal("3.27"),                           # signed by what it did to the account
        price=meridian.Money(Decimal("1.00"), "USD"),
        amount=meridian.Money(Decimal("-3.27"), "USD"),  # signed by what it did to the cash
        description=venue_activity["description"],
        raw_record=plugin.raw_record(f"activities/acct-1/{venue_activity['id']}"),
    ),
)
reply.activity_id, reply.already_recorded   # "ACT-…", False
```

## `list_activities` { #list_activities }

From 0.19.0, contract v14. Reads the activity of the accounts in the plugin's read scope, as the street store announced each, by trade date. The reply says from when the account's source can read history, so an operations plugin can say an opening balance is older than the history that would explain it. See [Reads are within the read scope](#reads).

```python
async def list_activities(
    self, *, account_id: str = "", trade_date_from: str = "", trade_date_to: str = "",
    since: Watermark | None = None, page_size: int = 0, cursor: str = "",
) -> ListActivitiesResult
```

| | |
|---|---|
| gRPC | `rpc ListActivities(ListActivitiesParams) returns (ListActivitiesResult)` |
| Workflow step | W2.11, List an account's activity |
| Kind | query, on `platform.street.query.list-activities` |
| Role | `operations` |
| Served by | the street store |
| Stability | `preview` in contract v14 |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `account_id` | `str` | no | One account, which must be in the plugin's read scope. Empty for every account in it. |
| `trade_date_from`, `trade_date_to` | `str` | no | ISO 8601 dates, inclusive. Empty for no bound on that side. |
| `since` | [`Watermark`](#watermark) or `None` | no | Only the activities recorded after it, in the order recorded rather than by trade date. |
| `page_size` | `int` | no | How many to a page: 100 when `0`, and never more than 500. |
| `cursor` | `str` | no | The previous page's `next_cursor`, or empty for the first. |

**Returns** `ListActivitiesResult`:

| Field | Type | Meaning |
|---|---|---|
| `activities` | sequence of [`ActivityRecordedEvent`](#activityrecordedevent) | The activities on the page, each as it was announced. |
| `next_cursor` | `str` | The next page's cursor, empty on the last. |
| `as_of` | [`Watermark`](#watermark) | The point in the store's record the page was read at. |
| `history_from` | `str` | The first date the named account's source can read activity from, as its latest sync status said. Empty where the read names no account, or the source has not said. |

**Errors:** `NotGranted` for an `account_id` outside the read scope, and without the `operations` role. `no handler`, `timeout` or `handler error` from the street store.

```python
page = await plugin.list_activities(account_id="ACC-…", trade_date_from="2026-09-01")
for each in page.activities:
    activity = each.activity
    if activity.kind == meridian.ActivityKind.ACTIVITY_KIND_REINVESTMENT:
        units = meridian.as_decimal(activity.units)
page.history_from   # "2024-06-03", or "" where the source has not said
```

## `list_sync_statuses` { #list_sync_statuses }

From 0.19.0, contract v14. Reads the sync statuses the street store kept, for the accounts in the plugin's read scope: the latest of each connection, or every one recorded since a watermark. The street hears each sync status a custody plugin reports ([`report_sync_status`](#report_sync_status)) and keeps it, so an operations plugin tells a connection that needs a person to sign in again apart from data that is merely old. See [Reads are within the read scope](#reads).

```python
async def list_sync_statuses(
    self, *, account_id: str = "", since: Watermark | None = None,
    page_size: int = 0, cursor: str = "",
) -> ListSyncStatusesResult
```

| | |
|---|---|
| gRPC | `rpc ListSyncStatuses(ListSyncStatusesParams) returns (ListSyncStatusesResult)` |
| Workflow step | W2.14, Read an account's sync status |
| Kind | query, on `platform.street.query.list-sync-statuses` |
| Role | `operations` |
| Served by | the street store, which announces each one it keeps as `SyncStatusRecorded` (W2.13) to `operations` |
| Stability | `preview` in contract v14 |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `account_id` | `str` | no | One account, which must be in the plugin's read scope. Empty for every account in it. |
| `since` | [`Watermark`](#watermark) or `None` | no | Unset: the latest of each connection. Set: every one recorded after it, in the order recorded. |
| `page_size` | `int` | no | How many to a page: 100 when `0`, and never more than 500. |
| `cursor` | `str` | no | The previous page's `next_cursor`, or empty for the first. |

**Returns** `ListSyncStatusesResult`: `statuses`, a sequence of [`SyncStatusRecordedEvent`](#syncstatusrecordedevent), each as it was announced; `next_cursor`, empty on the last page; and `as_of`, the [`Watermark`](#watermark) it was read at.

A sync status for an external account nobody has linked is kept with its account empty: it reaches no plugin, and the dashboard alone shows it.

**Errors:** `NotGranted` for an `account_id` outside the read scope, and without the `operations` role. `no handler`, `timeout` or `handler error` from the street store.

```python
page = await plugin.list_sync_statuses(account_id="ACC-…")
for each in page.statuses:
    if each.status.state == meridian.SyncState.SYNC_STATE_NEEDS_SIGN_IN:
        ...  # a person must sign in again at the venue: say so, rather than "old"
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

## `resolve_instrument` { #resolve_instrument }

From 0.13.0. Forward resolution: an instrument identifier to its record, so a position can be shown with a name rather than an opaque key, and a plugin that reads the book can join a position to its instrument by its ID. Reference data, so it is answered whatever the plugin's read scope.

```python
async def resolve_instrument(
    self, *, instrument_id: str = "", as_of_ns: int = 0,
) -> ResolveInstrumentResult
```

| | |
|---|---|
| gRPC | `rpc ResolveInstrument(ResolveInstrumentParams) returns (ResolveInstrumentResult)` |
| Workflow step | W3.6, Resolve an instrument for display |
| Kind | query, on `platform.reference.query.resolve-instrument` |
| Role | `portfolio`, `reporting`, `compliance`, `oms`, `operations` |
| Served by | the instrument store |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `instrument_id` | `str` | yes | An `INS-` instrument, or the deployment's `LCL-` placeholder. |
| `as_of_ns` | `int` | no | The reference time: the record as it stood then. |

**Returns** `ResolveInstrumentResult`:

| Field | Type | Meaning |
|---|---|---|
| `found` | `bool` | Whether the store holds the instrument. |
| `instrument` | [`InstrumentRecord`](#instrumentrecord) | Its record, when `found`. |

**Errors:** `no handler`, `timeout` or `handler error` from the instrument store. `NotGranted` without one of the five roles.

```python
answer = await plugin.resolve_instrument(instrument_id=position.instrument_id)
if answer.found:
    name = answer.instrument.description
```

## `record_opening_balance` { #record_opening_balance }

From 0.13.0. Records what an account holds when it enters the [book of record](../concepts/the-book-of-record.md), once, as of a business date: its positions, each with its trade-date quantity, its settled quantity, its pending settlements by value date and its lots, each lot with its quantity, cost and acquisition date, as the custodian or the prior system reports them and a person completes them, naming that source. An account holding nothing enters with no positions. From contract v9 the book refuses one missing any of what it requires, naming each missing field: see [What the book requires](#what-the-book-requires).

It is a person's act, the fact every later break inherits: send it `acting_for` the person confirming it, with their reason. See [The book's commands](#the-books-commands).

```python
async def record_opening_balance(
    self, *, account_id: str = "", as_of_date: str = "", sources: Sequence[OpeningSource] = (),
    positions: Sequence[OpeningPosition] = (), reason: str = "", replaces_entry_id: str = "",
    idempotency_key: str = "", acting_for: str | None = None,
) -> RecordOpeningBalanceResult
```

| | |
|---|---|
| gRPC | `rpc RecordOpeningBalance(RecordOpeningBalanceParams) returns (RecordOpeningBalanceResult)` |
| Workflow step | W9.1, Record an account's opening balance |
| Kind | command, on `platform.book.command.record-opening-balance` |
| Role | `operations` |
| Served by | the book of record, which journals it as one entry opening each position, lot and pending settlement from zero (W9.2) |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `account_id` | `str` | yes | The account. It must be in the plugin's write scope, and one the person may write. |
| `as_of_date` | `str` | yes | The ISO 8601 business date it stands for. |
| `sources` | sequence of [`OpeningSource`](#openingsource) | yes, by the book from contract v9 | One per custodian or system it was composed from, each naming it and the street records it was composed from. |
| `positions` | sequence of [`OpeningPosition`](#openingposition) | no | What the account holds. Empty: it enters holding nothing. |
| `reason` | `str` | yes, by the book | The person's own words. |
| `replaces_entry_id` | `str` | no | The reversed opening balance this one replaces. Empty for the first. |
| `idempotency_key` | `str` | no | See [Idempotency keys](#idempotency-keys). |
| `acting_for` | `str` or `None` | yes, by the book | The `Meridian-Caller` header of the person confirming it. |

A position held under a placeholder instrument enters under the placeholder, flagged `placeholder` on the [`BookPosition`](#bookposition), and the book moves it onto the instrument when the instrument is identified. Its settled quantity and its pending quantities must account for its trade-date quantity, and its lots must sum to it; cash sends none.

**Returns** `RecordOpeningBalanceResult`, a [book entry's result](#book-entry-result): the positions it opened, and the account's attributes naming the standing opening balance.

**Errors:**

- [`CommandRefused`](#the-books-refusals): `REFUSAL_REASON_ACTOR_REQUIRED` with no person, `REFUSAL_REASON_REASON_REQUIRED` with no reason, `REFUSAL_REASON_OPENING_BALANCE_RECORDED` while one stands, `REFUSAL_REASON_INCOMPLETE` from 0.14.0 for a field the book requires left out, each in `fields` (`positions[0].settled_quantity`, `positions[1].lots[0].terms.cost`), `REFUSAL_REASON_LOTS_UNBALANCED` for lots that do not sum to their position, `REFUSAL_REASON_IDEMPOTENCY_CONFLICT` for a key used by a different command.
- `TypeError` or `ValueError` for a number, an amount or an enum, named by its path (`positions[0].lots[1].terms.cost`).
- `NotGranted` for an account outside the write scope, a person who may not write it, or a session not opened by Open. `not vouched for` for an `acting_for` that is not accepted.
- `handler error` from the book for anything else it refuses, such as a position that states no side, with its reason. `no handler` or `timeout` from the book.
- `NotGranted` without the `operations` role.

```python
import meridian

reply = await plugin.record_opening_balance(
    account_id=account,
    as_of_date="2026-09-08",
    sources=[meridian.OpeningSource(kind="custodian", name="Interactive Brokers",
                                    as_of_date="2026-09-08", basis="trade_date")],
    positions=positions,               # each complete: settled, pending by date, lots with cost and date
    reason=reason,                     # the person's own words
    idempotency_key=f"opening/{account}/{statement_id}",
    acting_for=request.caller.header,  # the person confirming it
)
```

## `record_break` { #record_break }

From 0.13.0. Records a difference between the book and the street as a break, or brings an open one up to date: the account, the position or account-level figure it concerns, its category, each differing field with the book's value and the street's, what was compared, the business date it was seen, and the candidate causes the plugin's matching found. A finding, so the plugin may send it as itself.

```python
async def record_break(
    self, *, account_id: str = "", break_id: str = "", position: PositionKey | None = None,
    figure: FigureKey | None = None, category: BreakCategory | str | None = None,
    differences: Sequence[BreakDifference] = (), book_watermark: Watermark | None = None,
    street: StreetRecordRef | None = None, business_date: str = "",
    candidate_causes: Sequence[BreakCause] = (), idempotency_key: str = "",
    acting_for: str | None = None,
) -> RecordBreakResult
```

| | |
|---|---|
| gRPC | `rpc RecordBreak(RecordBreakParams) returns (RecordBreakResult)` |
| Workflow step | W9.4, Record a break |
| Kind | command, on `platform.book.command.record-break` |
| Role | `operations` |
| Served by | the book of record |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `account_id` | `str` | yes | The account, in the plugin's write scope. |
| `break_id` | `str` | no | Empty for a new break, whose identifier the book mints; an open break's, to bring it up to date. |
| `position` | [`PositionKey`](#positionkey) or `None` | one of these two | The position it concerns: an instrument and a side. |
| `figure` | [`FigureKey`](#figurekey) or `None` | one of these two | The account-level figure it concerns, under its margin agreement. |
| `category` | [`BreakCategory`](#breakcategory), `str` or `None` | yes | What differs. |
| `differences` | sequence of [`BreakDifference`](#breakdifference) | no | Each differing field, with the book's value and the street's. |
| `book_watermark` | [`Watermark`](#watermark) or `None` | no | Where the book was read. |
| `street` | [`StreetRecordRef`](#streetrecordref) or `None` | no | The street record compared, by value. |
| `business_date` | `str` | yes | The reconciliation's ISO 8601 business date: first seen for a new break, last seen for one brought up to date. |
| `candidate_causes` | sequence of [`BreakCause`](#breakcause) | no | The causes the plugin's matching found, for a person to confirm one. |
| `idempotency_key` | `str` | no | See [Idempotency keys](#idempotency-keys). |
| `acting_for` | `str` or `None` | no | Unset: the plugin reports the finding as itself. |

Every difference is recorded: a plugin may rank or group breaks for its people, never drop one. A difference that persists is one break, brought up to date by its `break_id`, not a new one each day.

**Returns** `RecordBreakResult`, a [book entry's result](#book-entry-result) holding the break.

**Errors:** `CommandRefused` with `REFUSAL_REASON_NO_OPENING_BALANCE` for an account with no opening balance, `REFUSAL_REASON_BREAK_STATE` for a `break_id` that is not open, or `REFUSAL_REASON_IDEMPOTENCY_CONFLICT`. `ValueError` for both `position` and `figure`. `NotGranted` for an account outside the write scope, and without the `operations` role. `handler error`, `no handler` or `timeout` from the book.

```python
await plugin.record_break(
    account_id=account,
    position=meridian.PositionKey(instrument_id=instrument, side="long"),
    category="trade_date_quantity",
    differences=[meridian.BreakDifference(
        field="trade_date_quantity",
        book=meridian.BreakValue(quantity=Decimal("150")),
        street=meridian.BreakValue(quantity=Decimal("175")),
    )],
    book_watermark=book_page.as_of,
    street=meridian.StreetRecordRef(statement_id=statement.statement_id, as_of_date=statement.as_of_date),
    business_date=statement.as_of_date,
    candidate_causes=[meridian.BreakCause(category="unbooked_trade", none_found=True)],
    idempotency_key=f"break/{account}/{statement.statement_id}/{instrument}/long/trade_date_quantity",
)
```

## `record_account_figures` { #record_account_figures }

From 0.13.0. Records the account's figures for a business date, one set per margin agreement, each as the street recorded it, with the collateral held under it and the custodian's own value and margin requirement for each position, labelled as the custodian's. A record of what was reported, never a figure the book computed. A finding, so the plugin may send it as itself.

```python
async def record_account_figures(
    self, *, account_id: str = "", business_date: str = "", source: StreetRecordRef | None = None,
    agreements: Sequence[AgreementFigures] = (), idempotency_key: str = "",
    acting_for: str | None = None,
) -> RecordAccountFiguresResult
```

| | |
|---|---|
| gRPC | `rpc RecordAccountFigures(RecordAccountFiguresParams) returns (RecordAccountFiguresResult)` |
| Workflow step | W9.5, Record the account's figures |
| Kind | command, on `platform.book.command.record-account-figures` |
| Role | `operations` |
| Served by | the book of record |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `account_id` | `str` | yes | The account, in the plugin's write scope. |
| `business_date` | `str` | yes | The ISO 8601 business date the figures are for. |
| `source` | [`StreetRecordRef`](#streetrecordref) or `None` | no | The statement they were read from. |
| `agreements` | sequence of [`AgreementFigures`](#agreementfigures) | no | One set per margin agreement. |
| `idempotency_key` | `str` | no | See [Idempotency keys](#idempotency-keys). |
| `acting_for` | `str` or `None` | no | Unset: the plugin reports the finding as itself. |

**Returns** `RecordAccountFiguresResult`, a [book entry's result](#book-entry-result) holding the figures, one record per account, agreement and business date.

**Errors:** `CommandRefused` with `REFUSAL_REASON_NO_OPENING_BALANCE` or `REFUSAL_REASON_IDEMPOTENCY_CONFLICT`. `TypeError` or `ValueError` for a number or an amount, named by its path. `NotGranted` for an account outside the write scope, and without the `operations` role. `handler error`, `no handler` or `timeout` from the book.

## `record_encumbrances` { #record_encumbrances }

From 0.13.0. Records what of each position cannot move, as a completed statement states it: for each position, its encumbrances, the whole set, empty when the statement reports none. An attribute of the position, never a movement: its quantities do not change, and the book derives its free quantity from them. A finding, so the plugin may send it as itself.

```python
async def record_encumbrances(
    self, *, account_id: str = "", business_date: str = "", source: StreetRecordRef | None = None,
    positions: Sequence[PositionEncumbrances] = (), idempotency_key: str = "",
    acting_for: str | None = None,
) -> RecordEncumbrancesResult
```

| | |
|---|---|
| gRPC | `rpc RecordEncumbrances(RecordEncumbrancesParams) returns (RecordEncumbrancesResult)` |
| Workflow step | W9.15, Record a position's encumbrances |
| Kind | command, on `platform.book.command.record-encumbrances` |
| Role | `operations` |
| Served by | the book of record |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `account_id` | `str` | yes | The account, in the plugin's write scope. |
| `business_date` | `str` | yes | The statement's ISO 8601 business date. |
| `source` | [`StreetRecordRef`](#streetrecordref) or `None` | no | The statement they were read from. |
| `positions` | sequence of [`PositionEncumbrances`](#positionencumbrances) | no | Each position's whole set of encumbrances. |
| `idempotency_key` | `str` | no | See [Idempotency keys](#idempotency-keys). |
| `acting_for` | `str` or `None` | no | Unset: the plugin reports the finding as itself. |

The book holds the kinds `PLEDGED`, `POSTED`, `ON_LOAN`, `BLOCKED`, `RESTRICTED`, `IN_TRANSIT` and `OTHER`, which needs the source's own code. The street's `PENDING`, `REHYPOTHECATED` and `BORROWED` are not the book's: pending stays in the settlement buckets.

**Returns** `RecordEncumbrancesResult`, a [book entry's result](#book-entry-result) holding each position changed, with its `encumbrances` and `free_quantity`.

**Errors:** `CommandRefused` with `REFUSAL_REASON_NO_OPENING_BALANCE` or `REFUSAL_REASON_IDEMPOTENCY_CONFLICT`. `handler error` from the book, naming the field, for an unspecified kind, a kind the book does not hold, `OTHER` with no code, or a position the book does not hold; that difference is a break of its own. `NotGranted` for an account outside the write scope, and without the `operations` role. `no handler` or `timeout` from the book.

## `handle_break` { #handle_break }

From 0.13.0. For a person: confirms one of a break's candidate causes, or records another, and sets who owns the break, its escalation level and its due date. Cause and handling are recorded attributes, not states: a break stays open until it is resolved or closed.

```python
async def handle_break(
    self, *, account_id: str = "", break_id: str = "", confirmed_cause: BreakCause | None = None,
    handling: BreakHandling | None = None, reason: str = "", idempotency_key: str = "",
    acting_for: str | None = None,
) -> HandleBreakResult
```

| | |
|---|---|
| gRPC | `rpc HandleBreak(HandleBreakParams) returns (HandleBreakResult)` |
| Workflow step | W9.6, Set a break's cause and handling |
| Kind | command, on `platform.book.command.handle-break` |
| Role | `operations` |
| Served by | the book of record |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `account_id` | `str` | yes | The account, in the plugin's write scope, and one the person may write. |
| `break_id` | `str` | yes | The break, which must be open. |
| `confirmed_cause` | [`BreakCause`](#breakcause) or `None` | no | The cause the person confirms. `None`: unchanged. |
| `handling` | [`BreakHandling`](#breakhandling) or `None` | no | Its owner, escalation level and due date. `None`: unchanged; set, it replaces the handling whole. |
| `reason` | `str` | yes, by the book | The person's own words. |
| `idempotency_key` | `str` | no | See [Idempotency keys](#idempotency-keys). |
| `acting_for` | `str` or `None` | yes, by the book | The `Meridian-Caller` header of the person. |

**Returns** `HandleBreakResult`, a [book entry's result](#book-entry-result) holding the break.

**Errors:** `CommandRefused` with `REFUSAL_REASON_ACTOR_REQUIRED`, `REFUSAL_REASON_REASON_REQUIRED`, `REFUSAL_REASON_BREAK_STATE` or `REFUSAL_REASON_IDEMPOTENCY_CONFLICT`. `NotGranted` for an account outside the write scope, a person who may not write it, a session not opened by Open, or without the `operations` role. `not vouched for`, `handler error`, `no handler` or `timeout`.

## `resolve_break` { #resolve_break }

From 0.13.0. For a person: resolves one or more open breaks by the entry that corrects the book, in the same act, or by naming entries already recorded; or closes them with an explanation and no entry. The book moves only by the resolving entry, which names the breaks, never by an overwrite.

```python
async def resolve_break(
    self, *, account_id: str = "", break_ids: Sequence[str] = (), reason: str = "",
    adjustment: Adjustment | None = None, reversal: Reversal | None = None,
    entries: ResolvedByEntries | None = None, explanation: str | None = None,
    idempotency_key: str = "", acting_for: str | None = None,
) -> ResolveBreakResult
```

| | |
|---|---|
| gRPC | `rpc ResolveBreak(ResolveBreakParams) returns (ResolveBreakResult)` |
| Workflow step | W9.7, Resolve or close a break |
| Kind | command, on `platform.book.command.resolve-break` |
| Role | `operations` |
| Served by | the book of record |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `account_id` | `str` | yes | The account, in the plugin's write scope, and one the person may write. |
| `break_ids` | sequence of `str` | yes | The breaks, each open. |
| `reason` | `str` | yes, by the book | The person's own words. |
| `adjustment` | [`Adjustment`](#adjustment) or `None` | one of these four | Resolves them by an adjustment journalled in the same act: its movement lines and lot basis adjustments, effective after the opening balance's date. |
| `reversal` | [`Reversal`](#reversal) or `None` | one of these four | Resolves them by reversing an entry: the book negates its lines. |
| `entries` | [`ResolvedByEntries`](#resolvedbyentries) or `None` | one of these four | Resolves them by entries already recorded. |
| `explanation` | `str` or `None` | one of these four | Closes them with this explanation, moving nothing. |
| `idempotency_key` | `str` | no | See [Idempotency keys](#idempotency-keys). |
| `acting_for` | `str` or `None` | yes, by the book | The `Meridian-Caller` header of the person. |

**Returns** `ResolveBreakResult`, a [book entry's result](#book-entry-result): the breaks resolved or closed, and the positions the resolving entry moved.

**Errors:**

- `CommandRefused`: `REFUSAL_REASON_ACTOR_REQUIRED`, `REFUSAL_REASON_REASON_REQUIRED`, `REFUSAL_REASON_BREAK_STATE` for a break that is not open, `REFUSAL_REASON_INCOMPLETE` from 0.14.0 for an adjustment's line opening a lot without its cost or acquisition date (`adjustment.lines[0].opens_lot.cost`, `adjustment.lines[0].opens_lot.acquired_date`), `REFUSAL_REASON_BEFORE_OPENING_BALANCE` for an entry effective on or before the opening balance's date, `REFUSAL_REASON_LOTS_UNBALANCED` for an entry that would leave a position's open lots not summing to it, `REFUSAL_REASON_LATER_ENTRIES_STAND` for a reversal of the opening balance while a later entry moves the account's positions, `REFUSAL_REASON_IDEMPOTENCY_CONFLICT`.
- `ValueError` for more than one of the four, and `TypeError` or `ValueError` for a number or an amount, named by its path.
- `NotGranted` for an account outside the write scope, a person who may not write it, a session not opened by Open, or without the `operations` role. `not vouched for`, `handler error`, `no handler` or `timeout`.

```python
await plugin.resolve_break(
    account_id=account,
    break_ids=[break_id],
    reason="The custodian's statement shows a buy of 25 we had not booked.",
    adjustment=meridian.Adjustment(
        effective_date="2026-09-10",
        lines=[meridian.MovementLine(
            instrument_id=instrument, side="long", bucket="settled", quantity=Decimal("25"),
            opens_lot=meridian.LotTerms(cost=meridian.Money(Decimal("4625.00"), "USD"),
                                        acquired_date="2026-09-10", source="adjustment"),
        )],
    ),
    acting_for=request.caller.header,
)
```

## `close_breaks_as_cleared` { #close_breaks_as_cleared }

From 0.13.0. For a person: closes breaks whose difference has gone, a settlement landing or the custodian catching up, citing the statement where it was gone, and moves nothing. A break is never closed by silence.

```python
async def close_breaks_as_cleared(
    self, *, account_id: str = "", break_ids: Sequence[str] = (),
    cleared_at: StreetRecordRef | None = None, reason: str = "", idempotency_key: str = "",
    acting_for: str | None = None,
) -> CloseBreaksAsClearedResult
```

| | |
|---|---|
| gRPC | `rpc CloseBreaksAsCleared(CloseBreaksAsClearedParams) returns (CloseBreaksAsClearedResult)` |
| Workflow step | W9.7, Resolve or close a break |
| Kind | command, on `platform.book.command.close-breaks-as-cleared` |
| Role | `operations` |
| Served by | the book of record |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `account_id` | `str` | yes | The account, in the plugin's write scope, and one the person may write. |
| `break_ids` | sequence of `str` | yes, by the book | The breaks, each open. |
| `cleared_at` | [`StreetRecordRef`](#streetrecordref) or `None` | yes, by the book | The statement where the difference was gone, by value, its `statement_id` set. |
| `reason` | `str` | yes, by the book | The person's own words. |
| `idempotency_key` | `str` | no | See [Idempotency keys](#idempotency-keys). |
| `acting_for` | `str` or `None` | yes, by the book | The `Meridian-Caller` header of the person. |

**Returns** `CloseBreaksAsClearedResult`, a [book entry's result](#book-entry-result) holding the breaks closed.

**Errors:** `CommandRefused` with `REFUSAL_REASON_ACTOR_REQUIRED`, `REFUSAL_REASON_REASON_REQUIRED`, `REFUSAL_REASON_BREAK_STATE` or `REFUSAL_REASON_IDEMPOTENCY_CONFLICT`. `handler error` from the book for no breaks or no statement. `NotGranted` for an account outside the write scope, a person who may not write it, a session not opened by Open, or without the `operations` role. `not vouched for`, `no handler` or `timeout`.

## `list_positions` { #list_positions }

From 0.13.0. Reads the book's positions within the plugin's read scope, or one account's, each with its lots, pending settlements, encumbrances and free quantity, and its opening balance's sources; or those changed since a watermark; or the positions at the end of a business date, as known at a watermark or now. See [Reads are within the read scope](#reads).

```python
async def list_positions(
    self, *, account_id: str = "", since: Watermark | None = None, business_date: str = "",
    at: Watermark | None = None, page_size: int = 0, cursor: str = "",
) -> ListPositionsResult
```

| | |
|---|---|
| gRPC | `rpc ListPositions(ListPositionsParams) returns (ListPositionsResult)` |
| Workflow step | W9.10, Read positions |
| Kind | query, on `platform.book.query.list-positions` |
| Role | `portfolio`, `reporting`, `compliance`, `oms`, `operations` |
| Served by | the book of record |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `account_id` | `str` | no | One account, which must be in the plugin's read scope. Empty for every account in it. |
| `since` | [`Watermark`](#watermark) or `None` | no | Only the positions whose last change is after it, removed ones included. |
| `business_date` | `str` | no | The positions at the end of this ISO 8601 business date, served by replay from the journal. |
| `at` | [`Watermark`](#watermark) or `None` | no | As the book knew them at this watermark, so a report re-run there reproduces itself. |
| `page_size` | `int` | no | How many to a page: 100 when `0`, and never more than 500. |
| `cursor` | `str` | no | The previous page's `next_cursor`, or empty for the first. |

A read by business date or at a watermark takes no `since`.

**Returns** `ListPositionsResult`: `positions`, a sequence of [`BookPosition`](#bookposition); `next_cursor`; and `as_of`, the [`Watermark`](#watermark) it was read at.

**Errors:** `NotGranted` for an `account_id` outside the read scope, and without one of the five roles. `handler error` from the book for a `since` beside `business_date` or `at`, or a business date that is not `YYYY-MM-DD`. `no handler` or `timeout` from the book.

```python
page = await plugin.list_positions(account_id=account)
for position in page.positions:
    trade_date = meridian.as_decimal(position.trade_date_quantity)
    free = meridian.as_decimal(position.free_quantity) if position.HasField("free_quantity") else None
```

## `list_breaks` { #list_breaks }

From 0.13.0. Reads breaks within the plugin's read scope, or one account's, open, resolved, closed or any of them, each with its cause, handling and resolution; or those changed since a watermark. See [Reads are within the read scope](#reads).

```python
async def list_breaks(
    self, *, account_id: str = "", states: Sequence[BreakState | str] = (),
    since: Watermark | None = None, page_size: int = 0, cursor: str = "",
) -> ListBreaksResult
```

| | |
|---|---|
| gRPC | `rpc ListBreaks(ListBreaksParams) returns (ListBreaksResult)` |
| Workflow step | W9.11, Read breaks |
| Kind | query, on `platform.book.query.list-breaks` |
| Role | `operations`, `oms`, `compliance`, `portfolio`, `reporting` |
| Served by | the book of record |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `account_id` | `str` | no | One account, in the read scope. Empty for every account in it. |
| `states` | sequence of [`BreakState`](#breakstate) or `str` | no | The states to answer. Empty for every state. |
| `since` | [`Watermark`](#watermark) or `None` | no | Only the breaks changed after it. |
| `page_size`, `cursor` | `int`, `str` | no | As on [`list_positions`](#list_positions). |

**Returns** `ListBreaksResult`: `breaks`, a sequence of [`Break`](#break); `next_cursor`; and `as_of`.

**Errors:** `NotGranted` for an `account_id` outside the read scope, and without one of the five roles. `no handler`, `timeout` or `handler error` from the book.

## `list_account_figures` { #list_account_figures }

From 0.13.0. Reads the accounts' figures within the plugin's read scope, by account and margin agreement, for a business date or a range of them; or those recorded since a watermark. Margin movement is a series per agreement: the book adds nothing up across agreements, and a reader that wants a total adds them. See [Reads are within the read scope](#reads).

```python
async def list_account_figures(
    self, *, account_id: str = "", agreement: MarginAgreementRef | None = None,
    from_date: str = "", to_date: str = "", since: Watermark | None = None,
    at: Watermark | None = None, page_size: int = 0, cursor: str = "",
) -> ListAccountFiguresResult
```

| | |
|---|---|
| gRPC | `rpc ListAccountFigures(ListAccountFiguresParams) returns (ListAccountFiguresResult)` |
| Workflow step | W9.12, Read the account's figures |
| Kind | query, on `platform.book.query.list-account-figures` |
| Role | `operations`, `portfolio`, `compliance`, `reporting` |
| Served by | the book of record |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `account_id` | `str` | no | One account, in the read scope. Empty for every account in it. |
| `agreement` | [`MarginAgreementRef`](#marginagreementref) or `None` | no | One agreement. `None` for every agreement. |
| `from_date`, `to_date` | `str` | no | ISO 8601 business dates, inclusive. Empty for open-ended. |
| `since` | [`Watermark`](#watermark) or `None` | no | Only the figures recorded after it. |
| `at` | [`Watermark`](#watermark) or `None` | no | As the book knew them at this watermark. |
| `page_size`, `cursor` | `int`, `str` | no | As on [`list_positions`](#list_positions). |

**Returns** `ListAccountFiguresResult`: `figures`, a sequence of [`AccountFigures`](#accountfigures); `next_cursor`; and `as_of`.

**Errors:** `NotGranted` for an `account_id` outside the read scope, and without one of the four roles. `no handler`, `timeout` or `handler error` from the book.

## `list_account_attributes` { #list_account_attributes }

From 0.13.0. Reads the book's attributes of the accounts within the plugin's read scope, or one account's: the base currency, the default method of relieving lots, and the standing opening balance, with its entry, its date and its sources; or those changed since a watermark. A plugin learns from it that an account is in the book, and from which date it reconciles, without proposing an opening balance again. A deployment admin sets the first two on the dashboard's [Books tab](../concepts/the-book-of-record.md#the-books-tab). See [Reads are within the read scope](#reads).

```python
async def list_account_attributes(
    self, *, account_id: str = "", since: Watermark | None = None, page_size: int = 0,
    cursor: str = "",
) -> ListAccountAttributesResult
```

| | |
|---|---|
| gRPC | `rpc ListAccountAttributes(ListAccountAttributesParams) returns (ListAccountAttributesResult)` |
| Workflow step | W9.14, Read an account's attributes |
| Kind | query, on `platform.book.query.list-account-attributes` |
| Role | `portfolio`, `reporting`, `compliance`, `oms`, `operations` |
| Served by | the book of record |

| Name | Type | Required | Meaning |
|---|---|---|---|
| `account_id` | `str` | no | One account, in the read scope. Empty for every account in it. |
| `since` | [`Watermark`](#watermark) or `None` | no | Only the attributes changed after it. |
| `page_size`, `cursor` | `int`, `str` | no | As on [`list_positions`](#list_positions). |

**Returns** `ListAccountAttributesResult`: `attributes`, a sequence of [`AccountAttributes`](#accountattributes); `next_cursor`; and `as_of`.

**Errors:** `NotGranted` for an `account_id` outside the read scope, and without one of the five roles. `no handler`, `timeout` or `handler error` from the book.

```python
page = await plugin.list_account_attributes(account_id=account)
if page.attributes and page.attributes[0].HasField("opening_balance"):
    d0 = page.attributes[0].opening_balance.as_of_date  # in the book since this date
```

## Types { #types }

The plugin-facing types these operations take and return. [`Identifier`](python-sdk.md#identifier) and [`MissReason`](python-sdk.md#missreason) are described with the Python SDK. `Money`, `StatementFigures`, `ReportedCollateral`, `ReportedLot` and, from 0.13.0, `ReportedEncumbrance` and the book's `OpeningSource`, `OpeningPosition`, `OpeningLot`, `PendingSettlement`, `LotTerms`, `PositionKey`, `BreakDifference`, `BreakValue`, `BreakCause`, `PendingSettlementRef`, `AgreementFigures`, `ReportedPositionValue`, `PositionEncumbrances`, `Encumbrance`, `Adjustment`, `MovementLine` and `BasisAdjustment` are the SDK's frozen dataclasses, exported from `meridian`, which take their numbers as `Decimal` and their amounts as `Money`, and are converted and refused as a call's own parameters are. Every other type below is a generated protobuf message or enum in `meridian.plugin.v1.operations_pb2`, and `AssetClass`, `CollateralDirection`, `ExternalAccount`, `HoldingSide` and `SyncState` are also exported from `meridian`. What a read answers is all generated messages, `StatementFigures` among them: read a number or an amount off one with [`as_decimal` and `as_money`](#numbers-and-amounts).

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
| `venue_account_type` | `str` | The venue's own word for the kind of account, verbatim and for display only. Deprecated in contract v11 for the account kind, and the venue's word as reported where it does not convert. |

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
| `reusable` | `bool` or `None` | Whether the receiver may reuse it, as the agreement states and the venue reports it; `None` where it does not say. Received collateral is never a holding, reusable or not. From 0.13.0. |

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
| `available_quantity`, `not_available_quantity`, `available_basis`, `encumbrances` | as on [`record_holding`](#record_holding) | The same, from 0.13.0. |
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
| `security_interest` | optional `bool` | As the statement said, from 0.13.0; unset where it did not say. |
| `recorded_at_ns` | `int` | When it was completed. |
| `journal`, `cause` | `JournalRef`, `ChangeCause` | Where its completion sits in the store's record, and who caused it. A handler is handed `cause` as [`Heard.cause`](python-sdk.md#heard), and no `journal`. |

### `CustodialActivity` { #custodialactivity }

One activity on an account as the custodian states it, `meridian.CustodialActivity(...)`, the SDK's form: a number as a `Decimal`, an amount as a [`Money`](#money), the kind as an enum's value or name, each converted and refused naming its path (`activity.units`), as a parameter is. From 0.19.0. Each field's meaning and bounds are in the data dictionary, [the street's `CustodialActivity`](../boundaries/street.md#meridian.v1.CustodialActivity).

| Field | Type | Meaning |
|---|---|---|
| `external_activity_id` | `str` | The custodian's own identifier for the activity, never a time or a random value: with the source and the account, the street's key for it. Required. |
| `kind` | [`ActivityKind`](#activitykind), `str` or `None` | What happened, converted from the custodian's type. `None` where the type converts to none of the kinds, and then `kind_as_reported` carries it. |
| `kind_as_reported` | `AsReported` or `None` | The custodian's type, `meridian.edge.as_reported(scheme, code, text)`, set only when `kind` is not known. For a person to map; nothing reads it. |
| `instrument_id` | `str` | The instrument, resolved at the edge as a holding's is: the deployment's record, or the currency's cash instrument. Empty where the activity concerns none, or the custodian's code did not resolve. |
| `instrument_as_reported` | `AsReported` or `None` | The custodian's code for the instrument, set only when it did not resolve: a plan's own fund code nobody has linked to an instrument, say. |
| `trade_date`, `settlement_date` | `str` | ISO 8601: when it was traded or took effect, and when it settles or settled. The trade date is required; the settlement date is empty where the custodian does not state it. |
| `units` | `Decimal`, `int` or `None` | The units of the instrument it moved, signed by what it did to the account: positive added units (a purchase, a reinvestment, the units a split added, a transfer in), negative removed them (a sale, a fee taken in units, a transfer out). `None` where it moved none, such as a cash dividend: never zero. |
| `price` | `Money` or `None` | The price per unit, as stated. `None` where the custodian states none: never worked out from the amount and the units. |
| `amount` | `Money` or `None` | The cash it moved, signed by what it did to the account's cash: positive in (a sale, a dividend, a contribution), negative out (a purchase, a fee, a withdrawal). `None` where it moved none, such as a split: never zero. |
| `description` | `str` | The custodian's own words, for a person. Nothing branches on it. |
| `raw_record` | `RawRecordRef` | The raw record it was converted from, `plugin.raw_record(key)`. Required. |
| `provenance` | sequence of `Provenance` | One for each value the plugin closed rather than read: an instrument a named person linked (`meridian.edge.supplied("instrument_id", person)`), a settlement date derived by a named rule. |

Activity is never netted or deduplicated against holdings: a sweep fund's purchases are reported as the custodian lists them.

### `ActivityKind` { #activitykind }

What an activity was, in the platform's own words, never a custodian's. From 0.19.0.

| Value | Number | Meaning |
|---|---|---|
| `ACTIVITY_KIND_UNSPECIFIED` | 0 | Not known: the custodian's type converts to none of these, and travels beside it as reported (`kind_as_reported`). |
| `ACTIVITY_KIND_PURCHASE` | 1 | Units bought. |
| `ACTIVITY_KIND_SALE` | 2 | Units sold. |
| `ACTIVITY_KIND_REINVESTMENT` | 3 | Income the custodian reinvested in units, as a money market fund's monthly dividend is. |
| `ACTIVITY_KIND_DIVIDEND` | 4 | A dividend paid in cash. |
| `ACTIVITY_KIND_INTEREST` | 5 | Interest paid in cash. |
| `ACTIVITY_KIND_FEE` | 6 | A fee, in cash or in units. |
| `ACTIVITY_KIND_TAX` | 7 | A tax withheld or paid. |
| `ACTIVITY_KIND_SPLIT` | 8 | A split: the units it added or removed. |
| `ACTIVITY_KIND_CORPORATE_ACTION` | 9 | Another corporate action, as the custodian states it. |
| `ACTIVITY_KIND_TRANSFER_IN` | 10 | Units or cash moved in from another account. |
| `ACTIVITY_KIND_TRANSFER_OUT` | 11 | Units or cash moved out to another account. |
| `ACTIVITY_KIND_CONTRIBUTION` | 12 | Cash paid into the account. |
| `ACTIVITY_KIND_WITHDRAWAL` | 13 | Cash taken out of the account. |
| `ACTIVITY_KIND_JOURNAL` | 14 | A movement between the account's own positions or sub-accounts, as the custodian journals it. |

### `ActivityRecordedEvent` { #activityrecordedevent }

An activity, as the street store announced it when it was recorded (W2.12), and each item of [`list_activities`](#list_activities). The `activity_recorded` handler of [`receive`](python-sdk.md#receive) is handed one. From 0.19.0.

| Field | Type | Meaning |
|---|---|---|
| `activity_id` | `str` | The street's identifier for it. |
| `account_id`, `external_account_id`, `source` | `str` | The account it is on, as the sidecar stamped it, and as the source knows it; the source's scheme. |
| `activity` | `CustodialActivity` | The activity whole, as the custody plugin sent it. |
| `recorded_at_ns` | `int` | When the street recorded it: the deployment's clock, never back-dated. A backfilled activity's own time is its `trade_date`. |
| `journal`, `cause` | `JournalRef`, `ChangeCause` | Its record in the street's partition, chained per account with the activities before it, and who caused it. A handler is handed `cause` as [`Heard.cause`](python-sdk.md#heard), and no `journal`. |

### `SyncStatusRecordedEvent` { #syncstatusrecordedevent }

A sync status the street store heard and kept (W2.13), and each item of [`list_sync_statuses`](#list_sync_statuses). The `sync_status_recorded` handler of [`receive`](python-sdk.md#receive) is handed one. From 0.19.0.

| Field | Type | Meaning |
|---|---|---|
| `status` | `SyncStatusEvent` | As the custody plugin published it ([`report_sync_status`](#report_sync_status)), its `state` and `history_from` among it; its account as the sidecar stamped it, empty when the external account is not linked, and then delivered to no plugin. |
| `recorded_at_ns` | `int` | When the street recorded it. |
| `journal`, `cause` | `JournalRef`, `ChangeCause` | Its record in the street's partition, chained per account, and the custody plugin whose sync status it was. |

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

### `InstrumentRecord` { #instrumentrecord }

An instrument's record, as [`resolve_instrument`](#resolve_instrument) answers it. From 0.13.0.

| Field | Type | Meaning |
|---|---|---|
| `instrument_id` | `str` | `INS-`, minted only by the platform, or the deployment's `LCL-` placeholder. |
| `identifiers` | sequence of `Identifier` | Its full identifier set. |
| `asset_class` | [`AssetClass`](#assetclass) | Its asset class. |
| `currency` | `str` | ISO 4217. |
| `exchange_mic` | `str` | Its listing venue, ISO 10383; empty where there is none. |
| `description` | `str` | Its name. |
| `lifecycle_state` | `InstrumentLifecycleState` | `DEFINE` (its attributes may be incomplete), `ACTIVE` or `DECOMMISSIONED`. |
| `version`, `valid_from_ns`, `record_time_ns` | `int` | The record's version, when its mapping became true, and when the store recorded it. |

### `AvailableBasis` { #availablebasis }

What a holding's available quantity is on, as the source says. From 0.13.0.

| Value | Number | Meaning |
|---|---|---|
| `AVAILABLE_BASIS_UNSPECIFIED` | 0 | The source does not say. |
| `AVAILABLE_BASIS_SETTLED` | 1 | `settled`. |
| `AVAILABLE_BASIS_TRADED` | 2 | `traded`. |
| `AVAILABLE_BASIS_CONTRACTUAL` | 3 | `contractual`. |
| `AVAILABLE_BASIS_ORDER_NETTED` | 4 | `order_netted`: a venue's figure net of its open orders, such as Alpaca's `qty_available`. The order reservation is never an encumbrance. |

### `ReportedEncumbrance` { #reportedencumbrance }

One sub-balance of a holding the source reports as encumbered, `meridian.ReportedEncumbrance(...)`, keyword only, as the source reports it. From 0.13.0.

| Field | Type | Meaning |
|---|---|---|
| `kind` | [`EncumbranceKind`](#encumbrancekind), `str` or `None` | Why it cannot move. Refused when not said. |
| `quantity` | `Decimal` or `int` | Signed as the holding's quantity. Required. One larger than the holding is recorded as reported. |
| `available` | `bool` or `None` | Whether the source reports it available. `None` where it does not say: the kind does not imply it. |
| `source_code` | `str` | The source's own code or label, verbatim, such as `"PLED"`. Required for `OTHER`. |
| `pledgee` | `str` | To whom it is pledged, posted or lent, as reported. |
| `held_at` | `str` | The safekeeping place or third party holding it, as reported. |
| `segment` | `str` | The margin segment it is under, where the source names one. |
| `detail` | `str` | The source's narrative. |

### `EncumbranceKind` { #encumbrancekind }

Why some of a holding cannot move. From 0.13.0.

| Value | Number | Meaning |
|---|---|---|
| `ENCUMBRANCE_KIND_UNSPECIFIED` | 0 | Not said. Refused. |
| `ENCUMBRANCE_KIND_PLEDGED` | 1 | `pledged`: pledged in place to a pledgee. |
| `ENCUMBRANCE_KIND_POSTED` | 2 | `posted`: delivered to a third party as collateral. |
| `ENCUMBRANCE_KIND_ON_LOAN` | 3 | `on_loan`: lent. |
| `ENCUMBRANCE_KIND_BLOCKED` | 4 | `blocked`: blocked for a stated purpose. |
| `ENCUMBRANCE_KIND_RESTRICTED` | 5 | `restricted`: movable only under conditions or with documents. |
| `ENCUMBRANCE_KIND_IN_TRANSIT` | 6 | `in_transit`: between depositories, agents or registers. |
| `ENCUMBRANCE_KIND_OTHER` | 7 | `other`: a sub-balance the plugin cannot map; its `source_code` is required. |
| `ENCUMBRANCE_KIND_PENDING` | 8 | The street's only, as reported: the book refuses it. |
| `ENCUMBRANCE_KIND_REHYPOTHECATED` | 9 | The street's only: used by the broker under a right of use, which reduces nothing. The book refuses it. |
| `ENCUMBRANCE_KIND_BORROWED` | 10 | The street's only: borrowed, with a return obligation. The book refuses it. |

### Book entry result { #book-entry-result }

Every command of the book answers after its entry commits, with the same fields: `RecordOpeningBalanceResult`, `RecordBreakResult`, `RecordAccountFiguresResult`, `RecordEncumbrancesResult`, `HandleBreakResult`, `ResolveBreakResult` and `CloseBreaksAsClearedResult`. A repeat, by its message identifier or its idempotency key, is answered with the first's. From 0.13.0.

| Field | Type | Meaning |
|---|---|---|
| `entry` | [`EntryMeta`](#entrymeta) | The entry. |
| `journal` | `JournalRef` | Its place in the account's partition: the number of the first change it made. |
| `positions` | sequence of [`BookPosition`](#bookposition) | Each position it changed, as it stands after it. |
| `breaks` | sequence of [`Break`](#break) | Each break it changed. |
| `figures` | sequence of [`AccountFigures`](#accountfigures) | Each figures record it changed. |
| `attributes` | [`AccountAttributes`](#accountattributes) | The account's attributes, where it changed them: an opening balance and its reversal set and clear the standing one. |

### `EntryMeta` { #entrymeta }

What a journal entry records. From 0.13.0.

| Field | Type | Meaning |
|---|---|---|
| `entry_id` | `str` | Minted by the book. |
| `kind` | `str` | `opening-balance`, `placeholder-moved`, `figures-recorded`, `break-recorded`, `break-handled`, `break-resolved`, `break-closed`, `adjustment`, `reversal`, `attribute-set` or `encumbrances-recorded`: an open list, which a reader takes as data. |
| `actor` | `Actor` | Who made it, set by the book from what the sidecar stamped: `person`, with the person's `subject`, or `system`, with the `instance_id` of the plugin that reported a finding as itself, empty for the book's own act. |
| `event_time_ns`, `received_at_ns` | `int` | The time on the message that caused it, and when the book received it. When it committed is its cause's `committed_at_ns`. |
| `effective_date` | `str` | The ISO 8601 business date it stands for. |
| `control_sequence` | `int` | The control partition's sequence in force. |
| `reference_versions` | sequence of `ReferenceVersion` | Each instrument it names, with the version of its record in force when it was recorded. |
| `reason` | `str` | The person's reason, on a justified act. |
| `break_ids` | sequence of `str` | The breaks it records, handles, resolves or closes. |
| `idempotency_key` | `str` | The key it was sent with, where it was sent one. |

### `BookPosition` { #bookposition }

A position in the book. From 0.13.0.

| Field | Type | Meaning |
|---|---|---|
| `account_id`, `instrument_id`, `side` | `str`, `str`, [`HoldingSide`](#holdingside) | Whose, of what, and which side. |
| `trade_date_quantity` | `Decimal` message | The settled quantity plus what is pending: by construction. On a position a contract v8 opening balance opened with some of it not stated, that too. |
| `settled_quantity` | `Decimal` message, optional | Set on every position contract v9 records. Unset only while some of the quantity is in the not-stated bucket a v8 opening balance opened: unknown, never zero. |
| `not_stated_quantity` | `Decimal` message | Retired in contract v9: zero on every position v9 records. What a v8 opening balance's source did not say was settled or pending. |
| `pending` | sequence of [`PendingSettlement`](#pendingsettlement) | What is pending, by value date. |
| `lots` | sequence of [`Lot`](#lot) | Its open lots, whose open quantities sum to its trade-date quantity; cash has none. |
| `opened_from` | sequence of [`OpeningSource`](#openingsource) | Its opening balance's sources. |
| `effective_date` | `str` | The business date of its last change. |
| `last_change` | `JournalRef` | Where its last change sits in the book's record. |
| `removed` | `bool` | Removed, after the book moved it from a placeholder onto its instrument: answered only to a read given `since`, and heard once. |
| `placeholder` | `bool` | Held under a placeholder instrument, until the book follows its replacement. |
| `encumbrances` | sequence of [`Encumbrance`](#encumbrance) | What of it cannot move, as last recorded from a statement. |
| `free_quantity` | `Decimal` message, optional | Derived, never reported: the quantity on `free_basis` less the encumbrances. Unset while that quantity is unknown. |
| `free_basis` | `FreeBasis` | `FREE_BASIS_SETTLED`, the only basis in this release. |

### `Lot` { #lot }

One of a position's lots, the book's own record. From 0.13.0.

| Field | Type | Meaning |
|---|---|---|
| `lot_id` | `str` | Minted by the book. |
| `open_quantity`, `original_quantity` | `Decimal` message | What is open of it, and what it opened with. |
| `terms` | [`LotTerms`](#lotterms) | As opened, with each basis adjustment applied. |
| `opened_by`, `relieved_by`, `adjusted_by` | `JournalRef`, sequences of `JournalRef` | The entries that opened, relieved and adjusted it. |

### `Encumbrance` { #encumbrance }

One encumbrance of a position, as the book holds it, `meridian.Encumbrance(...)` when sent. From 0.13.0.

| Field | Type | Meaning |
|---|---|---|
| `kind` | [`EncumbranceKind`](#encumbrancekind), `str` or `None` | `PLEDGED` to `OTHER` only. |
| `quantity` | `Decimal` or `int` | Signed as the position's quantity. Required. |
| `pledgee`, `held_at` | `str` | To whom, and where, as the statement states them. |
| `agreement` | [`MarginAgreementRef`](#marginagreementref) or `None` | The margin agreement, where the source names one. |
| `source_code` | `str` | The source's code, verbatim; required for `OTHER`. |
| `detail` | `str` | The source's narrative. |
| `source` | [`StreetRecordRef`](#streetrecordref) or `None` | The statement it was recorded from. |
| `since_date`, `set_by` | `str`, `JournalRef` | Set by the book: the business date it was first recorded under its kind, pledgee, location and agreement, and the change that last set it. |

### `PositionEncumbrances` { #positionencumbrances }

One position's encumbrances as a statement states them, `meridian.PositionEncumbrances(instrument_id=..., side=..., encumbrances=[...])`: the whole set, empty when the statement reports none. From 0.13.0.

### `OpeningSource` { #openingsource }

A source an opening balance was composed from, `meridian.OpeningSource(...)`, keyword only. From 0.13.0.

| Field | Type | Meaning |
|---|---|---|
| `kind` | `OpeningSourceKind`, `str` or `None` | `custodian` or `prior_system`. |
| `name` | `str` | The custodian or system as the deployment knows it: the external account's institution, or the prior system's name. |
| `as_of_date` | `str` | The ISO 8601 date the source's figures are as of. |
| `basis` | `PositionBasis`, `str` or `None` | Whether it reports `trade_date` or `settle_date` positions. |
| `street_records` | sequence of [`StreetRecordRef`](#streetrecordref) | The street records it was composed from, by value. |

### `OpeningPosition` { #openingposition }

One position of an opening balance, `meridian.OpeningPosition(...)`, keyword only. From 0.13.0.

| Field | Type | Meaning |
|---|---|---|
| `instrument_id` | `str` | An instrument, a placeholder, or a currency's cash instrument. |
| `side` | [`HoldingSide`](#holdingside), `str` or `None` | Long or short. |
| `trade_date_quantity` | `Decimal` or `int` | Required. |
| `settled_quantity` | `Decimal`, `int` or `None` | Required by the book from contract v9: where the source states none, a person supplies it. `None` is refused as `positions[n].settled_quantity`. |
| `pending` | sequence of [`PendingSettlement`](#pendingsettlement) | Its pending settlements, each with its value date. With the settled quantity they account for the whole trade-date quantity, or the book refuses it as `positions[n].pending`. |
| `lots` | sequence of `OpeningLot` | As reported and completed by a person, each `meridian.OpeningLot(quantity=..., terms=LotTerms(...))` with its quantity, and its terms' `cost` and `acquired_date` from contract v9; they must sum to the trade-date quantity. Required but on cash, which sends none. |

### `PendingSettlement` { #pendingsettlement }

Quantity pending on a value date, `meridian.PendingSettlement(...)`. From 0.13.0.

| Field | Type | Meaning |
|---|---|---|
| `value_date` | `str` | ISO 8601, which may be years out. Required at an opening balance from contract v9. Empty on a position only for "date not stated", from a contract v8 opening balance or an adjustment the street gave no date for. |
| `quantity` | `Decimal` or `int` | Required. |
| `state` | `PendingState` or `None` | Where the source reports a fail: `failing`, `fail_reason` as reported, and `expected_date`, when it is now expected. |

### `LotTerms` { #lotterms }

A lot's terms, `meridian.LotTerms(...)`, each unset where not known and never derived one from another. From 0.13.0. From contract v9 a lot the book opens, at an opening balance or by an adjustment, carries its `cost` and `acquired_date`, or the book refuses it; a lot a contract v8 book opened may lack them.

| Field | Type | Meaning |
|---|---|---|
| `unit_cost`, `cost` | [`Money`](#money) or `None` | Its cost per unit, and in all. |
| `acquired_date` | `str` | When it was acquired. |
| `holding_period_start` | `str` | Where its holding period starts, apart from acquisition; empty is the acquired date. |
| `settlement_date` | `str` | When it settled. |
| `source` | `LotSource`, `str` or `None` | `opening_balance` or `adjustment`. |

### `StreetRecordRef` { #streetrecordref }

A street record named by value, never a key the book follows: `statement_id`, `change` (the custodial position's change, a `JournalRef`, where one was compared or used) and `as_of_date`, the custodian's. From 0.13.0.

### `PositionKey` { #positionkey }

A position a break concerns, `meridian.PositionKey(instrument_id=..., side=...)`. From 0.13.0.

### `FigureKey` { #figurekey }

An account-level figure a break concerns: `agreement`, a [`MarginAgreementRef`](#marginagreementref); `figure`, by its field's name in the data dictionary; and `instrument_id`, for a collateral balance. From 0.13.0.

### `MarginAgreementRef` { #marginagreementref }

A margin agreement. In this release its one arm is `statement_segment`, a `StatementSegmentRef`: the statement's `external_account_id`, its `segment` as the venue names it (empty for the account as a whole), and its `counterparty`, the external account's institution as reported. From 0.13.0.

### `BreakCategory` { #breakcategory }

| Value | Number | Meaning |
|---|---|---|
| `BREAK_CATEGORY_UNSPECIFIED` | 0 | Not said. |
| `BREAK_CATEGORY_TRADE_DATE_QUANTITY` | 1 | `trade_date_quantity`. |
| `BREAK_CATEGORY_SETTLED_QUANTITY` | 2 | `settled_quantity`. |
| `BREAK_CATEGORY_COST_OR_LOTS` | 3 | `cost_or_lots`. |
| `BREAK_CATEGORY_SETTLED_AGAINST_PENDING` | 4 | `settled_against_pending`. |
| `BREAK_CATEGORY_BOOK_ONLY` | 5 | `book_only`: a position on the book's side only. |
| `BREAK_CATEGORY_STREET_ONLY` | 6 | `street_only`: a position on the street's side only. |
| `BREAK_CATEGORY_FIGURE` | 7 | `figure`: a figure the book holds a value of its own for, such as the street's available and not available against the book's position, or an encumbrance against the book's. |

### `BreakDifference` { #breakdifference }

One differing field, `meridian.BreakDifference(field=..., book=..., street=...)`: `field`, by its name in the data dictionary (`"settled_quantity"`, `"lots[2].terms.cost"`), and each side a `meridian.BreakValue` of one of `quantity`, `amount` or `text`, or `None` where it is absent on that side. From 0.13.0.

### `BreakState` { #breakstate }

`BREAK_STATE_OPEN` (1), `BREAK_STATE_RESOLVED` (2) or `BREAK_STATE_CLOSED` (3); `open`, `resolved` or `closed` in a string. From 0.13.0.

### `BreakCause` { #breakcause }

The item found to cause a break, linked by value, `meridian.BreakCause(...)`. From 0.13.0.

| Field | Type | Meaning |
|---|---|---|
| `category` | `BreakCauseCategory`, `str` or `None` | `unbooked_trade`, `settlement_timing`, `cost_or_price`, `corporate_action`, `fail`, `custodian_error` or `unknown`; from 0.19.0, `income_reinvested`, income the custodian reinvested in units that the book has not booked, such as a money market fund's monthly dividend. |
| `street_record`, `book_entry`, `pending_settlement`, `event_reference`, `none_found`, `activity` | one of these | The item: a street record, a book entry, a pending settlement (`meridian.PendingSettlementRef`), a corporate action's reference as reported, `none_found=True`, or, from 0.19.0, the custodian's activity that explains it, an [`ActivityRef`](#activityref). |
| `note` | `str` | A note. |

### `ActivityRef` { #activityref }

An activity the street recorded, named by value, `meridian.ActivityRef(activity_id=..., change=..., trade_date=...)`: the street's `activity_id`, its record in the street's partition (`change`, the `journal` of its [`ActivityRecordedEvent`](#activityrecordedevent)), and its `trade_date` as the custodian stated it. The book records it as given and follows no key to the street, as it does a street record's. From 0.19.0.

```python
# each: an ActivityRecordedEvent that list_activities answered
meridian.BreakCause(
    category="income_reinvested",
    activity=meridian.ActivityRef(
        activity_id=each.activity_id, change=each.journal, trade_date=each.activity.trade_date,
    ),
    note="the custodian reinvested income in 3.27 units",
)
```

### `BreakHandling` { #breakhandling }

A break's handling: `owner_subject`, a user the deployment knows; `escalation_level`, the operations plugin's own levels, to which core gives no meaning; and `due_date`. From 0.13.0.

### `Break` { #break }

A break, as the book holds it. From 0.13.0.

| Field | Type | Meaning |
|---|---|---|
| `break_id`, `account_id` | `str` | Minted by the book; the account. |
| `position` or `figure` | [`PositionKey`](#positionkey) or [`FigureKey`](#figurekey) | What it concerns. |
| `category`, `differences` | as on [`record_break`](#record_break) | |
| `book_watermark`, `street` | [`Watermark`](#watermark), [`StreetRecordRef`](#streetrecordref) | What was compared. |
| `first_seen_date`, `last_seen_date` | `str` | Business dates. Its age is derived from them, never stored. |
| `state` | [`BreakState`](#breakstate) | Open, resolved or closed. |
| `candidate_causes`, `confirmed_cause` | sequence of [`BreakCause`](#breakcause), `BreakCause` | What the matching found, and what a person confirmed. |
| `handling` | [`BreakHandling`](#breakhandling) | Its owner, escalation level and due date. |
| `resolution` | `BreakResolution` | How it ended: `entries` that resolved it, or the `explanation` it was closed with, or `cleared_at`, the statement where it cleared; with its `actor` and `reason`. |
| `recorded_by` | `Actor` | Who recorded it. |
| `last_change` | `JournalRef` | Where its last change sits. |

### `AgreementFigures` { #agreementfigures }

One agreement's figures to record, `meridian.AgreementFigures(...)`: `agreement`, a [`MarginAgreementRef`](#marginagreementref); `figures`, a [`StatementFigures`](#statementfigures) as the street recorded them, its segment the agreement's; and `position_values`, on the set with no segment only, each a `meridian.ReportedPositionValue` of `instrument_id`, `side`, and the custodian's `market_value` and `margin_requirement`, labelled as the custodian's and never a position's own. From 0.13.0.

### `AccountFigures` { #accountfigures }

The record: one per account, agreement and business date, with `account_id`, `business_date`, `agreement`, `figures`, `position_values`, `source` (the statement, a [`StreetRecordRef`](#streetrecordref)) and `last_change`. From 0.13.0.

### `AccountAttributes` { #accountattributes }

An account's attributes in the book. From 0.13.0.

| Field | Type | Meaning |
|---|---|---|
| `account_id` | `str` | The account. |
| `base_currency_code` | `str` | ISO 4217. |
| `lot_relief_default` | `LotReliefMethod` | What a sale relieves lots by when it names no method: `FIRST_IN_FIRST_OUT`, `LAST_IN_FIRST_OUT`, `HIGHEST_COST`, `LOWEST_COST` or `AVERAGE_COST`. |
| `last_change` | `JournalRef` | Where its last change sits. |
| `opening_balance` | `OpeningBalance`, unset while none stands | The standing opening balance: its `entry_id`, `as_of_date` (D0), `sources`, `recorded_by`, `journal` and the person's `reason`. |

### `Adjustment` { #adjustment }

An adjustment that resolves a break, `meridian.Adjustment(...)`. From 0.13.0.

| Field | Type | Meaning |
|---|---|---|
| `effective_date` | `str` | After the opening balance's date. |
| `lines` | sequence of `meridian.MovementLine` | Each an `instrument_id` and `side`, a `bucket` (`settled`, or `pending` with its `value_date`, which may be empty where the street gave none), a signed `quantity` added to the position, and the `lot_id` it adds to or relieves, or `opens_lot`, the [`LotTerms`](#lotterms) of a lot it opens, with its `cost` and `acquired_date` from contract v9. |
| `basis_adjustments` | sequence of `meridian.BasisAdjustment` | Each a `lot_id`, and one of `cost_change`, added to a known cost, or `stated_cost`, the cost of a lot a contract v8 book opened with its cost unknown, from contract v9 the only such lots; and `holding_period_start`, where it moves. |
| `event_reference` | `str` | A corporate action's reference, as reported, where it records one; from 0.19.0, the street's `activity_id` where the adjustment was proposed from the custodian's activity. |

### `Reversal` { #reversal }

`Reversal(entry_id=...)`: the entry it reverses, whose lines the book negates at that entry's effective date. From 0.13.0.

### `ResolvedByEntries` { #resolvedbyentries }

`ResolvedByEntries(entry_ids=[...])`: entries already recorded that resolve the breaks. From 0.13.0.

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
  rpc ResolveInstrument(ResolveInstrumentParams) returns (ResolveInstrumentResult);
  rpc RecordOpeningBalance(RecordOpeningBalanceParams) returns (RecordOpeningBalanceResult);
  rpc RecordBreak(RecordBreakParams) returns (RecordBreakResult);
  rpc RecordAccountFigures(RecordAccountFiguresParams) returns (RecordAccountFiguresResult);
  rpc RecordEncumbrances(RecordEncumbrancesParams) returns (RecordEncumbrancesResult);
  rpc HandleBreak(HandleBreakParams) returns (HandleBreakResult);
  rpc ResolveBreak(ResolveBreakParams) returns (ResolveBreakResult);
  rpc CloseBreaksAsCleared(CloseBreaksAsClearedParams) returns (CloseBreaksAsClearedResult);
  rpc ListPositions(ListPositionsParams) returns (ListPositionsResult);
  rpc ListBreaks(ListBreaksParams) returns (ListBreaksResult);
  rpc ListAccountFigures(ListAccountFiguresParams) returns (ListAccountFiguresResult);
  rpc ListAccountAttributes(ListAccountAttributesParams) returns (ListAccountAttributesResult);
  rpc Receive(ReceiveRequest) returns (stream Delivery);
}
```

Each `…Params` message keeps the field numbers of the domain message it stands for and drops the fields the sidecar stamps, so its encoding is the domain message's. `acting_for` is field 1000 on the eleven operations that take it, a `meridian.v1.CallerAssertion`. The SDK decodes it from the base64url `Meridian-Caller` header you pass. A number is a `Decimal` message, `high` and `low` halves of a 128-bit integer and a `scale` of 0 to 18, and an amount a `Money` message, a `Decimal` and a `currency_code`. `Identifier`, `MissReason` and the other types are plugin-facing mirrors of the domain types. `Receive`, from 0.12.0, is a stream: each item a `Delivery`, a row's message beside what is known of it, or a `Lost` where the sidecar dropped deliveries. The SDK's [`receive`](python-sdk.md#receive) reads it, and catches up from the store where it missed something.
