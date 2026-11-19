# Run a plugin as shards or with a standby pod

One plugin instance can run as several pods: **shards**, which share its
subjects between them, and a **standby pod**, which waits and takes over a
shard whose pod is lost. The instance stays one instance: one set of
settings, one licence and entitlements, one page, one set of records.
Only the pods change.

- **Shards** spread a data plugin's subjects over pods, each with its own
  connection to the vendor, up to as many as the vendor allows.
- **A standby pod** keeps a plugin answering when its pod or its node is
  lost, without waiting for Kubernetes to start it again. Run one for an
  `oms`, an `ems`, a `connectivity` plugin and a live `data` plugin.

This page is for a deployment admin. For what each launch setting is, see
[Its limits, shards and standby pod](../concepts/plugins.md#its-limits-shards-and-standby-pod).

## Before you start

- **The deployment runs standbys of its own.** Shards and a standby pod
  take leases under an account the deployment makes where its stores run a
  standby, as [the HA profile](../concepts/service-levels.md#the-ha-profile)
  sets. Elsewhere a launch asking for either is refused, saying so.
- **Shards are for a `data` plugin** whose version declares more than one
  (its `most_shards`, the vendor's limit on connections). Any plugin may
  run a standby pod.
- **A plugin that keeps storage needs storage its pods share.** A plugin
  holding an edge role keeps its vendor's raw records in storage of its
  own. On one node its pods share it as they are. On several nodes they
  share it through a ReadWriteMany storage class (a cloud's file store,
  CephFS, NFS, Longhorn's RWX) that supports POSIX record locks, named in
  `pluginStorage.shared.storageClassName`:

    ```bash
    meridian upgrade-deployment --set pluginStorage.shared.storageClassName=efs-sc
    ```

    or, at install, `meridian up --shared-storage-class efs-sc`.
    `meridian doctor` says, for each plugin that keeps storage, whether it
    can take a standby here.

## To launch it

=== "Dashboard"

    On **Plugins**, open the version's **Launch** sheet. Under its limits,
    tick **Standby pod**, and set **Shards** where the version declares more
    than one. Approve its roles and **Launch**.

=== "Command line"

    ```bash
    meridian plugin launch my-data 0.2.0 --instance my-data-1 --shards 2 --standby
    ```

    It shows the shards and the standby beside the roles before it asks,
    and reads back what the deployment kept.

=== "Your agent"

    [`dashboard__launch_plugin`](../api/core-tools.md#dashboard__launch_plugin)'s
    `shards` and `standby`.

The instance runs a pod per shard and one more for the standby. Each
shard's sidecar holds its share of the instance's limits, the limits
divided by the shard count, so a count above the instance's
**Requests at once** or **Answers in flight** is refused, naming `shards`.

To change the count, or to go back to one pod, launch the instance again
with the new values, or with neither `--shards` nor `--standby`.

## What runs

- **Each shard holds a lease** in the deployment, `<instance>-shard-<n>`.
  A standby holds none until it takes one. The deployment makes the leases
  and keeps them, also after the instance stops; deleting one by hand is
  refused.
- **Subjects are shared out by the deployment**, over the shards that hold
  a lease. Each sidecar hands its plugin only its share of what is wanted,
  so the plugin follows its share with no code of its own.
- **A standby stands by.** Its plugin is not started until its sidecar
  takes a lease, and the pod shows as not ready while it waits. Its sidecar
  keeps the instance's standing wants meanwhile, so it can serve at once.

`meridian status` counts the shards as what the plugin wants ready, and its
standby beside them:

```text
Plugins:
  my-data-1  2/2 ready, 1 standby  no restarts  memory 91 MiB of 512 MiB (18%)  …
```

## What a takeover looks like

When a shard's pod or its node is lost, its lease lapses, and:

1. **The standby takes the shard.** Before it serves, the deployment raises
   the shard's epoch in the lake and the book, so nothing the lost pod sends
   afterwards is kept: its writes are refused as fenced, and its sidecar
   stands by again.
2. **It serves at once.** It hands its plugin the shard's share of the
   standing wants it kept, and the plugin's pages and reads go on from the
   lake as before.
3. **Without a standby**, the shards still holding leases share the lost
   shard's subjects between them until its pod is back.

Each takeover is its own record. It shows on the Resilience page's
**History** as `shard taken over`, naming the instance, the shard, the pod
that took it, the one before, the epoch and why (its lease lapsed, or it
was released). `meridian doctor` prints each shard's epoch and its last
takeover.

**On the order path.** A placement sent before the takeover whose answer
never came is reported once as **outcome unknown** by the pod that now
holds the shard, and never sent again by itself: the trader resolves it,
as with any outcome unknown (see
[The order lifecycle](../concepts/the-order-lifecycle.md)). A venue's
charge is booked once, however often it is reported.

**While the Kubernetes API does not answer,** a data plugin's shards keep
recording. An order-path plugin's pods stop sending until they can renew
their lease, since a fence cannot call back an order a venue has.

## Its storage { #its-storage }

The instance's pods share one claim, `<release>-meridian-runtime-shared-storage-<instance>`.
Shard *n* writes only in its own folder, `shard-<n>/`, and every pod reads
every folder, so a standby that takes a shard carries on its records, and
a raw record any shard kept is read from any pod.

**The first launch as several pods copies the storage.** An instance that
ran as one pod has its own storage copied into the shared claim's
`shard-0/` before its pods start. The launch waits for the copy, and the
Plugins page and `meridian plugin list` then say where it went:

```text
Its storage was copied from meridian-meridian-runtime-storage-my-data-1 into meridian-meridian-runtime-shared-storage-my-data-1, folder shard-0/, on 2026-11-19. The old claim is kept.
```

The old claim is kept as it was, and the deployment never deletes either.
A later launch of one pod runs as shard 0 on the shared claim.

**An archive in a bucket.** An instance of several pods runs under an
account of its own, `<fullname>-shards-<instance>` (`<release>-meridian-runtime-shards-<instance>`
by default), and its archive's bucket must trust that account as well as
the deployment's own. Until it does, the plugin waits unregistered and says
the bucket refuses that account. `meridian doctor` names each account and
the step for its cloud:

| Cloud | The step |
|---|---|
| EKS, IAM roles for service accounts | In the role's trust policy, a `StringLike` condition on the token's `sub` of `system:serviceaccount:<namespace>:<fullname>-shards-*`. A change is picked up within a minute. |
| EKS Pod Identity | An association for each instance's account. One added after the pod started needs the plugin launched again. |
| GKE Workload Identity | `roles/iam.workloadIdentityUser` on the Google service account, bound for each instance's account alone: `serviceAccount:<project>.svc.id.goog[<namespace>/<fullname>-shards-<instance>]`. Never the namespace as a whole, which every pod in it would share. |
| Azure Workload Identity | A federated identity credential for each instance's account. |

## If the launch is refused

| It says | What to do |
|---|---|
| `... asked shards or a standby pod, and this deployment's chart renders no shape for them ...` | Run the stores with standbys, as the HA profile does, then launch again. |
| `... its plugin keeps storage: this deployment's chart offers no shared storage (pluginStorage.shared.storageClassName)` | Name a ReadWriteMany class, as above. |
| `shards: ... was asked <n> shards, and its ... is <limit> ...` | Fewer shards, or a higher limit for the instance. |
| `reading <instance>'s copy; launch again once it ends` | Wait, then launch again. |

An upgrade that would leave the stores with no standby, such as
`resilience.profile=tolerant`, is refused while any plugin runs as shards
or with a standby pod, naming each. Launch them as one pod first.

## If you write the plugin

- **Declare the shards your vendor allows:** `Declaration(most_shards=...)`,
  the most connections one key may hold. 0 or 1 says it is not shardable.
- **Write only in `edge.storage_dir()`.** Once the plugin has registered as
  a shard, it is its own shard's folder; `edge.instance_storage_dir()` is
  every shard's, to read. Raw record keys and archive objects are prefixed
  `shard-<n>/` by the SDK, and `find_record` finds a record whichever shard
  kept it. A unit of another shard is restored by that shard's own pod.
- **Let the plugin wait.** A standby's role classes start only once its
  sidecar holds a lease. When a sidecar is lost, `meridian.run` stops the
  role classes (`on_stop`) and waits for it in the same process; the plugin
  never exits for it.

See [The Python SDK](../api/python-sdk.md#instance_storage_dir).

## Related

- [Plugins, roles and grants](../concepts/plugins.md#its-limits-shards-and-standby-pod).
- [Service levels](../concepts/service-levels.md#what-a-failover-looks-like):
  what a failover looks like.
- [Keep older records in the archive](keep-older-records-in-the-archive.md).
