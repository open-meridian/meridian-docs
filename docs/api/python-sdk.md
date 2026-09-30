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
| Version | 0.6.1 |
| Python | 3.11 or newer |
| Dependencies | `grpcio>=1.68,<2`, `protobuf>=5.28,<7` |
| Licence | Apache-2.0 |

!!! warning "Not `meridian-sdk`"
    The PyPI package `meridian-sdk` belongs to an unrelated company. Don't install it.

A plugin pins the SDK exactly, `open-meridian==0.6.1`, in its `pyproject.toml`. The sidecar it runs beside speaks one version of the contract, and a version range would let a rebuild pick up another. See [Plugin manifest](plugin-manifest.md).

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

`meridian plugin new` writes a complete plugin built this way. See [Your first plugin](../getting-started/first-plugin.md).

## What the package exports

`meridian.__all__`:

| Name | Kind | Described in |
|---|---|---|
| `connect` | async function | [`meridian.connect`](#connect) |
| `Plugin` | class | [`Plugin`](#plugin) |
| `Identity`, `Grants`, `Interface`, `Page`, `Setting`, `Choice`, `AppliesWhen`, `Settings`, `AccountScope`, `Caller` | frozen dataclasses | [Types](#types) |
| `Money` | frozen dataclass | [Typed operations](typed-operations.md#money) |
| `as_decimal`, `as_money` | functions | [Typed operations](typed-operations.md#numbers-and-amounts) |
| `Identifier`, `MissReason` | generated protobuf message and enum | [Types](#types) |
| `ExternalAccount`, `HoldingSide`, `SyncState` | generated protobuf message and enums | [Typed operations](typed-operations.md#types) |
| `CallerMiddleware` | ASGI middleware | [`CallerMiddleware`](#callermiddleware) |
| `MeridianError`, `Refused`, `NoSidecar`, `NotRegistered`, `NotGranted`, `CallFailed` | exceptions | [Exceptions](#exceptions) |
| `DEFAULT_ADDRESS` | `str` | `"127.0.0.1:9191"`, where a sidecar listens |
| `SCHEMA_VERSION` | `str` | `"v2"`, the contract version sent at registration |

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
) -> Plugin
```

Registers with the sidecar and returns the admitted plugin. A `Plugin` you hold is always one the sidecar admitted.

| Parameter | Type | Default | Meaning |
|---|---|---|---|
| `address` | `str` or `None` | `None` | The sidecar's address. When `None`, the value of `MERIDIAN_SIDECAR_ADDRESS`, then `127.0.0.1:9191`. No other configuration is read. |
| `heartbeat` | `bool` | `True` | Send a liveness heartbeat to the sidecar every 5 seconds in the background. |
| `wait` | `float` | `60.0` | Seconds to wait for a sidecar that is not answering yet. A plugin and its sidecar start together in one pod, in no promised order. |
| `interface` | `Interface` or `None` | `None` | The page the plugin serves on loopback, if any. |
| `settings` | sequence of `Setting` | `()` | The settings the plugin needs a deployment admin to give it. |
| `reads_external_accounts` | `bool` | `False` | `True` when the plugin reads accounts at an external source and names them by that source's identifiers. A deployment admin links those to accounts, and the sidecar translates them on the way in. |

The contract version it sends is `SCHEMA_VERSION`. A mismatch is refused at registration rather than found later in a decode failure.

**Raises:**

| Exception | When |
|---|---|
| `NoSidecar` | No sidecar answered within `wait` seconds. |
| `Refused` | The sidecar answered and declined to admit the plugin. Its `reason` says why. Not retried. |
| `TypeError` | A `Setting`'s `kind` is not `str`, `int` or `bool`; it has `choices` and a `kind` other than `str`; or its `default` is not of its `kind`. |
| `ValueError` | A secret `Setting` declares a `default`; a `default` is not one of its `choices`; or an admin `Page`'s path does not begin with `/`. |
| `grpc.aio.AioRpcError` | Any other gRPC failure during registration, unchanged. |

When run by the development runner on a development deployment, `connect` also records the `ready` event once the plugin is admitted. See [`plugin dev` events](plugin-dev-events.md).

## `Plugin` { #plugin }

Built by `connect`. It is an async context manager: leaving the `async with` block calls `leave()`, with the reason `"stopping"`, or the exception's class name if the block raised.

### Attributes

| Attribute | Type | Meaning |
|---|---|---|
| `identity` | `Identity` | Who the plugin was launched to be: instance, roles, deployment. Read from the registration reply, never sent by the plugin. |
| `grants` | `Grants` | What the deployment allowed, as the topic patterns it allowed them as. |

`grants` is for failing early with a good message, at startup, rather than at the first refused operation. The sidecar refuses independently of what the plugin believes, and the SDK offers no "is this allowed" check.

### Methods

| Method | Returns | Meaning |
|---|---|---|
| `settings()` | `AsyncIterator[Settings]` | The settings the plugin declared, now and again on every change. |
| `account_scope()` | `AsyncIterator[AccountScope]` | Every account anybody may read or write through this plugin, now and again on every change. |
| `access()` | `Awaitable[PluginAccessReply]` | Who may use this plugin. |
| `report(*, healthy, detail="")` | `Awaitable[None]` | Report liveness once, outside the heartbeat. |
| `leave(reason="")` | `Awaitable[None]` | Say the plugin is stopping, and close the connection. |
| Typed operations | see [Typed operations](typed-operations.md) | `report_external_accounts`, `report_sync_status`, `record_holdings_statement`, `record_holding`, `resolve_identifier`, `report_missing_instrument`, `read_accounts_for_linking`, `link_external_account`. |

Every method raises `NotRegistered` once the plugin has left.

#### `settings()`

```python
async def settings(self) -> AsyncIterator[Settings]
```

Yields the plugin's settings as the deployment holds them, typed by what it declared at `connect`, first as they are now and then on every change. Values for names the plugin did not declare are left out. A setting that declares a `default` and has no value holds its default, so the plugin uses what the form showed. A value that does not parse as its declared kind raises `ValueError` rather than being guessed at. A boolean accepts `true`, `yes`, `1`, `on`, `false`, `no`, `0` and `off`, in any case.

```python
async for current in plugin.settings():
    if current.missing_required:
        log.warning("waiting for %s", ", ".join(current.missing_required))
        continue
    token = current.values["api_token"]
```

While a required setting has no value, the sidecar reports the plugin unhealthy and names the setting.

#### `account_scope()`

```python
async def account_scope(self) -> AsyncIterator[AccountScope]
```

Yields the plugin's account scope, now and again on every change. The scope is derived from permissions and from the plugin's links to accounts, and never declared: see [Accounts](../concepts/accounts.md#how-accounts-bound-a-plugin). A plugin reads its whole read scope as itself and serves each person only what their access allows. The sidecar refuses a write outside `write`, whoever it is for.

#### `access()`

```python
async def access(self) -> meridian.v1.sidecar_pb2.PluginAccessReply
```

Returns who may use this plugin: each user group naming it, and each person who has signed in to the deployment, with their access. It is for shaping an interface; nothing here is an access decision. The reply is the generated protobuf message:

| Field | Type | Meaning |
|---|---|---|
| `user_groups` | repeated `UserGroupAccess` | `user_group_id`, `name`, `read_account_ids` and `write_account_ids`. |
| `people` | repeated `PersonAccess` | `subject`, `display_name`, `user_group_ids`, `last_signed_in_at_ns`, `read_account_ids` and `write_account_ids`. Only people who have signed in are listed: the deployment holds no directory. |

The account sets are this plugin's: what the group or person may read through it, and write through it. Every write account is also listed as read.

#### `report()`

```python
async def report(self, *, healthy: bool, detail: str = "") -> None
```

Reports liveness once, straight away. Ordinary liveness is already handled by the heartbeat. This is for a plugin that knows it is unwell and should say so before the next heartbeat.

#### `leave()`

```python
async def leave(self, reason: str = "") -> None
```

Stops the heartbeat, tells the sidecar the plugin is stopping, and closes the channel. It does nothing when called a second time. A sidecar that is already gone is ignored. Saying so is what tells a planned stop apart from a failure. A crash skips it, which is why it is optional.

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

A page the plugin serves to people, on loopback. Only the plugin's sidecar reaches it, forwarding requests the dashboard vouched for.

| Field | Type | Default | Meaning |
|---|---|---|---|
| `port` | `int` | | The loopback port the page listens on. |
| `title` | `str` | | The page's title. |
| `admin_pages` | `tuple[Page, ...]` | `()` | Pages for deployment admins, shown as tabs in the dashboard's admin view of the instance, in order, each framing its path. Serve them to a caller whose `deployment_admin` is `True`, and to nobody else. |

### `Page`

One of the plugin's pages, at a path on its own host.

| Field | Type | Meaning |
|---|---|---|
| `path` | `str` | The path, beginning with `/`. Anything else raises `ValueError` at `connect`. |
| `title` | `str` | The tab's title. |

```python
interface = meridian.Interface(
    port=8000, title="Holdings", admin_pages=(meridian.Page("/admin/accounts", "Accounts"),),
)
```

### `Setting`

One setting the plugin needs, declared at `connect`.

| Field | Type | Default | Meaning |
|---|---|---|---|
| `name` | `str` | | The setting's name. |
| `kind` | `type` | `str` | `str`, `int` or `bool`. Anything else raises `TypeError` at `connect`. |
| `required` | `bool` | `False` | Whether the plugin needs a value to be healthy. |
| `secret` | `bool` | `False` | A secret is set through the dashboard and never read back, displayed, logged, reported or bundled. The plugin receives it in `Settings` and nowhere else. |
| `description` | `str` | `""` | What the setting is, sent with its declaration. |
| `label` | `str` | `""` | The field's name on the dashboard's form. |
| `default` | `str`, `int`, `bool` or `None` | `None` | Shown greyed in the empty field, and held in `Settings.values` while the setting is unset. Of the setting's `kind`, one of its `choices` if it has any, and never on a secret. |
| `unit` | `str` | `""` | Shown beside a number. |
| `choices` | `tuple[Choice, ...]` | `()` | Makes the setting a choice, one of these, shown as radio buttons. Its `kind` must be `str`. |
| `applies_when` | `AppliesWhen` or `None` | `None` | The setting applies only while another holds one of some values. |
| `developer` | `bool` | `False` | Shown only on a development deployment. |

```python
plugin = await meridian.connect(
    settings=[
        meridian.Setting("api_token", secret=True, required=True, description="The rail's API token"),
        meridian.Setting("poll_seconds", kind=int, description="How often to poll"),
    ],
    reads_external_accounts=True,
)
```

### `Choice`

One option of a setting that is a choice.

| Field | Type | Default | Meaning |
|---|---|---|---|
| `value` | `str` | | The value the plugin receives. |
| `label` | `str` | `""` | What the form shows for it. |
| `description` | `str` | `""` | A line under it. |

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
| `values` | `dict` of `str` to `str`, `int` or `bool` | Each declared setting the deployment holds a value for, typed by its declaration, and the `default` of each that has one and no value. |
| `missing_required` | `tuple[str, ...]` | Required settings with no value yet. |

### `AccountScope`

| Field | Type | Default | Meaning |
|---|---|---|---|
| `read` | `frozenset[str]` | empty | Every account anybody may read through this plugin, and every account one of its external accounts is linked to. |
| `write` | `frozenset[str]` | empty | Every open account anybody may write through this plugin, and every open account one of its external accounts is linked to. |

### `Caller`

Who a request for the plugin's page came from, as the dashboard vouched and the sidecar checked before forwarding it. It is read, not checked, by the SDK: only the sidecar can reach the page, and the sidecar removes every other claim the request arrived with.

| Member | Type | Meaning |
|---|---|---|
| `subject` | `str` | The person, as the deployment's directory names them. Deployment-local, never an address. |
| `display_name` | `str` | Their name, for display. |
| `read` | `frozenset[str]` | The accounts this plugin may show them. |
| `write` | `frozenset[str]` | The accounts this plugin may act on for them. Every one is also in `read`. |
| `header` | `str` | The `Meridian-Caller` header as received. Pass it as `acting_for` on a typed command to send the command for this person. |
| `deployment_admin` | `bool` | Whether the person is a deployment admin. A plugin serves its admin pages to them and to nobody else. |
| `Caller.from_header(header: str) -> Caller` | classmethod | Decode a `Meridian-Caller` header: base64url, unpadded. |
| `may_read(account_id: str) -> bool` | method | Whether they may read the account through this plugin: `account_id in read`. |
| `may_write(account_id: str) -> bool` | method | Whether they may write the account through this plugin: `account_id in write`. |

A person's access to a plugin is `read` or `write`, the same for every plugin, granted in the deployment's access groups. A plugin names no parts of itself, so there is nothing finer to ask. See [Access](../concepts/access.md).

!!! note "`Caller.access` and `TagAccess` are gone"
    Releases up to 0.5.0 gave access tag by tag, as `Caller.access`, a tuple of `TagAccess`, and `Identity.tags`. Tags were retired in 0.6.0: `Caller.access` raises an `AttributeError`, and `from meridian import TagAccess` an `ImportError`, each saying to read `Caller.read` and `Caller.write`, or ask `may_read` and `may_write`, which keep their names.

### `Identifier`

The generated protobuf message `meridian.plugin.v1.operations_pb2.Identifier`: one typed identifier for an instrument.

| Field | Type | Meaning |
|---|---|---|
| `scheme` | `str` | A global scheme (`"figi"`, `"isin"`, `"cusip"`, `"sedol"`) or a source-scoped one (`"symbol"`). |
| `value` | `str` | The identifier. |
| `source` | `str` | The namespace a source-scoped identifier belongs to, such as `"snaptrade"`. Empty for a global scheme. |

```python
isin = meridian.Identifier(scheme="isin", value="US0378331005")
symbol = meridian.Identifier(scheme="symbol", value="AAPL", source="snaptrade")
```

### `MissReason`

The generated protobuf enum `meridian.plugin.v1.operations_pb2.MissReason`: why a resolution did not produce exactly one instrument.

| Value | Number | Meaning |
|---|---|---|
| `MISS_REASON_UNSPECIFIED` | 0 | Not set. |
| `MISS_REASON_NOT_FOUND` | 1 | No instrument matched. |
| `MISS_REASON_AMBIGUOUS` | 2 | More than one matched. It is reported as a miss rather than resolved by picking one. |

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

Every exception carries the sidecar's own words rather than a code, so a log line says whether the fix is the plugin author's, the operator's, or nobody's.

| Exception | Attributes | Raised when |
|---|---|---|
| `MeridianError` | | Base class for everything below. |
| `Refused` | `reason: str` | `connect`: the sidecar declined registration, for example because access control has not loaded, the role carries no grants, or the schema does not match. A refusal is a statement about configuration. It is not retried, and asking again changes nothing. |
| `NoSidecar` | `address: str`, `waited_seconds: float` | `connect`: no sidecar answered at `address` within `wait` seconds. It may still be starting, or not be there at all. |
| `NotRegistered` | | Any method, after `leave()`. |
| `NotGranted` | `topic: str`, `reason: str` | A typed operation was refused permission. `topic` holds the operation's name (for example `"RecordHolding"`), and `reason` names what was missing. |
| `CallFailed` | `topic: str`, `kind: str`, `detail: str` | A typed operation did not produce an answer. `topic` holds the operation's name. `kind` says which failure it was; see [Typed operations](typed-operations.md#errors). |

The sidecar's status is mapped onto these for typed operations:

| gRPC status from the sidecar | Raised as |
|---|---|
| `PERMISSION_DENIED` | `NotGranted` |
| `FAILED_PRECONDITION` | `CallFailed`, `kind="refused"` |
| `UNAVAILABLE` | `CallFailed`, `kind="no handler"` |
| `DEADLINE_EXCEEDED` | `CallFailed`, `kind="timeout"` |
| `ABORTED` | `CallFailed`, `kind="handler error"` |
| `INVALID_ARGUMENT` | `CallFailed`, `kind="invalid"` |
| `UNAUTHENTICATED` | `CallFailed`, `kind="not vouched for"` |
| any other | `grpc.aio.AioRpcError`, unchanged |

!!! note
    `settings()`, `account_scope()`, `access()` and `report()` do not map gRPC errors. A failure there reaches the caller as `grpc.aio.AioRpcError`.

## Environment variables

| Variable | Read by | Meaning |
|---|---|---|
| `MERIDIAN_SIDECAR_ADDRESS` | `connect` | The sidecar's address, when `address` is not given. |
| `MERIDIAN_LIVE_DIR` | `meridian-dev run` | The live folder. Default `/plugin/live`. |
| `MERIDIAN_LIVE_SEED` | `meridian-dev run` | What a new live folder is filled from. Default `/plugin`. |
| `MERIDIAN_DEV_EVENTS`, `MERIDIAN_DEV_REVISION` | `connect` | Set by `meridian-dev run` for the process it starts. When present, `connect` records `ready` for that revision. |

## `meridian-dev`

The package installs one command, `meridian-dev run`. On a development deployment it is the plugin container's command. It runs the plugin's own entry point, the first one in `[project.scripts]`, from the live folder, and restarts it on each change the sidecar writes. The pod, the sidecar and its credential stay as they are. It uses the standard library alone. A plugin author doesn't run it directly. See [Development deployments](../concepts/development-deployments.md) and [`plugin dev` events](plugin-dev-events.md).
