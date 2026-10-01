# Prove your plugin against a released runtime

A plugin's unit tests prove its own code. To prove that what it sends lands where it should, run
it beside a real sidecar, broker and street store, from a released runtime image, and compare the
store with what you expect. Every runtime image carries a deployment for exactly this: the
**plugin harness**. This page shows how to run your plugin on it from a `make e2e` target, with
[meridian-snaptrade](https://github.com/open-meridian/meridian-snaptrade)'s target as the worked
example.

!!! warning "A development deployment, for a test"
    The harness is never a way to run a deployment. It has no platform, so no instrument resolves
    and every row your plugin records names the deployment's placeholder. Its dashboard runs as a
    [development deployment](../concepts/development-deployments.md), so developer settings are
    shown and accepted. Its account, passwords and keys are fixed test values, it publishes no
    port, and nothing outlives `down -v`. To run a deployment,
    [install one](../getting-started/installation.md).

It names no plugin and adds nothing to the contract: your plugin reaches it only through its
sidecar, as it reaches any deployment.

## What you need

- Docker with Compose v2.
- Your plugin's image, built as `meridian plugin upload` builds it (from your `Dockerfile`).
- The plugin's roles, as `[tool.meridian]` in `pyproject.toml` declares them.
- A setting that lets the plugin produce known data without a vendor's credentials, such as a
  synthetic or sandbox mode. The harness holds no secret you do not give it.

## What is in the harness

The directory `/usr/share/meridian/harness/` in `ghcr.io/open-meridian/meridian-runtime`,
versioned with the binaries beside it:

| File | What it is |
|---|---|
| `compose.yaml` | The deployment: Postgres, NATS configured for one plugin instance and its roles, the stores migrated, street, instrument, conductor, a development dashboard, the plugin's sidecar, a `plugin` service running your image, and a `runner` |
| `harness.py` | The runner: does what an admin does in the dashboard (`ready`, `settings`, `account`, `page`, `form`, `unlinked`) |
| `street.sql` | Prints the street store as stable, sorted lines |
| `README.md` | The same reference as this page, for that image |

## 1. Pin a runtime image

Pin the image by tag and digest. The tag says which core; the digest makes it immutable, so your
e2e never changes under you:

```bash
docker pull ghcr.io/open-meridian/meridian-runtime:<commit>
docker image inspect --format '{{index .RepoDigests 0}}' ghcr.io/open-meridian/meridian-runtime:<commit>
```

```makefile
RUNTIME_IMAGE ?= ghcr.io/open-meridian/meridian-runtime:<commit>@sha256:<digest>
```

The image pulls without a token. Choose one whose contract version is your SDK's: a sidecar
refuses an SDK of another contract version. Move the pin by a deliberate commit, and with your SDK
when a contract version changes.

## 2. Copy the harness out of that image

Any command will do for `create`; it is never run:

```bash
id=$(docker create "$RUNTIME_IMAGE" none)
docker cp "$id:/usr/share/meridian/harness" .e2e/harness
docker rm "$id"
```

Add `.e2e/` to `.gitignore` and `.dockerignore`, and remove the copy when the run ends, however it
ends: `meridian plugin check` reads every source file under your plugin's directory, and the
harness's runner is not your plugin.

## 3. Give every compose command its three variables

Compose reads the whole file on every command, `down` and `run` included, so each one needs all
three:

| Variable | Value |
|---|---|
| `MERIDIAN_RUNTIME_IMAGE` | The image you copied the harness from, so the file never guesses its own tag. |
| `MERIDIAN_HARNESS_PLUGIN_IMAGE` | Your plugin's image. |
| `MERIDIAN_HARNESS_PLUGIN_ROLES` | Its roles, comma separated, as it declares them; empty for a plugin holding none. A name that is not a role stops the run at `broker-config`, naming it. |

Name the project after your plugin with `-p`, so two harnesses never share one:

```bash
H="docker compose -p my-plugin-e2e -f .e2e/harness/compose.yaml"
```

Your plugin runs as instance `plugin-1`, in its sidecar's network namespace, and reaches the
sidecar at `127.0.0.1:9191` (`MERIDIAN_SIDECAR_ADDRESS`), as it would in a deployment. To give it
environment, a command or a volume, add a compose file of your own that overrides the `plugin`
service (`-f .e2e/harness/compose.yaml -f e2e/plugin.yaml`), with any path in it absolute: a second
file's relative paths resolve against the first file's directory.

The harness starts your plugin beside its sidecar without waiting for the rest of the deployment.
In a deployment, a plugin that exits with an error is started again by its pod; if yours makes a
call at start that the conductor answers, such as reading its links, give it the same in your
override:

```yaml
# e2e/plugin.yaml
services:
  plugin:
    restart: on-failure
```

## 4. Drive it as an admin would

The runner signs in as the deployment's admin, the dashboard's local account `harness`, and does one
thing per command:

```bash
$H run --rm -T runner <command>
```

Each prints what it found and exits 0, or exits non-zero saying why. Every wait is bounded by
`--seconds`.

| Command | What it does |
|---|---|
| `ready [--seconds N]` | Waits until the plugin has registered and the dashboard lists it, healthy or not. The first command of a run. |
| `settings NAME=VALUE ... [--seconds N]` | Sets the plugin's settings in its settings form, once it has declared each; a secret in its secret field. A developer setting is accepted. |
| `account NAME [--seconds N]` | Defines an account and prints its ID, for a page that links only to an account that exists. |
| `page --level admin\|write\|read PATH [--until TEXT] [--seconds N]` | Opens a session on the plugin's own host at that level (Manage, Open, View), GETs `PATH`, prints the status and the body; with `--until`, again until the body says `TEXT`. |
| `form --level L --page PATH --post PATH [--csrf-field NAME] [--expect TEXT] FIELD=VALUE ...` | In such a session, reads `--page`, takes its CSRF field (`csrf`, the SDK's name), posts the fields to `--post`, prints the status and the body. With `--expect`, fails unless the body says `TEXT`. A 4xx or 5xx fails. |
| `unlinked [--expect N] [--seconds N]` | Prints how many external accounts the plugin reported that nothing links, as the dashboard counts them; with `--expect`, waits for `N`. |

A link is the plugin's to send, acting for an admin, so the harness never sends one: `form` drives
your plugin's own link page under Manage, which also proves that the page links. See
[Build a plugin's page](build-a-plugin-page.md#to-link-external-accounts-om-account-map).

## 5. Read the street store

```bash
$H exec -T postgres psql -U meridian -d meridian -At -v ON_ERROR_STOP=1 -f /harness/street.sql
```

prints every account's rows, ordered bytewise:

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
    A changed setting and a new link each wake a plugin that reads on them. Poll `street.sql` until
    the statement you expect says `complete`, not merely until a row appears, or the comparison can
    catch one half recorded.

## Worked example: SnapTrade's `make e2e`

[meridian-snaptrade](https://github.com/open-meridian/meridian-snaptrade) reads brokerage accounts
and holds the `custody` role. In synthetic mode it serves invented data for three connections with
no SnapTrade key. Its `make e2e` builds its image, then, on the harness of the runtime its `Makefile`
pins, with `e2e/plugin.yaml` restarting the plugin as a pod would:

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
# Its roles as pyproject.toml declares them, as `meridian plugin upload` would.
ROLES := $(shell sed -n 's/^roles *= *\[\(.*\)\]/\1/p' pyproject.toml | tr -d '" ')
E2E     := MERIDIAN_RUNTIME_IMAGE=$(RUNTIME_IMAGE) MERIDIAN_HARNESS_PLUGIN_IMAGE=$(IMAGE) \
           MERIDIAN_HARNESS_PLUGIN_ROLES=$(ROLES) \
           docker compose -p snaptrade-e2e -f .e2e/harness/compose.yaml -f e2e/plugin.yaml
E2E_RUN := $(E2E) run --rm -T runner
E2E_STREET := $(E2E) exec -T postgres psql -U meridian -d meridian -At -v ON_ERROR_STOP=1 -f /harness/street.sql

e2e: image
	@rm -rf .e2e && mkdir -p .e2e
	@trap '$(E2E) down -v --remove-orphans >>.e2e/components.log 2>&1; rm -rf .e2e/harness' EXIT; \
	fail() { echo "e2e FAILED: $$1" >&2; $(E2E) logs --no-color >>.e2e/components.log 2>&1; exit 1; }; \
	id="$$(docker create $(RUNTIME_IMAGE) none)" \
		&& docker cp "$$id:/usr/share/meridian/harness" .e2e/harness >/dev/null \
		&& docker rm "$$id" >/dev/null || exit 1; \
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
		$(E2E_STREET) >.e2e/street || fail "street.sql did not run"; \
		grep -q '^statement|E2E Alpaca|snaptrade|[0-9]*|complete|' .e2e/street && break; \
		sleep 1; \
	done; \
	diff -u e2e/expected.street .e2e/street >&2 || fail "the street store is not e2e/expected.street"; \
	$(E2E_RUN) unlinked --expect 2 || fail "the dashboard did not count the two accounts left unlinked"
```

The repository's own target adds the elapsed time and a few messages; the steps are these.
`e2e/expected.street` is Alpaca's statement as the synthetic data serves it, and nothing for the
two accounts left unlinked:

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

## Run it in CI

A job that runs the same target. The runtime image and the harness's other images pull without a
token, so a synthetic run needs no secret:

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

To learn early that moving the pin will need work, run the same target weekly against the
runtime's `latest`, on `schedule` and `workflow_dispatch` only, so it blocks nothing:

```bash
make e2e RUNTIME_IMAGE=ghcr.io/open-meridian/meridian-runtime:latest
```

## Related

- [Development deployments](../concepts/development-deployments.md): what a development
  deployment allows, and why the harness is one.
- [Record a holdings statement](../tutorials/record-a-holdings-statement.md): what a custody
  plugin sends, and how its rows reach the street store.
- [Build a plugin's page](build-a-plugin-page.md): the link page the runner's `form` drives.
- [Release a plugin version](release-a-plugin.md): ship the change once it is proven.
