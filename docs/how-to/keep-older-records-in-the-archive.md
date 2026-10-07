# Keep older records in the archive

A plugin at the edge keeps the raw records its vendor sent, and past each
kind's window it archives them, keeps them or deletes them, as its admin
chose. This page shows a deployment admin how to name the archive at
install, allow a plugin its archive and set holds, and an admin of a plugin
how to set its windows and restore what was archived. Why it works this way
is in [The archive](../concepts/the-archive.md).

!!! note "Contract v16"
    This page describes a runtime serving contract v16 (chart 0.1.277 or later),
    open-meridian 0.21.0, CLI 0.1.36 and the SnapTrade plugin 0.13.0.

Who does what:

| Task | Who |
|---|---|
| Name the archive, or none, at install | Whoever runs `meridian up` |
| Allow a plugin its archive, and set its bound | A deployment admin |
| Set a hold | A deployment admin |
| Set a plugin's windows, and what is done past them | An admin of the plugin |
| Restore an archived unit | A person holding `write` on the plugin |

## Name the archive at install

On a local or on-premises deployment the archive is a directory on the
cluster's node: a NAS export or a second disk mounted there. `meridian up`
asks for it before it installs, or you answer with a flag:

```bash
meridian up --id DEP-XXXXXXXXXXXXXXXXXXXXXXXXXX --archive /mnt/nas/meridian-archive
meridian up --id DEP-XXXXXXXXXXXXXXXXXXXXXXXXXX --no-archive
```

`--archive <path>` takes the directory's absolute path on the node, and
`--no-archive` declines one. Given neither, `up` asks at a terminal, and
pressing Enter is none; with no terminal to ask at, it takes none. A
`--params` file answers it with `archive`, a path or `none`, so a scripted
install is never stopped by the question:

```yaml title="first-run.yaml"
archive: /mnt/nas/meridian-archive
# ... the wizard's own answers
```

The answer is the chart's `pluginArchive.path`, made into a volume and a
claim of their own (`pluginArchive.size`, 100Gi by default). On a cluster of
more than one node, name a claim already made on shared storage instead, in a
values file. In a cloud, the archive is a bucket in the provider's cold
class, made for the deployment, named in a values file with the account
whose workload identity is scoped to it; `up` then asks nothing:

```yaml title="archive.yaml"
pluginArchive:
  bucket: s3://firm-meridian-archive
  serviceAccount: meridian-archive
  objectLock: true    # only where the bucket was made with object lock
```

```bash
meridian up --id DEP-XXXXXXXXXXXXXXXXXXXXXXXXXX -f archive.yaml
```

The archive said in two places, such as a flag and a values file, is refused
before anything is installed, rather than one of them dropped. None is the
default: nothing is archived, and records past their window stay in each
plugin's storage.

`meridian upgrade-deployment` keeps the archive, as it keeps every value the
deployment was given, and says so in its plan:

```text
  Its archive, /mnt/nas/meridian-archive on the cluster's node, is kept: the deployment's own values carry it.
```

Naming an archive allows no plugin one. Allow each, below.

## Allow an archive and set its bound

As a deployment admin:

1. On the dashboard's home, choose **Manage** on the edge plugin. Its
   **Summary** opens.
2. Choose its **Raw records** part. Its head says **No archive allowed:
   records past their window are kept.**
3. Choose **Allow archive**. In the dialog, give the **Bound, in GiB**, a
   whole number, or leave it empty for no bound, and the archive may then
   grow without limit.
4. Choose **Allow**.

The plugin is restarted with its archive, and the head now says how much of
the bound is used, such as **Archive allowed: 1.2 GiB of at most 50 GiB
used**, or that it is full. Each kind's line shows the size it uses, and the
foot every kind's against the bound. A plugin whose archive is full keeps
the units that would not fit in its storage, and tries again later.

**Change bound** opens the same dialog. **Withdraw** restarts the plugin
without its archive: what the archive holds is kept, records past their
window stay in storage, and the head says **Archive withdrawn**. Allowing,
changing the bound and withdrawing are each recorded, naming you.

Allowing is refused, saying why, on a deployment installed with no archive,
and for a plugin holding no edge role. An admin of the plugin who is not a
deployment admin sees the part and no button.

## Set a hold

As a deployment admin:

1. Open the dashboard's **Settings** (the gear at the top right), and its
   **Holds** tab.
2. Choose **Set a hold**. In the dialog, choose what it **Covers**: one edge
   role, or **Every edge role**.
3. Give **Kept at least, in days**, up to 36,500.
4. Tick **Records that cannot be altered** only where the deployment's
   archive is a bucket made with object lock. Anywhere else the hold is
   refused rather than claimed.
5. Choose **Set**.

Each hold is one line: what it covers, the days, whether it is write-once,
and who set it and when. **Edit** changes it, and **Clear**, or 0 days,
clears it. The longest hold over a plugin's edge roles is the one over it,
and its **Raw records** part says so: **A hold of 400 days is over it:
nothing younger is deleted.** Each change is its own record.

Inside the hold, a deletion is refused and the unit kept, and a window
cannot be saved shorter than the hold.

## Set a plugin's windows

As an admin of the plugin, on its **Settings** form (see
[Set a plugin's settings](set-a-plugins-settings.md#open-the-form)), each
kind the plugin declares has two settings:

| Field | What to give |
|---|---|
| *Kind*: window | How long a record of the kind stays in the plugin's storage, in days from when it was received. Empty, it is the version's default. |
| *Kind*: past the window | **Archived**, moved to the archive and restorable; **Kept**, left in the plugin's storage; or **Deleted**, never inside the hold. Empty, it is **Archived** where the plugin has an archive and the kind can be archived, and **Kept** otherwise. |

SnapTrade 0.13.0's are **Reported activity: window** (2,555 days by
default), **Reported activity: past the window**, **Raw responses: window**
(30 days) and **Raw responses: past the window**.

Choose **Save settings**. The deployment refuses the save, naming the
setting, for a window shorter than the hold over the plugin
(`activity_window_days: 90 is below the hold of 400 days`), and for
**Archived** where no archive is allowed or the kind cannot be archived.
The change reaches the plugin without a restart; SnapTrade 0.13.0 moves what
is now past its window when its settings arrive and after each read. Each
change is recorded, naming you.

The **Raw records** part of the plugin's Summary shows each kind's window,
marked **(default)** where nobody set it, and its **Moves** part each move
made, by which window or which person.

## Restore archived records

As a person holding `write` on the plugin, on the plugin's own page, under
**Open**. In SnapTrade 0.13.0:

1. Open SnapTrade with **Open**, and its **Raw responses** tab.
2. Choose the account, then the **Archive** view. Each unit SnapTrade moved
   for the accounts you may read is one line: the account, the kind, when
   its records were received, how many, and where it stands.
3. Choose **Restore** on a unit in the archive.

The unit is copied back to the plugin's storage and readable for seven days:
SnapTrade shows restored reads on **Read** and **Kept reads** as any kept
read. Then it is removed again, and its return recorded. A row's reference
to a record that moved opens where it stands, with **Restore** beside it
while it is in the archive. The restore is recorded, naming you.

An agent connected to the deployment for you restores the same way, with the
plugin's `restore_unit` tool, the kind and the unit (see
[Offer your pages to agents](offer-your-pages-to-agents.md)).

## Upgrade SnapTrade to 0.13.0

SnapTrade 0.12.0 kept each read's responses for **Keep raw responses for**
(`raw_retention_days`) and each activity's record for **Keep activity
records for** (`activity_retention_days`), then deleted them. 0.13.0 drops
both settings and carries neither value over: its two kinds' windows take
their place, and the deployment admin sets them once at upgrade.

| 0.12.0's setting | 0.13.0's setting | Default |
|---|---|---|
| `raw_retention_days` (Keep raw responses for) | `responses_window_days` (Raw responses: window) | 30 days |
| `activity_retention_days` (Keep activity records for) | `activity_window_days` (Reported activity: window) | 2,555 days |

1. Upgrade the deployment to a runtime serving contract v16 first
   ([Upgrade a deployment](upgrade-a-deployment.md)): SnapTrade 0.13.0 is
   built on open-meridian 0.21.0, which a runtime serving v15 refuses at
   registration, naming both versions.
2. On SnapTrade's **Settings** form, under 0.12.0, note what the two old
   settings hold. One never saved, or holding its default, needs nothing
   set later.
3. Move the instance to 0.13.0:

    ```bash
    meridian plugin stop snaptrade
    meridian plugin launch snaptrade 0.13.0 --instance snaptrade
    ```

4. On SnapTrade's **Settings** form, set **Raw responses: window** and
   **Reported activity: window** to the values you noted, and choose what is
   done past each window.
5. If SnapTrade should archive, allow it an archive (above).

Until a window is set it is its default. From 0.13.0 nothing is deleted
unless an admin chooses **Deleted**, and a reported activity is never
deleted within the history SnapTrade reported. What 0.12.0 deleted past its
retention is not brought back. On its first pass 0.13.0 moves 0.12.0's
records into units, keeping their times.

## Related

- [The archive](../concepts/the-archive.md): kinds and windows, holds,
  restore, and the records every move leaves.
- [The archive in the Python SDK](../api/python-sdk.md#the-archive), for a
  plugin's developer.
- [`meridian up`](../api/cli.md#meridian-up) and
  [`meridian upgrade-deployment`](../api/cli.md#meridian-upgrade-deployment).
