# API reference

Reference pages for building on Open Meridian, taken from the code of each release. For a guided start, begin with [Your first plugin](../getting-started/first-plugin.md). For the ideas behind these pages, read [Plugins, roles and grants](../concepts/plugins.md).

| Page | What it covers |
|---|---|
| [Command line](cli.md) | `meridian`: every command and flag, their defaults, exit codes and `--json` output. It covers installing a deployment, signing in, and uploading, launching and developing plugins. |
| [Python SDK](python-sdk.md) | The `open-meridian` package, imported as `meridian`: `meridian.connect()`, the `Plugin` object, `receive`, its types, `meridian.Pages` and its templates, `meridian.testing`, `CallerMiddleware`, the exceptions it raises, the order path and settlement calendars, its release notes, and how to move a plugin to a new release. |
| [Typed operations](typed-operations.md) | The workflow steps a plugin calls through its sidecar: each operation's Python method, gRPC rpc, role, parameters, result and errors. |
| [Core's tools](core-tools.md) | The deployment's own tools on its MCP surface for a plugin's area, the Data sources page, prepared changes, the service accounts, the trading instructions, the account attributes, the Instruments and Calendars tabs: who may call each, its inputs, its answer and its refusals, the two exceptions, and where each change is recorded. |
| [Data dictionary](../boundaries/street.md) | One page per store, every field anchored by its name, with its meaning, bounds and history, [the lake's](../boundaries/lake.md) and the venue master's record in the instrument store among them. |
| [Plugin manifest](plugin-manifest.md) | `[tool.meridian]` in a plugin's `pyproject.toml`: its roles and whether it serves pages, and what a change to them takes. |
| [`plugin dev` events](plugin-dev-events.md) | The JSON event stream of `meridian plugin dev --json` and `meridian plugin events --json`, for scripts and AI agents following a live plugin. |

!!! note "What is not here"
    The typed operations cover holdings ingestion, reading what was recorded, instrument resolution, the lake's prices, bars, trades, quotes and outcomes, [the order path](typed-operations.md#the-order-path), booking and [settlement calendars' reads](typed-operations.md#settlement-calendars-reads). RFQs and axes, confirming an allocation with a client, non-order transactions and settlement have no operations yet: see [The order lifecycle](../concepts/the-order-lifecycle.md#not-built-yet).
