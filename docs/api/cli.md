# Command line

`meridian` is Open Meridian's command line. It brings a deployment up where you have a terminal, signs you in to one that is already running, and brings plugins into it: uploading, launching, stopping, and developing them live.

Nothing in a cloud install depends on it. A marketplace listing's form and the deployment's own wizard are the whole path there; `meridian` makes the same things convenient from a terminal.

This page describes release 0.1.26 of the command line. `meridian --version` says which one you have. For installing it, see [Install a deployment](../getting-started/installation.md).

## Synopsis

```text
meridian doctor
meridian up --id <id> [options]
meridian down [--release <name>] [--delete-namespace]
meridian upgrade-deployment [--release <name>] [--chart-version <v>] [options]
meridian connect [<address>]
meridian sign-out [<address>]
meridian plugin new <name> [--into <dir>]
meridian plugin check [--dir <dir>] [--run-tests] [--json]
meridian plugin migrate [--to <version>] [--dir <dir>] [--image <ref>] [--force] [--run-tests] [--json]
meridian plugin upload [--dir <dir>]
meridian plugin list
meridian plugin launch <name> <version> --instance <id> [--yes]
meridian plugin stop <id>
meridian plugin dev --instance <id> [--dir <dir>] [--yes] [--json] [--release]
meridian plugin logs --instance <id> [--since <revision>] [--json]
meridian plugin events --instance <id> [--since <revision>] [--follow] [--json]
meridian plugin open --instance <id> [--level manage|open|view] [--print <path>] [--json]
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
| `--image` | `<ref>` | `ghcr.io/open-meridian/meridian-runtime:latest` | The runtime image. Used by `doctor` and `up`. `up` passes it to the chart only when you give it. `plugin migrate` reads it as something else: the SDK image its steps run in (see [`meridian plugin migrate`](#plugin-migrate)). |
| `-h`, `--help` | | | Print the usage text and exit 0. |
| `-v` | | | Reserved for verbose output, which is not built yet. It prints a note saying so and is otherwise ignored. |

## Exit codes

Every command exits 0 when it succeeds. What a non-zero code means depends on the command:

| Code | Meaning |
|---|---|
| `0` | Done. |
| `1` | Refused or failed. The reason is on stderr. |
| `2` | Asked wrongly: an unknown command or flag, a missing argument, or an argument of the wrong form. Nothing was done. |
| `3` | `plugin` commands that act on a deployment (`upload`, `list`, `launch`, `stop`, `dev`, `logs`, `events`, `open`): this computer is not connected to the deployment, or its delegation was revoked or has lapsed. The message names the `meridian connect` to run. |

A `plugin` command exits 3 in three cases:

- when this computer is not connected to the deployment, or is connected to several and `--deployment` does not pick one;
- when the deployment answers `401 Unauthorized`: the delegation was revoked or has lapsed, its directory groups are older than the deployment allows, or it is one the deployment does not know; or, for a session an earlier CLI kept, the session lapsed or was ended. That includes the deployment's registry, which `plugin upload` pushes through. The message says which, and ends with the `meridian connect` to run, for example ``your delegation to this computer at https://meridian.localhost was revoked: `meridian connect` to sign in again``. Before CLI 0.1.15, `plugin upload` reported a lapsed session met at the registry as `the registry did not start an upload: 401 Unauthorized: invalid_token` and exited 1;
- from CLI 0.1.25, when refreshing the access token is refused: the delegation was revoked or has lapsed, its directory groups are too old, or a refresh token was presented twice, which revokes it (see [The delegation](#the-delegation)).

An access token that has only expired never exits 3: the command refreshes it and asks again.

A script or an AI agent should treat 3 as "ask the person to connect again". Retrying won't help.

!!! note "`--json`"
    The CLI README says every command takes `--json`. The parser does accept `--json` on every command, but only `plugin check`, `plugin migrate`, `plugin dev`, `plugin logs`, `plugin events` and `plugin open` change their output for it. Every other command prints text whether or not you pass it.

## `meridian doctor`

```text
meridian doctor [-n <name>] [--platform <url>] [--image <ref>]
```

Checks whether this machine and this cluster can run a deployment. It changes nothing.

The checks run in this order:

1. Helm is present and recent enough.
2. The cluster is reachable, and you have the rights to install into the namespace.
3. There is a storage class for the deployment's key.
4. No node is short of disk.
5. The runtime image can be pulled from here.
6. Each plugin launched in the namespace runs the sidecar its deployment's components run. One that does not is `worth`, with the commands that relaunch it; it never stops an install.
7. The platform is reachable, and this machine's clock is within the tolerance a signed assertion allows.

Each result is one of:

| Result | Meaning |
|---|---|
| `ok` | Nothing to do. |
| `stops` | Would stop an install. Printed with its fix. |
| `worth` | Worth knowing, and not in the way. |
| `unknown` | Could not be checked from here. This does not mean it passed. |

The disk check is new in CLI 0.1.17. A node under disk pressure is `stops`: its `DiskPressure` condition is `True`, or it carries the `node.kubernetes.io/disk-pressure` taint. Kubernetes evicts that node's pods and schedules none onto it until it has disk again, so a deployment there stops and its pods wait as `Pending`. The fix is to free disk on the node and wait a few minutes for the taint to lift; the pods come back by themselves. On a local VM such as Rancher Desktop's, Docker's build cache is often most of it (`docker builder prune -a`).

Before that, low free disk is `worth`. The line is 20% of the disk free, or 10 GiB where that is more. Kubernetes' default is to start evicting at 10% free for the node's own disk and 15% for images, and on one shared disk, as a local VM has, the 15% comes first. Warning at 20% leaves room for an image pull or a build before then, and the 10 GiB floor keeps that room on a small disk. Where images have a disk of their own, each disk is read on its own.

The free disk is what each node's kubelet reports, read through the API server (`kubectl get --raw /api/v1/nodes/<node>/proxy/stats/summary`). That needs the cluster-wide right to get `nodes/proxy`. Without it, free disk is `unknown` and says which right is missing. Disk pressure needs only the right to list nodes, and is still read. Neither needs anything run on the node.

A right the cluster refuses is `stops`, naming the right to ask for. `kubectl auth can-i` answers "no" by exiting 1, and from CLI 0.1.15 that is read as the refusal it is rather than as `unknown`; `unknown` is left for a question `kubectl` could not answer.

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
| `--archive` | `<path>` | asked | From CLI 0.1.36. Where edge plugins' older records go: a directory on the cluster's node, such as a NAS export or a second disk mounted there, by its absolute path. It becomes the chart's `pluginArchive.path`. See [Where older records go](#where-older-records-go). |
| `--no-archive` | | asked | From CLI 0.1.36. No archive: records past their window stay in each plugin's storage. |

Plus the [global options](#global-options) `-n`, `--platform` and `--image`.

### Where older records go

!!! note "CLI 0.1.36"
    `--archive` and `--no-archive` are in CLI 0.1.36, for a runtime serving contract v16.

A plugin at the edge keeps what its vendor sent it, and past the window its admin sets it archives the older records, keeps them or deletes them (see [The archive](../concepts/the-archive.md)). Before it installs, `up` asks where the archive is, unless something has said:

```text
Where do edge plugins' older records go? Past the window a plugin's admin sets, a plugin moves them to an archive, if a deployment admin allows it one. Name a directory on the cluster's node for the archive -- a NAS export or a second disk mounted there -- or press Enter for none, and records past their window stay in each plugin's storage.
```

`--archive <path>` answers it, and `--no-archive` declines; given both, it is refused. Given neither, `up` asks at a terminal and takes none where there is no terminal to ask at. A `--params` file answers it with `archive`, a path or `none`, which `up` takes out before the wizard's fields are matched and never posts to the wizard. A values file (`-f`) naming `pluginArchive` itself, as a cloud's bucket or a claim on shared storage is, is not asked over. The archive said in two places, such as a flag and a values file, is refused before anything is installed. A path must be absolute, with no `..`.

Naming an archive allows no plugin one: a deployment admin allows each, with a bound or none, on the plugin's Summary. See [Keep older records in the archive](../how-to/keep-older-records-in-the-archive.md).

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
| `2` | `--id` is missing or malformed, there is no enrolment code, `--port` is not a port number, or the archive is said twice or is not an absolute path. Nothing is installed. |

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
    - no node is under disk pressure, read as [`doctor`](#meridian-doctor) reads it. An upgrade pulls the new version's images onto the node, which would take more of the disk it is short of, and its new pods would be scheduled nowhere. This check is new in CLI 0.1.17. Low free disk is printed as `worth` and does not stop it;
    - the release exists and Helm holds it as `deployed`. A `failed` or `pending-…` release is refused with how to recover it;
    - the chart version is published, and it is the chart the release was installed from;
    - it is not older than the installed version. If it is the same, it says so and exits 0.

    Two more are printed as `unknown` every time, because they are not built: whether the upgrade is within the skip policy, which is not ruled yet, and whether every installed plugin's runtime floor is met, which nothing declares yet. `unknown` does not stop it, and does not mean it passed.

    If the deployment's own values set `image.tag`, it says so as `worth`: the upgrade keeps that tag rather than moving to the chart's.

2. **Show and ask.** It prints the release, the namespace, the version and image it is on, the version and image it moves to, and the `helm upgrade` it will run, then asks `Upgrade it?`. Anything but `y` or `yes` is no. With no terminal to ask at, it is refused unless you pass `--yes`.

3. **Apply and wait.** It runs `helm upgrade <release> <chart> --version <v> --namespace <ns> --reset-then-reuse-values --timeout <d>`, never `--wait`. Then it waits, up to `--timeout`, for the new revision's migration Job to complete, every Deployment and StatefulSet of the release to roll out, and every one of their pods to run the image its template names. It prints each thing it is waiting for once, when it first sees it.

4. **Clean up and report.** It deletes the finished Jobs of this release from earlier revisions, found by the release's label, and nothing else. Old ReplicaSets are left to the chart's `revisionHistoryLimit`. It then prints the versions it moved between, each component's images and readiness, every container that restarted during the upgrade with the reason Kubernetes gives, and what it cleaned up.

    Last, it names each launched plugin still on a sidecar that is not the one the components now run, since a plugin keeps the sidecar it was launched with until it is relaunched, and each plugin whose pod started during the upgrade before the new launcher was ready, since the old launcher may have launched it. For each it prints `meridian plugin stop <instance>` and `meridian plugin launch <name> <version> --instance <instance>` (`meridian plugin dev --instance <instance>` for a live one). The name comes from the plugin's image; the version is left as `<version>`, which `meridian plugin list` gives. It relaunches nothing itself.

It never prints the deployment's values, which hold its enrolment code. What it reads from them is `image`, where the deployment is reached, and, from CLI 0.1.36, where its edge plugins' archive is (`pluginArchive`), which `--reset-then-reuse-values` keeps as it keeps every value the deployment was given. The plan says so: `Its archive, /mnt/nas/meridian-archive on the cluster's node, is kept: the deployment's own values carry it.`

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

Signs you in to a deployment's dashboard in your browser, however that deployment signs people in, and asks you to let the CLI on this computer act as you there: a delegation, for up to 90 days. It never takes a password. From CLI 0.1.25; an earlier CLI kept a session of 12 hours at most (see [With an older dashboard or an older CLI](#with-an-older-dashboard-or-an-older-cli)).

With no address it signs in to `https://meridian.localhost`, the deployment `meridian up` installs on this machine by default. Give an address for any other.

`<address>` is the dashboard's address alone, with no path:

- `https://<host>`;
- `http://` only for this machine: `127.0.0.1`, `[::1]`, `localhost`, or a name under `.localhost` such as `http://meridian.localhost`.

Plain HTTP to any other machine is refused, because it would send your sign-in and your tokens in the clear.

It does this:

1. **Registers this computer** with the dashboard, the first time it connects there, as a client named `meridian on <host>`, after this computer's host name. Each computer is its own client, listed and revoked apart. Registering grants nothing.
2. **Signs you in.** It prints the sign-in link and opens it in your browser, then waits up to 5 minutes for the sign-in to come back to a loopback address on this machine. The sign-in is always made afresh, never taken from a browser already signed in.
3. **Asks you.** The dashboard then shows **Allow a client to act as you**: the client's name, that its codes go to this computer, and:
    - **What it may do:** **Everything you hold, as that changes**, or **Only what is ticked below**, ticked from what you hold: each plugin at each level you hold on it (Manage, Open, View), the account groups your permissions name, and, if you hold it, **Deployment admin**: the deployment's own settings, accounts and plugins, but never who holds access.
    - **Until:** 7, 30 or 90 days.

    For the CLI the page starts at everything and 90 days. Choose **Allow**, or **Don't allow**. Allow it only if you started it yourself, just now.

4. **Keeps the delegation.** It exchanges the one-time code for a ten-minute access token and a single-use refresh token, keeps them, and prints who you are connected as and when the delegation lapses.

### The delegation

Every command presents the access token. When it has under a minute left, the command refreshes it first, and when the deployment refuses it as expired, the command refreshes it once and asks again. Refreshing spends the refresh token and keeps the next pair. Nothing asks for a browser again until the delegation lapses or is revoked, so `plugin dev` can watch overnight.

A refresh token is single use, and the deployment revokes the delegation when a spent one is presented, because that only happens when somebody else holds it too. So refreshing takes an exclusive lock on that deployment's sessions file and reads it again under the lock: a second command finds the pair the first wrote, and `plugin dev` in one terminal and `plugin list` in another never revoke your CLI.

What a command may reach is what you hold at that moment, cut to what the delegation covers. `plugin upload`, `list`, `launch`, `stop`, `dev`, `logs` and `events` need it to cover the deployment admin's capabilities, and a delegation that does not is refused, saying to connect again to widen it; `plugin open` needs it to cover the level it opens at. Everything the CLI does is recorded as yours, through it.

Within a week of the lapse, every command says when, once:

```text
Your delegation to this computer at https://meridian.firm.example lapses at <time>. `meridian connect https://meridian.firm.example` renews it.
```

The dashboard's home says so too. Connecting again renews it: this computer keeps its registration, and the page says you delegated to it before. You see the delegation, and can revoke it, in **Connected clients** on the dashboard; see [Access](../concepts/access.md#delegations-to-the-cli).

It ends when you run `meridian sign-out`, when you or a deployment admin revoke it from Connected clients, when it lapses, or when the account's password is reset. The next command then exits 3, saying why and naming the `meridian connect` to run.

This computer holds one delegation per deployment. Each is kept in a file readable only by you, in `$XDG_CONFIG_HOME/meridian/sessions`, `%APPDATA%\meridian\sessions`, or `~/.config/meridian/sessions`, whichever is found first. Connecting again replaces what the file holds; a session an earlier CLI left there is ended at the deployment.

### With an older dashboard or an older CLI

- **CLI 0.1.25 needs a dashboard that takes delegations,** chart 0.1.223 or later. An older dashboard answers the registration with `404 Not Found`, and `connect` says so and exits 1: upgrade the deployment ([Upgrade a deployment](../how-to/upgrade-a-deployment.md)), or connect with 0.1.24, the last release that signs in the old way (`meridian upgrade --to 0.1.24`).
- **A session an earlier CLI kept keeps working** after you upgrade the CLI, until it lapses: 30 minutes unused, 12 hours at most. Then `meridian connect` makes a delegation in its place. Chart 0.1.223 still accepts such sessions; a runtime at contract v15 accepts none.
- **A runtime at contract v15 serves CLI 0.1.25 or later.** It keeps no session for a terminal, takes nothing on the CLI's paths but an access token on a delegation, and answers a CLI naming an older version with `400`, saying it serves 0.1.25 or later. Upgrade the CLI (`meridian upgrade`) and connect again.

**Exit codes:** `0` connected; `1` the sign-in was declined, timed out, or failed, the dashboard does not take delegations, or the delegation could not be kept, in which case it is revoked; `2` no address, or an address of the wrong form.

## `meridian sign-out`

```text
meridian sign-out [<address>]
```

Revokes this computer's delegation at the deployment and forgets it here. With no address, it signs out of the one deployment you are connected to. If you are connected to more than one, it lists the commands to run and exits 2.

If the deployment can't be reached, the delegation is still forgotten here. It says so, with when the delegation lapses: revoke it from Connected clients on the dashboard, or it lapses then. A session an earlier CLI kept is ended at the deployment instead, and if the deployment can't be reached, lapses there within 30 minutes.

**Exit codes:** `0` signed out, or not connected to begin with; `1` the sessions file could not be removed; `2` a malformed address, more than one address, or no address when connected to several.

## `meridian plugin new`

```text
meridian plugin new <name> [--into <dir>] [--role dgm|reporting]
```

Writes a working plugin to start from: the Python SDK's reference plugin, renamed to `<name>`, or with `--role` that role's template. It needs no network, because the template is compiled into the binary. It writes the plugin's code and its pages, each a view function and a Jinja2 template declared with the levels it serves (a **Setup** page under Manage, at `admin`, and an **Accounts** page under Open and View, at `write` and `read`), its tests (`tests/test_page.py`), a `Dockerfile`, `pyproject.toml`, `.dockerignore`, `.gitignore`, `README.md`, `AGENTS.md`, `CLAUDE.md`, a `develop-live` skill for Claude Code, and a CI workflow that runs `meridian plugin check --run-tests` (`.github/workflows/check.yaml`), then prints the next steps. From the CLI release after 0.1.36 (built, not released) the plugin pins SDK 0.22.0, and needs a deployment whose sidecar accepts contract v18 (chart 0.1.291, not yet released). CLI 0.1.36 pins SDK 0.21.0, and needs a deployment whose sidecar accepts contract v16 (0.1.35 pinned 0.20.0, 0.1.34 pinned 0.19.0, 0.1.33 pinned 0.18.0, 0.1.29 to 0.1.32 pinned 0.17.0, 0.1.28 pinned 0.16.0, 0.1.27 pinned 0.15.0, 0.1.26 pinned 0.14.0, 0.1.24 and 0.1.25 pinned 0.12.0, 0.1.23 pinned 0.11.0, 0.1.22 pinned 0.10.1, 0.1.21 pinned 0.10.0, 0.1.20 pinned 0.9.0, 0.1.18 and 0.1.19 pinned 0.7.1, and 0.1.16 and 0.1.17 pinned 0.6.1). From the same release its `AGENTS.md` teaches a coding agent the kinds of raw record a plugin at the edge declares and their windows, and that a custody plugin keeps each activity's raw record at least as long as the history it reported. See [Your first plugin](../getting-started/first-plugin.md).

`<name>` must be lowercase letters, digits and single hyphens, starting with a letter. It becomes the package name, and, with hyphens as underscores, the module name.

| Flag | Argument | Default | Meaning |
|---|---|---|---|
| `--into` | `<dir>` | `./<name>` | Where to write it. Never somewhere that already exists. |
| `--role` | `dgm` or `reporting` | none | From the CLI release after 0.1.36 (built, not released): write that role's template instead, from the SDK's `templates/`, a whole plugin holding the role with its tests running the role's suite. A role with no template of its own is refused, naming those that have one; the reference plugin takes any role in its `pyproject.toml`. |

**`--role dgm`** writes a plugin that puts a stand-in vendor's daily closes and bars into the [lake](../concepts/the-lake.md): its catalogue declared from code, every price parsed from the vendor's text as a `Decimal`, every subject and venue resolved before a row names it, wants answered, and its **Connection** and **Datasets** pages under Manage, each with its read tool, `read_connection` and `read_datasets`. Replace the vendor (`vendor.py`) with your own. Its tests run the `dgm` suite. See [Write a `dgm` against its suite](../how-to/write-a-dgm.md).

**`--role reporting`** writes a plugin that shows the positions in its account scope valued at the last close from the lake, on a **Closes** page under Open and View and a **Datasets** page under Manage, and records nothing. Its tests run the `reporting` suite. See [Value the book](../how-to/value-the-book.md).

**Exit codes:** `0` written, `1` refused (bad name, the directory exists, or a role with no template), `2` asked wrongly.

## `meridian plugin check` { #plugin-check }

```text
meridian plugin check [--dir <dir>] [--run-tests] [--verified] [--json]
```

From CLI 0.1.15. Holds the plugin in `--dir` to the framework's rules: the rules every plugin is built to, so that plugins written by different people and different coding agents look and behave alike, and a change to what plugins call can be applied to all of them. It needs no deployment and no session, changes nothing, and reads nothing outside the directory. Run it while you work, and in the plugin's own CI.

Each failure names the rule, the file and line, and what to write instead, so that a coding agent can fix it without asking. The rules are compiled into the binary: the check a plugin meets is the one of the `meridian` that runs it.

| Flag | Argument | Default | Meaning |
|---|---|---|---|
| `--dir` | `<dir>` | `.` | The plugin's directory. |
| `--run-tests` | | off | Also run the plugin's tests with pytest: `.venv/bin/python -m pytest` when the plugin has a `.venv`, otherwise `python3 -m pytest`, which must have the plugin and pytest installed. No cache or bytecode is written. |
| `--verified` | | off | Hold it as a verified plugin is: every route that changes something a tool for agents, none kept from them (`tools-cover-routes`), and from the CLI release after 0.1.36 each role it holds with a suite run in its tests (`role-suite`). |
| `--json` | | off | One JSON object on stdout instead of the report. |

### The rules

| Rule | Holds | Fails on |
|---|---|---|
| `template-shape` | The project keeps the template's shape. | No `pyproject.toml`, or one with no plugin name or version; the SDK not pinned exactly (`open-meridian==<version>`); no `Dockerfile`, or one not built on `ghcr.io/open-meridian/plugin-python:<the pinned version>`; no `src/<module>/__main__.py`; nothing calling `meridian.connect()`; no `AGENTS.md`; a `CLAUDE.md` that does not begin from `@AGENTS.md`; a `.dockerignore` that does not name `AGENTS.md` and `.meridian`. |
| `tool-meridian` | `[tool.meridian]` names roles from the fixed list, and no tags. | No `[tool.meridian]`; a role not in the deployment's list (`ccm`, `compliance`, `custody`, `dgm`, `ems`, `match`, `oms`, `operations`, `portfolio`, `reporting`, `servicing`, `settlement`, `signal`); `tags`, empty or not; an `interface` that is not true or false. |
| `edge-storage` | Only a plugin at the edge asks for storage in its declaration. | A plugin holding no edge role asking for storage. See [Keep what your custody plugin converts](../how-to/keep-what-the-edge-converts.md). |
| `role-suite` | A verified plugin holding a role with a suite runs the suite in its tests. | With `--verified`: a plugin holding `custody`, or from the CLI release after 0.1.36 `dgm`, with no test running that role's suite, which `--run-tests` then runs. Without `--verified` it is reported skipped, from the CLI release after 0.1.36: a plugin not passing its role's suite is not verified for it, and breaks no rule, so the reference plugin given `custody` keeps every rule. CLI 0.1.36 and earlier hold every custody plugin to it. See [Keep what your custody plugin converts](../how-to/keep-what-the-edge-converts.md) and [Write a `dgm` against its suite](../how-to/write-a-dgm.md#hold-it-to-the-suite). |
| `kit-linked` | Every page links the kit from `/.meridian/ui/`, and the plugin holds no copy of it. | A file that writes a document (`<!doctype html>`, `<html>` or `<head>`) with no link to `/.meridian/ui/…/meridian.css`; a file named `meridian.css` or `meridian.js` in the plugin. |
| `no-raw-colour` | No raw colour in a page or its styles. | A hex colour where a colour goes, `rgb()`, `rgba()`, `hsl()`, `hsla()`, `hwb()`, `oklch()` or `oklab()`, or a CSS colour name as the value of a colour property (`color`, `background`, `border`, `fill`, `stroke` and the like), a colour attribute (`fill="…"`) or a script's `.style.…Color`. A fallback in `var(--x, #fff)` is a raw colour too. |
| `own-origin` | A page loads nothing from another origin. | An absolute or protocol-relative address (`https://…`, `//…`, `wss://…`) as a script's, stylesheet's, image's or frame's source, in `@import` or `url()`, or given to `fetch`, `EventSource`, `WebSocket` or `import`. A link people follow (`<a href>`) is not loading. |
| `tools-cover-routes` | Every route that changes something is a tool for agents, or says why not. | A route that changes something with no `params=` record and no `tool=False` with `why=`. See [Offer your plugin's pages to agents](../how-to/offer-your-pages-to-agents.md). |
| `roles-declared` | On a plugin holding several roles, every page, route and setting names its roles, and a changing route sends only its roles' commands. | From CLI 0.1.35, only on a plugin whose `[tool.meridian]` names several roles: a page, route or setting naming no `roles=`, or a role the plugin does not hold, a tool held to its route's roles unless it names its own; a route that changes something (any method but GET and HEAD) whose view sends a command none of its roles holds, by meridian-schema's published `roles.json`, at the line of the call, naming the roles that hold it. `roles=` is read as written or through a constant bound at the top of a module. A plugin holding one role, or none, names none, and the rule holds. See [Roles](python-sdk.md#roles). |
| `window-settings` | No setting of the plugin's own takes a declared kind's window setting's name. | From CLI 0.1.36: a setting named `<kind>_window_days` or `<kind>_past_window` for a kind the plugin declares with `RecordKind(...)`, at its line, as written or through a constant bound at the top of a module. The SDK declares both settings for every kind, and refuses a plugin declaring either itself. See [The window settings](python-sdk.md#the-window-settings). |
| `settings-declared` | Settings are declared to the SDK, not read from the environment. | `os.environ`, `os.getenv`, `getenv(` or `environ[…]`. One name is allowed: a variable ending `_PAGE_PORT`, where the page listens on loopback for its sidecar, as the template's does. That is the plugin's own wiring, which nobody configures. |
| `secrets-kept` | No secret setting's value is logged or put in a page. | For each `meridian.Setting(…, secret=True)`, by its name or the constant that names it: its value (`values[NAME]`, `.get(NAME)`, `.name`, `{name}`) in a logging call, `print`, a `raise`, or a statement that writes HTML. Its name alone, as in "waiting for broker_api_key", is not its value. |
| `through-the-sdk` | The deployment is reached only through the SDK. | Importing `nats`, `psycopg`, `psycopg2`, `asyncpg`, `sqlalchemy`, `pg8000`, `aiopg`, `grpc`, `kubernetes`, or the sidecar's raw `*_pb2_grpc` stubs; naming `nats://`, `postgres://`, a cluster service (`*.svc`, `*.svc.cluster.local`), `meridian.localhost`, a dashboard `/terminal/` path, or `MERIDIAN_SIDECAR_ADDRESS`. |
| `tests-exist` | The plugin has tests. | No `test_*.py` or `*_test.py` with a `def test_…` in it. |
| `tests-pass` | Its tests pass. | With `--run-tests`: pytest exits non-zero, collects nothing, or is not installed. Without it the rule is reported as not run, and does not fail. |

The page rules read HTML, CSS, SVG, script and templates, and the Python that renders a page, so they hold for a plugin in any language. The rules about the plugin's code read Python, the one SDK there is. Tests (`tests/`, `test_*.py`, `conftest.py`) are not held to the page and code rules: a test may name a colour to assert it is absent. Comments are not read, so a colour in a comment is on no page.

Nothing a checkout, a build, a virtual environment or an agent leaves beside the plugin is read, such as `.git`, `.venv`, `build`, `dist` and `.claude`. From CLI 0.1.24 neither is `.e2e`, where [a plugin's e2e](../how-to/prove-a-plugin-against-a-released-runtime.md) copies core's plugin harness out of its image: core's code, not the plugin's, which reads its own environment.

The rules match what can be decided from the text: the obvious forms, not every form. A secret copied into another variable before it is logged, or a colour built from parts in a script, gets past them. They are the floor, not the review.

### What it cannot check

These stay advice, in the template's `AGENTS.md`, because deciding them takes judgement:

- which of the kit's components or classes fits what the page shows;
- the page's layout, and whether it draws only its content, with no header bar, navigation, sign-in or theme switch of its own;
- custom properties the kit does not define, other than the page's own layout ones (the check does not know the kit's list);
- that prices and quantities reach the page as decimal strings and are never parsed as floats;
- names: of the plugin, its settings, its pages and its tests;
- whether the tests test what matters.

### Output

In text, one line per rule, and under a failed one each place it failed and what to write instead:

```text
meridian plugin check: ., by the rules of meridian 0.1.15

  ok    template-shape     the project keeps the template's shape
  ok    tool-meridian      [tool.meridian] names roles from the fixed list, and no tags
  ok    kit-linked         every page links the kit from /.meridian/ui/, and holds no copy of it
  FAIL  no-raw-colour      no raw colour: no hex, rgb(), hsl() or colour name in a page or its styles
        src/my_plugin/page.py:41: `#c0ffee` is a raw colour, which no scheme can change
          instead: the kit's custom property for what the colour means, as var(--name): …
  ok    own-origin         a page loads nothing from another origin
  ok    settings-declared  settings are declared to the SDK, not read from the environment
  ok    secrets-kept       no secret setting's value is logged or put in a page
  ok    through-the-sdk    the deployment is reached only through the SDK
  ok    tests-exist        the plugin has tests
  --    tests-pass         its tests pass: --run-tests runs them

1 of 10 rules failed, 1 place(s) in all. Fix each as it says, then check again.
```

With `--json`, one object. `line` is `null` when the failure is a whole file, or a file that is missing:

```json
{
  "dir": ".",
  "meridian": "0.1.15",
  "passed": false,
  "rules": [{"rule": "no-raw-colour", "holds": "no raw colour: …", "outcome": "failed"}, …],
  "failures": [
    {"rule": "no-raw-colour", "file": "src/my_plugin/page.py", "line": 41,
     "found": "`#c0ffee` is a raw colour, which no scheme can change",
     "instead": "the kit's custom property for what the colour means, as var(--name): …"}
  ]
}
```

`outcome` is `passed`, `failed`, or `skipped` for `tests-pass` without `--run-tests`, and from the CLI release after 0.1.36 for `role-suite` without `--verified`, its line saying `--verified holds it`.

!!! note "A freshly scaffolded plugin"
    From CLI 0.1.16, the plugin `meridian plugin new` writes keeps every rule, with its own tests and a CI workflow (`.github/workflows/check.yaml`) that runs `meridian plugin check --run-tests`. At 0.1.15 it failed `tests-exist` until you added a test.

**Exit codes:** `0` every rule holds; `1` at least one does not; `2` asked wrongly, or `--dir` is not a directory.

## `meridian plugin migrate` { #plugin-migrate }

```text
meridian plugin migrate [--to <version>] [--dir <dir>] [--image <ref>] [--force] [--run-tests] [--json]
```

From CLI 0.1.18. Moves the plugin in `--dir` to a newer release of the Python SDK, `open-meridian`. Every release of the SDK that changes what a plugin calls carries a migration from the release before it: code that rewrites the plugin to the new form, and a record of what it cannot rewrite and what a person or a coding agent must then do. Every other release carries one that only moves the pins. So the steps from any recorded release to the newest exist, and `plugin migrate` runs them in order. The first recorded step is from 0.5.0.

It needs no deployment and no session. It needs `docker`, and, unless you name both `--to` and `--image`, the Python package index, which it asks for the SDK's releases. It needs no Python on your machine.

In order, it:

1. finds the plugin's two pins, `open-meridian==<version>` in `pyproject.toml` and `ghcr.io/open-meridian/plugin-python:<version>` in the `Dockerfile`, which must name the same release;
2. refuses, changing nothing, if the plugin's directory has changes git does not hold yet, or is not in a git repository at all, unless you pass `--force`. A migration rewrites files, and git is how you see what it did and take it back;
3. picks the target: `--to`, or the latest release. It never goes backwards, and a `--to` that is not released is refused unless you name the image to use with `--image`;
4. moves both pins to the target;
5. runs each step between the two releases, in order, each over what the one before it wrote;
6. writes every file that changed, all at once, after the last step;
7. runs [`meridian plugin check`](#plugin-check) on the result;
8. reports what each step rewrote, what is left by hand, each with its rule, file and line, and the check's result.

A plugin already on the target is only checked.

| Flag | Argument | Default | Meaning |
|---|---|---|---|
| `--to` | `<version>` | the latest release | The release to move to. Never an older one than the plugin pins. |
| `--dir` | `<dir>` | `.` | The plugin's directory. |
| `--image` | `<ref>` | `ghcr.io/open-meridian/plugin-python:<the latest release>` | The SDK image the steps run in. The latest release carries every step there is. Name another to migrate with an SDK built locally, such as `plugin-python:local` from meridian-python's `make base-image`. |
| `--force` | | off | Migrate a directory whose changes git does not hold yet, or that is not in a git repository. |
| `--run-tests` | | off | Run the plugin's tests in the check, as `plugin check --run-tests` does. |
| `--json` | | off | One JSON object on stdout instead of the report. |

### Where the steps come from, and where they run

The migrations are the SDK's, released inside it: the `meridian.migrations` package in `open-meridian`, one directory per step, each holding a record, `migration.toml`, and the rewrite code the record names. So every `plugin-python:<version>` image holds the steps up to its own release.

`plugin migrate` builds an image of its own from the SDK image, once, tagged `meridian-migrate:<the SDK image's name>`: the SDK image with the SDK's `migrate` extra installed, which is [libcst](https://libcst.readthedocs.io), the library the rewrites read Python with. A plugin's own image never carries it. It runs `python -m meridian.migrations --from <pinned> --to <target>` in that image with no network and a read-only filesystem, mounting nothing. The plugin's Python files and its `pyproject.toml`, pins already moved, go in on stdin; the steps, the new text of each file that changed, and what is left by hand come back on stdout. Only `meridian` writes the plugin's directory, and only once every step has run.

An SDK image released before migrations existed (open-meridian 0.7.0 and earlier) carries none. `plugin migrate` says so, and asks for an `--image` that does.

The rewrites keep a file's formatting and comments wherever they change nothing. They do not reformat what they change to your formatter's taste: run your formatter after migrating.

### What each step does

| Step | Rewrites | Leaves by hand |
|---|---|---|
| 0.5.0 to 0.6.0: access to a plugin is read or write, and a plugin declares no tags | `tags` in `[tool.meridian]`, with the comment directly above it (`tags-undeclared`); `any(a in held.read for held in caller.access)` to `a in caller.read`, and the same for `write` (`access-any`); accounts gathered over the tags into one set to `caller.read` or `caller.write` (`access-union`); `Caller(access=(TagAccess(...), ...))` to `Caller(read=..., write=...)`, each the union over the tags (`caller-read-write`); an import of `TagAccess` nothing uses (`tag-access-import`) | `caller.access` read by a tag's own name (`access-tag-by-tag`); `TagAccess` still named (`tag-access`); `plugin.identity.tags` (`identity-tags`); tags that were declared, whose holders a deployment admin now gives read or write (`tags-granted`); a `tags` declaration it could not remove (`tags-declared`) |
| 0.6.0 to 0.6.1 | Nothing: only the pins move | |
| 0.6.1 to 0.7.0: the unlinked refusal is `meridian.NotLinked` | a meridian error's words tested for "not linked" (`"is not linked" in str(err)`, or in `err.detail`) to `isinstance(err, meridian.NotLinked)`, dropping the `isinstance(err, CallFailed)` and `err.kind == "refused"` beside it (`not-linked-isinstance`); `except meridian.CallFailed as err: if <that>: ... else: raise` to `except meridian.NotLinked: ...`, in a try's last handler (`not-linked-except`); a test's `CallFailed(topic, "refused", "... is not linked ...")` to `NotLinked(topic, "...")` (`not-linked-raised`) | the words "not linked" matched anywhere else in the plugin's code (`not-linked-by-text`) |
| 0.7.0 to 0.7.1 | Nothing: only the pins move. 0.7.1 is the first release that carries the migrations | |
| 0.7.1 to 0.8.0: the SDK declares contract v3 | Nothing: only the pins move | |
| 0.8.0 to 0.9.0: the SDK declares contract v4, and the asset class a plugin reports with a miss is an enum | `report_missing_instrument`'s `asset_class`, a string naming one of the seven classes in another case or with its prefix (`"EQUITY"`, `"asset_class_cash"`), to the class's spelling (`"equity"`, `"cash"`) (`asset-class-spelling`) | an `asset_class` string naming no class, such as `"etf"` (`asset-class-unknown`); one the migration cannot read, such as a variable (`asset-class-computed`) |
| 0.9.0 to 0.10.0: the SDK declares contract v5; pages carry their levels, and a session the level it was opened at | `Interface(admin_pages=...)` to `pages=` (`admin-pages-keyword`); a `Page(path, title)` naming no levels to `Page(path, title, levels=["admin"])` (`page-at-admin`) | `caller.deployment_admin` read to decide who is served, which opens no page since contract v5: declare the page at `admin` or ask `caller.admin` (`deployment-admin-gate`); `admin_pages` read as an attribute (`admin-pages-read`); admin pages passed as `Interface`'s third argument (`admin-pages-positional`) |
| 0.10.0 to 0.10.1: pages answer HEAD and refuse a large body; `assert_no_account_data` looks for account data, not identities | Nothing: only the pins move | |
| 0.10.1 to 0.11.0: the SDK declares contract v6; a plugin may report figures on its Summary, and a reported health stands until it is reported again | Nothing: only the pins move | |
| 0.11.0 to 0.12.0: the SDK declares contract v7; a plugin hears what its roles hear with `receive`, and reads within its read scope; a statement names its external account and states its figures per margin segment; a holding carries its cost, lots and margin requirement as reported | a `record_holdings_statement` call's flat `buying_power=`, `margin_requirement=` and `maintenance_excess=` to `figures=[StatementFigures(segment="", ...)]`, the account's figures as a whole, importing `StatementFigures` from `meridian` (`statement-flat-figures`) | a `record_holdings_statement` call naming no `external_account_id`, which a sidecar at v7 refuses from a plugin built for it: pass the external account the statement was read for, the one its rows name, and `institution=`, the institution holding it, where the connector says (`statement-external-account`) |
| 0.12.0 to 0.13.0: the SDK declares contract v8; the book of record's operations, reads and deliveries, and what of a holding cannot move | Nothing: only the pins move | |
| 0.13.0 to 0.14.0: the SDK declares contract v9; the book refuses an incomplete entry, naming each missing field in `CommandRefused.fields`, and a `Caller` names the delegation it came through | Nothing: only the pins move. A plugin that sent a lot of unknown cost or the "not stated" settlement bucket completes the entry first, whatever SDK it is built on: see [What the book requires](typed-operations.md#what-the-book-requires) | |
| 0.14.0 to 0.15.0: the SDK declares contract v10; a deployment mints its own instrument records, a resolve may state what the source says of a security, and the book requires each instrument's asset class and currency | a resolve result's `.placeholder` to `.minted` (`resolve-minted`) | a book position's `.placeholder`, which is gone: drop it, and send the person to the dashboard's Instruments page where the book refuses an incomplete record (`position-placeholder`) |
| 0.15.0 to 0.16.0: the SDK declares contract v11, the edge keeps its own: the version's declaration, a row's raw record and provenance, values as reported, each asset counted once. See [Keep what your custody plugin converts](../how-to/keep-what-the-edge-converts.md) | Nothing | an external account's `venue_account_type=` (`account-kind`), a holding's `also_counted_in_cash=` (`counted-once`) and `currency_assumed=` (`currency-provenance`), each replaced by the plugin's own conversion |
| 0.16.0 to 0.17.0: the SDK declares contract v12, the deployment serves its MCP: a route's one typed record of inputs, and tools derived from typed routes. See [Offer your pages to agents](../how-to/offer-your-pages-to-agents.md) | Nothing | a page or route that changes something and declares no `params=`: give it its record, or `tool=False` with `why=` (`typed-route`) |
| 0.17.0 to 0.18.0: the SDK declares contract v13; a plugin files a ticket for a person and reads what it filed | Nothing: only the pins move | |
| 0.18.0 to 0.19.0: the SDK declares contract v14; a custody plugin reports the custodian's activity, and operations reads, hears and links it, and each sync status the street keeps; a setting may be a table of typed columns. See [Report the custodian's activity](../how-to/report-the-custodians-activity.md#move-a-plugin-to-0190) and [Set a plugin's settings](../how-to/set-a-plugins-settings.md#declare-a-table-setting-and-read-its-rows) | Nothing: only the pins move | |
| 0.20.0 to 0.21.0: the SDK declares contract v16; a plugin at the edge declares the kinds of raw record it keeps, and past each kind's window archives, keeps or deletes them as its admin chose, each move reported. See [The archive](python-sdk.md#the-archive) and [Move a plugin to 0.21.0](../how-to/keep-what-the-edge-converts.md#move-a-plugin-to-0210) | Nothing: only the pins move. A plugin keeping one retention (`Storage(retention_days=...)`) keeps it. One adopting kinds drops any setting of its own that held a window, and its release notes name it and the window it maps to, for the admin to set once at upgrade; a setting of its own named as a declared kind's window setting is reported by `plugin check` (`window-settings`) | |
| 0.19.0 to 0.20.0: the SDK declares contract v15; a person's access to a plugin is granted per role, and a page, route, tool and setting names the roles it serves; a custody plugin re-resolves an activity once its instrument resolves, which operations reads and hears. See [Roles](python-sdk.md#roles) and [Report the custodian's activity](../how-to/report-the-custodians-activity.md#move-a-plugin-to-0200) | Nothing: only the pins move. A plugin holding one role, or none, names no role anywhere; one that comes to hold a second names `roles=` on every page, route, tool and setting, which `plugin check` reports (`roles-declared`) | |
| 0.21.0 to 0.22.0: the SDK declares contract v18, the lake: a `dgm`'s catalogue, prices and bars recorded in batches, wants, the lake's reads by business date, as of and side by side, venues resolved, the `dgm` suite; a `Money` names its cash instrument, and every date field takes a `datetime.date`. See [The lake](python-sdk.md#the-lake) | Nothing: only the pins move. `Money(amount, code)` keeps its shape | a test comparing a Money read back with one it made, which now carries `instrument_id`: compare `amount` and `currency_code`; a date sent as text that is no date, now refused |

`plugin migrate` adds two rules of its own: `pin-elsewhere`, for the old release still named in another file (a Makefile's base image, a workflow, a README), which it reports rather than moves because some of those are history; and `unreadable`, for a file that is not UTF-8, or that a step could not read as Python, which it leaves as it was.

### Output

In text, the pins it moved, each step with the files it rewrote and how many places each rule did, what is left by hand with what to write instead, and then the check's own report:

```text
meridian plugin migrate: ., open-meridian 0.5.0 to 0.7.0, the steps run in ghcr.io/open-meridian/plugin-python:0.12.0

  pins  pyproject.toml:10     open-meridian==0.5.0 -> open-meridian==0.7.0
        Dockerfile:2          ghcr.io/open-meridian/plugin-python:0.5.0 -> ghcr.io/open-meridian/plugin-python:0.7.0

  0.5.0 to 0.6.0  Access to a plugin is read or write, the same for every plugin, and a plugin declares no tags (decisions/026).
        pyproject.toml      tags-undeclared
        src/desk/access.py  access-any (3), access-union (2)

  0.6.0 to 0.6.1  A new account created by a link carries its custodian, type, owner and note: …
        nothing to rewrite: only the pins move

  0.6.1 to 0.7.0  A row refused because its external account is not linked raises meridian.NotLinked, …
        src/desk/record.py  not-linked-except, not-linked-isinstance

Wrote Dockerfile, pyproject.toml, src/desk/access.py, src/desk/record.py.

Left by hand, 1 place(s): do each as it says.
  access-tag-by-tag  src/desk/access.py:33: return any(held.tag == "statements" and held.write for held in caller.access)
        instead: read caller.read and caller.write, … A tag's name is gone: decide whether what it guarded is showing (read) or doing (write)

meridian plugin check: ., by the rules of meridian 0.1.18
  …
```

With `--json`, one object. `image` is `null` when the plugin was on its target already; `line` is `null` for a file as a whole; a place left by hand has the step it came from in `from` and `to`, or `null` for `plugin migrate`'s own rules; `check` is [`plugin check --json`](#plugin-check)'s object; `done` is true when nothing is left by hand and every rule holds:

```json
{
  "dir": ".", "meridian": "0.1.18", "sdk": "open-meridian",
  "from": "0.5.0", "to": "0.7.0", "image": "ghcr.io/open-meridian/plugin-python:0.12.0",
  "done": false,
  "pins": [{"file": "pyproject.toml", "line": 10, "from": "open-meridian==0.5.0", "to": "open-meridian==0.7.0"}, …],
  "steps": [{"from": "0.5.0", "to": "0.6.0", "summary": "…", "breaking": true,
             "rewrote": [{"file": "src/desk/access.py", "rule": "access-any", "what": "…", "places": 3}, …]}, …],
  "wrote": ["Dockerfile", "pyproject.toml", "src/desk/access.py", "src/desk/record.py"],
  "by_hand": [{"rule": "access-tag-by-tag", "file": "src/desk/access.py", "line": 33,
               "found": "…", "instead": "…", "from": "0.5.0", "to": "0.6.0"}],
  "check": {"passed": true, …}
}
```

`breaking` says whether a plugin left on the old release's code fails on the new one (0.5.0 to 0.6.0, 0.8.0 to 0.9.0, 0.11.0 to 0.12.0, and 0.14.0 to 0.15.0), rather than keeping a form the new release no longer promises (0.6.1 to 0.7.0, whose refusal still says "is not linked" today, and 0.9.0 to 0.10.0, which still takes `admin_pages` as pages at `admin`, with a `DeprecationWarning`). It is about the code once the pins move: a plugin left on 0.11.0, pins and all, keeps working at contract v6 on a sidecar at v7, which reads its flat figures as the set with no segment and its statement's account from its rows.

**Exit codes:** `0` migrated, nothing left by hand, and every rule holds; `1` something is left by hand or a rule does not hold, or it could not run (docker failed, or the SDK image carries no migrations), in which case nothing was changed; `2` asked wrongly, or refused before changing anything: `--dir` not a directory, no pins or pins that disagree, a `--to` older than the pin or not released, no recorded steps from the pinned release, or changes git does not hold yet without `--force`.

## Plugin commands on a deployment

`plugin upload`, `list`, `launch`, `stop`, `dev`, `logs`, `events` and `open` act on the delegation `meridian connect` made, or, on a runtime before contract v15, a session an earlier CLI kept. The deployment answers `upload`, `list`, `launch`, `stop`, `dev`, `logs` and `events` for a deployment admin only. It answers `open` for anybody who holds a level on that plugin, at a level they hold. See [Access](../concepts/access.md).

These flags are shared among them:

| Flag | Argument | Default | Used by | Meaning |
|---|---|---|---|---|
| `--deployment` | `<addr>` | the one deployment connected | all | Which connected deployment, when you are connected to more than one. |
| `--dir` | `<dir>` | `.` | `upload`, `dev` | The plugin's directory. Its image is built with `docker`, from its own `Dockerfile`. |
| `--instance` | `<id>` | none (required) | `launch`, `dev`, `logs`, `events`, `open` | The instance's name. Its page is found by it. Lowercase letters, digits and single hyphens, starting with a letter, at most 63 characters. |
| `--yes` | | off | `launch`, `dev` | Approve the roles the version asks for without being asked. For a script that has already shown them to a person. |
| `--json` | | off | `dev`, `logs`, `events`, `open` | JSON on stdout: one object, or one per line for `dev` and `--follow`. Progress goes to stderr. |
| `--release` | | off | `dev` | Upload the plugin as it is now as a version, and run that version in place of the live instance. |
| `--since` | `<revision>` | none | `logs`, `events` | Only what came after that revision, a whole number. |
| `--follow` | | off | `events` | Keep reporting events as they happen, until interrupted. |
| `--print` | `<path>` | none | `open` | The page at that path on the plugin's host, as you are served it, instead of a link. |
| `--level` | `manage`, `open` or `view` | the first level you hold | `open` | The level the session is opened at, as the dashboard's buttons: `manage` (`admin`), `open` (`write`) or `view` (`read`). From CLI 0.1.21. |

**Exit codes** for all of them: `0` done, `1` refused or failed, `2` asked wrongly, `3` not connected, or the delegation was revoked or has lapsed.

### `meridian plugin upload`

```text
meridian plugin upload [--dir <dir>] [--deployment <addr>]
```

Builds the plugin's image on this machine and puts it in the deployment's catalogue as a version. The steps:

1. Read `pyproject.toml` and check its [plugin manifest](plugin-manifest.md). From CLI 0.1.14, a `[tool.meridian]` that declares `tags` is refused here, before anything is built: a plugin declares none, since a person's level on a plugin is `admin`, `read` or `write`, in the deployment's access groups.
2. Build the image with `docker build`, tagged `meridian-plugin/<name>:<version>`.
3. Read the image back with `docker save`.
4. Push it into the deployment's registry through the dashboard. A layer the registry already holds is not sent again, and one another plugin's repository holds is mounted from there.
5. Send the manifest's metadata with the image's digest. The deployment records the version.

A version is recorded once and never replaced: uploading a name and version already in the catalogue is refused. On success it prints `Uploaded to <address>, as sha256:<digest>.`

### `meridian plugin list`

```text
meridian plugin list [--deployment <addr>]
```

Prints the catalogue: every version uploaded, with its roles, whether it serves a page, and the SDK version it pins, and every launch, with its instance, version and state (`launched`, `stopped` or `failed`, with the failure). Because it needs a live delegation, it is also the way to check you are connected: it exits 3 when you aren't.

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
- from CLI 0.1.24, `.e2e`, where a plugin's e2e copies core's plugin harness out of its image, which `plugin check` does not read either;
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
meridian plugin open --instance <id> [--level manage|open|view] [--print <path>] [--json] [--deployment <addr>]
```

A session on a plugin carries one level, as the dashboard home's buttons do: **Manage** at `admin`, **Open** at `write`, **View** at `read`. See [Manage, Open and View](../concepts/plugins.md#manage-open-and-view).

`--level` names it: `manage`, `open` or `view`, or the level's own name, `admin`, `write` or `read`, in any case. Anything else is refused before anything is asked, and so is a level you do not hold, by the deployment, naming the levels you do. Without `--level`, the session is opened at the first level you hold, Manage before Open before View, as the home's first button is. From CLI 0.1.21; an earlier CLI names no level, and the dashboard opens at the first held.

A page serves only the levels it is declared with. So the first level you hold may well be refused the page you ask for: as a plugin's admin, which a deployment admin is on every plugin through All plugins (admin), the scaffold's Accounts page at `/` is refused at Manage. Name the level the page is for:

```bash
meridian plugin open --instance my-plugin --level manage --print /setup   # the Setup page
meridian plugin open --instance my-plugin --level open --print /          # the Accounts page, if you hold write
```

Without `--print`, it prints a link to the plugin's page, at that level. The first browser that opens the link, within a minute, is signed in to that plugin's page alone, for as long as your delegation to the CLI lasts and 12 hours at most, and lands on its `/`; any other path on the same host is then open to it at that level. Run `open` again for another browser. With `--json`, the level the dashboard opened it at comes too:

```json
{"instance_id": "my-plugin", "url": "https://…", "level": "admin"}
```

With `--print <path>`, it prints the page at that path on the plugin's host, as you would be served it in a session at that level, instead of a link:

- `<path>` starts with a single `/`, and may not be under `/.meridian`.
- A page is at most 8 MiB, and redirects are not followed.
- It exits 1 when the plugin answers with a status outside 200–299, after printing what the plugin answered. The message on stderr names the level it was asked at. A 403 at the first level you hold, with no `--level` given, says so, and which `--level` asks at another:

```text
meridian plugin open: my-plugin answered 403 for / at Manage (admin), the first level you hold; a page serves only the levels it is declared with, and `--level open` or `--level view` asks at another
```

A page built on `meridian.Pages` answers such a request with why, such as `/ is not served under Manage; it is for Open and View.`

With `--json`, one object:

```json
{"instance_id": "my-plugin", "status": 200, "level": "write", "content_type": "text/html; charset=utf-8", "body": "…"}
```

A body that is not UTF-8 text comes as `body_base64` instead of `body`. `level` is left out by a dashboard older than levels.

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

1. Every delegation it holds, revoked at each deployment, and any session an earlier CLI kept, ended there. One with a deployment it can't reach is forgotten here: it says when the delegation lapses, which you can bring forward by revoking it from Connected clients, and a session lapses there within 30 minutes.
2. The sessions directory.
3. The binary.

| Flag | Argument | Default | Meaning |
|---|---|---|---|
| `--yes` | | off | Remove without being asked. With no terminal to ask at, it is refused without this. |

**Exit codes:** `0` removed, `1` not approved or failed. If the binary's directory is not writable, it stops before revoking or ending anything.

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
