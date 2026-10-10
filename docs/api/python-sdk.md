# Python SDK

The Python SDK is how an Open Meridian plugin talks to the deployment. A plugin's whole contract with the platform is its **sidecar**, listening on loopback beside it, and the SDK is a client for that surface and nothing more. It never learns the bus's address, never holds a broker credential, and never discovers another plugin. Access control, stamping and the bus all live on the sidecar's side. Anything the SDK offers is a convenience, never a decision.

## Install

```sh
pip install open-meridian
```

| | |
|---|---|
| PyPI name | `open-meridian` |
| Import name | `meridian` |
| Version | 0.22.0 (built, not yet on PyPI; 0.21.0 is the latest released) |
| Python | 3.11 or newer |
| Dependencies | `grpcio>=1.68,<2`, `protobuf>=5.28,<7`, `jinja2>=3.1,<4` (from 0.10.0, for [pages](#pages)) |
| Licence | Apache-2.0 |

!!! warning "Not `meridian-sdk`"
    The PyPI package `meridian-sdk` belongs to an unrelated company. Don't install it.

A plugin pins the SDK exactly, `open-meridian==0.22.0`, in its `pyproject.toml`. The sidecar it runs beside speaks one version of the contract, and a version range would let a rebuild pick up another. Its `Dockerfile` builds on the base image for the same version, `ghcr.io/open-meridian/plugin-python:0.22.0`, so move the two together: [`meridian plugin migrate`](cli.md#plugin-migrate) moves both, and rewrites the plugin's code where a release changed what it calls; from 0.12.0 to 0.13.0, from 0.13.0 to 0.14.0, from 0.19.0 to 0.20.0, from 0.20.0 to 0.21.0 and from 0.21.0 to 0.22.0, only the pins move. `meridian plugin new` writes a plugin pinned to 0.19.0 from CLI 0.1.34, to 0.20.0 from CLI 0.1.35, to 0.21.0 from CLI 0.1.36, and to 0.22.0 from the release after it.

!!! note "0.22.0: built, not released"
    open-meridian 0.22.0 declares contract v18, [the lake](#the-lake): a
    `dgm`'s catalogue, prices and bars recorded in batches, wants, the
    readers, a `Money` naming its instrument and real dates. It is built and
    not yet on PyPI, and needs a runtime serving contract v18 (chart
    0.1.292, not yet released), which refuses nothing a plugin on 0.21.0
    sends. See [Plugin manifest](plugin-manifest.md).

| Optional extra | Installs | For |
|---|---|---|
| `migrate` | `libcst` | Running the SDK's own migrations, `python -m meridian.migrations`, which `meridian plugin migrate` does in an image of its own. A plugin never needs it. |

The package includes the wire bindings it speaks to the sidecar with, as `meridian.v1` and `meridian.plugin.v1`.

## Quick start

```python
import asyncio
import meridian


async def main() -> None:
    async with await meridian.connect(
        interface=meridian.Interface(port=8000, title="My plugin"),
    ) as plugin:
        print(plugin.identity.instance_id, plugin.identity.roles)
        print(plugin.grants.publish, plugin.grants.subscribe)
        await plugin.report(healthy=True, detail="started")
        await asyncio.Event().wait()  # run until stopped


asyncio.run(main())
```

A plugin that serves pages declares them with [`meridian.Pages`](#pages) and passes it as `Interface(pages=...)`. `meridian plugin new` writes a complete plugin built this way, with one page under Manage and one under Open and View. See [Your first plugin](../getting-started/first-plugin.md).

## What the package exports

`meridian.__all__`:

| Name | Kind | Described in |
|---|---|---|
| `connect` | async function | [`meridian.connect`](#connect) |
| `Plugin` | class | [`Plugin`](#plugin) |
| `Identity`, `Grants`, `Interface`, `Page`, `Setting`, `Choice`, `AppliesWhen`, `Settings`, `AccountScope`, `LinkedExternalAccount`, `Caller` | frozen dataclasses | [Types](#types) |
| `Column` | frozen dataclass | [`Column`](#column), from 0.19.0 |
| `Pages`, `Request`, `Response` | class, frozen dataclasses | [Pages](#pages) |
| `AccessLevel` | generated protobuf enum | [`AccessLevel`](#accesslevel) |
| `Money` | frozen dataclass | [Typed operations](typed-operations.md#money); its `instrument_id` from 0.22.0 |
| `StatementFigures`, `ReportedCollateral`, `ReportedLot` | frozen dataclasses | [Typed operations](typed-operations.md#statementfigures), from 0.12.0 |
| `ReportedEncumbrance` | frozen dataclass | [Typed operations](typed-operations.md#reportedencumbrance), from 0.13.0 |
| `OpeningSource`, `OpeningPosition`, `OpeningLot`, `PendingSettlement`, `LotTerms`, `PositionKey`, `BreakDifference`, `BreakValue`, `BreakCause`, `PendingSettlementRef`, `AgreementFigures`, `ReportedPositionValue`, `PositionEncumbrances`, `Encumbrance`, `Adjustment`, `MovementLine`, `BasisAdjustment` | frozen dataclasses | [Typed operations](typed-operations.md#types), the book's, from 0.13.0 |
| `BreakCategory`, `BreakCauseCategory`, `BreakState`, `LotReliefMethod`, `LotSource`, `OpeningSourceKind`, `PositionBasis`, `SettlementBucket`, `BreakHandling`, `FigureKey`, `MarginAgreementRef`, `PendingState`, `ResolvedByEntries`, `Reversal`, `StatementSegmentRef`, `StreetRecordRef` | generated protobuf enums and messages | [Typed operations](typed-operations.md#types), the book's, from 0.13.0 |
| `as_decimal`, `as_money` | functions | [Typed operations](typed-operations.md#numbers-and-amounts) |
| `Identifier`, `MissReason` | generated protobuf message and enum | [Types](#types) |
| `Figure`, `FigureState` | frozen dataclass, generated protobuf enum | [Figures](#figures) |
| `AssetClass`, `CollateralDirection`, `ExternalAccount`, `HoldingSide`, `SyncState` | generated protobuf enums and message | [Typed operations](typed-operations.md#types); `CollateralDirection` from 0.12.0 |
| `Heard` | frozen dataclass | [Receive](#receive), from 0.12.0 |
| `TicketKind`, `TicketState`, `TicketResolution`, `TicketSubject`, `TicketReference` | generated protobuf enums, `StrEnum`, frozen dataclass | [`file_ticket()`](#file_ticket), from 0.18.0 |
| `CustodialActivity` | frozen dataclass | [Typed operations](typed-operations.md#custodialactivity), from 0.19.0 |
| `Storage`, `RecordKind` | frozen dataclasses | [The archive](#the-archive); `RecordKind` from 0.21.0 |
| `StoredSpan`, `MoveOutcome` | generated protobuf message and enum | [The archive](#the-archive), from 0.21.0 |
| `ActivityKind`, `ActivityRef` | generated protobuf enum and message | [Typed operations](typed-operations.md#activitykind), from 0.19.0 |
| `DatasetDeclaration`, `DatasetLicence` | frozen dataclasses | [A dgm's catalogue](#a-dgms-catalogue), from 0.22.0 |
| `Price`, `Bar`, `ObservationMeta`, `SourceTime` | frozen dataclasses | [Typed operations](typed-operations.md#price), from 0.22.0 |
| `ObservationMode`, `PriceKind`, `PriceBasis`, `SourceTimeKind`, `UnansweredReason`, `VenueKind`, `Source`, `SourceChoice`, `SubjectRef`, `DatasetRef`, `Unanswered`, `VenueRecord` | generated protobuf enums and messages | [Typed operations](typed-operations.md#types), the lake's, from 0.22.0 |
| `CallerMiddleware` | ASGI middleware | [`CallerMiddleware`](#callermiddleware) |
| `MeridianError`, `Refused`, `NoSidecar`, `NotRegistered`, `NotGranted`, `CallFailed`, `NotLinked`, `CommandRefused` | exceptions | [Exceptions](#exceptions); `CommandRefused` from 0.13.0, its `fields` from 0.14.0 |
| `DEFAULT_ADDRESS` | `str` | `"127.0.0.1:9191"`, where a sidecar listens |
| `SCHEMA_VERSION` | `str` | the contract version sent at registration: `"v18"` from 0.22.0 (no SDK declares v17, a revision of core's alone), `"v16"` in 0.21.0, `"v15"` in 0.20.0, `"v14"` in 0.19.0, `"v13"` in 0.18.0, `"v12"` in 0.17.0, `"v11"` in 0.16.0, `"v10"` in 0.15.0, `"v9"` in 0.14.0, `"v8"` in 0.13.0, `"v7"` in 0.12.0, `"v6"` in 0.11.0, `"v5"` in 0.10.0 and 0.10.1, `"v4"` in 0.9.0, `"v3"` in 0.8.0, `"v2"` before |

The module `meridian.testing` holds [`PageClient`](#testing) and [`heartbeat`](#testing), for a plugin's own tests.

## `meridian.connect` { #connect }

```python
async def connect(
    address: str | None = None,
    *,
    heartbeat: bool = True,
    wait: float = 60.0,
    interface: Interface | None = None,
    settings: Sequence[Setting] = (),
    reads_external_accounts: bool = False,
    declaration: Declaration | None = None,
) -> Plugin
```

Registers with the sidecar and returns the admitted plugin. A `Plugin` you hold is always one the sidecar admitted.

| Parameter | Type | Default | Meaning |
|---|---|---|---|
| `address` | `str` or `None` | `None` | The sidecar's address. When `None`, the value of `MERIDIAN_SIDECAR_ADDRESS`, then `127.0.0.1:9191`. No other configuration is read. |
| `heartbeat` | `bool` | `True` | Send a liveness heartbeat to the sidecar every 5 seconds in the background, carrying the health last reported and the plugin's [figures](#figures). |
| `wait` | `float` | `60.0` | Seconds to wait for a sidecar that is not answering yet. A plugin and its sidecar start together in one pod, in no promised order. |
| `interface` | `Interface` or `None` | `None` | The pages the plugin serves on loopback, if any. |
| `settings` | sequence of `Setting` | `()` | The settings the plugin needs an admin of it to give it, on the dashboard's Settings form, or a table on its own tab beside it. A plugin sets none of them itself. |
| `reads_external_accounts` | `bool` | `False` | `True` when the plugin reads accounts at an external source and names them by that source's identifiers. An admin of the plugin links those to accounts, and the sidecar translates them on the way in. |
| `declaration` | `Declaration` or `None` | `None` | The version's declaration, the same one `meridian plugin upload` reads from the image: its secret settings' names, what it does not carry and the storage it asks for. See [Keep what your custody plugin converts](../how-to/keep-what-the-edge-converts.md). From 0.21.0, where its storage declares kinds of raw record, `connect` declares each kind's two window settings and the restore route besides; see [The archive](#the-archive). From 0.22.0, a `dgm`'s catalogue; see [A dgm's catalogue](#a-dgms-catalogue). |

The contract version it sends is `SCHEMA_VERSION`, `"v18"` from 0.22.0, `"v16"` in 0.21.0. A sidecar accepts a range of versions, v2 through the one its runtime serves, v18 at contract v18: a plugin built for an older version it still supports registers, and one built for a newer version than the sidecar knows is refused at registration, naming both, rather than running without what it was built for. After an upgrade, relaunch plugins so they get the newer sidecar (`meridian upgrade-deployment` names the ones that need it).

**Raises:**

| Exception | When |
|---|---|
| `NoSidecar` | No sidecar answered within `wait` seconds. |
| `Refused` | The sidecar answered and declined to admit the plugin. Its `reason` says why. Not retried. From contract v15 it refuses a page or setting naming a role the plugin was not launched with, and, on a plugin holding several roles, one naming none, naming it and the plugin's roles. |
| `TypeError` | A `Setting`'s `kind` is not `str`, `int`, `bool` or `list`; it has `choices` and a `kind` other than `str`; its `default` is not of its `kind`; or its `kind` is `list` without `columns`, or another kind with them. |
| `ValueError` | A secret `Setting` declares a `default`; a `default` is not one of its `choices`; a table is secret, or declares a `default` or `choices`, names a column twice, or has `most_rows` outside 0 to 500; a `Column`'s `kind` is not one of the seven, it is named `changed_by` or `changed_at`, or it is a choice without `choices`; or a `Page`'s path does not begin with `/`, or it names no level. From 0.20.0, when the declaration is made: a `roles=` naming something no role could be (a role is lower-case letters, such as `custody`), or more than 13 roles. |
| `grpc.aio.AioRpcError` | Any other gRPC failure during registration, unchanged. |

When run by the development runner on a development deployment, `connect` also records the `ready` event once the plugin is admitted. See [`plugin dev` events](plugin-dev-events.md).

## `Plugin` { #plugin }

Built by `connect`. It is an async context manager: leaving the `async with` block calls `leave()`, with the reason `"stopping"`, or the exception's class name if the block raised.

### Attributes

| Attribute | Type | Meaning |
|---|---|---|
| `identity` | `Identity` | Who the plugin was launched to be: instance, roles, deployment. Read from the registration reply, never sent by the plugin. |
| `grants` | `Grants` | What the deployment allowed, as the topic patterns it allowed them as. |
| `figures` | sequence of `Figure` | The figures the plugin reports on its Summary, as last set. Set it to report a new list. From 0.11.0; see [Figures](#figures). |
| `stored` | sequence of `StoredSpan` | What the plugin's storage holds of each kind of raw record it declared, as last set, on every heartbeat from the next on. From 0.21.0; see [What is stored](#what-is-stored). |

`grants` is for failing early with a good message, at startup, rather than at the first refused operation. The sidecar refuses independently of what the plugin believes, and the SDK offers no "is this allowed" check.

### Methods

| Method | Returns | Meaning |
|---|---|---|
| `settings()` | `AsyncIterator[Settings]` | The settings the plugin declared, now and again on every change. |
| `account_scope()` | `AsyncIterator[AccountScope]` | Every account anybody may read or write through this plugin, and the plugin's own links, now and again on every change. |
| `access()` | `Awaitable[PluginAccessReply]` | Who may use this plugin. |
| `file_ticket(*, title, kind, idempotency_key, for_caller, ...)` | `Awaitable[FileTicketReply]` | File a ticket for the person whose request the plugin is serving. From 0.18.0; see [`file_ticket()`](#file_ticket). |
| `filed_tickets(*, for_caller, ticket_ids=(), idempotency_keys=(), cursor="")` | `Awaitable[ReadFiledTicketsReply]` | What became of the tickets the plugin filed. From 0.18.0; see [`filed_tickets()`](#filed_tickets). |
| `archive_unit(record_kind, unit, *, record_count, first_received_ns, last_received_ns)` | `Awaitable[None]` | Move a unit past its window to the archive. From 0.21.0; see [The archive](#archive_unit). |
| `restore_unit(record_kind, unit, *, for_caller)` | `Awaitable[Path]` | Restore an archived unit for a person, answering where it is readable. From 0.21.0; see [The archive](#restore_unit). |
| `delete_unit(record_kind, unit, *, record_count=0, first_received_ns=0, last_received_ns=0, for_caller=None)` | `Awaitable[None]` | Delete a unit, the deletion reported first. From 0.21.0; see [The archive](#delete_unit). |
| `find_record(key)` | `RecordMoveRequest` or `None` | Where a raw record's key stands: the last move of the unit holding it. From 0.21.0; see [The archive](#find_record). |
| `report(*, healthy, detail="", figures=None)` | `Awaitable[None]` | Report the plugin's health now, outside the heartbeat. It stands until reported again. |
| `leave(reason="")` | `Awaitable[None]` | Say the plugin is stopping, and close the connection. |
| `receive(*, statement_recorded=None, custodial_position_updated=None, position_changed=None, break_changed=None, account_figures_recorded=None, account_attribute_changed=None, activity_recorded=None, sync_status_recorded=None, activity_re_resolved=None, seed=True)` | `Awaitable[None]` | Hear the rows the plugin's roles hear, a handler per row, until cancelled. From 0.12.0, the book's rows from 0.13.0, the custodian's activity and each sync status from 0.19.0, an activity re-resolved from 0.20.0; see [Receive](#receive). |
| Typed operations | see [Typed operations](typed-operations.md) | `report_external_accounts`, `report_sync_status`, `record_holdings_statement`, `record_holding`, `list_custodial_positions`, `list_statements`, `resolve_identifier`, `report_missing_instrument`, `read_accounts_for_linking`, `link_external_account`; from 0.13.0, `resolve_instrument` and the book's `record_opening_balance`, `record_break`, `record_account_figures`, `record_encumbrances`, `handle_break`, `resolve_break`, `close_breaks_as_cleared`, `list_positions`, `list_breaks`, `list_account_figures` and `list_account_attributes`; from 0.19.0, `record_activity`, `list_activities` and `list_sync_statuses`; from 0.20.0, `re_resolve_activity`. |

Every method raises `NotRegistered` once the plugin has left.

#### `settings()`

```python
async def settings(self) -> AsyncIterator[Settings]
```

Yields the plugin's settings as the deployment holds them, typed by what it declared at `connect`, first as they are now and then on every change. Values for names the plugin did not declare are left out. A setting that declares a `default` and has no value holds its default, so the plugin uses what the form showed. A value that does not parse as its declared kind raises `ValueError` rather than being guessed at. A boolean accepts `true`, `yes`, `1`, `on`, `false`, `no`, `0` and `off`, in any case.

An admin of the plugin sets its settings on the dashboard's Settings form, and each table on its own tab beside it, the only places a setting is set, and the deployment records each change, naming who made it. The plugin only reads them: the SDK has no call that sets a setting, and the deployment refuses an update a plugin sends. See [Set a plugin's settings](../how-to/set-a-plugins-settings.md).

```python
async for current in plugin.settings():
    if current.missing_required:
        log.warning("waiting for %s", ", ".join(current.missing_required))
        continue
    token = current.values["api_token"]
```

While a required setting has no value, the sidecar reports the plugin unhealthy and names the setting.

A [table setting](#column), from 0.19.0, arrives as a list of rows, each a `dict` of its cells as text by column name, with `changed_by`, the person who added or last changed the row, and `changed_at`, when, in RFC 3339 UTC. The deployment stamps both when it stores the table; a row left as it was keeps its own. A value that is not a table's rows raises `ValueError`.

```python
async for current in plugin.settings():
    for row in current.values.get("plan_code_links", []):
        row["code"], row["instrument"], row["changed_by"], row["changed_at"]
```

#### `account_scope()`

```python
async def account_scope(self) -> AsyncIterator[AccountScope]
```

Yields the plugin's account scope, now and again on every change. The scope is derived from permissions and from the plugin's links to accounts, and never declared: see [Accounts](../concepts/accounts.md#how-accounts-bound-a-plugin). A plugin reads its whole read scope as itself and serves each person only what their access allows. The sidecar refuses a write outside `write`, whoever it is for.

Beside the scope come the plugin's own **links**: which of its external accounts an admin has linked, to which account, and that account's name as the deployment holds it now. They are read as the plugin itself, for nobody. The first delivery comes at once, so a plugin that has just started has every link. Another comes whenever a permission changes, a link is made or removed, or a linked account is renamed or closed. Hold the latest one: a plugin keeps nothing of its own across a restart.

```python
async for scope in plugin.account_scope():
    for link in scope.links:
        print(link.external_account_id, "->", link.account_id, link.account_name)
    if scope.link_of("acct-3") is None:
        ...  # not linked: a row for it raises NotLinked
```

#### `access()`

```python
async def access(self) -> meridian.v1.sidecar_pb2.PluginAccessReply
```

Returns who may use this plugin: each user group naming it, and each person who has signed in to the deployment, with their access. It is for shaping an interface; nothing here is an access decision. The reply is the generated protobuf message:

| Field | Type | Meaning |
|---|---|---|
| `user_groups` | repeated `UserGroupAccess` | `user_group_id`, `name`, `read_account_ids` and `write_account_ids`; from contract v15, `roles`. |
| `people` | repeated `PersonAccess` | `subject`, `display_name`, `user_group_ids`, `last_signed_in_at_ns`, `read_account_ids` and `write_account_ids`; from contract v15, `roles`. Only people who have signed in are listed: the deployment holds no directory. |

The account sets are this plugin's: what the group or person may read through it, and write through it. Every write account is also listed as read.

From contract v15 each also carries `roles`, a `RoleAccess` for each of the plugin's roles the group or person holds a data level on: `role`, `level` (`read` or `write`, never `admin`, since the table lists data access only), and `read_positions` and `write_positions`, the role's accounts as positions in that same message's `read_account_ids`. The two sets above stay the union over the roles.

#### `file_ticket()` { #file_ticket }

```python
async def file_ticket(
    self,
    *,
    title: str,
    kind: str | int,
    idempotency_key: str,
    for_caller: Caller | str,
    seen: str = "",
    concerns: TicketSubject | str = TicketSubject.PLUGIN,
    step: str = "",
    operation: str = "",
    reason: str = "",
    paths: Sequence[str] = (),
    references: Sequence[TicketReference] = (),
) -> meridian.v1.sidecar_pb2.FileTicketReply
```

From 0.18.0, with a runtime serving contract v13. Files a
[ticket](../concepts/tickets-and-the-inbox.md) for the person whose request the
plugin is serving: a problem they met that the plugin cannot handle, for
someone in the deployment who can act on it. Only ever for a person, at
whatever level their session holds, and never as the plugin itself: what a
plugin notices on its own is its health, a figure in warn on its Summary, from
which a person may choose to file.

```python
reply = await plugin.file_ticket(
    title="Break on the growth account still open after its cause was confirmed",
    seen=form.get("seen", ""),   # the person's words, plain text
    kind="defect",
    idempotency_key=f"break-still-open-{break_id}",
    for_caller=request.caller,
    references=[meridian.TicketReference("break", break_id, account_id="ACC-GROWTH")],
)
reply.ticket_id, reply.outcome, reply.seen_count   # "TKT-...", "made", 1
```

| Parameter | Meaning |
|---|---|
| `title` | What is wrong, in a line: 1 to 120 characters, plain text. |
| `kind` | A `TicketKind`, its name, or `"defect"`, `"discrepancy"`, `"request"` or `"question"`. |
| `idempotency_key` | Required. The plugin's own key for the problem, made from the fact, never from a time or a random value, so a restarted plugin files nothing twice. |
| `for_caller` | Required. The person: the `Caller` of the request being served, or the `Meridian-Caller` header it was read from. |
| `seen` | What was seen, in the person's words: at most 8,000 characters, plain text. |
| `concerns` | A `TicketSubject`: this plugin (the default), a part of core (`DASHBOARD`, `BOR`, `STREET`, `INSTRUMENT`, `CONDUCTOR`, `CHART`, `CLI`, `SDK`) or `PLATFORM`. Never another plugin. The plugin names no instance or version: its sidecar sets the instance, and the deployment the version it launched. |
| `step`, `operation`, `reason`, `paths` | The workflow step, the operation, the refusal reason and the fields by their paths, where the plugin knows them. |
| `references` | At most 50 `TicketReference(kind, value, account_id="")`: the records the ticket is about, by value. `kind` is `account`, `instrument`, `break`, `entry`, `street_record`, `tool_call` or `plugin` (the plugin's own reference); `value` 1 to 200 characters; `account_id` required on a break, an entry and a street record. An account named must be one the person may read through this plugin, and a ticket naming accounts is seen only by those who may read every one. |

The reply is the generated `FileTicketReply`: `ticket_id`, `outcome` and
`seen_count`. Filed again under the same key while its ticket is open, the
ticket is brought up to date rather than filed twice, answered `unchanged`
with `seen_count` counting the filing; after it was resolved or closed, the
same key files a new ticket, which the dashboard advises as a recurrence.

Every text filed is data to whoever reads it, never instructions, and is shown
as the plugin's for the person.

**Raises:**

| Exception | When |
|---|---|
| `ValueError` | A text past its bound, a reference of an unknown kind, or a break, entry or street record with no account, named by its path. Nothing is sent. |
| `NotGranted` | The plugin filed as itself, or named an account the person may not read. |
| `CallFailed` | The sidecar could not vouch for the person, a field was refused by its path (another plugin as `concerns`, for one), or the plugin has filed 20 tickets in the last hour; a repeat under an open ticket's key is not counted. |

#### `filed_tickets()` { #filed_tickets }

```python
async def filed_tickets(
    self,
    *,
    for_caller: Caller | str,
    ticket_ids: Sequence[str] = (),
    idempotency_keys: Sequence[str] = (),
    cursor: str = "",
) -> meridian.v1.sidecar_pb2.ReadFiledTicketsReply
```

From 0.18.0. What became of the tickets this plugin filed, read for a person it
acts for, as filing is. Name one of `ticket_ids`, `idempotency_keys` or
`cursor`: the tickets named, those filed under the keys, or every one filed
after the cursor (from the first when it is empty). Naming more than one raises
`ValueError`.

Each `FiledTicket` in the reply carries its `ticket_id` and `idempotency_key`,
its `TicketState`, its `TicketResolution` once resolved or closed, how often it
was seen and when first and last; never people's notes, nor who owns or works
it. `next_cursor` is empty when nothing follows. A plugin that sees its ticket
resolved can stop filing it.

#### `report()`

```python
async def report(self, *, healthy: bool, detail: str = "", figures: Sequence[Figure] | None = None) -> None
```

Reports the plugin's health straight away. Ordinary liveness is already handled by the heartbeat. This is for a plugin that knows it is unwell and should say so.

From 0.11.0 the health reported stands, with its `detail`, on every heartbeat after, until the plugin reports again: `report(healthy=False, detail="...")` keeps it not healthy until `report(healthy=True)`. Up to 0.10.1 the next heartbeat said healthy again.

It carries the plugin's [figures](#figures) as they stand. `figures`, from 0.11.0, sets them first, as setting `plugin.figures` does, and sends them now. Figures refused raise as setting them does, leave the health as it was, and send nothing.

#### `leave()`

```python
async def leave(self, reason: str = "") -> None
```

Stops the heartbeat, tells the sidecar the plugin is stopping, and closes the channel. It does nothing when called a second time. A sidecar that is already gone is ignored. Saying so is what tells a planned stop apart from a failure. A crash skips it, which is why it is optional.

## Receive { #receive }

From 0.12.0. A plugin whose roles hear rows receives them with `plugin.receive`, a handler per row. The street store's rows are heard by the `operations` role, the custodian's activity and each sync status among them from 0.19.0, and an activity re-resolved from 0.20.0; from 0.13.0, the book of record's are heard by the roles that read the book:

| Handler | Row | `heard.message` | Workflow step |
|---|---|---|---|
| `statement_recorded` | `StatementRecorded` | A `StatementRecordedEvent`: a completed statement, with its account, external account and institution, its counts and its figures per margin segment, as the street store announced it. The same message [`list_statements`](typed-operations.md#list_statements) reads. | W2.5 |
| `custodial_position_updated` | `CustodialPositionUpdated` | A `CustodialPositionUpdatedEvent`: the position's whole new state in `position`, `removed` set when it was removed, the statement that changed it, and its previous quantity. | W2.6 |
| `position_changed` | `PositionChanged` | A `PositionChangedEvent`: the book's position whole in `position`, a [`BookPosition`](typed-operations.md#bookposition) with its lots, pending settlements and encumbrances, `removed` set when it was moved off a placeholder; its `previous_trade_date_quantity`; and the `entry` that changed it. Heard by `portfolio`, `reporting`, `compliance`, `oms` and `operations`. From 0.13.0. | W9.8 |
| `break_changed` | `BreakChanged` | A `BreakChangedEvent`: the [`Break`](typed-operations.md#break) whole in `break_record`, and the `entry`. Heard by `operations`, `oms`, `compliance`, `portfolio` and `reporting`. From 0.13.0. | W9.8 |
| `account_figures_recorded` | `AccountFiguresRecorded` | An `AccountFiguresRecordedEvent`: one agreement's [`AccountFigures`](typed-operations.md#accountfigures) in `figures`, and the `entry`. Heard by `operations`, `portfolio`, `compliance` and `reporting`. From 0.13.0. | W9.8 |
| `account_attribute_changed` | `AccountAttributeChanged` | An `AccountAttributeChangedEvent`: the account's [`AccountAttributes`](typed-operations.md#accountattributes) in `attributes`, its standing opening balance among them, and the `entry`. Heard by `portfolio`, `reporting`, `compliance`, `oms` and `operations`. From 0.13.0. | W9.8 |
| `activity_recorded` | `ActivityRecorded` | An [`ActivityRecordedEvent`](typed-operations.md#activityrecordedevent): an activity on the account as the custodian stated it, recorded once. The same message [`list_activities`](typed-operations.md#list_activities) reads, so a break waiting on its cause can be compared again. From 0.19.0, `preview`. | W2.12 |
| `sync_status_recorded` | `SyncStatusRecorded` | A [`SyncStatusRecordedEvent`](typed-operations.md#syncstatusrecordedevent): a sync status the street kept, so "needs sign-in" is told apart from merely old. The same message [`list_sync_statuses`](typed-operations.md#list_sync_statuses) reads. From 0.19.0, `preview`. | W2.13 |
| `activity_re_resolved` | `ActivityReResolved` | An [`ActivityReResolvedEvent`](typed-operations.md#activityreresolvedevent): an activity recorded before its instrument resolved, re-resolved, its re-resolution kept beside it. Caught up from the `re_resolutions` of [`list_activities`](typed-operations.md#list_activities). From 0.20.0, `preview`. | W2.16 |
| `prices_recorded` | `PricesRecorded` | A `PricesRecordedEvent`: one [`Price`](typed-operations.md#price) the lake recorded, in `price`, for a subject named in `subjects=`. Heard by `reporting`, `portfolio`, `compliance` and `signal`, from a dataset the plugin is entitled to. Caught up by [`list_prices`](typed-operations.md#list_prices). From 0.22.0, `preview`. | W10.5 |
| `bars_recorded` | `BarsRecorded` | A `BarsRecordedEvent`: one [`Bar`](typed-operations.md#bar), in `bar`, likewise. Caught up by [`list_bars`](typed-operations.md#list_bars). From 0.22.0, `preview`. | W10.5 |
| `observations_wanted` | `ObservationsWanted` | An `ObservationsWantedEvent`, heard by the `dgm` serving its dataset alone: `want_id`, `dataset`, `data_type`, `subjects`, `kinds`, `interval_ns`, the `business_date` or valid range wanted, and `standing`. See [Wants](#wants). From 0.22.0, `preview`. | W10.7 |
| `want_withdrawn` | `WantWithdrawn` | A `WantWithdrawnEvent`, `want_id` and `dataset`: a standing want no reader asked for within its dataset's cadence. From 0.22.0, `preview`. | W10.7 |

```python
async def receive(
    self, *,
    statement_recorded: Callable[[Heard[StatementRecordedEvent]], Awaitable[None]] | None = None,
    custodial_position_updated: Callable[[Heard[CustodialPositionUpdatedEvent]], Awaitable[None]] | None = None,
    position_changed: Callable[[Heard[PositionChangedEvent]], Awaitable[None]] | None = None,
    break_changed: Callable[[Heard[BreakChangedEvent]], Awaitable[None]] | None = None,
    account_figures_recorded: Callable[[Heard[AccountFiguresRecordedEvent]], Awaitable[None]] | None = None,
    account_attribute_changed: Callable[[Heard[AccountAttributeChangedEvent]], Awaitable[None]] | None = None,
    activity_recorded: Callable[[Heard[ActivityRecordedEvent]], Awaitable[None]] | None = None,
    sync_status_recorded: Callable[[Heard[SyncStatusRecordedEvent]], Awaitable[None]] | None = None,
    activity_re_resolved: Callable[[Heard[ActivityReResolvedEvent]], Awaitable[None]] | None = None,
    prices_recorded: Callable[[Heard[PricesRecordedEvent]], Awaitable[None]] | None = None,
    bars_recorded: Callable[[Heard[BarsRecordedEvent]], Awaitable[None]] | None = None,
    observations_wanted: Callable[[Heard[ObservationsWantedEvent]], Awaitable[None]] | None = None,
    want_withdrawn: Callable[[Heard[WantWithdrawnEvent]], Awaitable[None]] | None = None,
    seed: bool = True,
    subjects: Sequence[str] = (),
) -> None
```

```python
import meridian


async def statement_recorded(heard: meridian.Heard) -> None:
    statement = heard.message  # the whole statement, as the store announced it
    ...


async def custodial_position_updated(heard: meridian.Heard) -> None:
    position = heard.message.position  # removed=True when it was removed
    ...


await plugin.receive(
    statement_recorded=statement_recorded,
    custodial_position_updated=custodial_position_updated,
)
```

It runs until cancelled, so give it a task of its own beside the pages. It hears only the rows given a handler.

- **Seeded.** It reads the store first, every row's records across the plugin's read scope, and hands each on, marked `caught_up`. With `seed=False` it reads the store without handing on what it holds, and hands on only what changes after.
- **Once and in order.** Then it hands on each change heard, once, and in order for each account.
- **Caught up.** Deliveries are at most once: the sidecar queues at most 1024 for the plugin and drops past that, and marks each drop in the stream as a `Lost`. Where one was missed (a gap in an account's changes, a `Lost`, a stream that broke, or an account entering the read scope), it reads the changes since from the store and hands them on before anything heard after, each marked `caught_up`. A stream that broke is opened again, half a second later and doubling to 15 seconds. An account leaving the read scope is heard of no more.

A plugin catches up from the store, never from the bus, and the SDK does it: a handler never sees the store's numbers, and keeps nothing to catch up with. A change carries its whole new state, so one handed on twice changes nothing a handler keeps; where reading a page at a time cannot say exactly where the store was, a change may be handed on twice rather than never.

**The lake's rows, from 0.22.0.** A price or a bar is heard only for the subjects named in `subjects=`, by their instrument IDs, at most 500, and none without them, from the datasets the plugin is entitled to. Each is delivered latest value first: the sidecar keeps one value waiting per key (a price's dataset, subjects, venue and kind; a bar's dataset, subjects, venue and interval start), a later value replacing one not yet delivered, and the SDK hands on the newest per key, never an older value after a newer one. On start, after a `Lost` and after a broken stream it reads them again by `list_prices` or `list_bars`, latest first and side by side, marked `caught_up`. Each carries its dataset in [`Heard.dataset`](#heard). A plugin built before 0.22.0, naming no `subjects`, is unchanged.

Everything heard is within the plugin's read scope, as the [reads](typed-operations.md#list_custodial_positions) are, and a plugin whose read scope is empty hears nothing. It reads and hears for its whole scope, as itself: serve each person from it with `caller.read`, as always.

### `Heard` { #heard }

```python
@dataclass(frozen=True)
class Heard(Generic[Message]):
    row: str
    message: Message
    caught_up: bool = False
    own: bool = False
    cause: ChangeCause | None = None
    message_id: str = ""
    correlation_id: str = ""
    causation_id: str = ""
    published_at_ns: int = 0
    dataset: DatasetRef | None = None
```

| Field | Meaning |
|---|---|
| `row` | The row, such as `"CustodialPositionUpdated"`. |
| `message` | The row's message, from `meridian.plugin.v1.operations_pb2`, with the store's numbers taken off. |
| `caught_up` | `True` when it was read from the store rather than heard: when the plugin started, after a gap or a `Lost`, after the stream broke, or when an account entered its read scope. |
| `own` | `True` when the plugin's own act caused it. |
| `cause` | Who caused it, where the store recorded it, a `ChangeCause`: `instance_id`, the instance that sent the command; `acting_for_subject`, the person it was sent for, empty when the plugin acted as itself; `correlation_id`; `causation_id`, the command's `message_id`; and `committed_at_ns`. |
| `message_id`, `correlation_id`, `causation_id`, `published_at_ns` | From the envelope it was heard in. Empty, and `0`, for what was read. |
| `dataset` | From 0.22.0, for a price or a bar: the dataset it came from, a [`DatasetRef`](typed-operations.md#datasetref) with its instance, vendor, aggregator and catalogue entry, as `list_datasets` answers it, which the lake names once rather than on every row. `None` for any other row, and where the plugin may not list the datasets. |

**Raises:** `ValueError` when no handler is given. [`NotGranted`](#exceptions) for a row none of the plugin's roles hears. A read to catch up that finds nothing serving it, has no answer in time, or is refused by what serves it is tried again with the stream; any other refusal raises as the read's own would.

## Figures { #figures }

From 0.11.0. Manage opens on the plugin's **Summary**, which core draws: its status first (its health and why, the version running and the contract it registered with), then a few figures the plugin reports about its own work, each a tile. A plugin gives them on its heartbeat and builds no summary page of its own. See [Manage, Open and View](../concepts/plugins.md#manage-open-and-view).

```python
from datetime import datetime, timezone
import meridian

plugin.figures = [
    meridian.Figure("Connections", 3, state="warn",
                    why="1 connection needs attention: the brokerage asked to reconnect"),
    meridian.Figure("Accounts reached", 7),
    meridian.Figure("Last read", datetime.now(timezone.utc)),
]
```

The list goes on every heartbeat from the next on, in its order, each heartbeat replacing the last; an empty list clears it. `await plugin.report(healthy=True, figures=[...])` sends it at once. A figure is about the plugin's own work: it names no account and carries none of an account's data, since Manage shows none. Report figures only where the plugin has work worth counting.

### `Figure`

```python
@dataclass(frozen=True)
class Figure:
    label: str
    value: int | Decimal | str | datetime
    as_of: datetime | None = None
    state: str | int | None = None
    why: str | None = None
```

| Field | Meaning |
|---|---|
| `label` | As a person reads it, `"Connections"`. 1 to 40 characters, and given once in the list. |
| `value` | What kind of figure it is: an `int` is a count, a `Decimal` a decimal, a `str` a text, at most 40 characters, and a timezone-aware `datetime` a time, such as `"Last read"`. Always given. |
| `as_of` | When the value was true, where that is not the heartbeat's moment. A timezone-aware `datetime`. |
| `state` | The tile's mark: `"ok"`, `"warn"` or `"error"`, or a `meridian.FigureState`. `None` is no state, drawn plain. |
| `why` | The note beside the tile. At most 200 characters. |

A decimal is carried exactly, as [typed operations](typed-operations.md#numbers-and-amounts) carry one: at most 18 decimal places and 38 digits, refused rather than rounded. Core writes a time as the dashboard writes every moment.

### Bounds

At most 8 figures; a label of 1 to 40 characters, given once; a text of at most 40; a why of at most 200; a state of ok, warn or error; a value always given; a decimal within what the wire carries. Anything past a bound is refused, never cut, at the line that sets the list, in the words the sidecar would refuse it with, and nothing is set: the last list stands.

| Raises | When |
|---|---|
| `ValueError` | A bound is broken, for example `9 figures; a plugin reports at most 8`, `figures[0].label is 44 characters; a label is at most 40`, or `figures[0].state is 'amber', which the contract does not define`. |
| `TypeError` | A value is none of a figure's kinds, a `datetime` has no timezone, or one `Figure` is given where a list is. |

The sidecar checks them again. A heartbeat it refuses still says the plugin is alive; the plugin is then reported not healthy, the refusal as its why, with no figures. Core draws no figures for a plugin that is not registered or has fallen silent, since they would be stale; its status says why.

In a plugin's tests, [`meridian.testing.heartbeat`](#testing) is the heartbeat its sidecar receives, or the refusal.

## The archive { #the-archive }

From 0.21.0, contract v16. A plugin holding an edge role declares the kinds of raw record it keeps; past each kind's window it archives, keeps or deletes them, as its admin chose, in units it can find again; and it reports every move through its sidecar before it removes anything. What that means for the people using it is in [The archive](../concepts/the-archive.md). Each field on the wire is in the data dictionary: [`RawRecordKind`](../boundaries/sidecar.md#meridian.v1.RawRecordKind), [`StoredSpan`](../boundaries/sidecar.md#meridian.v1.StoredSpan) and [`RecordMoveRequest`](../boundaries/sidecar.md#meridian.v1.RecordMoveRequest).

```python
import meridian
from meridian.declaration import Declaration, RecordKind, Storage

DECLARATION = Declaration(
    settings=SETTINGS,
    storage=Storage(kinds=[
        RecordKind("activity", "Reported activity", window_days=2555),
        RecordKind("responses", "Raw responses", window_days=30),
        RecordKind("session", "Session state", window_days=7, archivable=False),
    ]),
)

async with await meridian.connect(declaration=DECLARATION, interface=INTERFACE) as plugin:
    async for settings in plugin.settings():
        window = settings.values["activity_window_days"]   # days, the admin's
        past = settings.values["activity_past_window"]     # archived, kept or deleted
        for unit, count, first, last in units_past(window):  # the plugin's own units
            if past == "archived":
                await plugin.archive_unit("activity", unit, record_count=count,
                                          first_received_ns=first, last_received_ns=last)
            elif past == "deleted":
                await plugin.delete_unit("activity", unit, record_count=count,
                                         first_received_ns=first, last_received_ns=last)
        plugin.stored = [meridian.StoredSpan(record_kind="activity", record_count=...,
                                             first_received_ns=..., last_received_ns=...)]
```

### `Storage` and `RecordKind` { #recordkind }

```python
@dataclass(frozen=True)
class Storage:
    retention_days: int = 0
    kinds: Sequence[RecordKind] = ()

@dataclass(frozen=True)
class RecordKind:
    name: str
    label: str
    window_days: int
    archivable: bool = True
```

`Storage` is the storage a version asks for, on its `Declaration`; only a plugin holding an edge role may ask for it. From 0.21.0 it takes `kinds`.

| Field | Meaning |
|---|---|
| `Storage.kinds` | The kinds of raw record the version keeps, at most 16, each named once. |
| `Storage.retention_days` | The reach of a backfill, 1 to 36,500 days. Left 0 with kinds, it is the longest of their windows. A version declaring no kinds keeps its records under it, as before 0.21.0. |
| `RecordKind.name` | The name its code and settings use: 1 to 40 lowercase letters, digits and underscores, beginning with a letter, such as `activity`. |
| `RecordKind.label` | The label a person reads, 1 to 40 characters, such as `Reported activity`. |
| `RecordKind.window_days` | Its default window, 1 to 36,500 days from when a record was received. |
| `RecordKind.archivable` | Whether a unit of it can be moved to an archive. `False` for state read and updated in place. |

**Raises** `ValueError` when the declaration is built: a bound broken, a kind declared twice, or a setting of the plugin's own taking one of the window settings' names below.

### The window settings

For each kind, `connect` declares two settings beside the plugin's own, the same for every edge plugin, which an admin of the plugin sets on its Settings form. On a plugin naming roles, they serve its edge roles.

| Setting | Label | Kind | Default |
|---|---|---|---|
| `<kind>_window_days` | *Label*: window | `int`, days | the kind's `window_days` |
| `<kind>_past_window` | *Label*: past the window | a choice of `archived`, `kept` or `deleted` | `archived` where the instance was given an archive and the kind is archivable; `kept` otherwise |

The names are the SDK's: a plugin declaring a setting of either name for a kind it declares is refused by the SDK, by the sidecar at registration, and by `meridian plugin check` ([`window-settings`](cli.md#the-rules)). Read them from [`settings()`](#settings) as delivered. The deployment refuses a save setting a window below the hold over the instance, naming the setting, and `archived` for a kind not archivable or an instance allowed no archive.

### `edge.archive_dir()` { #archive_dir }

```python
def archive_dir() -> Path | None
```

In `meridian.edge`. The archive a deployment admin allowed this instance, where it is mounted (`MERIDIAN_ARCHIVE_DIR`), or `None`: in a test, for an instance allowed none, or where the archive is a bucket instead (`MERIDIAN_ARCHIVE_BUCKET`, an `s3://` URL read through `boto3`, which a plugin deployed with one installs). The helpers below reach either through the same interface; a plugin need not read the archive itself. Its storage is `edge.storage_dir()`, as before.

### A unit

A **unit** is a file or a directory in the plugin's storage, named by its path there, such as `activity/ACC-1/2019-03`. The records it holds are the paths within it, which rows name as their raw record's key (`plugin.raw_record("activity/ACC-1/2019-03/act-77.json")`). The helpers keep an index of what moved inside the storage, under `.meridian/`, which is never a unit.

### `archive_unit()` { #archive_unit }

```python
async def archive_unit(
    self, record_kind: str, unit: str, *,
    record_count: int, first_received_ns: int, last_received_ns: int,
) -> None
```

Moves one unit past its window to the archive: writes it there, checks that each file landed (its size and SHA-256), reports the move through the sidecar with its rule, the kind's window setting and its value (`activity_window_days 2555`), and only then removes it from storage. `record_count` and the span are the records the unit holds, 1 or more, the span from the first received to the last.

| Raises | When |
|---|---|
| `ValueError` | The kind is not declared, or declared not archivable; the unit is archived already; the count or span is out of bounds; or the kind's `<kind>_past_window` is not `archived`. |
| `RuntimeError` | The instance is allowed no archive; the settings have not arrived yet; or the unit would take the archive past its bound (`MERIDIAN_ARCHIVE_MOST_BYTES`), saying what the archive holds, its bound and the unit's size. Nothing is written or reported, and the unit stays in storage. |
| `FileNotFoundError` | The unit is not in the plugin's storage. |
| `CallFailed`, `NotGranted` | The sidecar refused the move: nothing is recorded, and the unit is kept. |

### `restore_unit()` { #restore_unit }

```python
async def restore_unit(self, record_kind: str, unit: str, *, for_caller: Caller | str) -> Path
```

Restores an archived unit for the person who asked: copies it back from the archive to the restore area in storage, each file checked against what was archived, reports the restore for `for_caller` (their `Caller`, or the header it was read from), and answers where the unit is readable. It stays readable for seven days, the restore period; then it is removed and its return reported, under the rule `restore period 7 days`. Asked again meanwhile, it answers the same path and reports nothing.

| Raises | When |
|---|---|
| `ValueError` | The unit is not archived. |
| `RuntimeError` | The instance has no archive now: what it holds is kept, and restorable once a deployment admin allows one again. |
| `NotGranted` | The person does not hold `write` on one of the plugin's edge roles. The copy is removed. |
| `OSError` | A file did not come back as it was archived. |

### The restore route

An edge plugin declaring kinds and serving pages through [`meridian.Pages`](#pages) offers `POST /archive/restore` on its host, which `connect` declares at `write` on the plugin's edge roles and the deployment derives as the `restore_unit` tool on its MCP surface. It takes `record_kind` (at most 40 characters) and `unit` (at most 512), as a form or as the tool's input, restores the unit for the person the claims name, and answers a form with a redirect to the page it came from and the tool with `{"record_kind": ..., "unit": ..., "outcome": "restored"}`. A refusal names the field (`record_kind` or `unit`), or says `not_granted` or `not_restored`. A plugin's page offers it as a form under Open, posting the two fields:

```html+jinja
{% if level == "write" %}
<form method="post" action="/archive/restore">{{ csrf_input }}
  <input type="hidden" name="record_kind" value="responses">
  <input type="hidden" name="unit" value="{{ unit }}">
  <button>Restore</button>
</form>
{% endif %}
```

### `delete_unit()` { #delete_unit }

```python
async def delete_unit(
    self, record_kind: str, unit: str, *,
    record_count: int = 0, first_received_ns: int = 0, last_received_ns: int = 0,
    for_caller: Caller | str | None = None,
) -> None
```

Deletes one unit, the deletion reported before anything is removed, so a refusal keeps it. Either a unit in storage past its window, as the plugin itself, where the kind's `<kind>_past_window` is `deleted`, its count and span given; or an archived unit, which is an admin's act, `for_caller` the person holding `admin` on one of the plugin's edge roles, its count and span the index's.

| Raises | When |
|---|---|
| `CommandRefused` | The unit's last record was received inside the deployment's hold over the instance: `reason_name` is `REFUSAL_REASON_WITHIN_HOLD`. Nothing is recorded, and nothing is deleted. The plugin is never told the hold; try again on a later pass. |
| `ValueError` | The kind is not declared; the unit is deleted already; the unit is archived and no `for_caller` is given; or, as the plugin itself, the kind's `<kind>_past_window` is not `deleted`. |
| `RuntimeError` | The settings have not arrived yet. |
| `FileNotFoundError` | The unit is not in the plugin's storage. |
| `NotGranted` | The person does not hold `admin` on one of the plugin's edge roles. |
| `CallFailed` | The sidecar or the deployment refused it otherwise. |

### `find_record()` { #find_record }

```python
def find_record(self, key: str) -> RecordMoveRequest | None
```

Where a raw record's key stands, by the index: the last move of the unit holding it, the unit itself or a path in it, whose `outcome` is `MOVE_OUTCOME_ARCHIVED` (archived, restorable), `MOVE_OUTCOME_RESTORED` (readable in the restore area) or `MOVE_OUTCOME_DELETED`; or `None` for a record never moved, in storage where the plugin put it. A row's raw-record key resolves through it on the plugin's own page, never to nothing.

### What is stored { #what-is-stored }

`plugin.stored` is what the plugin's storage holds of each kind, as only the plugin knows it: one `StoredSpan` per kind, set whenever it changes and sent on every heartbeat from the next on, which the plugin's Summary draws beside what the archive holds.

| `StoredSpan` field | Meaning |
|---|---|
| `record_kind` | A declared kind, once. |
| `record_count` | How many records of it the storage holds. |
| `first_received_ns`, `last_received_ns` | When the first and the last of them were received; both 0 with no record. |
| `bytes` | The bytes the kind uses of the archive. The SDK fills it in from its index on every heartbeat, in place of any the plugin set, and adds a kind the plugin left out that the archive holds some of. |

**Raises** `ValueError` for a kind not declared, a kind twice, more than 16, or a span that is not from the first record to the last, and `TypeError` for anything but a `StoredSpan`; nothing is set then.

### The moves

What a move carries, as the sidecar records it (`RecordMoveRequest`, contract v16): `record_kind`, `unit`, `record_count`, `first_received_ns`, `last_received_ns`, `outcome` (`MoveOutcome`: `MOVE_OUTCOME_ARCHIVED`, `MOVE_OUTCOME_RESTORED`, `MOVE_OUTCOME_RETURNED` or `MOVE_OUTCOME_DELETED`) and `rule`, a window's or the restore period's. A move made for a person names no rule: the person is read from the assertion, never a field. Nothing of a record's content is in a move.

The sidecar checks each before it leaves, refusing `CallFailed` with `kind="invalid"` naming the field by its path: a kind the version did not declare, `archived` of a kind not archivable, a key, count, span or rule out of bounds. The deployment refuses `archived` for an instance allowed no archive. A restore, its return and an archiving for a person need `write` on one of the plugin's edge roles, and a deletion for a person `admin` (`NotGranted`).

## The lake { #the-lake }

From 0.22.0, contract v18, `preview`. [The lake](../concepts/the-lake.md) keeps what sources say about prices, append-only and point in time. A `dgm` plugin puts prices and bars in; `reporting`, `portfolio`, `compliance` and `signal` read and hear them. The SDK carries the typed operations and nothing of any vendor's: no HTTP or WebSocket client, no vendor-file parser, no reconnecting stream. Each operation is in [Typed operations](typed-operations.md#record_prices); each field in the [lake's data dictionary](../boundaries/lake.md).

### A dgm's catalogue { #a-dgms-catalogue }

A `dgm` declares the datasets it serves in its declaration, from code, beside its settings and storage: `Declaration(catalogue=[DatasetDeclaration(...)])`. A dataset's ID in a deployment is the instance, a colon and its key, `f"{plugin.identity.instance_id}:daily"`, which each row names.

```python
from meridian import DatasetDeclaration, DatasetLicence, Declaration, RecordKind, Storage

DECLARATION = Declaration(
    settings=SETTINGS,
    storage=Storage(kinds=[RecordKind("responses", "Raw responses", window_days=30)]),
    catalogue=[
        DatasetDeclaration(
            key="daily",
            vendor="Coinbase",
            data_types=["meridian.v1.Price", "meridian.v1.Bar", "meridian.v1.Bar.trade_count"],
            modes=["pull", "push"],
            cadence=86_400,
            history=3650,
            licence_default=DatasetLicence(kept=True, personal_use=True),
            day_time_zone="Etc/UTC",
            day_end_minute=0,
        ),
    ],
)
```

`DatasetDeclaration`, keyword only:

| Field | Type | Meaning |
|---|---|---|
| `key` | `str` | Required. 1 to 40 lowercase letters, digits and underscores, a letter first; once in the catalogue. |
| `vendor` | `str` | Required. Who originated the data, 1 to 64 characters, as the plugin names it. |
| `data_types` | sequence of `str` | Required, 1 to 32: the lake's types it serves by their message (`meridian.v1.Price`, `meridian.v1.Bar`), and the optional fields it fills by their dictionary entry (`meridian.v1.Bar.vwap`), each once. |
| `modes` | sequence of `str` or `ObservationMode` | Required, 1 to 3, each once: `pull`, `push`, `stream`. |
| `aggregator` | `str` | Who carries it, where an aggregator does; empty when reached directly. |
| `cadence` | `int` | Seconds between the source's updates, which say when it is silent; 0 when it updates only when asked. |
| `history` | `int` | Days of history the source serves; 0 for none stated. |
| `licence_default` | `DatasetLicence` or `None` | What the vendor's standard terms say. |
| `day_time_zone` | `str` | The IANA zone its business dates are in; empty for a dataset that is not daily. |
| `day_end_minute` | `int` | Minutes after local midnight the day ends, 0 to 1,439. See [Dates and time](../concepts/dates-and-time.md). |
| `venue_id` | `str` | The venue the dataset is, a venue master ID (`VEN-`); empty for a consolidated dataset. |

`DatasetLicence`, keyword only, every field optional: `kept` (`False`: served, not kept), `retention_days` (0 to 36,500; 0 for no limit set), `derived_use`, `display`, `default_fields` (at most 64 dictionary entries; none for every field) and `personal_use`. It records what the vendor's terms say, which a deployment admin confirms or replaces (see [Licences and entitlements](../concepts/licences-and-entitlements.md)), never whether a deployment meets them.

**Raises** `ValueError` when the declaration is built, naming the dataset: a key out of form, a vendor or aggregator too long, a data type or field no dictionary entry names, one named twice, no mode or a mode twice, a negative cadence or history, a zone that is no IANA zone, a day end out of range, a venue that is no `VEN-` ID, and a catalogue on a version not holding `dgm`. The upload's JSON carries the catalogue only where one is declared, its modes as words. The sidecar holds a catalogue to the same rules at registration, and refuses the plugin naming the field.

### Recording

A `dgm` records with [`record_prices`](typed-operations.md#record_prices) and [`record_bars`](typed-operations.md#record_bars), 1 to 500 rows a call, refused outside the bound before anything is sent, recorded whole or refused naming the row and field. Resolve each subject first with [`resolve_identifier`](typed-operations.md#resolve_identifier), and each venue with [`resolve_venue`](typed-operations.md#resolve_venue); report what does not resolve. A want for an instrument another source resolved, such as a custodian's, names the deployment's ID: read its record with [`resolve_instrument`](typed-operations.md#resolve_instrument) and name it to the vendor by an identifier the vendor takes. The answer counts the rows `recorded`, `restated` and `unchanged`.

### Wants { #wants }

A `dgm` hears what the lake wants of it with `receive(observations_wanted=..., want_withdrawn=...)`, records against a want with `want_id=`, and declines per subject with [`decline_want`](typed-operations.md#decline_want):

```python
async def wanted(heard: meridian.Heard) -> None:
    want = heard.message           # dataset, data_type, subjects, kinds, business_date or a range
    await plugin.record_prices(prices=fetched(want), want_id=want.want_id)
    await plugin.decline_want(want_id=want.want_id, subjects=uncovered, reason="not_covered")

await plugin.receive(observations_wanted=wanted, want_withdrawn=stop_keeping_current)
```

A standing want asks that its subjects be kept current until it is withdrawn.

### Reading

A reader reads with [`list_prices`](typed-operations.md#list_prices) and [`list_bars`](typed-operations.md#list_bars), and learns the datasets it may read with [`list_datasets`](typed-operations.md#list_datasets). The readers' choices are the reads' parameters, not a library:

```python
from datetime import date

closes = await plugin.list_prices(subjects=held, kinds=["close"], business_date=date(2026, 10, 8))
then = await plugin.list_prices(subjects=held, business_date=date(2026, 10, 8), as_of_ns=cut)
both = await plugin.list_prices(subjects=held, sources=meridian.SourceChoice(side_by_side=True))
named = await plugin.list_prices(subjects=held, sources=meridian.SourceChoice(named=["alpaca-1:daily"]))
```

and hears what is recorded after with `receive(prices_recorded=..., bars_recorded=..., subjects=...)`; see [Receive](#receive).

### The `dgm` suite { #the-dgm-suite }

`meridian.suites` carries each role's conformance suite, as for `custody`: a plugin maps each case to its own recorded or synthetic exchange with its vendor, runs its own conversion against a `Recorder` (its typed operations, recorded rather than sent, answered as a sidecar answers them), and `run` compares what it sent with the case.

```python
from meridian.suites import run

report = run("dgm", PRODUCERS, instance_id="my-prices-1")
assert report.passed, report.failures
```

A case naming a row the plugin hears, such as a want, gives it what `recorder.answer(row, reply)` returns, through the plugin's own `receive` called on the recorder:

```python
async def a_want_recorded_against(recorder):
    recorder.answer("ObservationsWanted", lambda _: synthetic_want())
    await recorder.receive(observations_wanted=MyDgm(recorder).on_want)
```

The thirteen cases are listed in [Write a `dgm` against its suite](../how-to/write-a-dgm.md#hold-it-to-the-suite). A plugin holding `dgm` is verified for it only by passing every case, which [`meridian plugin check --verified --run-tests`](cli.md#plugin-check) holds it to. The reading roles, `reporting`, `portfolio`, `compliance` and `signal`, have suites of their own, run the same way.

### Money and dates

From 0.22.0 a [`Money`](typed-operations.md#money) names its cash instrument: `Money(Decimal("12.50"), "USD")` keeps its shape, and core resolves the code; a token is named by `instrument_id` alone. Every field the dictionary types `date` takes a `datetime.date` or its ISO text, and refuses text that is no date and a `datetime`. See [Money and instruments](../concepts/money-and-instruments.md) and [Dates and time](../concepts/dates-and-time.md).

## Types

All the dataclasses are frozen.

### `Identity`

| Field | Type | Default | Meaning |
|---|---|---|---|
| `instance_id` | `str` | | The instance's name. |
| `roles` | `tuple[str, ...]` | `()` | The roles the instance was launched with. They decide its topic access. None is a plugin admitted with no topics. |
| `deployment_id` | `str` | `""` | The deployment it runs in. |

### `Grants`

| Field | Type | Default | Meaning |
|---|---|---|---|
| `publish` | `tuple[str, ...]` | `()` | Topic patterns the plugin may publish to. |
| `subscribe` | `tuple[str, ...]` | `()` | Topic patterns it may subscribe to. |

### `Interface`

The pages the plugin serves to people, on loopback. Only the plugin's sidecar reaches them, forwarding requests the dashboard vouched for.

| Field | Type | Default | Meaning |
|---|---|---|---|
| `port` | `int` | | The loopback port the pages listen on. |
| `title` | `str` | | The plugin's title. |
| `pages` | `Pages` or sequence of `Page` | `()` | The plugin's pages, one list in the order shown, each with the levels it serves. A [`Pages`](#pages) registry declares each where its view is and refuses a session at a level it does not serve. Keyword only. |
| `admin_pages` | sequence of `Page` | `()` | Retired by contract v5. Still taken in 0.10.0 and 0.10.1, as pages at `admin` after `pages`, with a `DeprecationWarning`; [`meridian plugin migrate`](cli.md#plugin-migrate) rewrites it into `pages`. |

The dashboard shows a plugin's pages in its area, under the home's button for each level a page serves: **Manage** for `admin`, **Open** for `write`, **View** for `read`. A plugin that declares no page at `write` or `read` has one there, its `/`. See [Manage, Open and View](../concepts/plugins.md#manage-open-and-view).

A plugin built before contract v5, on SDK 0.9.0 or earlier, keeps its admin pages: while the sidecar accepts its contract version, it reads the plugin's `admin_pages` as pages at `admin`, shown under Manage. Such a plugin still serves them by `caller.deployment_admin`, so of its admins only a deployment admin gets past it until it is migrated.

```python
interface = meridian.Interface(port=8000, title="Statements", pages=pages)
```

### `Page`

One of the plugin's pages, at a path on its own host, and the levels it serves. `Pages` makes one for each `@pages.page`; build one yourself only for a page served some other way.

| Member | Type | Meaning |
|---|---|---|
| `path` | `str` | The path, beginning with `/`. Anything else raises `ValueError` at `connect`. |
| `title` | `str` | The tab's title. |
| `levels` | sequence of `str` or `AccessLevel` | The levels it serves: one or several of `"admin"`, `"write"` and `"read"`, an `AccessLevel`, or its name (`"ACCESS_LEVEL_ADMIN"`). A string alone is one level. Anything else raises `ValueError`, and a page with none raises it at `connect`. |
| `roles` | sequence of `str` | The roles it serves, from those the plugin was launched with. Default `()`: a plugin holding one role, or none, names none. From 0.20.0; see [Roles](#roles). |
| `serves(caller: Caller) -> bool` | method | Whether the caller's session is at one of its levels; for a page naming roles, from 0.20.0, whether the caller's level on one of them is. A session at no level is served nothing. |

```python
statements = meridian.Page("/statements", "Statements", levels=["write", "read"])
if not statements.serves(caller):
    ...  # answer 403
```

One path may serve several levels, and adapts by `caller.level`: the dashboard frames the same path under Open and under View.

### `AccessLevel` { #accesslevel }

The generated protobuf enum `meridian.v1.sidecar_pb2.AccessLevel`: a person's level on a plugin, the same three for every plugin.

| Value | Number | Button | Spelling |
|---|---|---|---|
| `ACCESS_LEVEL_UNSPECIFIED` | 0 | | A session at no level, which holds nothing. |
| `ACCESS_LEVEL_READ` | 1 | View | `"read"` |
| `ACCESS_LEVEL_WRITE` | 2 | Open | `"write"` |
| `ACCESS_LEVEL_ADMIN` | 3 | Manage | `"admin"` |

### `Setting`

One setting the plugin needs, declared at `connect`.

| Field | Type | Default | Meaning |
|---|---|---|---|
| `name` | `str` | | The setting's name. |
| `kind` | `type` | `str` | `str`, `int` or `bool`, or from 0.19.0 `list` for a table. Anything else raises `TypeError` at `connect`. |
| `required` | `bool` | `False` | Whether the plugin needs a value to be healthy. |
| `secret` | `bool` | `False` | A secret is set through the dashboard and never read back, displayed, logged, reported or bundled. The plugin receives it in `Settings` and nowhere else. |
| `description` | `str` | `""` | What the setting is, sent with its declaration. |
| `label` | `str` | `""` | The field's name on the dashboard's form; for a table, the title of its tab. |
| `default` | `str`, `int`, `bool` or `None` | `None` | Shown greyed in the empty field, and held in `Settings.values` while the setting is unset. Of the setting's `kind`, one of its `choices` if it has any, and never on a secret. |
| `unit` | `str` | `""` | Shown beside a number. |
| `choices` | `tuple[Choice, ...]` | `()` | Makes the setting a choice, one of these, shown as radio buttons. Its `kind` must be `str`. |
| `applies_when` | `AppliesWhen` or `None` | `None` | The setting applies only while another holds one of some values. |
| `developer` | `bool` | `False` | Shown only on a development deployment. |
| `columns` | `tuple[Column, ...]` | `()` | A table's columns, in the order its tab shows them. Only with `kind=list`, which needs at least one. From 0.19.0. |
| `most_rows` | `int` | `0` | The most rows a table holds, at most 500; `0` is 500. From 0.19.0. |
| `roles` | sequence of `str` | `()` | The roles it serves, from those the plugin was launched with: it is shown to an admin of any of them and set only by one holding admin on every one. Not who may read the value: the plugin reads every setting it declared. None on a plugin holding one role or none. From 0.20.0; see [Roles](#roles). |

```python
plugin = await meridian.connect(
    settings=[
        meridian.Setting("api_token", secret=True, required=True, description="The rail's API token"),
        meridian.Setting("poll_seconds", kind=int, description="How often to poll"),
    ],
    reads_external_accounts=True,
)
```

A table, from 0.19.0, is rows of typed columns an admin enters in the dashboard on a tab of its own, after Settings and titled with its `label`: an entry grid checked cell by cell, saved through the same checks as the form. It has no `default` and is never secret:

```python
PLAN_CODES = meridian.Setting(
    "plan_code_links",
    list,
    label="Plan-code links",
    columns=(
        meridian.Column("account", "external_account", label="Account", required=True),
        meridian.Column("code", label="Plan code", required=True),
        meridian.Column("instrument", "instrument", label="Instrument", required=True),
    ),
    most_rows=200,
)
```

### `Column`

One column of a table setting, from 0.19.0.

| Field | Type | Default | Meaning |
|---|---|---|---|
| `name` | `str` | | The key each row's cell is held under. Never `changed_by` or `changed_at`, which the deployment stamps on each row. |
| `kind` | `str` | `"text"` | How the form takes a cell and the deployment checks it: `"text"`, `"integer"`, `"decimal"`, `"date"`, `"choice"`, `"external_account"` or `"instrument"`. |
| `label` | `str` | `""` | The column's heading on the table's tab. |
| `required` | `bool` | `False` | Every row must fill it; a row with it empty is refused, naming the cell. |
| `description` | `str` | `""` | Words shown beside its heading. |
| `choices` | `tuple[Choice, ...]` | `()` | A choice column's options, which it needs; a cell holds an option's `value`. |

Every cell arrives as text. What each kind accepts:

| Kind | A cell is |
|---|---|
| `"text"` | One line of plain text, at most 500 characters: no newline, tab, control character, or character that hides or reorders text (bidirectional, zero-width, tag or private-use). |
| `"integer"` | A whole number, such as `"42"`. |
| `"decimal"` | An exact decimal, at most 18 places, such as `"12.5"`. Read it with `decimal.Decimal`, never `float`. |
| `"date"` | A date, `"YYYY-MM-DD"`. |
| `"choice"` | One of the column's `choices`, by its `value`. |
| `"external_account"` | The identifier of an external account this plugin reported. |
| `"instrument"` | A deployment instrument record's ID, picked by search and checked to exist, never a symbol. |

See [Set a plugin's settings](../how-to/set-a-plugins-settings.md#a-table-setting) for what a table's tab checks, and the data dictionary's [`SettingColumn`](../boundaries/sidecar.md#meridian.v1.SettingColumn).

### `Choice`

One option of a setting that is a choice.

| Field | Type | Default | Meaning |
|---|---|---|---|
| `value` | `str` | | The value the plugin receives. |
| `label` | `str` | `""` | What the form shows for it. |
| `description` | `str` | `""` | What it means: a line of the setting's hint on the form. |

### `AppliesWhen`

| Field | Type | Meaning |
|---|---|---|
| `setting` | `str` | Another setting, declared before this one. |
| `one_of` | `tuple[str, ...]` | The values of it for which this setting applies. Only then does the form show it, and ask for it when it is required. |

```python
plugin = await meridian.connect(
    settings=[
        meridian.Setting(
            "environment",
            label="Environment",
            default="sandbox",
            choices=(meridian.Choice("sandbox", "Sandbox"), meridian.Choice("live", "Live")),
        ),
        meridian.Setting(
            "live_account", label="Live account", required=True,
            applies_when=meridian.AppliesWhen("environment", ("live",)),
        ),
    ],
)
```

### `Settings`

| Field | Type | Meaning |
|---|---|---|
| `values` | `dict` of `str` to `str`, `int`, `bool` or `list` | Each declared setting the deployment holds a value for, typed by its declaration, and the `default` of each that has one and no value. A table's is a `list` of rows, each a `dict` of text by column name with `changed_by` and `changed_at`. |
| `missing_required` | `tuple[str, ...]` | Required settings with no value yet. |

### `AccountScope`

| Field | Type | Default | Meaning |
|---|---|---|---|
| `read` | `frozenset[str]` | empty | Every account anybody may read through this plugin, and every account one of its external accounts is linked to. |
| `write` | `frozenset[str]` | empty | Every open account anybody may write through this plugin, and every open account one of its external accounts is linked to. |
| `links` | `tuple[LinkedExternalAccount, ...]` | `()` | This plugin's links, and nobody else's. An external account the plugin reported that none of them names is unlinked. Added in 0.7.0. |

| Method | Returns | Meaning |
|---|---|---|
| `link_of(external_account_id: str)` | `LinkedExternalAccount` or `None` | The link naming this external account, or `None` while it is unlinked. |

A link puts its account in both `read` and `write` while it stands. A closed account stays in `read` alone, and its link is still listed.

### `LinkedExternalAccount`

One of the plugin's external accounts, linked to one of the deployment's accounts by an admin of the plugin. Added in 0.7.0.

| Field | Type | Default | Meaning |
|---|---|---|---|
| `external_account_id` | `str` | | The external account, as the plugin reported it with `report_external_accounts`. |
| `account_id` | `str` | | The deployment's account it is linked to. |
| `account_name` | `str` | `""` | That account's name as the deployment holds it now, so a page can say which account a link points at without acting for anybody. A rename arrives as a new delivery. |

### `Caller`

Who a request for the plugin's page came from, as the dashboard vouched and the sidecar checked before forwarding it. It is read, not checked, by the SDK: only the sidecar can reach the page, and the sidecar removes every other claim the request arrived with.

A person opens a plugin at one level they hold, by a button on the dashboard's home: **Manage** at `admin`, **Open** at `write`, **View** at `read`. The session carries only that level, and the accounts are cut to it: under Open, `read` and `write`; under View, `read` alone; under Manage, neither, since admin configures a plugin and sees no account's data.

From 0.20.0, contract v15, a person holds a level on each role of a plugin, and the session carries one entry for each role they hold something on within its button: under Open a role held at `write` is at `write` and one held at `read` at `read`, under View each at `read`, under Manage each role they administer at `admin`, with no account. `roles`, `level_for`, `read_for` and `write_for` read it. `level`, `read` and `write` stay the session's button and the union over its roles.

| Member | Type | Meaning |
|---|---|---|
| `subject` | `str` | The person, as the deployment's directory names them. Deployment-local, never an address. |
| `display_name` | `str` | Their name, for display. |
| `level` | `int`, an [`AccessLevel`](#accesslevel) | The level the session was opened at. `ACCESS_LEVEL_UNSPECIFIED` is a session that holds nothing. Added in 0.10.0. |
| `admin` | `bool` property | Whether the session was opened by Manage: `level` is `ACCESS_LEVEL_ADMIN`. Added in 0.10.0. |
| `read` | `frozenset[str]` | The accounts this plugin may show them in this session. Empty under Manage. |
| `write` | `frozenset[str]` | The accounts this plugin may act on for them in this session. Every one is also in `read`. Empty under View and Manage. |
| `header` | `str` | The `Meridian-Caller` header as received. Pass it as `acting_for` on a typed operation to send it for this person. |
| `deployment_admin` | `bool` | Whether the person is a deployment admin. It opens no page and reaches no account. It says only that, linking an external account under Manage, they may name a new account rather than an existing one. |
| `delegation_id` | `str` | The delegation the person acted through, when they came through a client, such as the CLI, their own agent or an MCP client, rather than a browser. Empty for a browser. Added in 0.14.0. |
| `client_name` | `str` | That client's registered name. Empty for a browser. Added in 0.14.0. |
| `through_a_client` | `bool` property | Whether the person came through a client on a delegation: `delegation_id` is not empty. Added in 0.14.0. |
| `roles` | `Mapping[str, int]` | Each role's level within the session's button, an [`AccessLevel`](#accesslevel) by role. Empty where the claims carry no per-role entry. Added in 0.20.0. |
| `level_for(role: str) -> int` | method | Their level on `role` within the session's button; `ACCESS_LEVEL_UNSPECIFIED` for a role they hold nothing on here. Claims carrying no per-role entry read every role at `level`. Added in 0.20.0. |
| `read_for(role: str) -> frozenset[str]` | method | The accounts the plugin may show them for `role`: within `read`, empty under Manage and for a role they hold nothing on. Claims carrying no per-role entry read every role as `read`. Added in 0.20.0. |
| `write_for(role: str) -> frozenset[str]` | method | The accounts the plugin may act on for them in `role`, those the sidecar admits a command of that role for: within `read_for(role)`, empty under View and Manage and for a role held at `read`. Claims carrying no per-role entry read every role as `write`. Added in 0.20.0. |
| `Caller.from_header(header: str) -> Caller` | classmethod | Decode a `Meridian-Caller` header: base64url, unpadded. |
| `may_read(account_id: str) -> bool` | method | Whether they may read the account through this plugin in this session: `account_id in read`. |
| `may_write(account_id: str) -> bool` | method | Whether they may write the account through this plugin in this session: `account_id in write`. |

The levels are the same for every plugin, granted in the deployment's access groups. A plugin names no parts of itself, so there is nothing finer to ask than, from 0.20.0, the person's level on each of its roles, which are the deployment's, not the plugin's. The sidecar checks every command sent for a person again, whatever the plugin believes: it admits one only in a session at `write`, and from contract v15 only by their `write` on a role whose grants include the command, the account among that role's write accounts, refusing otherwise and naming the role. See [Access](../concepts/access.md#access-per-role).

The per-role accounts reach the plugin as positions in the claims' read accounts, which `Caller` resolves; a position past them is a header that does not read. Claims carrying no per-role entry, from a plugin holding no role or a dashboard before contract v15, read every role as the session's level and accounts.

A person who came through a client on a delegation stays the actor: `delegation_id` and `client_name` say only through what, for the plugin to show and record as it chooses. From contract v9 the sidecar stamps the delegation beside the person on every command sent for them. See [The delegation](cli.md#the-delegation).

!!! note "`deployment_admin` opens no page since 0.10.0"
    Up to 0.9.0 a plugin served its admin pages to a caller whose `deployment_admin` was `True`. Since contract v5 a deployment admin holds on a plugin what their grants give, and a plugin's admin need not be one. Serve a page at `admin` by the session's level: declare it with `levels=["admin"]`, or ask `caller.admin`.

!!! note "`Caller.access` and `TagAccess` are gone"
    Releases up to 0.5.0 gave access tag by tag, as `Caller.access`, a tuple of `TagAccess`, and `Identity.tags`. Tags were retired in 0.6.0: `Caller.access` raises an `AttributeError`, and `from meridian import TagAccess` an `ImportError`, each saying to read `Caller.read` and `Caller.write`, or ask `may_read` and `may_write`, which keep their names.

### `Identifier`

The generated protobuf message `meridian.plugin.v1.operations_pb2.Identifier`: one typed identifier for an instrument, or from 0.22.0 for a venue.

| Field | Type | Meaning |
|---|---|---|
| `scheme` | `str` | A global scheme (`"figi"`, `"isin"`, `"cusip"`, `"sedol"`; a currency's `"iso4217"`, a token's `"caip19"`; from 0.22.0 a venue's MIC, `"iso10383"`) or a source-scoped one (`"symbol"`). |
| `value` | `str` | The identifier. |
| `source` | `str` | The namespace a source-scoped identifier belongs to, such as `"snaptrade"`. Empty for a global scheme. |

```python
isin = meridian.Identifier(scheme="isin", value="US0378331005")
symbol = meridian.Identifier(scheme="symbol", value="AAPL", source="snaptrade")
mic = meridian.Identifier(scheme="iso10383", value="XNYS")              # a venue, for resolve_venue
letter = meridian.Identifier(scheme="symbol", value="V", source="alpaca")  # a vendor's code for one
```

### `MissReason`

The generated protobuf enum `meridian.plugin.v1.operations_pb2.MissReason`: why a resolution did not produce exactly one instrument.

| Value | Number | Meaning |
|---|---|---|
| `MISS_REASON_UNSPECIFIED` | 0 | Not set. |
| `MISS_REASON_NOT_FOUND` | 1 | No instrument matched. |
| `MISS_REASON_AMBIGUOUS` | 2 | More than one matched. It is reported as a miss rather than resolved by picking one. |

## Pages { #pages }

From 0.10.0. A plugin's pages are declared and enforced in one place: each page is a view function and a template, declared where the view is with the levels it serves. `meridian.Pages` sends the list at registration and answers 403 to a session at any other level before the view runs, so the dashboard's tab row and the plugin agree by the same declaration.

```python
from pathlib import Path

import meridian

pages = meridian.Pages("Statements", templates=Path(__file__).parent / "templates")


@pages.page("/connections", "Connections", levels="admin")
async def connections(request: meridian.Request) -> str:
    return pages.render("connections.html", linked=...)  # no account's data


@pages.page("/", "Statements", levels=["write", "read"])
async def statements(request: meridian.Request) -> str:
    rows = [...]  # cut to request.caller.read
    return pages.render("statements.html", rows=rows)


@pages.route("/sync", levels="write", methods=["POST"])  # an endpoint, not a tab
async def sync(request: meridian.Request) -> str: ...


async with await meridian.connect(
    interface=meridian.Interface(port=8000, title="Statements", pages=pages),
) as plugin:
    server = pages.serve(plugin, 8000)
```

### `Pages`

```python
class Pages(title: str = "", *, templates: str | os.PathLike | None = None, kit: str = "0.7.0", max_body: int = MAX_BODY)
```

| Parameter | Meaning |
|---|---|
| `title` | The heading the base template draws, and the end of each page's `<title>`. |
| `templates` | The directory `render` reads templates from. A directory that does not exist raises `FileNotFoundError`. |
| `kit` | The kit version the base template links, at `/.meridian/ui/<kit>/`. The dashboard answers any 0.x with the newest 0.x it carries. |
| `max_body` | The largest request body, in bytes, the pages take: `meridian.pages.MAX_BODY`, 1 MiB, unless said. A larger one is answered 413 before any view runs, so a view need not measure what it is sent. A negative number, or anything but an `int`, raises `ValueError`. From 0.10.1. |

| Member | Meaning |
|---|---|
| `page(path, title, *, levels, roles=(), methods=("GET",))` | Decorator. A tab, shown under the home's button for each of `levels`, in the order declared, and served only in a session at one of them; naming `roles`, from 0.20.0, in a session where the person's level on one of them is. |
| `route(path, *, levels, roles=(), methods=("GET",))` | Decorator. An endpoint that is not a tab, such as a form's action or a page's data, served only in a session at one of `levels`; naming `roles`, as a page's. Its tool serves the same roles. |
| `tool(*, replaces, ..., roles=None)` | Decorator. A tool replacing the one derived from the route at `replaces`; it serves the route's roles, or from 0.20.0 those `roles=` names. See [Offer your plugin's pages to agents](../how-to/offer-your-pages-to-agents.md). |
| `render(template, /, **context) -> str` | `template`, from `templates`, rendered with `context`. Called from a view, while it serves a request; anywhere else raises `RuntimeError`. |
| `csrf_token(caller) -> str` | The token a request from this person, in a session at this level, carries back when it changes something. |
| `declared` | The tabs, in the order declared: what registration sends. |
| `dispatch(request) -> Response` | The view at the request's path and method: 404 for no such path, 405 for a method the path does not take, 403 for a level it does not serve, or from 0.20.0 for a session holding none of its levels on any of its roles. A HEAD runs the GET view, where no view is declared for HEAD, and answers its headers with no body. |
| `app(plugin=None)` | The pages as an ASGI application, with the caller read as [`CallerMiddleware`](#callermiddleware) reads it. A body over `max_body` is answered 413 without being read; a view that raises is logged and answered 500. |
| `serve(plugin, port, *, loop=None, max_body=None)` | Runs `app(plugin)` on `127.0.0.1:<port>` with the standard library's threaded server, in a thread of its own; each view runs on `loop`, the running one by default, where the plugin's operations are. A request whose `Content-Length` is over `max_body`, the pages' own unless said, is answered 413 without its body being read (`max_body` from 0.10.1). Returns the server, whose `shutdown()` stops it. A view taking more than 60 seconds is answered 500. |

`levels` takes the same values as [`Page`](#page). A path or a route with no level raises `ValueError` when it is declared, and so does the same path and method declared twice. A view is sync or async, takes a `Request`, and answers a `str`, the page's HTML, or a `Response`.

From 0.10.1, HEAD is answered for every path that takes GET: the GET view runs, with `request.method` `"HEAD"`, and its answer's headers are sent, with the length of the body, and no body. A path that takes GET lists HEAD in a 405's `Allow` too.

| `Request` field | Meaning |
|---|---|
| `method`, `path` | As asked. |
| `caller` | The [`Caller`](#caller), with the session's level. |
| `plugin` | The registered `Plugin` the pages serve, whose operations a view calls, with `acting_for=request.caller.header` to act for the person. |
| `query`, `form` | The query string's and a urlencoded form's fields, the last of each name. |
| `headers` | By lower-case name. |
| `body` | The body as sent. |
| `csrf_token` | The token a request that changes something carries back, set before the view runs. |

| `Response` field | Default | Meaning |
|---|---|---|
| `body` | `""` | `str` or `bytes`. `text` reads it as text. |
| `status` | `200` | |
| `content_type` | `"text/html; charset=utf-8"` | |
| `headers` | `()` | More headers, as `(name, value)` pairs. |

### Roles { #roles }

From 0.20.0, contract v15. A person's level is granted on each role of a plugin, so a plugin holding several names the roles each page, route, tool and setting serves with `roles=`, from those it was launched with. **A plugin holding one role, or none, names none, and nothing changes**: the sidecar serves its declarations that role.

```python
@pages.page("/statements", "Statements", roles=["custody"], levels=["write", "read"])
async def statements(request: meridian.Request) -> str:
    caller = request.caller
    rows = [...]  # cut to caller.read_for("custody")
    return pages.render("statements.html", rows=rows,
                        may_record=bool(caller.write_for("custody")))


@pages.page("/blotter", "Blotter", roles=["custody", "operations"], levels=["write", "read"])
async def blotter(request: meridian.Request) -> str: ...  # each role's rows by read_for(role)


settings = [meridian.Setting("api_key", secret=True, roles=["custody", "operations"])]
```

- **A page or route** is served, and a page's tab shown, when the person's level on one of its roles within the session's button is one of its levels. Otherwise `Pages` answers 403 before the view, naming the roles and what the session holds on each, such as `/statements is for custody under Open and View; under Open this session holds nothing on custody.`
- **A tool** derived from a route takes its route's roles; `@pages.tool(..., roles=[...])` names others. It is listed at the deployment's `/mcp` to a person holding one of its levels on one of its roles.
- **A setting** is shown to an admin of any of its roles and set only by one holding admin on every one.
- **On a plugin holding several roles**, the sidecar refuses the registration of a page or setting naming no role, or a role the plugin was not launched with, naming it; a tool so declared is refused by name, without refusing the plugin. [`meridian plugin check`](cli.md#plugin-check) says where first (`roles-declared`).
- **What is shown, never what is admitted.** A declaration's roles decide what a person is shown. The sidecar decides every command sent for them, by their `write` on the role whose grants include it.

A page serving several roles adapts per role with [`caller.level_for(role)`, `read_for(role)` and `write_for(role)`](#caller): offer a role's actions only where `write_for(role)` holds accounts.

### Templates

`render` renders a [Jinja2](https://jinja.palletsprojects.com) template, autoescaped, so every value is escaped unless it is `meridian.pages.Markup`, text that is HTML already. Beside what the view passes, the context always holds:

| Name | What it is |
|---|---|
| `caller` | The `Caller` asking. |
| `level` | The session's level, as `"admin"`, `"write"` or `"read"`. A template adapts by it: `{% if level == "write" %}`. |
| `csrf_input` | The hidden field carrying the CSRF token, for inside a form. |
| `csrf_token` | The token itself, for a script's `X-CSRF-Token` header. |

A page's template extends the kit's base template, `meridian/base.html`, which `Pages` carries. It links the kit's stylesheet and script, draws the page's heading and, where more than one page is at the session's level, its tab row, marking the tab the request is for; the kit drops both when the dashboard frames the page, and draws them when the page is opened on its own. From 0.10.1, a form's action that answers by rendering a page, at a path that is no tab, marks the tab the form was posted from, by the request's `Referer`, and takes that tab's title. It has four blocks:

| Block | Holds |
|---|---|
| `title` | The document's `<title>`: by default the page's title and the plugin's, as `Statements · Holdings`. |
| `status` | An `om-status` marked `data-om-header`, which the dashboard draws beside the plugin's name (kit 0.7.0). |
| `head_actions` | Buttons marked `data-om-action`, which the dashboard draws in its header, left of the level switch (kit 0.4.0); one also marked `data-om-icon="refresh"` is drawn as a circular arrow (kit 0.8.0). |
| `content` | The page. |

```html+jinja
{% extends "meridian/base.html" %}
{% block status %}<om-status data-om-header state="ok" label="Synced"></om-status>{% endblock %}
{% block head_actions %}{% if level == "write" %}
  <form class="inline" method="post" action="/sync">{{ csrf_input }}<button data-om-action="sync">Sync</button></form>
{% endif %}{% endblock %}
{% block content %}
  <om-grid row-key="id"><script type="application/json">{{ grid | tojson }}</script></om-grid>
{% endblock %}
```

`tojson` writes a kit component's data safely inside its `<script>`. `{% include %}` and macros compose a page from pieces. See [Build a plugin's page](../how-to/build-a-plugin-page.md).

### CSRF

A request that changes something carries this plugin's CSRF token. The plugin's host keeps the person's session in a cookie, and every plugin's host is the same site as the dashboard, so the cookie's SameSite does not stop another plugin's page from posting here as the person, and the plugin never sees the host it is reached at to check an `Origin` against. So `Pages` refuses every request but `GET` and `HEAD` with 403, before the view runs, unless it carries the token back: `{{ csrf_input }}` inside a form, which sends a field named `csrf`, or the `X-CSRF-Token` header from a script.

The token is an HMAC of the person and the session's level, under a secret the process makes when it starts. A restart, which each save on a development deployment is, makes a page open before it stale until it is reloaded.

## `meridian.testing` { #testing }

From 0.10.0. `PageClient` asks a plugin's pages in its own tests, in process, as its sidecar would forward them: each request carries a `Meridian-Caller` header for a session at one level, its accounts cut to that level as the dashboard cuts them.

```python
from meridian.testing import PageClient

from my_plugin.page import pages

client = PageClient(pages, plugin=stand_in, read={"ACC-1", "ACC-2"}, write={"ACC-2"})
assert client.get("/", "write").status == 200
assert client.get("/", "admin").status == 403
client.assert_no_account_data("AAPL", "125", "12,500.00")  # what the stand-in holds for ACC-1
```

| Member | Meaning |
|---|---|
| `PageClient(pages, plugin=None, *, read=(), write=(), subject=..., display_name=..., deployment_admin=False, roles=())` | `plugin` is what a view reaches as `request.plugin`: a stand-in whose operations answer in the test. `read` and `write` are the accounts the person may read and write, cut to each session's level. The person is Ada Park, a local account, unless `subject` and `display_name` say otherwise, and a deployment admin when `deployment_admin` is `True` (from 0.10.1), which every request the client sends says. `roles`, from 0.20.0, are the roles the plugin was launched with, each of which the person holds at every level; none, for a plugin holding one role or none, carries no per-role entry, and pages serve as before. |
| `get(path, level, **query)` | A GET in a session at `level`: `"admin"`, `"write"` or `"read"`. |
| `post(path, level, form=None, *, headers=None, roles=None)` | A form posted from the plugin's page, carrying its CSRF token back unless `form` gives one of its own. `headers`, from 0.10.1, sends more, such as the `Referer` of the page it was posted from. `roles`, from 0.20.0, narrows the session as `caller` does. |
| `request(method, path, level, *, form=None, query=None, headers=None, roles=None)` | The request as given, with no token added: for testing that one without a token, or with somebody else's, is refused. `roles` as `post`'s. |
| `caller(level, *, roles=None, deployment_admin=None)` | The client's person, as a `Caller` in a session at `level`: a deployment admin as the client was made, unless `deployment_admin` says (from 0.10.1). From 0.20.0 the session carries an entry for each of the client's roles at `level`, or for those `roles` names; a mapping gives each its own level within the button, `{"operations": "write", "custody": "read"}` under Open. A role the client was not made with raises `ValueError`, and so does a level the button cannot carry: under Open a role is at `write` or `read`, under View at `read`, under Manage at `admin`. |
| `call_tool(name, arguments=None, *, level=None, ..., roles=None)` | Calls a tool as the deployment's `/mcp` would; see [Offer your plugin's pages to agents](../how-to/offer-your-pages-to-agents.md#test-it-as-the-surface-calls-it). `roles`, from 0.20.0, as `caller`'s. |
| `every_page()` | Each declared page, in order, under Manage, Open and View: a list of `Rendered`, each with `page`, `level` and `response`, 200 where the page serves the level and 403 where it does not. On a client made with roles, from 0.20.0, under each level for each role alone and for all of them together, each `Rendered` naming them in `roles`. |
| `assert_no_account_data(*held)` | Fails, naming the page and what it showed, when under Manage a page at `admin` does not answer 200, any other page does not answer 403, or a page at `admin` shows any of `held`, as given or as a template escapes it. `held` is the account data the test put where the plugin reads it: holdings, quantities, values, balances, a statement's rows. Called with nothing to look for, it raises `ValueError`. |

`meridian.testing.heartbeat(*, healthy=True, detail="", figures=())`, from 0.11.0, is the heartbeat a plugin's sidecar receives from a plugin reporting these: its figures as the wire carries them, in the plugin's order. It raises as setting `plugin.figures` does, so a test of the figures a plugin computes asserts on it, or on the refusal. See [Figures](#figures).

`meridian.testing.caller_header(level, *, read=(), write=(), subject=..., display_name=..., deployment_admin=False, delegation_id="", client_name="", tool_name="", roles=())` makes the header alone, for a test that serves the pages another way. `delegation_id` and `client_name`, from 0.14.0, are a person's who came through a client rather than a browser. `roles`, from 0.20.0, are the roles the session carries an entry for, as `caller`'s, each role's accounts as positions in the claims' read accounts, as the dashboard mints them. It is unsigned: only a plugin's tests read it, never a sidecar.

A plugin holding several roles holds each page to them in its tests:

```python
client = PageClient(pages, plugin=stand_in, read={"ACC-1", "ACC-2"}, write={"ACC-2"},
                    roles=["custody", "operations"])
session = {"operations": "write", "custody": "read"}
assert client.get("/blotter", "write").status == 200
# a route at write naming custody, asked where custody is at read: refused before the view
assert client.post("/statements/record", "write", {...}, roles=session).status == 403
for rendered in client.every_page():   # each level, each role alone, and both
    ...
```

The client is synchronous, for a plain pytest test, and not for use inside a running event loop. A view that raises fails the test with its traceback.

A Manage session holds no account's data, and the sidecar refuses reads for the person in one. What the plugin holds for an account, such as a synced statement's holdings, quantities, values and balances, nothing technical keeps off a page at `admin`, so the plugin's tests do, with `assert_no_account_data`.

An account's identity is not its data: its ID, name, custodian, type, owner and note. A Manage page may list every account of the deployment, as the accounts read answers them, as a link target, so from 0.10.1 `assert_no_account_data` no longer looks for every account the person may read or write, only for the strings the test names. A string named is looked for whatever it is, an identity too. In 0.10.0 it also looked for each account ID in `read` and `write`, looked for each string only as given, and took a call that named nothing.

## `CallerMiddleware` { #callermiddleware }

```python
from meridian import CallerMiddleware

app = CallerMiddleware(app)
```

A pure ASGI middleware, so it works with any ASGI framework and needs none. On each HTTP request it reads the one `Meridian-Caller` header the sidecar forwarded and puts a `Caller` at `scope["state"]["caller"]`. In Starlette or FastAPI that is `request.state.caller`.

| Request | Answer |
|---|---|
| Exactly one `Meridian-Caller` header that decodes | Passed to the app with `scope["state"]["caller"]` set. |
| No `Meridian-Caller` header, or more than one | `401`, `open this page from the dashboard`. Such a request did not come through a sidecar. |
| A header that does not decode | `401`, `the caller header does not read`. |
| A scope that is not `http` | Passed to the app unchanged, with no caller. |

It checks nothing about the caller. That is the sidecar's job, and only the sidecar can reach the page.

## Exceptions

Every exception carries the sidecar's own words, so a log line says whether the fix is the plugin author's, the operator's, or nobody's. The words are for a person, and may be reworded at any release. Where a plugin must act on which refusal it met, the SDK raises a class of its own for it, chosen by the code the sidecar sends beside the refusal and never by the words: `NotLinked`, and from 0.13.0 `CommandRefused`.

| Exception | Attributes | Raised when |
|---|---|---|
| `MeridianError` | | Base class for everything below. |
| `Refused` | `reason: str` | `connect`: the sidecar declined registration, for example because access control has not loaded, the role carries no grants, or the schema does not match. A refusal is a statement about configuration. It is not retried, and asking again changes nothing. |
| `NoSidecar` | `address: str`, `waited_seconds: float` | `connect`: no sidecar answered at `address` within `wait` seconds. It may still be starting, or not be there at all. |
| `NotRegistered` | | Any method, after `leave()`. |
| `NotGranted` | `topic: str`, `reason: str` | A typed operation was refused permission. `topic` holds the operation's name (for example `"RecordHolding"`), and `reason` names what was missing. |
| `CallFailed` | `topic: str`, `kind: str`, `detail: str` | A typed operation did not produce an answer. `topic` holds the operation's name. `kind` says which failure it was; see [Typed operations](typed-operations.md#errors). |
| `NotLinked` | as `CallFailed`, with `kind="refused"` | A typed operation named an external account nobody has linked to an account, so nothing was recorded for it. A subclass of `CallFailed`, so code that caught `CallFailed` still catches it. Raised only when the refusal carries the code `REFUSAL_REASON_EXTERNAL_ACCOUNT_NOT_LINKED`. Not worth retrying: the next statement after an admin links the account records it. Added in 0.7.0; see [Typed operations](typed-operations.md#an-unlinked-external-account). |
| `CommandRefused` | as `CallFailed`, with `kind="refused"`; `reason: int`, `reason_name: str`, `fields: tuple[str, ...]` | The book of record refused a command with a code of its own, such as `REFUSAL_REASON_OPENING_BALANCE_RECORDED`; `reason` is the code's number and `reason_name` its name. `fields`, from 0.14.0, names each field an incomplete entry left out, by its path in the call (`positions[0].settled_quantity`, `positions[1].lots[0].terms.cost`), for `REFUSAL_REASON_INCOMPLETE`, and is empty for every other refusal. A subclass of `CallFailed`. Not retried: the same command meets the same refusal. Added in 0.13.0; see [Typed operations](typed-operations.md#the-books-refusals). From 0.21.0 also the sidecar's refusal of a deletion inside the deployment's hold, `REFUSAL_REASON_WITHIN_HOLD`, from [`delete_unit()`](#delete_unit): the unit is kept, and a later pass may try again once the hold has passed. |

The sidecar's status is mapped onto these for typed operations:

| gRPC status from the sidecar | Raised as |
|---|---|
| `PERMISSION_DENIED` | `NotGranted` |
| `FAILED_PRECONDITION` carrying `REFUSAL_REASON_EXTERNAL_ACCOUNT_NOT_LINKED` | `NotLinked`, `kind="refused"` |
| `FAILED_PRECONDITION` carrying any other code, from 0.21.0 | `CommandRefused`, `kind="refused"`: `REFUSAL_REASON_WITHIN_HOLD` |
| `FAILED_PRECONDITION`, with no code | `CallFailed`, `kind="refused"` |
| `UNAVAILABLE` | `CallFailed`, `kind="no handler"` |
| `DEADLINE_EXCEEDED` | `CallFailed`, `kind="timeout"` |
| `ABORTED` carrying a code | `CommandRefused`, `kind="refused"` |
| `ABORTED`, with no code | `CallFailed`, `kind="handler error"` |
| `INVALID_ARGUMENT` | `CallFailed`, `kind="invalid"` |
| `UNAUTHENTICATED` | `CallFailed`, `kind="not vouched for"` |
| any other | `grpc.aio.AioRpcError`, unchanged |

!!! note
    `settings()`, `account_scope()`, `access()` and `report()` do not map gRPC errors. A failure there reaches the caller as `grpc.aio.AioRpcError`.

## Environment variables

| Variable | Read by | Meaning |
|---|---|---|
| `MERIDIAN_SIDECAR_ADDRESS` | `connect` | The sidecar's address, when `address` is not given. |
| `MERIDIAN_STORAGE_DIR` | `edge.storage_dir()` | Where the deployment mounted the instance's own storage, for a plugin holding an edge role. Unset where none is granted. |
| `MERIDIAN_ARCHIVE_DIR` | `edge.archive_dir()`, the archive's helpers | From 0.21.0: where the instance's archive is mounted, beside its storage, once a deployment admin allows it one. Unset where none is allowed. See [The archive](#the-archive). |
| `MERIDIAN_ARCHIVE_BUCKET` | the archive's helpers | From 0.21.0: in a cloud, the instance's own prefix of the deployment's bucket, in place of `MERIDIAN_ARCHIVE_DIR`. 0.21.0 reads an `s3://` URL, through `boto3`. |
| `MERIDIAN_ARCHIVE_MOST_BYTES` | `archive_unit()` | From 0.21.0: the archive's bound in bytes, as a deployment admin set it. Unset, or 0, for none. A value that is not a whole number of bytes is refused. |
| `MERIDIAN_LIVE_DIR` | `meridian-dev run` | The live folder. Default `/plugin/live`. |
| `MERIDIAN_LIVE_SEED` | `meridian-dev run` | What a new live folder is filled from. Default `/plugin`. |
| `MERIDIAN_DEV_EVENTS`, `MERIDIAN_DEV_REVISION` | `connect` | Set by `meridian-dev run` for the process it starts. When present, `connect` records `ready` for that revision. |

## `meridian-dev`

The package installs one command, `meridian-dev run`. On a development deployment it is the plugin container's command. It runs the plugin's own entry point, the first one in `[project.scripts]`, from the live folder, and restarts it on each change the sidecar writes. The pod, the sidecar and its credential stay as they are. It uses the standard library alone. A plugin author doesn't run it directly. See [Development deployments](../concepts/development-deployments.md) and [`plugin dev` events](plugin-dev-events.md).
