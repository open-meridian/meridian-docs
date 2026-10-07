# The archive

A plugin at the edge (`ccm`, `custody`, `servicing`, `match`, `settlement`,
`dgm`, `reporting`) speaks to a vendor and keeps what the vendor sent it, its
**raw records**, in storage the deployment gives its instance alone. It keeps
them to reach further back than the vendor does: a custodian may keep two
years of activity, and the deployment's history should not stop where the
vendor's does. From contract v16 how long a record stays in that storage is
an admin's to set, per kind of record, and what happens after that is an
admin's choice too: the record moves to an **archive**, stays where it is,
or, only when an admin chose it, is deleted. Every move leaves its own
record.

!!! note "Contract v16"
    This page describes a runtime serving contract v16 (chart 0.1.277 or later),
    open-meridian 0.21.0, CLI 0.1.36 and the SnapTrade plugin 0.13.0. A runtime serving v15 or earlier refuses a plugin
    built on 0.21.0 at registration, naming both versions, and a plugin
    declaring no kinds keeps its records as before.

## Kinds and windows

A plugin's version declares the **kinds** of raw record it keeps, each with
a name, a label people read, a default **window** in days and whether a unit
of it can be archived. SnapTrade 0.13.0 declares two:

| Kind | Label | Default window | Archivable |
|---|---|---|---|
| `activity` | Reported activity | 2,555 days (seven years) | yes |
| `responses` | Raw responses | 30 days | yes |

A kind's window is how long a record of it stays in the plugin's storage,
counted from when the record was received. The version only gives the
default: an admin of the plugin sets each kind's window on the plugin's
**Settings** form, longer or shorter, never below a hold (see
[Holds](#holds)). A kind of state read and updated in place, such as a
session's, is declared not archivable.

The two settings for each kind are the SDK's, the same for every edge plugin,
so every edge plugin's admin sees the same controls:

| Setting | Label | What it holds |
|---|---|---|
| `<kind>_window_days` | *Label*: window | The window, in days. Its default is the kind's window. |
| `<kind>_past_window` | *Label*: past the window | `archived`, `kept` or `deleted`. |

No plugin may declare a setting of either name for a kind it declares: the
SDK refuses it when the declaration is built, the sidecar at registration,
and `meridian plugin check` before either
([`window-settings`](../api/cli.md#the-rules)). A plugin declaring no kinds
keeps one retention for its records, as before contract v16.

## Past the window

Past its window a record is, as the plugin's admin chose for its kind:

- **Archived**: moved to the instance's archive, and restorable. The
  default where a deployment admin has allowed the instance an archive and
  the kind is archivable.
- **Kept**: left in the plugin's storage. The default otherwise.
- **Deleted**: only when an admin chose it, and never inside a hold.

Choosing **archived** is refused, naming the setting, where a deployment
admin has allowed the instance no archive, or for a kind declared not
archivable. An instance with no archive keeps its records past their window.

The plugin moves its own records, because only it knows how they group: it
moves them in **units** it can find again, such as an account's day of
SnapTrade's responses, or its month of activity records, once the day or
month has ended and its last record is past the window. Through the SDK it
writes a unit to the archive, checks that each file landed, reports the move,
and only then removes the unit from its storage. It reports a deletion before
it deletes anything, so a refused deletion keeps the unit. An index of what
moved stays in the plugin's storage, so a row's reference to a record in a
moved unit still resolves: to the record, or to "archived, restorable",
never to nothing.

## The archive

The archive is where the deployment keeps an edge plugin's older records,
named when the deployment is installed:

- **On a local or on-premises deployment**, a directory on the cluster's
  node, such as a NAS export or a second disk mounted there.
  `meridian up --archive <path>` names it, and `--no-archive` declines one
  (see [Name the archive at install](../how-to/keep-older-records-in-the-archive.md#name-the-archive-at-install)).
  A cluster of more than one node names a claim already made on shared
  storage instead.
- **In a cloud**, a bucket in the provider's cold class, made for the
  deployment and named in the chart's values with the account whose workload
  identity is scoped to it. The chart and the launcher make no bucket. The
  SDK 0.21.0 reads an `s3://` bucket.
- **None**, the default. Nothing is archived, and records past their window
  are kept in each plugin's storage.

Naming one allows no plugin an archive by itself. A **deployment admin**
allows each edge plugin its archive, because it grants the deployment's
resources, possibly without limit: on the plugin's **Summary**, under
Manage, with a **bound** on its size, or none. The plugin is restarted with
its archive beside its storage: its own directory of the local archive, or
its own prefix of the bucket, the pod running as the bucket's account and
never holding a key. It is told its bound, and the SDK refuses to archive a
unit that would take the archive past it: the unit stays in storage and the
plugin tries again later. A deployment admin may change the bound, or
withdraw the archive, which restarts the plugin without it. What a withdrawn
archive holds is kept, and nothing in the deployment deletes an archive,
uninstalling included.

An admin of the plugin then configures what the plugin does within that:
each kind's window, and what is done past it.

## Holds

A **hold** is the least number of days a raw record is kept anywhere, in a
plugin's storage or its archive, counted from when it was received. Holds
are a deployment admin's, set on the **Holds** tab of the dashboard's
**Settings**, each for one edge role or for every edge role, and the longest
hold over a plugin's edge roles is the one over it. Inside it:

- **Nothing is deleted.** A deletion of a unit whose last record was received
  inside the hold is refused, by the plugin's sidecar and again by the
  deployment, with the code `REFUSAL_REASON_WITHIN_HOLD`. Nothing is
  recorded, and the unit is kept. A window's deletion and a person's alike.
- **No window goes below it.** Saving a kind's window shorter than the hold
  is refused, naming the setting and the hold. A window set shorter before
  the hold was set is marked "held longer" on the plugin's Summary.

The plugin is never told the hold: its sidecar holds it to it. A hold set to
0 days is cleared.

A hold may also ask for records that cannot be altered, **write-once**. The
deployment accepts that only where its archive is a bucket the chart says
was made with object lock (`pluginArchive.objectLock: true`). On a local
archive, or with no archive, a write-once hold is refused rather than
claimed. Holds and write-once are settings of the deployment, set to what
the firm chooses.

## Restore

An archived unit stays findable. The plugin's own pages list what moved and
where it stands, and a person holding `write` on one of the plugin's edge
roles may **restore** a unit. Every edge plugin with pages offers the same
route for it, `POST /archive/restore`, which the deployment also offers to
agents as the `restore_unit` tool, acting for the person. The unit is copied
back from the archive to a restore area in the plugin's storage, each file
checked against what was archived, and is readable there for seven days.
Then it is removed and its return recorded. Asking again meanwhile changes
nothing.

SnapTrade 0.13.0 offers it on its **Raw responses** tab, in the **Archive**
view: each unit it moved, for the accounts the person may read, with
**Restore** under Open.

Deleting a unit already in the archive is an admin's act, never a window's:
the deployment refuses a deletion of an archived unit that names no person,
and the person must hold `admin` on one of the plugin's edge roles. SnapTrade
0.13.0 offers no such action.

## Every move is its own record

Each archiving, restore, return and deletion is reported by the plugin before
it removes anything, and the deployment records it as its own record: the
kind, the unit, how many records it holds and from when to when they were
received, what became of it, and who moved it, either the rule (a window's
move names its setting and value, such as `responses_window_days 30`) or the
person, read from the assertion the plugin was handed, never written by the
plugin. A move reported again is recorded once. Nothing of a record's
content is ever in one.

So are the decisions around them: allowing an archive, changing its bound and
withdrawing it; setting, changing and clearing a hold; and changing a window,
which is a settings change naming who made it.

The plugin's **Summary**, under Manage, shows them in two parts:

- **Raw records**: one line per kind, with its window (marked default where
  nobody set it, and "held longer" under a hold), what its storage holds and
  from when to when, as the plugin last said, what the archive holds, summed
  from the moves, and the size it uses of the archive, with every kind's in
  the foot against the bound. Its head says whether an archive is allowed and
  how much of its bound is used, that it is full, that it was withdrawn, or
  that none is allowed. A deployment admin sees **Allow archive**, then
  **Change bound** and **Withdraw**, here.
- **Moves**: each move, newest first, one line each, paged: when, what
  became of the unit, its kind, the unit, its records and who moved it.

## Related

- [Keep older records in the archive](../how-to/keep-older-records-in-the-archive.md):
  allowing an archive, setting a hold and a plugin's windows, restoring,
  and upgrading SnapTrade to 0.13.0.
- [The archive in the Python SDK](../api/python-sdk.md#the-archive): what a
  plugin declares and calls.
- [Keep what your custody plugin converts](../how-to/keep-what-the-edge-converts.md):
  the storage, the raw record a row names, and its provenance.
