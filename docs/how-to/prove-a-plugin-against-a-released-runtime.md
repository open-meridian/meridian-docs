# Prove your plugin against a released runtime

A plugin's unit tests prove its own code. To prove that what it sends lands where it should, run
it beside a real sidecar, broker, street store and book, from a released runtime image, and compare
the stores with what you expect. Core publishes a deployment for exactly this beside every runtime
image: the **plugin harness**. This page shows how to run your plugin on it from a `make e2e`
target, with [meridian-snaptrade](https://github.com/open-meridian/meridian-snaptrade)'s target as
the worked example.

!!! warning "A development deployment, for a test"
    The harness is never a way to run a deployment. It has no platform, so no instrument resolves
    and every row your plugin records names the deployment's placeholder. Its dashboard runs as a
    [development deployment](../concepts/development-deployments.md), so developer settings are
    shown and accepted. It publishes no port, and nothing outlives `down -v`. To run a deployment,
    [install one](../getting-started/installation.md).

It names no plugin and adds nothing to the contract: your plugin reaches it only through its
sidecar, as it reaches any deployment.

## What you need

- Docker with Compose v2.
- Your plugin's image, built as `meridian plugin upload` builds it (from your `Dockerfile`).
- The plugin's roles, as `[tool.meridian]` in `pyproject.toml` declares them.
- A setting that lets the plugin produce known data without a vendor's credentials, such as a
  synthetic or sandbox mode. The harness holds no secret you do not give it.
- The image of any other plugin yours needs beside it, such as the custody plugin whose statements
  an `operations` plugin reconciles.

## What is in the harness

`ghcr.io/open-meridian/meridian-harness`, an image of files only, never run. It is published at
each commit of meridian-core after the runtime image of that commit, with the same tag, and
`latest` beside it. The runtime image carries none of it. Its files are in `/harness`:

| File | What it is |
|---|---|
| `compose.yaml` | The deployment without its plugins: `keys`, which draws the run's keys and passwords; Postgres; NATS configured for the plugins and their roles; the stores migrated; street, the book (`bor`), instrument, conductor and a development dashboard; the `runner`; and `store` |
| `harness.py` | The runner, standard library only: does what an admin does in the dashboard (`ready`, `settings`, `account`, `page`, `form`, `unlinked`, `grant`); and `compose`, which writes the plugins' half of the deployment |
| `street.sql` | The street store as stable, sorted lines, which `store street` prints |
| `book.sql` | The book of record as stable, sorted lines, which `store book` prints |
| `README.md` | The same reference as this page, for that commit |

## 1. Pin a runtime image and its harness

Pin both images by tag and digest, at the same commit. The tag says which core; the digest makes it
immutable, so your e2e never changes under you:

```bash
docker pull ghcr.io/open-meridian/meridian-runtime:<commit>
docker pull ghcr.io/open-meridian/meridian-harness:<commit>
docker image inspect --format '{{index .RepoDigests 0}}' ghcr.io/open-meridian/meridian-runtime:<commit>
docker image inspect --format '{{index .RepoDigests 0}}' ghcr.io/open-meridian/meridian-harness:<commit>
```

```makefile
RUNTIME_IMAGE ?= ghcr.io/open-meridian/meridian-runtime:<commit>@sha256:<digest>
HARNESS_IMAGE ?= ghcr.io/open-meridian/meridian-harness:<commit>@sha256:<digest>
```

Both pull without a token. Keep the two tags the same: a harness and a runtime of different commits
may disagree about the dashboard's pages the runner reads. Choose a commit whose contract version is
your SDK's: a sidecar refuses an SDK of another contract version. Move the pins together, by a
deliberate commit, and with your SDK when a contract version changes.

## 2. Copy the harness out of its image

Any command will do for `create`; it is never run:

```bash
id=$(docker create "$HARNESS_IMAGE" none)
docker cp "$id:/harness" .e2e/harness
docker rm "$id"
```

Add `.e2e/` to `.gitignore` and `.dockerignore`, and remove the copy when the run ends, however it
ends: the harness's runner is not your plugin. From CLI 0.1.24, `meridian plugin check` reads
nothing under `.e2e/` and `meridian plugin dev` sends nothing from it; an earlier `plugin check`
read the runner as your plugin's code, and failed it on `settings-declared`.

## 3. Write the plugins

`compose.yaml` holds no plugin. The plugins are a second compose file, which the harness writes
itself from a JSON list of any number of them, before anything starts:

```json
[
  {"instance": "snaptrade", "image": "snaptrade:local", "roles": ["custody"]}
]
```

```bash
docker run --rm -i -v "$PWD/.e2e/harness":/harness:ro python:3.12-alpine \
    python /harness/harness.py compose <.e2e/plugins.json >.e2e/harness/plugins.yaml
```

For each plugin it writes a sidecar, as instance `instance` holding its `roles`, and the plugin
itself as the compose service named `instance`, in its sidecar's network namespace, reaching it at
`127.0.0.1:9191` (`MERIDIAN_SIDECAR_ADDRESS`), as it would in a deployment. It configures the broker
for every instance and its roles; a name that is not a role stops the run at `broker-config`,
naming it.

- `instance` is lower case letters, digits and inner hyphens, at most 32, starting with a letter,
  and none of the names the harness already holds: its services, `runtime`, `first-run`,
  `dashboard-1`, or a name starting `sidecar-`.
- `image` is the plugin's image.
- `roles` is a list, empty for a plugin holding none. Give your plugin the roles it declares.
- The first plugin listed is the one the runner acts on when a command names no `--instance`.

**A plugin is started again whenever it exits failing**, as a pod's container is. The harness starts
each plugin beside its sidecar without waiting for the rest of the deployment, so a plugin whose
first call reaches its sidecar before the deployment serves is refused, exits, and finds it serving
on its next start. You need no override for that.

Write the file again for another list; never edit it. To give a plugin environment, a command or a
volume, add a compose file of your own that overrides its service by its instance name
(`-f e2e/plugin.yaml`), with any path in it absolute: a later file's relative paths resolve against
the first file's directory.

```yaml
# e2e/plugin.yaml: the root read-only and /tmp writable, as a deployment's pod has them
services:
  snaptrade:
    read_only: true
    tmpfs:
      - /tmp:uid=65532,gid=65532,mode=1777
```

## 4. Give every compose command both files and the runtime

Compose reads every file on every command, `down` and `run` included, so each one names
`compose.yaml` and `plugins.yaml`, and has the one variable the deployment needs:

| Variable | Value |
|---|---|
| `MERIDIAN_RUNTIME_IMAGE` | The runtime image of the harness's commit, so the file never guesses its own tag. |

Name the project after your plugin with `-p`, so two harnesses never share one:

```bash
export MERIDIAN_RUNTIME_IMAGE=$RUNTIME_IMAGE
H="docker compose -p my-plugin-e2e -f .e2e/harness/compose.yaml -f .e2e/harness/plugins.yaml"
```

## Keys and passwords

None is written in the harness. When the run starts, `keys` draws at random the dashboard's signing
key, the key secret settings are sealed with, the database's password, a password for each broker
user, and the admin's password with its Argon2id hash. They live in the run's volumes until
`down -v`. The dashboard makes its one local account, `harness`, from the hash at its start, and the
conductor names that account the deployment's admin, as first run names one. The runner signs in
with the password, read from the run's volume and never printed; your plugin's container does not
mount it. Nothing you write needs a password: whoever reads a store uses `store`.

## 5. Drive it as an admin would

The runner signs in as the deployment's admin, `harness`, and does one thing per command:

```bash
$H run --rm -T runner <command>
```

Each prints what it found and exits 0, or exits non-zero saying why. Every wait is bounded by
`--seconds`. Every command acts on the first plugin listed, or on another with
`--instance <instance>`.

| Command | What it does |
|---|---|
| `ready [--seconds N]` | Waits until the plugin has registered and the dashboard lists it, healthy or not. The first command of a run, once for each plugin. |
| `settings NAME=VALUE ... [--seconds N]` | Sets the plugin's settings in its settings form, once it has declared each; a secret in its secret field. A developer setting is accepted. |
| `account NAME [--seconds N]` | Defines an account and prints its ID, for a page that links only to an account that exists. |
| `grant --level read\|write\|admin` | Grants the admin that level on the plugin, on All accounts, as a deployment admin does: a user group holding the admin, an access group, and the permission joining them. |
| `page --level admin\|write\|read PATH [--until TEXT] [--seconds N]` | Opens a session on the plugin's own host at that level (Manage, Open, View), GETs `PATH`, prints the status and the body; with `--until`, again until the body says `TEXT`. |
| `form --level L --page PATH --post PATH [--csrf-field NAME] [--from-page NAME ...] [--expect TEXT] FIELD=VALUE ...` | In such a session, reads `--page`, takes its CSRF field (`csrf`, the SDK's name) and each field `--from-page` names, with the value the page gives it, and posts them with the fields you give to `--post`; prints the status and the body. |
| `unlinked [--expect N] [--seconds N]` | Prints how many external accounts the plugin reported that nothing links, as the dashboard counts them; with `--expect`, waits for `N`. |

**The admin holds Manage alone until granted.** As a deployment's first administrator does, the
harness's admin opens every plugin under Manage and reads or acts on no account's data through one.
A session at `write` (Open) needs `grant --level write` first, and one at `read` (View) needs
`grant --level read` or `write`.

**`form` posts what the page holds.** `--from-page` names fields to take from the page it read,
repeated or comma separated, as a person posting the page's own form sends what it holds: a
proposal's digest, say, or every field of a completion form. A field you give wins over one taken
from the page, and a field the page does not have fails. With `--expect`, `form` fails unless the
body says `TEXT`. A 4xx or 5xx fails.

A link is the plugin's to send, acting for an admin, so the harness never sends one: `form` drives
your plugin's own link page under Manage, which also proves that the page links. See
[Build a plugin's page](build-a-plugin-page.md#to-link-external-accounts-om-account-map).

## 6. Read the stores

```bash
$H run --rm -T store street
$H run --rm -T store book
```

prints that store as stable, sorted lines, so a file from one run compares with the next. Whoever
reads a store needs no database user, password, file or query of their own.

### The street store

`store street` prints every account's rows, ordered bytewise:

```text
assumed|<account>|<instrument>|<side>
position|<account>|<instrument>|<side>|<quantity>|<settle-date quantity>|<market value> <currency>|<in-cash>
statement|<account>|<source>|<expected rows>|<complete or open>|<buying power>|<margin requirement>|<maintenance excess>|<currency assumed>
```

- `<account>` is the account's name, since its ID is minted per run.
- `<instrument>` is an `INS-` ID, or for a placeholder the identifiers it stands for, sorted:
  `placeholder(figi:BBG000B9XRY4, symbol:AAPL@snaptrade)`. In the harness every instrument is a
  placeholder, so name each expected row by the identifiers your plugin sent.
- A number is printed at the scale it was stated with. What was not reported is empty, never zero.
  `<in-cash>` is `in-cash` for a position the venue also counts in cash.
- `assumed` is a row of a latest statement whose currency the plugin assumed.
- `statement` is the latest statement of each source for each account. A statement none of whose
  rows was recorded, its account unlinked, belongs to no account and is not printed.

An account nothing links has no rows, so a file listing every account proves both what a linked
account holds and that an unlinked one holds nothing. Pair it with `unlinked`, which proves your
plugin reported the unlinked ones.

!!! tip "Wait for a complete statement"
    A changed setting and a new link each wake a plugin that reads on them. Poll `store street`
    until the statement you expect says `complete`, not merely until a row appears, or the
    comparison can catch one half recorded.

### The book of record

`store book` prints every account's [book](../concepts/the-book-of-record.md), ordered bytewise
within each kind of line:

```text
attributes|<account>|<base currency>|<lot relief>|<opening balance as of>
position|<account>|<instrument>|<side>|<trade date>|<settled>|<not stated>|<effective date>
pending|<account>|<instrument>|<side>|<value date>|<quantity>|<failing>
lot|<account>|<instrument>|<side>|<order opened>|<open>|<original>|<cost> <currency>|<acquired>|<source>
break|<account>|<subject>|<category>|<state>|<first seen>|<last seen>|<recorded by>|<confirmed cause>|<resolved by>
figures|<account>|<external account>/<segment>|<business date>
entry|<account>|<kind>|<effective date>|<actor>
```

- `<account>` and `<instrument>` as the street store prints them. No identifier the book mints, of
  an entry, a lot or a break, and no partition number or time is printed, so a file from one run
  compares with the next.
- `<not stated>` is 0 on every position a book at contract v9 records, and `<settled>` is set; on
  a position a v8 opening balance opened with some of its quantity not stated, `<settled>` is empty:
  unknown, never zero. A `pending` line with no value date is "date not stated", from a v8 opening
  balance or an adjustment the street gave no date for.
- An enum is printed as its number, 0 for none: `<lot relief>`, `<category>`, `<state>` (1 open,
  2 resolved, 3 closed), `<confirmed cause>` and `<source>`. `<resolved by>` is `entries`,
  `explanation` or `cleared`, empty while the break is open.
- `<recorded by>` and `<actor>` are a person's subject, such as `local|harness` for the harness's
  admin, `instance <id>` for a finding a plugin sent as itself, or `book` for the book's own act.
- Entries are listed in the order each account's were made.

A date the run decides, such as an opening balance's as of the statement it was composed from, can
differ from one day to the next: replace it with a fixed word, such as `D0`, before comparing.

## Worked example: SnapTrade's `make e2e`

[meridian-snaptrade](https://github.com/open-meridian/meridian-snaptrade) reads brokerage accounts
and holds the `custody` role. In synthetic mode it serves invented data for three connections with
no SnapTrade key. Its `make e2e` builds its image, then, on the harness its `Makefile` pins beside
the runtime, with itself as the one plugin, instance `snaptrade`:

1. waits for the plugin to register;
2. turns `synthetic` on in its settings form (a developer setting, accepted on the harness);
3. opens its Account links page under Manage until it lists Alpaca's account, `SYN-ALP-1001`;
4. posts that page's form to create an account **E2E Alpaca** linked to `ALPACA:SYN-ALP-1001`;
5. polls the street store until E2E Alpaca's statement is complete, and compares the store with
   `e2e/expected.street`;
6. checks that the dashboard counts two accounts reported and not linked.

The variables and the target, from its `Makefile`:

```makefile
RUNTIME_IMAGE ?= ghcr.io/open-meridian/meridian-runtime:<commit>@sha256:<digest>
HARNESS_IMAGE ?= ghcr.io/open-meridian/meridian-harness:<commit>@sha256:<digest>
# Its roles as pyproject.toml declares them, as `meridian plugin upload` would.
ROLES   := $(shell sed -n 's/^roles *= *\[\(.*\)\]/\1/p' pyproject.toml | tr -d ' ')
PLUGINS := [{"instance": "snaptrade", "image": "$(IMAGE)", "roles": [$(ROLES)]}]
E2E     := MERIDIAN_RUNTIME_IMAGE=$(RUNTIME_IMAGE) \
           docker compose -p snaptrade-e2e -f .e2e/harness/compose.yaml \
           -f .e2e/harness/plugins.yaml -f e2e/plugin.yaml
E2E_RUN    := $(E2E) run --rm -T runner
E2E_STREET := $(E2E) run --rm -T store street

e2e: image
	@rm -rf .e2e && mkdir -p .e2e
	@trap '$(E2E) down -v --remove-orphans >>.e2e/components.log 2>&1; rm -rf .e2e/harness' EXIT; \
	fail() { echo "e2e FAILED: $$1" >&2; $(E2E) logs --no-color >>.e2e/components.log 2>&1; exit 1; }; \
	id="$$(docker create $(HARNESS_IMAGE) none)" \
		&& docker cp "$$id:/harness" .e2e/harness >/dev/null \
		&& docker rm "$$id" >/dev/null || exit 1; \
	printf '%s\n' '$(PLUGINS)' >.e2e/plugins.json; \
	docker run --rm -i -v "$(CURDIR)/.e2e/harness":/harness:ro python:3.12-alpine \
		python /harness/harness.py compose <.e2e/plugins.json >.e2e/harness/plugins.yaml || exit 1; \
	$(E2E) down -v --remove-orphans >>.e2e/components.log 2>&1; \
	$(E2E) up -d >>.e2e/components.log 2>&1 || fail "the harness did not start"; \
	$(E2E_RUN) ready >>.e2e/runner.log || fail "the plugin never registered"; \
	$(E2E_RUN) settings synthetic=true >>.e2e/runner.log || fail "synthetic was not set"; \
	$(E2E_RUN) page --level admin /admin/accounts --until SYN-ALP-1001 >>.e2e/runner.log \
		|| fail "Account links never listed Alpaca's account"; \
	$(E2E_RUN) form --level admin --page /admin/accounts --post /admin/accounts/link \
		intent=create external_account_id=ALPACA:SYN-ALP-1001 'new_account_name=E2E Alpaca' \
		--expect "Created E2E Alpaca and linked" >>.e2e/runner.log \
		|| fail "the Account links form did not create and link E2E Alpaca"; \
	for i in $$(seq 1 60); do \
		$(E2E_STREET) >.e2e/street || fail "store street did not print the street store"; \
		grep -q '^statement|E2E Alpaca|snaptrade|[0-9]*|complete|' .e2e/street && break; \
		sleep 1; \
	done; \
	diff -u e2e/expected.street .e2e/street >&2 || fail "the street store is not e2e/expected.street"; \
	$(E2E_RUN) unlinked --expect 2 || fail "the dashboard did not count the two accounts left unlinked"
```

The repository's own target adds the elapsed time, a check of what the plugin kept on its read-only
root, and a few messages; the steps are these. `e2e/expected.street` is Alpaca's statement as the
synthetic data serves it, and nothing for the two accounts left unlinked:

```text
position|E2E Alpaca|placeholder(figi:BBG000B9XRY4, symbol:AAPL@snaptrade)|long|12.5|||
position|E2E Alpaca|placeholder(iso4217:CAD)|long|200.00||200.00 CAD|
position|E2E Alpaca|placeholder(iso4217:USD)|long|1523.45||1523.45 USD|
position|E2E Alpaca|placeholder(symbol:AAPL  261218C00250000@snaptrade)|long|2|||
position|E2E Alpaca|placeholder(symbol:BTC@snaptrade)|long|0.012345678|||
position|E2E Alpaca|placeholder(symbol:SYNXX@snaptrade)|long|500.00|||in-cash
position|E2E Alpaca|placeholder(symbol:ZZTOP@snaptrade)|short|-40|||
statement|E2E Alpaca|snaptrade|7|complete||||false
```

Every row names a placeholder by what SnapTrade sent: AAPL by its FIGI and symbol, the unresolvable
ZZTOP by its symbol, short, and the money-market fund also counted in cash. No position carries a
market value, since SnapTrade reports none, and the statement has no buying power, since Alpaca
reports two currencies.

To make your own expected file, run the target once with an empty one, read what it printed in
`.e2e/street` against the data your plugin served, row by row, and commit it once every row is
what you meant.

## Several plugins: an operations plugin beside a custody plugin

An `operations` plugin reconciles statements a custody plugin records, so its e2e runs both. List
them, the custody plugin first so the runner acts on it unless told otherwise:

```json
[
  {"instance": "snaptrade", "image": "snaptrade:local", "roles": ["custody"]},
  {"instance": "operations", "image": "my-operations:local", "roles": ["operations"]}
]
```

Then, after the custody plugin's statement is complete as above:

```bash
$H run --rm -T runner ready --instance operations
$H run --rm -T runner grant --instance operations --level write
$H run --rm -T runner page --instance operations --level write /opening --until 'Confirm'
$H run --rm -T runner form --instance operations --level write --page /opening --post /opening/confirm \
    --from-page account,statement,digest "reason=Checked against the custodian's statement." \
    --expect "Recorded"
$H run --rm -T store book >.e2e/book
diff -u e2e/expected.book .e2e/book
```

The paths, fields and words are your plugin's own: these confirm an opening balance on a page at
`write`, taking the proposal's account, statement and digest from the page as a person's browser
would, with the person's reason. An opening balance is a person's act, so it is sent for the
harness's admin, who needs `write` on the plugin; the book records `local|harness` as the entry's
actor. Compare the book once after confirming, and again after the next statement is reconciled.

core's own `make harness-check` is a working example with three stand-in plugins, one of them
restarted after failing first.

## Run it in CI

A job that runs the same target. The runtime and harness images and the harness's other images
pull without a token, so a synthetic run needs no secret:

```yaml
jobs:
  e2e:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
      - run: make e2e
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: e2e-logs
          path: .e2e/*.log
          if-no-files-found: ignore
```

To learn early that moving the pins will need work, run the same target weekly against both images'
`latest`, on `schedule` and `workflow_dispatch` only, so it blocks nothing:

```bash
make e2e RUNTIME_IMAGE=ghcr.io/open-meridian/meridian-runtime:latest \
         HARNESS_IMAGE=ghcr.io/open-meridian/meridian-harness:latest
```

## Related

- [Development deployments](../concepts/development-deployments.md): what a development
  deployment allows, and why the harness is one.
- [Record a holdings statement](../tutorials/record-a-holdings-statement.md): what a custody
  plugin sends, and how its rows reach the street store.
- [The book of record](../concepts/the-book-of-record.md): what `store book` prints, and how an
  operations plugin writes it.
- [Build a plugin's page](build-a-plugin-page.md): the pages the runner's `page` and `form` drive.
- [Release a plugin version](release-a-plugin.md): ship the change once it is proven.
