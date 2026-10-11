# Back up and restore a deployment

A deployment's records sit on its cluster's volumes: people, access, plugin settings and their
sealed secrets, instruments, the book, the street and the lake, in one database, beside the keys
those secrets are sealed with. A reset of Rancher Desktop, a lost node or a deleted namespace loses
them. A backup is one file that holds what a restore needs to bring the deployment back, sealed so
that only you can open it.

!!! note "Chart 0.1.298"
    Backups are made by chart 0.1.298 or later, in an image of their own,
    `ghcr.io/open-meridian/meridian-backup`, which the published chart pins to the image built with
    it. `meridian backup` and `meridian backup key` are in CLI 0.1.39 and later. Restore needs a
    later CLI: see [Restore a backup](#restore-a-backup).

| To | Run or do |
|---|---|
| Make the identity backups are sealed to | `meridian backup key` |
| Back up on a schedule | Set `backup.recipient`, `backup.path` and `backup.schedule` in the chart's values |
| Back up now | `meridian backup` |
| Back up now and copy the file here | `meridian backup --to <dir>` |
| Restore a backup | `meridian restore <file> --identity <file>` |

You back up and restore with your own cluster rights, through `kubectl` and, to restore, `helm`.
The backup itself runs in the cluster, as a Job that holds no rights there and changes nothing in
it. Nothing in the deployment restores itself.

## What a backup holds

One file per backup, named `<release>-<UTC time>.meridian-backup`, for example
`meridian-20261012T020000Z.meridian-backup`. It is a tar, sealed with age to the public key in
`backup.recipient`. It holds:

- **The keys and credentials** the chart keeps: the settings key that plugins' secret settings are
  sealed with, the dashboard's signing key and its public keys, the database's passwords and URLs,
  the broker's credentials, and the Secrets first run wrote. Without the settings key a restored
  deployment could not read its secret settings, and without the dashboard's key no sidecar would
  trust the dashboard.
- **Your own Secrets** that the values name, such as an `existingSecret`, a TLS Secret or a
  plugin's image pull Secret.
- **The deployment's key**, without which it would have to be registered with the platform again.
- **The values** the release was installed with, without `deployment.enrolmentCode`, which is spent
  once used.
- **The database**, when it is included (see [`backup.database`](#which-database-is-dumped)): a
  `pg_dump` of the database first run made, with every table's row count read in the dump's own
  snapshot.
- **A manifest** of what was taken, from which release, chart and app version, and every member's
  SHA-256, which restore checks.

It does not hold:

- **The plugin registry.** Plugins' images are uploaded again after a restore, which says which.
- **Edge plugins' own storage.** An edge plugin starts with empty storage after a restore, and
  gathers again what its vendor still serves. The book's and the street's rows are in the database.
- **A database somebody else runs**, unless you ask for it (`backup.database: true`). That database
  is its provider's to back up.

The cluster cannot read its own backups. The private half of the key, the identity, is yours, and
is needed only to restore. A copied backup volume reveals nothing without it.

## Make the identity

```bash
meridian backup key
```

It needs no deployment. It writes a new identity to `meridian-backup-identity.txt` in the current
directory, readable by you alone, and prints its public half:

```text
Wrote the identity to meridian-backup-identity.txt, readable by you alone. Keep it off the cluster,
and where a reset of this machine does not reach: a backup opens with it and nothing else.

Its public half, for backup.recipient:
  age1…
```

`--to <file>` writes it somewhere else. It never writes over a file that is already there, since a
backup sealed to the old identity would be lost with it.

Keep the identity off the cluster, and somewhere a reset of this machine does not reach, such as
your password manager or a vault. Every backup opens with it and with nothing else: lose it, and
the backups sealed to it cannot be restored. The public half, `age1…`, is not secret, and is safe
in your values and in Helm's release history.

## Turn backups on

Backups are set in the chart's values, under `backup`. Nothing is made until `backup.recipient` and
a place to write are both set. Then the chart makes a CronJob, `<release>-meridian-runtime-backup`,
that writes one backup each time it runs.

```yaml
backup:
  recipient: age1…                     # the public half `meridian backup key` printed
  path: /Users/<you>/meridian-backups  # a directory on the node
  schedule: "0 2 * * *"                # daily at 02:00, in the cluster's time zone
  keep: 14
```

| Value | Default | Meaning |
|---|---|---|
| `backup.recipient` | none | The age public key (`age1…`) every backup is sealed to. |
| `backup.path` | none | A directory on the node to write backups to. The chart makes a volume from it, which is kept when the release is uninstalled and never deleted by the deployment. |
| `backup.existingClaim` | none | A claim you made, on storage that outlives the cluster, in place of `backup.path`. On a cluster of several nodes, use this, on shared storage. |
| `backup.size` | `20Gi` | The size of the volume made from `backup.path`, requested once. |
| `backup.schedule` | none | When to back up, in cron, in the cluster's time zone. With none, nothing is scheduled, and `meridian backup` still takes one when asked. |
| `backup.keep` | `14` | How many of this release's backups to keep. Once a new one is written, the oldest beyond this are removed. |
| `backup.database` | none | Whether the database is dumped. See [below](#which-database-is-dumped). |
| `backup.image` | `ghcr.io/open-meridian/meridian-backup` | The image the backup runs in: `pg_dump` and `psql` at the major version of the database the chart brings, and `age`. |

Daily suits a deployment you depend on, hourly a development one. A restore brings the deployment
back as it was at the last backup, so the interval is what you can lose.

**Where backups go.** On Rancher Desktop, `backup.path` must be under your Mac's home folder, which
the VM mounts and a reset of Rancher Desktop keeps. A path inside the VM is wiped with it.
Elsewhere, name storage that survives the cluster: a disk or a share mounted on the node, or a claim
(`backup.existingClaim`).

**What is removed.** Only this release's backups in that place count against `backup.keep`, and
only once a new one is written. A backup that fails removes nothing. Neither does one taken while
the deployment has no database URL, before first run or while a restore withholds it, so a restore
in progress never rotates out a backup that holds the database.

The chart refuses values it cannot honour, before anything is installed:

| It refuses | Because |
|---|---|
| `backup.schedule` without `backup.recipient` | There is no unencrypted backup. |
| `backup.schedule` without `backup.path` or `backup.existingClaim` | There is nowhere to write. |
| Both `backup.path` and `backup.existingClaim` | Name one place for backups. |
| `backup.database` other than `true`, `false` or nothing | Those are the three it takes. |

### Which database is dumped

The keys, the values and the manifest are backed up whatever you choose. The database is dumped by
this rule:

| `backup.database` | A database the deployment brought | A database you run |
|---|---|---|
| Not set (the default) | Dumped | Not dumped: it is its provider's to back up |
| `true` | Dumped | Dumped, as its migrating role |
| `false` | Not dumped | Not dumped |

To dump a database you run, `backup.image` must hold a `pg_dump` no older than its server: name an
image that has one. Restore does not load such a dump yet (see [below](#with-a-database-you-run)).

### Apply the values

At install, pass them to `meridian up` in a values file:

```bash
meridian up --id DEP-… -f backup.yaml
```

On a running deployment, apply them with Helm, as an upgrade to the version it already runs,
keeping its own values (see [Upgrade a deployment](upgrade-a-deployment.md#plain-helm)):

```bash
helm upgrade meridian oci://ghcr.io/open-meridian/charts/meridian-runtime \
  --version <the version it runs> --namespace meridian --reset-then-reuse-values -f backup.yaml
```

`meridian upgrade-deployment` does not take a values file.

## Back up now

```bash
meridian backup
```

It runs the backup CronJob once, now, whether or not a schedule is set, waits for it, and says what
it wrote. Only names, counts, sizes and the file's hash are printed, never a value:

```text
Backed up meridian to meridian-20261012T143005Z.meridian-backup (<bytes> bytes), on the deployment's backup volume.
  backup: secrets: meridian-meridian-runtime-settings-key …
  backup: the deployment's key, from its volume
  backup: the database meridian: <n> tables, <n> rows, dump <bytes> bytes
  backup: wrote meridian-20261012T143005Z.meridian-backup <bytes> bytes sha256 <hash>
```

With `--to <dir>` it also copies the file to that directory on this machine, and checks its size
and SHA-256 against what the Job wrote:

```bash
meridian backup --to ~/meridian-backups
```

```text
Copied to /Users/<you>/meridian-backups/meridian-20261012T143005Z.meridian-backup, its SHA-256 checked. It opens only with the identity whose public half is backup.recipient.
```

Take one with `--to` before an upgrade, or before resetting Rancher Desktop.

If backups are not set up, it says so and names the values to set. `--release` and `-n` name another
release or namespace; `--timeout` (default `10m`) is how long it waits. See
[`meridian backup`](../api/cli.md#meridian-backup).

## Restore a backup

!!! warning "Restore needs CLI 0.1.40 or later"
    CLI 0.1.39 has `meridian restore`, but its restore gives the components the database's URL
    without restarting the conductor and the dashboard, which read it only when they start: the
    conductor is left without its database, and first run keeps waiting with its rights. Run
    `meridian upgrade` first. `meridian --version` says which you have.

You need the backup file, the identity it was sealed to, and a cluster to restore into, with
`kubectl` pointing at it. Restore goes only into a namespace that holds no release of that name and
none of the backup's Secrets, so it never restores over a deployment. It does not ask before it
starts: check `kubectl config current-context` first.

```bash
meridian restore meridian-20261012T143005Z.meridian-backup --identity meridian-backup-identity.txt
```

By default it restores into the namespace the backup was taken in, as the release it was taken of,
from the published chart at the version the backup was taken on. `-n` names another namespace.
The release must be the backup's own, because every object it restores is named for it.

It says each step on stderr as it goes:

1. **Open.** It decrypts the file with the identity, checks every member against the backup's
   SHA-256 list, and reads the manifest. A file sealed to another identity, or a member that is not
   what was written, is refused.
2. **Check where.** It names the cluster and namespace, and refuses, changing nothing, if the
   namespace holds the release or any of the backup's Secrets. It makes the namespace if there is
   none.
3. **Put the keys back.** It makes every Secret the backup holds, with the database's URL left empty
   so that nothing starts against the database yet. Where the deployment made its own key, the key
   goes into a Secret, `<release>-meridian-runtime-key`; where you gave it one
   (`key.existingSecret`), your own Secret is put back instead.
4. **Install.** It runs `helm install` with the values you chose, those that differ from the chart's
   own defaults, so a default the chart has changed since still applies.
5. **Restore the database.** It starts the database the deployment brings, makes the database and
   its two roles with the backed-up passwords, refuses a database that already holds tables, and
   loads the dump.
6. **Check it.** It counts every table's rows and compares them with the counts the backup took. If
   any differs it stops, names each table, and keeps the URL withheld: nothing runs against a
   database that does not hold what was backed up.
7. **Start.** Only then does it give the components the database's URL. The migration runs, the
   conductor and the dashboard restart with the URL, first run gives up its rights, and it waits for
   every component of the release to be ready.

```text
  Opened meridian-20261012T143005Z.meridian-backup: meridian (DEP-…) taken 20261012T143005Z of chart 0.1.…, every member's hash checked
  Restoring into the cluster rancher-desktop, namespace meridian
  Made <n> Secrets (the database's URL withheld), the deployment's key among them
  Installed meridian from oci://ghcr.io/open-meridian/charts/meridian-runtime 0.1.…
  Started the database, and made meridian and its two roles
  Restored meridian: <n> tables and <n> rows, each table's count as the backup counted it
  Gave the components the database's URL
  Restarted the conductor and the dashboard with it; first run gave up its rights
  Every component is ready
```

Then it reports what was restored on stdout:

```text
Restored meridian into meridian from meridian-20261012T143005Z.meridian-backup.
  The database meridian: <n> tables, <n> rows, every count as backed up.
  <n> Secrets and the deployment's key, as they were: secret settings open with the settings key they were sealed with, and every sidecar trusts the dashboard's key.
  Launched plugins, whose images were in the deployment's registry and are not in a backup: <instance>, …. Upload each again with `meridian plugin upload`; an edge plugin's own storage starts empty, and it gathers again what its vendor still serves.
```

### After a restore

- The same people, access, accounts, settings and book are there, and secret settings open with the
  restored settings key.
- Upload each launched plugin the report names again with `meridian plugin upload`.
- Where the deployment made its own key, it is now held in the Secret `<release>-meridian-runtime-key`.
- Its values are the ones it was backed up with, `backup` among them, so it backs up as before.

If a restore stops partway, the namespace holds what it made, and restore will not go into it
again. Empty the namespace, or restore into another with `-n`.

### Restoring on the same cluster

After a namespace is deleted, the volume made from `backup.path` is left behind, `Released`.
Delete it before you restore. The directory and the backups in it are
kept:

```bash
kubectl delete pv <namespace>-<release>-meridian-runtime-backup
```

A reset of Rancher Desktop leaves no such volume.

### With a database you run

When the database is one you run, and the backup does not include it, restore puts its URL back as
it was, and the deployment reaches that database again. Its records are the ones the database
holds, so restore it from your provider's own backups first if it was lost.

A backup taken with `backup.database: true` holds a dump of that database, which restore does not
load yet. It installs the release, stops with the URL withheld, and says to restore the database
with your provider's tools and then fill the database's Secret.

## Related

- [Upgrade a deployment](upgrade-a-deployment.md)
- [Remove or start over](remove-or-start-over.md)
- [Command line reference](../api/cli.md#meridian-backup)
