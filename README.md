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
change, the pages change with them. Today they describe CLI 0.1.43, SDK
0.27.0 (contract v23; chart 0.1.303): venue-originated fills, accepted or
answered DK by the `ems`, the FIX acknowledgements a venue takes, a venue's
value-date roll, financing and commission fees, an FX order's quote
currency, an event contract's outcomes in the lake, the closed-day flag and
the Data sources page's two counts and `unchanged` reads, a spot-date
rule's counting mode, the Calendars tab's subject and search (venues shown
by their `VEN-` IDs), `account_currency`, the suites' v23 cases, `about`
markers and `any_of`, `role-suite` holding a suite test to its outcome, and
the "Answer a venue-originated fill" how-to. Before it, core's order path
in the book (child orders, the release gate and waiting for compliance,
connectivity plugins linked to an `ems` and its venue account map, trading
instructions and the Trading instructions page, four tools; chart
0.1.301), the Instruments page's Calendars tab and its two tools, the
platform's settlement calendars, the ten G10 currencies' and the US
calendars, the suites' cases a plugin whose work never uses calendars,
settlement dates, locates or compliance waits marks not presented, core's
service accounts (chart 0.1.299), core's prepared changes, account grants
and Setting up (chart 0.1.298), backup and restore, the role renames
(`data`, `connectivity`, `confirmation`), the four "Using a ... plugin"
pages, and kit 0.12.0. The plugins on contract v23: Kalshi 0.5.0,
Polymarket 0.5.0 and the new Polymarket US 0.1.0 recording outcomes,
Alpaca 0.8.0 and Tradier 0.7.0 holding `connectivity` and `custody`
beside `data`, and SnapTrade 0.17.0 reporting venue-originated fills; on
contract v22, Tiingo 0.4.0, Fed H.10 0.4.0, Coinbase 0.5.0, Kraken 0.5.0,
the sample operations plugin 0.12.0 and its Flags tab, and the sample
reporting plugin 0.5.0 and its Orders tab.
**Notice for contract v24**, the one-ID revision: three stable reads,
`ResolveIdentifier`, `ResolveInstrument` and `ReportMissingInstrument`,
change. Every instrument comes to be keyed by its platform `INS-` ID; a
deployment's provisional records stay `LCL-`, resolved to their `INS-`
record, and a resolved `LCL-` ID is accepted forever. The `open_meridian`
identifier stops being added to records. Plugins treat IDs as opaque and
need no change; one that reads the `open_meridian` identifier should stop
relying on it.
The tutorials were walked on CLI 0.1.36 and SDK 0.21.0. A page describes
what is built, and says so where something is specified and not built yet.

## The roles page, the data dictionary and llms.txt

These pages are generated at every build, never written by hand:
`concepts/roles.md`; one page per store under `boundaries/` -- the street, the
instrument store, the book, the conductor's accounts, the sidecar, the
envelope and the shared types -- each that store's data dictionary at the
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
outside its list, when a status is other than `preview` or `released`, or
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
