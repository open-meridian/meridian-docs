# Prove your plugin against a released runtime

A plugin's unit tests prove its own code. To prove that what it sends lands where it should, run
it beside a real sidecar, broker, street store and book, from a released runtime image, and compare
the stores with what you expect. Core publishes a deployment for exactly this beside every runtime
image: the **plugin harness**. This page shows how to run your plugin on it from a `make e2e`
target, with [plugin-snaptrade](https://github.com/open-meridian/plugin-snaptrade)'s target as
the worked example.

!!! warning "A development deployment, for a test"
    The harness is never a way to run a deployment. Its platform is a stand-in that knows only the
    instruments you seed it with, so anything else your plugin records stays a provisional local
    record. Its dashboard runs as a
    [development deployment](../concepts/development-deployments.md), so developer settings are
    shown and accepted. It publishes no port, and nothing outlives
    `docker compose … --profile runner down -v` (see [step 4](#4-give-every-compose-command-both-files-and-the-runtime)).
    To run a deployment, [install one](../getting-started/installation.md).

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
| `compose.yaml` | The deployment without its plugins: `keys`, which draws the run's keys and passwords; Postgres; NATS configured for the plugins, their roles and their datasets; the stores migrated; street, the book (`bor`), the lake, instrument, the stand-in `platform`, conductor, `people` and a development dashboard; and, in the compose profile `runner`, the `runner` and `store` |
| `harness.py` | The runner, standard library only: does what an admin does in the dashboard (the commands in [step 5](#5-drive-it-as-an-admin-would)); and `compose`, which writes the plugins' half of the deployment |
| `platform.py` | The stand-in for the platform, standard library only: the currencies, seed settlement calendars, venues and test equity it holds, and contract v24's one-ID routes |
| `street.sql` | The street store as stable, sorted lines, which `store street` prints |
| `book.sql` | The book of record as stable, sorted lines, which `store book` prints |
| `activity.sql` | The custodian's activity and each connection's latest sync status, which `store activity` prints |
| `lake.sql` | The lake's rows, priorities, wants, servings, removals, misses and aliases, never a value, which `store lake` prints |
| `moves.sql` | An edge plugin's moves of its raw records, the holds and archives a deployment admin set, and each setting change, never a record's content or a setting's value, which `store moves` prints |
| `tickets.sql` | The dashboard's tickets, the records they name and their notes, never a text, which `store tickets` prints |
| `README.md` | The same reference as this page, for that commit |

`harness.py compose` writes a further file, `plugins.yaml`, beside them ([step 3](#3-write-the-plugins)).

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
ends: the harness's runner is not your plugin. `meridian plugin check` reads nothing under `.e2e/`
and `meridian plugin dev` sends nothing from it.

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
- `archive`, where given, is `true`, and only for a plugin holding an edge role.
- `declaration`, where given, is the file its registration is held to (below).
- The first plugin listed is the one the runner acts on when a command names no `--instance`.

**A plugin is started again whenever it exits failing**, as a pod's container is. The harness starts
each plugin beside its sidecar without waiting for the rest of the deployment, so a plugin whose
first call reaches its sidecar before the deployment serves is refused, exits, and finds it serving
on its next start. You need no override for that.

### Hold each registration to its declaration { #hold-each-registration-to-its-declaration }

From contract v25 a plugin declaring v25 registers exactly the declaration its version was uploaded
with, or its sidecar refuses it, naming the first difference. The harness performs no upload, so
list each plugin with `"declaration": PATH`, and its sidecar holds it to that file instead: the
SDK's JSON as `meridian-declaration` prints it from the plugin's own image, which is what
`meridian plugin upload` sends. Print it before writing the compose file, beside it, from the image
under test:

```bash
docker run --rm --network none --entrypoint meridian-declaration <image> \
    <module:attribute> >.e2e/harness/declaration.json
```

```json
[
  {"instance": "snaptrade", "image": "snaptrade:local", "roles": ["custody", "connectivity"],
   "declaration": "declaration.json"}
]
```

`<module:attribute>` is what `[tool.meridian]`'s `declaration` names. PATH is relative to the
directory of the first compose file (`.e2e/harness/`), or absolute, a path with no space, colon or
`$`. A plugin listed without one registers unchecked, as on any sidecar no launch made; with one,
the e2e proves that what it registers is what its upload would declare. Give a stand-in run beside
your plugin a declaration of its own the same way.

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

Name the project after your plugin with `-p`, so two harnesses never share one. A shell function
saves writing the files out each time, and works in bash and zsh alike:

```bash
export MERIDIAN_RUNTIME_IMAGE=$RUNTIME_IMAGE
e2e() {
  docker compose -p my-plugin-e2e -f .e2e/harness/compose.yaml -f .e2e/harness/plugins.yaml "$@"
}
```

A variable holding the command, `H="docker compose …"` run as `$H up -d`, works in bash but not
in zsh, which does not split a variable's value into words: zsh answers
`command not found: docker compose …`. In a `Makefile`, a variable is expanded before the shell
reads it, so the worked example below uses one.

Start the run with `e2e up -d`. End it, however it ends, with:

```bash
e2e --profile runner down -v --remove-orphans
```

`--profile runner` matters. The `runner` and `store` services are in that compose profile, so
`up` never starts them, and a `down` without the profile leaves the volume only the runner mounts,
`runner-state`, where an MCP client's tokens are kept between commands. With it, `down -v` removes
every volume of the run.

## Keys and passwords

None is written in the harness. When the run starts, `keys` draws at random the dashboard's signing
key, the key secret settings are sealed with, the database's password, a password for each broker
user, and the admin's password with its Argon2id hash. They live in the run's volumes until
`e2e --profile runner down -v`. The dashboard makes its one local account, `harness`, from the
hash at its start, and the conductor names that account the deployment's admin, as first run names
one. The runner signs in
with the password, read from the run's volume and never printed; your plugin's container does not
mount it. Nothing you write needs a password: whoever reads a store uses `store`.

## 5. Drive it as an admin would

The runner signs in as the deployment's admin, `harness`, and does one thing per command:

```bash
e2e run --rm -T runner <command>
```

Each prints what it found and exits 0, or exits non-zero saying why. Every wait is bounded by
`--seconds`. Every command acts on the first plugin listed, or on another with
`--instance <instance>`.

| Command | What it does |
|---|---|
| `ready [--seconds N]` | Waits until the plugin has registered and the dashboard lists it, healthy or not. The first command of a run, once for each plugin. |
| `settings NAME=VALUE ... [--seconds N] [--expect TEXT]` | Sets the plugin's settings in its settings form, as its admin does, once it has declared each; a secret in its secret field. A developer setting is accepted. A [table setting](set-a-plugins-settings.md#a-table-setting)'s cell is `NAME[ROW].COLUMN=VALUE`, the rows given being the table's whole, found on the table's own tab, and `--expect` reads the Settings tab after saving and fails unless it says `TEXT`, such as who last changed them. |
| `account NAME [--seconds N]` | Defines an account and prints its ID, for a page that links only to an account that exists. |
| `grant --level read\|write\|admin [--role ROLE]` | Grants the admin that level on the plugin, on All accounts, as a deployment admin does: a user group holding the admin, an access group, and the permission joining them. The grant is on one of the plugin's roles: `--role` names it, else the plugin's one role, or the plugin as a whole where it holds none. |
| `page --level admin\|write\|read PATH [--until TEXT] [--seconds N]` | Opens a session on the plugin's own host at that level (Manage, Open, View), GETs `PATH`, prints the status and the body; with `--until`, again until the body says `TEXT`. |
| `form --level L --page PATH --post PATH [--csrf-field NAME] [--from-page NAME ...] [--expect TEXT] FIELD=VALUE ...` | In such a session, reads `--page`, takes its CSRF field (`csrf`, the SDK's name) and each field `--from-page` names, with the value the page gives it, and posts them with the fields you give to `--post`; prints the status and the body. |
| `unlinked [--expect N] [--seconds N]` | Prints how many external accounts the plugin reported that nothing links, as the dashboard counts them; with `--expect`, waits for `N`. |
| `licence DATASET kept=true\|false retention_days=N derived_use=true\|false display=true\|false personal_use=true\|false [default_fields=A,B] [note=TEXT]` | Sets a dataset's licence on the Data sources page, as a deployment admin does, replacing it whole; a term left out is false. See [License and entitle a dataset](license-and-entitle-a-dataset.md). |
| `entitle DATASET [--fields A,B] [--withdraw] [note=TEXT]` | Entitles the plugin to a dataset, every field or those named, or withdraws it, and waits until the bus admits the plugin to the dataset's subject before the entitlement is recorded. |
| `priority DATA_TYPE [--kind KIND] DATASET ... [note=TEXT] [--against N]` | Sets the priority a default read takes for `meridian.v1.Price`, one kind of it (`close`, `last`, `nav`, `settlement`), or `meridian.v1.Bar`: the datasets first to last, replaced whole, against the priority as the page shows it. |
| `service-account create NAME --owner PERSON [--setting prepare_only\|act] [--purpose TEXT]`, `set SA [--setting ...] [--name NAME] [--owner PERSON]`, `disable\|enable\|remove SA`, `grant SA --role ROLE --level read\|write`, `runs-as (SA \| none) --role ROLE [--level write\|read]`, `list` | A [service account](../concepts/service-accounts.md), as a deployment admin makes it on Settings' Service accounts tab: created with a name, an owner (one of the run's people, or `harness`) and a setting, prepare only unless `--setting act`, its `SA-` ID printed; changed; disabled (by its owner too), re-enabled or removed. `grant` grants it a level on one of the plugin's roles, on All accounts, by its ID in a user group's logins; `runs-as` chooses, on the plugin's Access tab, what the role's autonomous work runs as, or none; `list` prints each account's ID, name, setting and state. With `--expect-refused TEXT`, fails unless the change is refused saying `TEXT`. |

The runner also takes
`connectivity available [--withdraw] [--note TEXT]` and `connectivity link --ems EMS
[--user person:SUBJECT ...] [--note TEXT]`, which make the plugin available, or withdraw it, as a
deployment admin does, and link it to an `ems` with who may route through it, people by subject,
service accounts as `account:SA-...` and user groups as `group:...`, as the `ems`'s admin does (see
[Route orders through a connectivity plugin](route-orders-through-a-connectivity-plugin.md));
`instruction active|pause|stop (--all | --account ID | --plugin ID | --person SUBJECT |
--service-account SA) [--within PLUGIN] note=TEXT [--expect-refused TEXT]`, which sets a trading
instruction at the Trading instructions page, as a deployment admin on any target or a plugin's
admin within their plugin, and prints what the page then lists for it; and `attribute ACCOUNT
waits=true|false note=TEXT [--expect-refused TEXT]`, whether the account's releases wait for
compliance (see [Set trading instructions](set-trading-instructions.md)).

The harness's stand-in for the platform also holds the seed
[settlement calendars](../concepts/settlement-calendars.md) and the US equities rule, the XNYS and
XNAS venue records, and one test equity, Apple Inc., with XNAS, where it lists, as its listing
venue. The runner's `instrument` command takes `--ask-platform`, asking the platform about a
record from its page as a deployment admin's button does, so a `compute_date` for that equity
gives its settlement date in a harness run (T+1) rather than "rule not held".

!!! note "TODO: contract v25's runtime and harness"
    Replace the pins below with core's v25 runtime and harness, released in chart
    `0.1.CHART25`, by commit and digest, and say what else the harness's stand-ins add for
    contract v25 (any stand-in registry `e2e-plugin-area` gains), from core as released. Each
    registration held to its declaration is in
    [Hold each registration to its declaration](#hold-each-registration-to-its-declaration).

Core 6eb6887's runtime and harness serve contract v24, released 2026-10-15 in chart 0.1.305,
pinned by digest as in [step 1](#1-pin-a-runtime-image-and-its-harness):

```makefile
RUNTIME_IMAGE ?= ghcr.io/open-meridian/meridian-runtime:6eb6887@sha256:68d54f7b0218e3aec9d2c2aa899533a068c458b253c12ac3da08a6b573a76fab
HARNESS_IMAGE ?= ghcr.io/open-meridian/meridian-harness:6eb6887@sha256:5eff46fe1ccc08ad380d9fbd27511bfa134f1277332667c50f8d2825c54849d5
```

Its stand-in for the platform answers contract v24's one-ID routes: the
matching and minting request, the template catalogue, the licence list,
the replacement feed and the usage reports. It mints a record only for a
FIGI its source confirms, so a record your plugin states with another
identifier alone stays a provisional local record, as in a deployment. In
the harness's environment, `HARNESS_LICENCE` names the licence list's
schemes, `HARNESS_PLATFORM_MINTS` the FIGIs its source confirms, and
`HARNESS_PLATFORM_V24=0` serves none of the routes, as a platform before
contract v24, which the deployment treats as not reached. The runner's
`instrument ID --ask-platform`, with nothing else, asks the platform about
a record and completes nothing, so a provisional record the platform holds
resolves; and a new command, `core-form PAGE POST FIELD=VALUE...
[--expect-refused TEXT]`, posts one of core's own forms as the deployment
admin, PAGE read for its form token and a FIELD given more than once sent
once for each: the setting **Allow orders on local records**, the usage
report's, an account's **Close**, or the migration's lines.

The commands above are its `README.md`'s.

The stand-in for the platform also serves the euro's
TARGET calendar and a EUR/USD spot-date rule as the platform keeps such a rule (lag 2 counted on
TARGET alone, the spot date good on TARGET and the US dollar's calendar, cut 17:00 New York), so
EUR/USD traded Friday 9 October 2026 spots on Tuesday 13 October; and `store lake` prints an
outcome's row as `outcome`, beside price, bar, trade and quote.

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
e2e run --rm -T store street
e2e run --rm -T store book
```

prints that store as stable, sorted lines, so a file from one run compares with the next. Whoever
reads a store needs no database user, password, file or query of their own.

`store lake` prints what the
[lake](../concepts/the-lake.md) kept, one line each: every row version (its dataset, data type,
sequence, row key, version, subject, kind or interval, venue, business date and how many values
were left unconverted), each priority's changes, each want asked, answered, declined or withdrawn,
each serving of a dataset not kept, each removal, each instance's misses and each alias. Never a
value: a price or a bar is read through a reading role, under its entitlements.

### The street store

`store street` prints every account's rows, ordered bytewise:

```text
assumed|<account>|<instrument>|<side>
position|<account>|<instrument>|<side>|<quantity>|<settle-date quantity>|<market value> <currency>|<in-cash>
statement|<account>|<source>|<expected rows>|<complete or open>|<buying power>|<margin requirement>|<maintenance excess>|<currency assumed>
pending|<account>|<instrument>|<side>|<value date>|<quantity>
closed|<account>|<instrument>|<side>|<field>|<kind>
amended|<account>|<instrument>|<side>|<contract version>|<field>|<raw record's key>
```

- `<account>` is the account's name, since its ID is minted per run.
- `<instrument>` takes one of two forms:
    - an `INS-` ID, for the platform's record, such as a currency the stand-in for the platform
      holds;
    - for a record the deployment minted, whose `LCL-` ID is drawn per run, its identifiers in
      force, sorted, as `local(<scheme>:<value>[@<source>], ...)`: `local(symbol:ACME@demo)` for
      one symbol a source scoped, `local(figi:BBG000B9XRY4, symbol:AAPL@snaptrade)` for a record
      holding two identifiers.

    The stand-in mints only for a FIGI its source confirms, so in the harness nearly every
    security your plugin records is a minted record: name each expected row by the identifiers
    your plugin sent.
- A number is printed at the scale it was stated with. What was not reported is empty, never zero.
  `<in-cash>` is `in-cash` for a position the venue also counts in cash.
- `assumed` is a row of a latest statement whose currency the plugin assumed.
- `pending` is a position's quantity not yet settled, by its value date. `closed` is a value of a
  position the custody plugin closed rather than read, by its path in the row (`quantity`,
  `settle_date_quantity`, `market_value.currency_code`), with its provenance's kind (`derived`,
  `supplied`, `second-source`, `reported`). `amended` is a backfill journaled beside a row of a
  latest statement: the version and field that are its cause, and the key of the raw record it
  was re-converted from.
- `statement` is the latest statement of each source for each account. A statement none of whose
  rows was recorded, its account unlinked, belongs to no account and is not printed.

For example, the plugin of [Record a holdings statement](../tutorials/record-a-holdings-statement.md),
run on the harness with `DEMO-ACCT-2` linked to an account named `Demo retirement account`, leaves
these two lines for that account, its ACME holding under the record the deployment minted for the
symbol the source scoped:

```text
position|Demo retirement account|local(symbol:ACME@demo)|long|12.5||2812.50 USD|
statement|Demo retirement account|demo|1|complete|1000.00 USD|||false
```

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
order|<account>|<instrument>|<sleeve>|<side>|<ordered>|<state>|<parent's instrument, or top>
placement|<account>|<instrument>|<connectivity instance>|<quantity>|<state>
execution|<account>|<instrument>|<sleeve>|<quantity>|<price>|<trade date>|<superseding or empty>
unplaced|<account, empty for none>|<fact kind>|<reason>|<instance>|<placed>
instruction|<partition>|<value>|<setter level>
```

- The [order path](../concepts/the-order-lifecycle.md)'s records print too, the last five kinds; `<side>`, `<state>`, `<reason>`, `<value>` and `<setter
  level>` are their enums' numbers. A book holding no orders prints none of them.

- `<account>` and `<instrument>` as the street store prints them. No identifier the book mints, of
  an entry, a lot or a break, and no partition number or time is printed, so a file from one run
  compares with the next.
- `<not stated>` is 0 on every position the book records now, and `<settled>` is set; on a
  position an older opening balance opened with some of its quantity not stated, `<settled>` is
  empty: unknown, never zero. A `pending` line with no value date is "date not stated", from such an
  opening balance or an adjustment the street gave no date for.
- An enum is printed as its number, 0 for none: `<lot relief>`, `<category>`, `<state>` (1 open,
  2 resolved, 3 closed), `<confirmed cause>` and `<source>`. `<resolved by>` is `entries`,
  `explanation` or `cleared`, empty while the break is open.
- `<recorded by>` and `<actor>` are a person's subject, such as `local|harness` for the harness's
  admin, `instance <id>` for a finding a plugin sent as itself, `service account <SA- ID> owned by <subject>` for an act a plugin's autonomous work made
  as its role's service account, or `book` for the book's own act.
- Entries are listed in the order each account's were made.

A date the run decides, such as an opening balance's as of the statement it was composed from, can
differ from one day to the next: replace it with a fixed word, such as `D0`, before comparing.

## Worked example: SnapTrade's `make e2e`

[plugin-snaptrade](https://github.com/open-meridian/plugin-snaptrade) reads brokerage accounts
and places orders at them: it holds the `custody` and `connectivity` roles. With its developer
setting **Sample data** on, it serves invented data for its connections and trades with a simulated
brokerage, with no SnapTrade key. Its `make e2e` builds its image, prints the declarations the
harness holds each registration to, then runs it on the harness its `Makefile` pins beside the
runtime, as instance `snaptrade` with the roles `pyproject.toml` declares and the harness's
archive, beside a desk stand-in from the same image (`e2e/desk.py`, holding `portfolio`, `oms`,
`ems` and `reporting`). The first steps:

1. waits for the plugin to register;
2. turns `sample_data` on in its settings form (a developer setting, accepted on the harness);
3. opens its Account links page under Manage until it lists Alpaca's account, `SYN-ALP-1001`;
4. posts that page's form to create an account **E2E Alpaca** linked to `ALPACA:SYN-ALP-1001`;
5. polls the street store until E2E Alpaca's statement is complete, and compares the store with
   `e2e/expected.street`;
6. checks that the dashboard counts three accounts reported and not linked.

The repository's target goes on from there: the custodian's activity against
`e2e/expected.activity`, the raw responses kept on a read-only root, a plan's own fund code linked
and re-resolved, a deposit counted as cash, raw records archived past their window, restored and
held, and then the order path with the desk (`e2e/orders.py`). Its variables and the target's first
steps, after its `Makefile`, each `down` naming `--profile runner` so that it removes every volume
of the run:

```makefile
RUNTIME_IMAGE ?= ghcr.io/open-meridian/meridian-runtime:<commit>@sha256:<digest>
HARNESS_IMAGE ?= ghcr.io/open-meridian/meridian-harness:<commit>@sha256:<digest>
# Its roles as pyproject.toml declares them, as `meridian plugin upload` would.
ROLES   := $(shell sed -n 's/^roles *= *\[\(.*\)\]/\1/p' pyproject.toml | tr -d ' ')
# The declaration [tool.meridian] names, printed from the image under test, as upload reads it.
DECLARATION_REF := $(shell sed -n 's/^declaration *= *"\(.*\)"/\1/p' pyproject.toml)
DECLARE := docker run --rm --network none --entrypoint meridian-declaration
PLUGINS := [{"instance": "snaptrade", "image": "$(IMAGE)", "roles": [$(ROLES)], "archive": true, \
             "declaration": "declaration.json"}, \
            {"instance": "desk", "image": "$(IMAGE)", "roles": ["portfolio", "oms", "ems", "reporting"], \
             "declaration": "desk.json"}]
E2E     := MERIDIAN_RUNTIME_IMAGE=$(RUNTIME_IMAGE) E2E_DIR=$(CURDIR)/e2e \
           docker compose -p snaptrade-e2e -f .e2e/harness/compose.yaml \
           -f .e2e/harness/plugins.yaml -f e2e/plugin.yaml
E2E_RUN    := $(E2E) run --rm -T runner
E2E_STREET := $(E2E) run --rm -T store street

e2e: image
	@rm -rf .e2e && mkdir -p .e2e
	@trap '$(E2E) --profile runner down -v --remove-orphans >>.e2e/components.log 2>&1; rm -rf .e2e/harness' EXIT; \
	fail() { echo "e2e FAILED: $$1" >&2; $(E2E) logs --no-color >>.e2e/components.log 2>&1; exit 1; }; \
	id="$$(docker create $(HARNESS_IMAGE) none)" \
		&& docker cp "$$id:/harness" .e2e/harness >/dev/null \
		&& docker rm "$$id" >/dev/null || exit 1; \
	$(DECLARE) $(IMAGE) $(DECLARATION_REF) >.e2e/harness/declaration.json || exit 1; \
	$(DECLARE) -v "$(CURDIR)/e2e":/e2e:ro -e PYTHONPATH=/e2e $(IMAGE) desk:DECLARATION \
		>.e2e/harness/desk.json || exit 1; \
	printf '%s\n' '$(PLUGINS)' >.e2e/plugins.json; \
	docker run --rm -i -v "$(CURDIR)/.e2e/harness":/harness:ro python:3.12-alpine \
		python /harness/harness.py compose <.e2e/plugins.json >.e2e/harness/plugins.yaml || exit 1; \
	$(E2E) --profile runner down -v --remove-orphans >>.e2e/components.log 2>&1; \
	$(E2E) up -d >>.e2e/components.log 2>&1 || fail "the harness did not start"; \
	$(E2E_RUN) ready >>.e2e/runner.log || fail "the plugin never registered"; \
	$(E2E_RUN) settings sample_data=true >>.e2e/runner.log || fail "sample data was not set"; \
	$(E2E_RUN) page --level admin /admin/accounts --until SYN-ALP-1001 >>.e2e/runner.log \
		|| fail "Account links never listed Alpaca's account"; \
	$(E2E_RUN) form --level admin --page /admin/accounts --post /admin/accounts/link \
		intent=create external_account_id=ALPACA:SYN-ALP-1001 'new_account_name=E2E Alpaca' \
		--expect "Created E2E Alpaca and linked" >>.e2e/runner.log \
		|| fail "the Account links form did not create and link E2E Alpaca"; \
	for i in $$(seq 1 90); do \
		$(E2E_STREET) >.e2e/street || fail "store street did not print the street store"; \
		grep -q '^statement|E2E Alpaca|snaptrade|[0-9]*|complete|' .e2e/street && break; \
		sleep 1; \
	done; \
	diff -u e2e/expected.street .e2e/street >&2 || fail "the street store is not e2e/expected.street"; \
	$(E2E_RUN) unlinked --expect 3 || fail "the dashboard did not count the three accounts left unlinked"
```

From contract v25 a plugin registers exactly the declaration its version was uploaded with, so a
stand-in run beside it, such as the desk, registers its interface in a declaration too,
`meridian.connect(declaration=meridian.Declaration(interface=...))`, and the target prints the
stand-in's declaration from the same image, its directory mounted, as it prints the plugin's (see
[Hold each registration to its declaration](#hold-each-registration-to-its-declaration)).

`e2e/expected.street` holds Alpaca's statement and its rows as the sample data serves them, in the
forms [above](#the-street-store), and nothing for the accounts left unlinked: each row names its
instrument by what SnapTrade sent, a security by its identifiers in a `local(...)` form, and what
SnapTrade does not report is empty.

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
e2e run --rm -T runner ready --instance operations
e2e run --rm -T runner grant --instance operations --level write
e2e run --rm -T runner page --instance operations --level write /opening --until 'Confirm'
e2e run --rm -T runner form --instance operations --level write --page /opening --post /opening/confirm \
    --from-page account,statement,digest "reason=Checked against the custodian's statement." \
    --expect "Recorded"
e2e run --rm -T store book >.e2e/book
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
