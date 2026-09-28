# API reference

Reference pages for building on Open Meridian, taken from the code of each release. For a guided start, begin with [Your first plugin](../getting-started/first-plugin.md). For the ideas behind these pages, read [Plugins, roles and grants](../concepts/plugins.md).

| Page | What it covers |
|---|---|
| [Command line](cli.md) | `meridian`: every command and flag, their defaults, exit codes and `--json` output. It covers installing a deployment, signing in, and uploading, launching and developing plugins. |
| [Python SDK](python-sdk.md) | The `open-meridian` package, imported as `meridian`: `meridian.connect()`, the `Plugin` object, its types, `CallerMiddleware`, and the exceptions it raises. |
| [Typed operations](typed-operations.md) | The workflow steps a plugin calls through its sidecar: each operation's Python method, gRPC rpc, role, parameters, result and errors. |
| [Plugin manifest](plugin-manifest.md) | `[tool.meridian]` in a plugin's `pyproject.toml`: its roles, tags and page, and what a change to them takes. |
| [`plugin dev` events](plugin-dev-events.md) | The JSON event stream of `meridian plugin dev --json` and `meridian plugin events --json`, for scripts and AI agents following a live plugin. |

!!! note "What is not here"
    Open Meridian has no order-routing or execution API in this release. The typed operations cover holdings ingestion and instrument resolution, and are read-only towards any brokerage.
