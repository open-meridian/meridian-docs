# meridian-docs

The documentation for [Open Meridian](https://open-meridian.com), the
open-source OEMS, published at [open-meridian.dev](https://open-meridian.dev).

A [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) site.
Every pull request builds it with `mkdocs build --strict`, so a broken link
fails before it merges; the merge to `main` builds it again and publishes it
to GitHub Pages.

## Working on it

```sh
pip install -r requirements.txt
mkdocs serve        # http://127.0.0.1:8000, reloading as you save
mkdocs build --strict
```

`mkdocs build --strict` is the whole gate: there is no Makefile here. To run it
as CI does, with nothing installed but Docker:

```sh
docker run --rm -v "$PWD":/docs -w /docs python:3.12-slim \
  sh -c "pip install -q -r requirements.txt && mkdocs build --strict -d /tmp/site"
```

Pages live under `docs/`, in the sections the navigation in `mkdocs.yml`
names: getting started, concepts, how-to, tutorials, API reference and the
developer guide. They are written from the code of
[meridian-core](https://github.com/open-meridian/meridian-core),
[meridian-cli](https://github.com/open-meridian/meridian-cli),
[meridian-python](https://github.com/open-meridian/meridian-python),
[meridian-schema](https://github.com/open-meridian/meridian-schema) and
[meridian-ui](https://github.com/open-meridian/meridian-ui); when those
change, the pages change with them.

**Pages describe the current release only.** A tutorial names the CLI and
SDK it needs once; an API page marks a field, tool or operation new or
changed in the last two releases with one line ("Added in SDK 0.28.0",
"Changed in contract 24"). History lives in two places: the Python SDK
page's [release notes](docs/api/python-sdk.md#release-notes), and its
[Moving a plugin to a new release](docs/api/python-sdk.md#moving-a-plugin-to-a-new-release)
with the CLI's `plugin migrate` step table. An upgrade fact a page drops
goes there first.

Today they describe contract v28, released in chart 0.1.313 (core
8def82a; its quality states served from chart 0.1.314, core d6781a1). CLI 0.1.53 (`meridian plugin install --pack` through the
deployment, one pack install it keeps, and `meridian plugin pack
list|show|update|remove`; new plugins on SDK 0.33.0). SDK 0.33.1 (an event-contract venue's bars, over 0.33.0's contract
v28: `meridian.SubjectRef` only, with its role; `ReportLatency` sent and
the three latency cases required; an `ems`'s read of the stale-reference
actions permitted; listed options' and futures' chains, lifecycle events
and package orders; a signal's derived series, saved scenarios and quality
escalated; the filings slice and quality states at the edge;
`DataEligibility`; every role's v28 cases marked by their `about`), with
kit 0.13.0 and `boundaries/` vendored from meridian-schema dcca81b, which
carries `operations.json` beside `roles.json`. The concept pages for listed
options and futures, companies and corporate actions, scenarios, the
analytics component's options measures, data age and latency, and
licences' eligibility, and their how-tos, describe them; the API reference
lists contract 28's typed operations and core's tools through contract 28.
Core serves the filings slice, quality states and the data-use counts in a
later chart release on contract 28, and the pages say so where they apply.
The plugins, as the Integrations page lists them (integrations/released.json
as refreshed on 2026-10-24), all on contract v27, which a contract-v28
deployment runs: SnapTrade 0.20.0, Alpaca 0.13.1, Tradier 0.12.0, OANDA
0.6.0, Tiingo 0.8.0, TrueFX 0.3.0, Coinbase 0.9.0, Kraken 0.9.0, Kalshi
0.9.0, Polymarket 0.9.0, Polymarket US 0.4.0, the Federal Reserve Board
1.0.0, the New York Fed 0.1.0, US Treasury 0.1.0, FRED 0.1.0 and the ECB
0.2.0. The platform lists each in its Community registry, with five starter
packs. What each SDK release added is in the Python SDK page's release
notes.
The tutorials were walked on CLI 0.1.36 and SDK 0.21.0. A page describes
what is built, and says so where something is specified and not built yet.

## The roles page, the data dictionary and llms.txt

These pages are generated at every build, never written by hand:
`concepts/roles.md`; one page per store under `boundaries/` -- the street, the
instrument store, the book, the conductor's accounts, the dashboard's records,
the analytics component, the sidecar, the envelope and the shared types -- each that store's data dictionary at the
contract version these docs describe, its records first and every entry
anchored by its name; and `llms.txt`, served at the site's root for agents. An
MkDocs hook, `tools/boundaries_page.py`, writes them from `boundaries/`, a copy
of meridian-schema's `boundaries/` (the roles, the principles, the method, the
worked examples and `fields.json`, every store's entries with their history).
The build fails when the copy is not what its `SHA256SUMS` says, when
`fields.json` names a store the hook gives no page, or when `llms.txt` links a
page or anchor the site does not publish, or omits a role, an operation or a
store page it does; a self-test proves those checks fail where they must.

`boundaries/vendored.json` records the schema revision the copy is from and
the contract version these docs describe. When meridian-schema's boundaries
change, refresh the copy and build:

```sh
python tools/boundaries_page.py refresh --rev <full commit or branch> --contract <n>
```

It takes `boundaries/` from meridian-schema at that revision (`--repo` names a
local clone instead of GitHub), checks its digests, and writes
`vendored.json`. Commit the copy; the pages follow it at the next build.

## The Integrations page

`how-to/integrations.md` lists the released plugins, one row each, with
filters. Its table is written at every build by an MkDocs hook,
`tools/integrations_page.py`, from `integrations/integrations.yaml`, the rows
kept by hand. The build fails when a row lacks a field or holds a value
outside its list, when a status is other than `released` (only released plugins are listed), or
when a row's roles, version or contract are not its plugin's release as
`integrations/released.json` records it: a snapshot of each plugin's main
`pyproject.toml`, its `[project]` version, `[tool.meridian]` roles and SDK
pin, with the contract that SDK release declares. The build reads nothing
from the network. When a plugin is released, refresh the snapshot, then
update its row:

```sh
python tools/integrations_page.py refresh
```

It reads each row's repository at `main`, and `meridian-python` at the tag of
each SDK release pinned, and says which rows now differ.

## Licence

The prose is licensed under [CC BY 4.0](LICENSE), and the code samples under
[Apache-2.0](LICENSE-CODE).
