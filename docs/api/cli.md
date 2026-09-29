# Command line

`meridian` is Open Meridian's command line. It brings a deployment up where you have a terminal, signs you in to one that is already running, and brings plugins into it: uploading, launching, stopping, and developing them live.

Nothing in a cloud install depends on it. A marketplace listing's form and the deployment's own wizard are the whole path there; `meridian` makes the same things convenient from a terminal.

This page describes release 0.1.14 of the command line. `meridian --version` says which one you have. For installing it, see [Install a deployment](../getting-started/installation.md).

## Synopsis

```text
meridian doctor
meridian up --id <id> [options]
meridian down [--release <name>] [--delete-namespace]
meridian upgrade-deployment [--release <name>] [--chart-version <v>] [options]
meridian connect [<address>]
meridian sign-out [<address>]
meridian plugin new <name> [--into <dir>]
meridian plugin upload [--dir <dir>]
meridian plugin list
meridian plugin launch <name> <version> --instance <id> [--yes]
meridian plugin stop <id>
meridian plugin dev --instance <id> [--dir <dir>] [--yes] [--json] [--release]
meridian plugin logs --instance <id> [--since <revision>] [--json]
meridian plugin events --instance <id> [--since <revision>] [--follow] [--json]
meridian plugin open --instance <id> [--print <path>] [--json]
meridian upgrade [--to <version>]
meridian uninstall [--yes]
meridian --version
meridian --help
```

## How arguments are read

- A flag that takes a value may be written either way: `--params first-run.yaml` or `--params=first-run.yaml`.
- An unknown flag is refused, not ignored, and so is a stray word after a command that takes none. `meridian up --no-docter` exits 2 rather than installing without the checks.
- A flag given with nothing after it is refused rather than defaulted.
- When a flag is given twice, the last one counts. The exception is `-f`/`--values`: every one is kept, in the order given.
- `--release` means two different things. After `up`, `down` or `upgrade-deployment` it takes a value, the Helm release's name. After `plugin` it takes none, and `plugin dev --release` releases the code as a version.

## Global options

These are read before any command runs.

| Flag | Argument | Default | Meaning |
|---|---|---|---|
| `-n`, `--namespace` | `<name>` | `meridian` | The Kubernetes namespace the deployment goes in. Used by `doctor`, `up`, `down` and `upgrade-deployment`. |
| `--platform` | `<url>` | `https://open-meridian.com` | The platform the deployment reports to. Used by `doctor` and `up`. `up` passes it to the chart only when you give it. |
| `--image` | `<ref>` | `ghcr.io/open-meridian/meridian-runtime:latest` | The runtime image. Used by `doctor` and `up`. `up` passes it to the chart only when you give it. |
| `-h`, `--help` | | | Print the usage text and exit 0. |
| `-v` | | | Reserved for verbose output, which is not built yet. It prints a note saying so and is otherwise ignored. |

## Exit codes

Every command exits 0 when it succeeds. What a non-zero code means depends on the command:

| Code | Meaning |
|---|---|
| `0` | Done. |
| `1` | Refused or failed. The reason is on stderr. |
| `2` | Asked wrongly: an unknown command or flag, a missing argument, or an argument of the wrong form. Nothing was done. |
| `3` | `plugin` commands that act on a deployment (`upload`, `list`, `launch`, `stop`, `dev`, `logs`, `events`, `open`): there is no session, or it has lapsed. The message names the `meridian connect` to run. |

A `plugin` command exits 3 in two cases:

- when no session is held for the deployment, or you hold several and `--deployment` does not pick one;
- when the deployment answers `401 Unauthorized`.

A script or an AI agent should treat 3 as "ask the person to connect again". Retrying won't help.

!!! note "`--json`"
    The CLI README says every command takes `--json`. The parser does accept `--json` on every command, but only `plugin dev`, `plugin logs`, `plugin events` and `plugin open` change their output for it. Every other command prints text whether or not you pass it.

## `meridian doctor`

```text
meridian doctor [-n <name>] [--platform <url>] [--image <ref>]
```

Checks whether this machine and this cluster can run a deployment. It changes nothing.

The checks run in this order:

1. Helm is present and recent enough.
2. The cluster is reachable, and you have the rights to install into the namespace.
3. There is a storage class for the deployment's key.
4. The runtime image can be pulled from here.
5. The platform is reachable, and this machine's clock is within the tolerance a signed assertion allows.

Each result is one of:

| Result | Meaning |
|---|---|
| `ok` | Nothing to do. |
| `stops` | Would stop an install. Printed with its fix. |
| `worth` | Worth knowing, and not in the way. |
| `unknown` | Could not be checked from here. This does not mean it passed. |

**Exit codes:** `0` when nothing would stop an install, `1` when at least one check says `stops`.

## `meridian up`

```text
meridian up --id <id> [options]
```

Installs the deployment's Helm chart into the cluster, waits for the dashboard, and prints the wizard's address. It runs `doctor` first unless you pass `--no-doctor`. It drives your own `helm` and `kubectl` and prints the commands it used.

| Flag | Argument | Default | Meaning |
|---|---|---|---|
| `--id` | `<id>` | none (required) | This deployment's identifier, exactly as the platform shows it: `DEP-` then 26 characters from `0-9` and `A-Z` without `I`, `L`, `O` or `U`. Any other shape is refused before anything is installed. |
| `--enrolment-code` | `<c>` | the value of `MERIDIAN_ENROLMENT_CODE` | The one-time code the deployment enrols its key with. Required, from one or the other. Prefer the variable: a flag is written to shell history. |
| `--release` | `<name>` | `meridian` | The Helm release name. |
| `--chart` | `<ref>` | `oci://ghcr.io/open-meridian/charts/meridian-runtime` | The chart to install. |
| `--chart-version` | `<v>` | not passed to Helm | Which version of the chart. |
| `-p`, `--params` | `<file>` | none | Answer the wizard from a file instead of a browser (see below). |
| `--first-run-code` | `<c>` | the value of `MERIDIAN_FIRST_RUN_CODE` | The claim code that `--params` redeems. |
| `-f`, `--values` | `<file>` | none | Helm-style chart values, passed straight through. May be repeated. |
| `--host` | `<name>` | `meridian.localhost` | The name the deployment is reached by through the cluster's ingress controller. A name under `.localhost` is plain HTTP on this machine. Any other name is reached over HTTPS, with its certificate Secrets named in a values file (`-f`). |
| `--no-ingress` | | off | Reach the deployment through a port-forward that this command holds, as on a cluster with no ingress controller. |
| `--development` | | off | Install for development. The deployment may run plugin code while it is being written, and every page says so. `plugin dev` needs this. See [Development deployments](../concepts/development-deployments.md). |
| `--port` | `<n>` | `8443` | The local port a port-forward uses. |
| `--timeout` | `<d>` | `10m` | How long Helm is given. |
| `--no-doctor` | | off | Skip the `doctor` checks. |

Plus the [global options](#global-options) `-n`, `--platform` and `--image`.

### Answering the wizard from a file

`--params` posts your answers to the wizard's own endpoints, behind the same first-run code a browser redeems. The file holds the wizard's answers and no credential. Every field the wizard asks for as a password is read from an environment variable, `MERIDIAN_<FIELD>`, instead. A file that names such a field is refused, and the refusal names the variable to use. Field names are the wizard's own, and a misspelled one is refused against the real form.

```yaml title="first-run.yaml"
db_host: postgres.internal
db_port: 5432
db_name: meridian
db_serving_role: meridian_app
db_migrating_role: meridian_migrate
backend: ldap
ldap_servers: ldaps://ldap.firm.internal:636
ldap_base_dn: ou=people,dc=firm,dc=internal
ldap_bind_dn: cn=meridian,ou=services,dc=firm,dc=internal
admin_group: meridian-admins
dashboard_url: https://meridian.firm.example
```

```sh
export MERIDIAN_ENROLMENT_CODE=…
export MERIDIAN_FIRST_RUN_CODE=…
export MERIDIAN_DB_SERVING_PASSWORD=…
export MERIDIAN_DB_MIGRATING_PASSWORD=…
export MERIDIAN_LDAP_BIND_PASSWORD=…
meridian up --id DEP-01M3GZ8K4Q7T2V9W6X5Y3R1N0P --params first-run.yaml
```

**Exit codes:**

| Code | When |
|---|---|
| `0` | Installed. |
| `1` | A `doctor` check said `stops` (nothing is installed), or the install failed. |
| `2` | `--id` is missing or malformed, there is no enrolment code, or `--port` is not a port number. Nothing is installed. |

## `meridian down`

```text
meridian down [--release <name>] [--delete-namespace] [-n <name>]
```

Uninstalls the release. It asks no question, because running `down` is the decision.

By default the namespace is kept, and with it the database the deployment brought and the deployment's own key. Running `meridian up` again picks both back up.

| Flag | Argument | Default | Meaning |
|---|---|---|---|
| `--release` | `<name>` | `meridian` | The Helm release to uninstall. |
| `--delete-namespace` | | off | Remove the namespace too. That removes the database the deployment brought, with all its data, which nothing backs up. It also removes the deployment's key, after which the platform won't give the deployment a new enrolment code until the key is revoked there. The cluster itself is never touched. |
| `-n`, `--namespace` | `<name>` | `meridian` | The namespace. |

Either way, the deployment still exists on the platform. Retiring it there is what revokes its key. Not to be confused with `meridian uninstall`, which removes the command line itself.

**Exit codes:** `0` done, `1` failed, `2` given a word it does not take.

## `meridian upgrade-deployment`

```text
meridian upgrade-deployment [--release <name>] [-n <name>] [--chart <ref>] [--chart-version <v>] [--timeout <d>] [--yes]
```

Moves a running deployment to a newer version of its chart, in place, with your own cluster rights. Not to be confused with `meridian upgrade`, which replaces the command line itself. For the whole task, and for upgrading from your own pipeline instead, see [Upgrade a deployment](../how-to/upgrade-a-deployment.md).

It works in four steps, and stops at the step that fails.

1. **Check.** It changes nothing if any of these fails, and says which and what to do:
    - `helm` is 3.14 or newer, for `--reset-then-reuse-values`;
    - the cluster is reachable, and you may patch Deployments and create and delete Jobs in the namespace;
    - the release exists and Helm holds it as `deployed`. A `failed` or `pending-…` release is refused with how to recover it;
    - the chart version is published, and it is the chart the release was installed from;
    - it is not older than the installed version. If it is the same, it says so and exits 0.

    Two more are printed as `unknown` every time, because they are not built: whether the upgrade is within the skip policy, which is not ruled yet, and whether every installed plugin's runtime floor is met, which nothing declares yet. `unknown` does not stop it, and does not mean it passed.

    If the deployment's own values set `image.tag`, it says so as `worth`: the upgrade keeps that tag rather than moving to the chart's.

2. **Show and ask.** It prints the release, the namespace, the version and image it is on, the version and image it moves to, and the `helm upgrade` it will run, then asks `Upgrade it?`. Anything but `y` or `yes` is no. With no terminal to ask at, it is refused unless you pass `--yes`.

3. **Apply and wait.** It runs `helm upgrade <release> <chart> --version <v> --namespace <ns> --reset-then-reuse-values --timeout <d>`, never `--wait`. Then it waits, up to `--timeout`, for the new revision's migration Job to complete, every Deployment and StatefulSet of the release to roll out, and every one of their pods to run the image its template names. It prints each thing it is waiting for once, when it first sees it.

4. **Clean up and report.** It deletes the finished Jobs of this release from earlier revisions, found by the release's label, and nothing else. Old ReplicaSets are left to the chart's `revisionHistoryLimit`. It then prints the versions it moved between, each component's images and readiness, every container that restarted during the upgrade with the reason Kubernetes gives, and what it cleaned up.

It never prints the deployment's values, which hold its enrolment code. The one thing it reads from them is `image`.

| Flag | Argument | Default | Meaning |
|---|---|---|---|
| `--release` | `<name>` | `meridian` | The Helm release to upgrade. |
| `--chart` | `<ref>` | `oci://ghcr.io/open-meridian/charts/meridian-runtime` | The chart the release was installed from. |
| `--chart-version` | `<v>` | the latest published | The version to move to. It is resolved once, and that version is what is checked and applied. |
| `--timeout` | `<d>` | `10m` | How long to wait for the migration and every component, and what Helm is given. Written as Helm writes a duration: `10m`, `90s`, `1h30m`. |
| `--yes` | | off | Upgrade without being asked. For a script that has already read the plan. |
| `-n`, `--namespace` | `<name>` | `meridian` | The namespace. |

**Exit codes:**

| Code | When |
|---|---|
| `0` | Upgraded, or already at that version. |
| `1` | A check stopped it (nothing was changed), it was not approved, Helm refused it, the migration failed, or the wait timed out. What is still waited for is listed, and nothing is rolled back. |
| `2` | Asked wrongly, for example a `--timeout` Helm would not read. Nothing was done. |

## `meridian connect`

```text
meridian connect [<address>]
```

Signs you in to a deployment's dashboard in your browser, however that deployment signs people in, and keeps the session on this machine. It never takes a password.

With no address it signs in to `http://meridian.localhost`, the deployment `meridian up` installs on this machine by default. Give an address for any other.

`<address>` is the dashboard's address alone, with no path:

- `https://<host>`;
- `http://` only for this machine: `127.0.0.1`, `[::1]`, `localhost`, or a name under `.localhost` such as `http://meridian.localhost`.

Plain HTTP to any other machine is refused, because it would send your session in the clear.

The command prints the sign-in link and opens it in your browser, then waits up to 5 minutes for the sign-in to come back. A session lasts 30 minutes unused, and ends at a fixed time at the latest; the command prints that time. The README gives the maximum as 12 hours.

This machine holds one session per deployment. Connecting again ends the earlier one at the deployment. Sessions are kept in files readable only by you, in `$XDG_CONFIG_HOME/meridian/sessions`, `%APPDATA%\meridian\sessions`, or `~/.config/meridian/sessions`, whichever is found first.

**Exit codes:** `0` connected; `1` the sign-in was declined, timed out, or failed, or the session could not be kept; `2` no address, or an address of the wrong form.

## `meridian sign-out`

```text
meridian sign-out [<address>]
```

Ends a session at the deployment and forgets it here. With no address, it signs out of the one deployment you are connected to. If you are connected to more than one, it lists the commands to run and exits 2.

If the deployment can't be reached, the session is still forgotten here and lapses there within 30 minutes.

**Exit codes:** `0` signed out, or not connected to begin with; `1` the session file could not be removed; `2` a malformed address, more than one address, or no address when several sessions are held.

## `meridian plugin new`

```text
meridian plugin new <name> [--into <dir>]
```

Writes a working plugin to start from: the Python SDK's reference plugin, renamed to `<name>`. It needs no network, because the template is compiled into the binary. It writes the plugin's code and page, a `Dockerfile`, `pyproject.toml`, `.dockerignore`, `.gitignore`, `README.md`, `AGENTS.md`, `CLAUDE.md`, and a `develop-live` skill for Claude Code, then prints the next steps. See [Your first plugin](../getting-started/first-plugin.md).

`<name>` must be lowercase letters, digits and single hyphens, starting with a letter. It becomes the package name, and, with hyphens as underscores, the module name.

| Flag | Argument | Default | Meaning |
|---|---|---|---|
| `--into` | `<dir>` | `./<name>` | Where to write it. Never somewhere that already exists. |

**Exit codes:** `0` written, `1` refused (bad name, or the directory exists), `2` asked wrongly.

## Plugin commands on a deployment

`plugin upload`, `list`, `launch`, `stop`, `dev`, `logs`, `events` and `open` act through the session `meridian connect` keeps. The deployment answers `upload`, `list`, `launch`, `stop`, `dev`, `logs` and `events` for a deployment admin only. It answers `open` for anybody who holds access on that plugin. See [Access](../concepts/access.md).

These flags are shared among them:

| Flag | Argument | Default | Used by | Meaning |
|---|---|---|---|---|
| `--deployment` | `<addr>` | the one deployment connected | all | Which connected deployment, when you hold sessions with more than one. |
| `--dir` | `<dir>` | `.` | `upload`, `dev` | The plugin's directory. Its image is built with `docker`, from its own `Dockerfile`. |
| `--instance` | `<id>` | none (required) | `launch`, `dev`, `logs`, `events`, `open` | The instance's name. Its page is found by it. Lowercase letters, digits and single hyphens, starting with a letter, at most 63 characters. |
| `--yes` | | off | `launch`, `dev` | Approve the roles the version asks for without being asked. For a script that has already shown them to a person. |
| `--json` | | off | `dev`, `logs`, `events`, `open` | JSON on stdout: one object, or one per line for `dev` and `--follow`. Progress goes to stderr. |
| `--release` | | off | `dev` | Upload the plugin as it is now as a version, and run that version in place of the live instance. |
| `--since` | `<revision>` | none | `logs`, `events` | Only what came after that revision, a whole number. |
| `--follow` | | off | `events` | Keep reporting events as they happen, until interrupted. |
| `--print` | `<path>` | none | `open` | The page at that path on the plugin's host, as you are served it, instead of a link. |

**Exit codes** for all of them: `0` done, `1` refused or failed, `2` asked wrongly, `3` no session or it has lapsed.

### `meridian plugin upload`

```text
meridian plugin upload [--dir <dir>] [--deployment <addr>]
```

Builds the plugin's image on this machine and puts it in the deployment's catalogue as a version. The steps:

1. Read `pyproject.toml` and check its [plugin manifest](plugin-manifest.md). From CLI 0.1.14, a `[tool.meridian]` that declares `tags` is refused here, before anything is built: a plugin declares none, since access to a plugin is `read` or `write` in the deployment's access groups.
2. Build the image with `docker build`, tagged `meridian-plugin/<name>:<version>`.
3. Read the image back with `docker save`.
4. Push it into the deployment's registry through the dashboard. A layer the registry already holds is not sent again, and one another plugin's repository holds is mounted from there.
5. Send the manifest's metadata with the image's digest. The deployment records the version.

A version is recorded once and never replaced: uploading a name and version already in the catalogue is refused. On success it prints `Uploaded to <address>, as sha256:<digest>.`

### `meridian plugin list`

```text
meridian plugin list [--deployment <addr>]
```

Prints the catalogue: every version uploaded, with its roles, whether it serves a page, and the SDK version it pins, and every launch, with its instance, version and state (`launched`, `stopped` or `failed`, with the failure). Because it needs a live session, it is also the way to check you are connected: it exits 3 when you aren't.

### `meridian plugin launch`

```text
meridian plugin launch <name> <version> --instance <id> [--yes] [--deployment <addr>]
```

Runs a recorded version as an instance. It first prints the roles the version declares, then asks `Launch it as <id>, with these?`. Anything but `y` or `yes` is no. With no terminal to ask at, it is refused unless you pass `--yes`.

The deployment runs the instance with exactly the roles it declares; an approval that names anything else is refused. On success it prints the instance's page address, `<address>/plugins/<id>`. See [Plugins, roles and grants](../concepts/plugins.md).

### `meridian plugin stop`

```text
meridian plugin stop <id> [--deployment <addr>]
```

Stops a launched instance. The instance is named as a word here, not with `--instance`.

### `meridian plugin dev` { #plugin-dev }

```text
meridian plugin dev --instance <id> [--dir <dir>] [--yes] [--json] [--deployment <addr>]
meridian plugin dev --release --instance <id> [--dir <dir>] [--yes] [--json] [--deployment <addr>]
```

Runs the plugin live on a development deployment: each save is sent as it is made, and the plugin's process restarts on it in the same pod, with the same sidecar and the same grants. A deployment not installed with `--development` refuses it. See [Development deployments](../concepts/development-deployments.md).

Without `--release`, it does the following:

1. It reads `pyproject.toml` in `--dir` for the plugin's name and version.
2. If the instance is already running live, it sends the directory to it and asks nothing. If the instance is running a version rather than live, it refuses: stop it first or choose another `--instance`.
3. Otherwise it uploads the plugin, unless that name and version are already in the catalogue. In that case the uploaded version runs, with the directory's files sent over it. It then launches the instance live, after the same approval as `plugin launch`.
4. It watches the directory until you press Ctrl-C, sending each change and reporting every event with its revision. The instance keeps running after Ctrl-C.

The directory is scanned four times a second, and events are polled twice a second. Some files are never sent:

- `.git`, `__pycache__`, `.venv`, `venv`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `build`, `dist`, `.meridian`, `.DS_Store`, `*.egg-info` and `*.pyc`;
- whatever the plugin's `.dockerignore` names. Negations and patterns with wildcards other than a leading `*` are not read, and a pattern that can't be read is sent rather than guessed at.

One change may carry at most 11 MiB before encoding.

A change to the plugin's dependencies or roles needs a new version. The live code runs on the image the instance was launched from.

With `--release`, it does the following:

1. It uploads the directory as it is, as the version in `pyproject.toml`. A version already recorded is refused: raise `version` first.
2. It asks for approval of the roles.
3. It stops the instance if one is running.
4. It launches the new version in its place, not live.

The result is an ordinary version in the catalogue.

**Output.** In text, one line per event, with its revision first:

```text
r1 sent (9 files, 0 deleted)
r1 synced (9 sent, 0 deleted)
r1 restarted
r1 ready
r2 sent (1 files, 0 deleted)
r2 crashed, exit 1
    Traceback (most recent call last):
    ...
```

With `--json`, one JSON object per line on stdout. Each event is described in [`plugin dev` events](plugin-dev-events.md). With `--release --json`, one object:

```json
{"instance_id": "my-plugin", "name": "my-plugin", "version": "0.2.0", "digest": "sha256:…"}
```

### `meridian plugin logs`

```text
meridian plugin logs --instance <id> [--since <revision>] [--json] [--deployment <addr>]
```

Prints what a live plugin printed, one line each. With `--since`, only lines from revisions after that one. Without it, everything kept, which is up to about 1 MiB of output.

With `--json`, one object:

```json
{"revision": 4, "lines": ["…", "…"]}
```

`revision` is the revision the instance is on now.

### `meridian plugin events`

```text
meridian plugin events --instance <id> [--since <revision>] [--follow] [--json] [--deployment <addr>]
```

Prints what happened to a live plugin: synced, restarted, ready, crashed, exited, refused, each with its revision. With `--since`, only events from revisions after that one. With `--follow`, it keeps polling and printing new events until interrupted.

With `--json` and no `--follow`, one object: `{"revision": <now>, "events": [ … ]}`. With `--json --follow`, one event object per line. The events are described in [`plugin dev` events](plugin-dev-events.md).

### `meridian plugin open`

```text
meridian plugin open --instance <id> [--print <path>] [--json] [--deployment <addr>]
```

Without `--print`, it prints a link to the plugin's page. The first browser that opens the link, within a minute, is signed in to that plugin's page alone, for as long as your terminal session lasts. Run `open` again for another browser. With `--json`:

```json
{"instance_id": "my-plugin", "url": "https://…"}
```

With `--print <path>`, it prints the page at that path on the plugin's host, as you would be served it, instead of a link:

- `<path>` starts with a single `/`, and may not be under `/.meridian`.
- A page is at most 8 MiB, and redirects are not followed.
- It exits 1 when the plugin answers with a status outside 200–299, after printing what the plugin answered.

With `--json`, one object:

```json
{"instance_id": "my-plugin", "status": 200, "content_type": "text/html; charset=utf-8", "body": "…"}
```

A body that is not UTF-8 text comes as `body_base64` instead of `body`.

## `meridian upgrade`

```text
meridian upgrade [--to <version>]
```

Replaces this binary with the latest release, or with the release `--to` names, older or newer. It upgrades the command line, not a deployment: that is [`meridian upgrade-deployment`](#meridian-upgrade-deployment). Releases come from `https://github.com/open-meridian/meridian-cli/releases`, or from `MERIDIAN_RELEASES`, which must be HTTPS unless it is this machine. The download is checked against the `.sha256` published beside it. This catches a broken download, not a compromised release; signing is not built yet.

It never looks for a newer release on its own.

| Flag | Argument | Default | Meaning |
|---|---|---|---|
| `--to` | `<version>` | the latest release | A named release. A leading `v` is optional. |

**Exit codes:** `0` replaced, or already that version; `1` failed, for example when the binary's directory is not writable. That check happens before anything is downloaded.

## `meridian uninstall`

```text
meridian uninstall [--yes]
```

Removes the command line. It lists what it will remove and asks first:

1. Every session it holds, ended at each deployment. A session with a deployment it can't reach is forgotten here and lapses there within 30 minutes.
2. The sessions directory.
3. The binary.

| Flag | Argument | Default | Meaning |
|---|---|---|---|
| `--yes` | | off | Remove without being asked. With no terminal to ask at, it is refused without this. |

**Exit codes:** `0` removed, `1` not approved or failed. If the binary's directory is not writable, it stops before ending any session.

## `meridian --version`

```text
meridian --version
```

Prints `meridian <version> (<target>; meridian-core <revision>)`. `meridian version` is the same.

## Environment variables

| Variable | Read by | Meaning |
|---|---|---|
| `MERIDIAN_ENROLMENT_CODE` | `up` | The enrolment code, when `--enrolment-code` is not given. |
| `MERIDIAN_FIRST_RUN_CODE` | `up --params` | The first-run claim code, when `--first-run-code` is not given. |
| `MERIDIAN_<FIELD>` | `up --params` | Each credential field the wizard asks for, by its field name in capitals. |
| `MERIDIAN_RELEASES` | `upgrade` | Where releases are fetched from, in place of GitHub. |
| `XDG_CONFIG_HOME`, `APPDATA`, `HOME` | session commands | Where the sessions directory is. |
| `MERIDIAN_INSTALL_DIR`, `MERIDIAN_VERSION` | `install.sh` | Where the install script puts the binary (default `~/.local/bin`), and which release it installs. |
