# Repositories

Open Meridian's code is in the [open-meridian](https://github.com/open-meridian)
organisation on GitHub. The runtime and the tools that drive it are AGPL; the
pieces a plugin links are Apache-2.0, so a plugin you write stays yours.

| Repository | What it is | Licence |
|---|---|---|
| [meridian-core](https://github.com/open-meridian/meridian-core) | The runtime, in Rust: the bus, the stores, the conductor, the dashboard, one sidecar per plugin, the launcher, and the Helm chart that installs them | AGPL-3.0-or-later |
| [meridian-cli](https://github.com/open-meridian/meridian-cli) | `meridian`, the command line: checks a cluster, installs a deployment, signs in to one, and brings plugins in and develops them live | AGPL-3.0-or-later |
| [meridian-python](https://github.com/open-meridian/meridian-python) | The Python SDK for writing plugins, and the reference plugin `meridian plugin new` starts from | Apache-2.0 |
| [meridian-schema](https://github.com/open-meridian/meridian-schema) | The contract a plugin links: the sidecar's gRPC service, the typed operations a plugin's roles may take, and the metadata every message carries, with Rust and Python code generation | Apache-2.0 |
| [meridian-ui](https://github.com/open-meridian/meridian-ui) | The plugin UI kit: the brand's tokens, colour schemes, CSS components and framework-free web components, which the dashboard serves to every plugin's page | Apache-2.0 |
| [meridian-snaptrade](https://github.com/open-meridian/meridian-snaptrade) | A plugin that reads brokerage accounts through SnapTrade, their positions, cash and freshness, and records them as the custodian's view. It holds the `custody` role, links its accounts on the kit's account map, and is the example other connectors copy | Apache-2.0 |
| [meridian-docs](https://github.com/open-meridian/meridian-docs) | This site | — |

All seven are public. The organisation's other repositories are private.

## Why two licences

**meridian-core** is AGPL-3.0-or-later. It is the runtime every firm runs, and
it stays open source.

**meridian-cli** is AGPL-3.0-or-later as a consequence rather than a
preference: it links meridian-core's crates, which are AGPL, so a customer who
runs the binary can ask for its source.

**meridian-python** and **meridian-schema** are Apache-2.0. A plugin links the
SDK and the contract, and nothing else from Open Meridian — a plugin talks only
to its sidecar, and these are the whole of that interface. Apache-2.0 there is
what lets a vendor, or a firm, keep its plugin to itself.

**meridian-ui** is Apache-2.0 too: a plugin's page links the kit, from the
plugin's own origin.

**meridian-snaptrade** is Apache-2.0 like the SDK it is built on: it is meant
as a plugin other vendors copy, so it models the promise that a vendor keeps
their plugin.

## What lives where

- **The domain messages** the runtime carries past a sidecar — statements,
  holdings, instruments, accounts — are in meridian-core's `proto/`, under its
  licence. A plugin never sees them.
- **The plugin-facing surface** is in meridian-schema, and generated from it:
  Rust bindings in `gen/rust`, Python in `gen/python`. The SDK vendors the
  Python bindings at a pinned schema revision.
- **Plugins** live in repositories of their own, beside their own vendor's
  code, not in the SDK.
- **The platform** at open-meridian.com is operated by Open Meridian and is not
  public. A deployment needs nothing from it but its address.

## Published artefacts

| Artefact | Where |
|---|---|
| The runtime image, carrying every binary and the plugin UI kit | `ghcr.io/open-meridian/meridian-runtime`, tagged by commit and `latest`, published from every green commit on meridian-core's `main` |
| The Helm chart | `oci://ghcr.io/open-meridian/charts/meridian-runtime`, versioned `0.1.<n>`, each naming the image it was published beside |
| The `meridian` CLI | Releases of meridian-cli, for macOS and Linux, each binary with a `.sha256` beside it, published by a version tag |
| The Python SDK | `open-meridian` on PyPI, imported as `meridian` |
| The plugin base image | `ghcr.io/open-meridian/plugin-python:<SDK version>`, which a plugin's `Dockerfile` builds on |
| The plugin UI kit | Not published on its own: the runtime image carries it, and the dashboard serves it at `/.meridian/ui/<version>/` |

!!! warning "The SDK's package name"
    The SDK is published as `open-meridian`. The name `meridian-sdk` on PyPI
    belongs to an unrelated company.
