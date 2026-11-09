# Service levels

A deployment can run on a laptop or across a cluster's zones, and the
failures it rides out grow with where it runs. This page names four levels,
each by where a deployment runs, says what each needs and the chart values
that reach it, as chart 0.1.477 delivers them.

It states tested behaviour only. It is no service agreement, no uptime
figure and no claim of readiness for any regulation. Recovery times are
given only where they are the design's **targets**, and are labelled so.
Real hardware may fail in ways the tests' injections do not reach.

## The levels at a glance

| Level | For | Tolerates | Configuration | Footprint |
|---|---|---|---|---|
| **Desktop** | Trying Open Meridian, building a plugin | A pod lost, by restart | The default; `meridian up` | Measured, [below](#desktop) |
| **Single node** | An individual or a small firm on one server | A pod lost, by restart; a lost volume, by restoring a backup | The default, plus scheduled backups kept off the machine | One server, and backup storage off it |
| **Multi-node** | A firm on several servers in one site | A pod or a node lost, by a warm standby taking over | A warm standby per writer, `<component>.standby: 1` | Three nodes |
| **Multi-zone** | A firm spread over a site's zones | A pod or a node lost, each writer and its standby in different zones | A warm standby per writer, spread over three zones, `zones` | Three nodes, one per zone, or more |

## How a component fails over { #how-a-component-fails-over }

Every store is one **writer**: the lake, the book of record, the street
store, the instrument store, the conductor and the launcher each write as
one member, so a second replica would be a second writer over the same
data. What adds a copy is a **warm standby**:

- **`<component>.standby: 1`** runs a standby beside the writer: the same
  image, holding no lease and serving nothing, following the writer's
  **change log**. Each store keeps a change log, one message per committed
  transaction, published only while a follower such as a standby is
  listening, so a deployment with no standby publishes nothing.
- **The lease.** The writer holds a Kubernetes `Lease` in the release's
  namespace and renews it every `leases.renewSeconds` (2 by default). When
  it lapses unrenewed for `leases.durationSeconds` (6 by default), the
  standby takes it.
- **The fence.** Taking over, the standby raises its partitions' epoch,
  which the store that is the record keeps, so nothing the old writer
  begins afterwards is kept. The old writer comes back as the standby.
- **Ready.** A standby is ready while its lag behind the writer's change
  log is under `<component>.readyLagMs` (5000 by default).
- **Placement.** With a standby, the writer and its standby are spread over
  nodes, and over the `zones` named, and a `PodDisruptionBudget` keeps a
  drain from taking both at once. A rollout starts the new member beside the
  writer, which hands its lease over as it stops.
- **A lost node.** Every stateless component tolerates a node that is not
  ready or unreachable for 30 seconds, not Kubernetes' 300, before it is
  moved, at every level. The database the chart brings keeps Kubernetes'
  own tolerations: it waits for its node and is never force-deleted. The
  chart's `tolerations` are added after these.

The default is the **tolerant** one: `standby: 0` for every component, one
member each, and a component lost is back by Kubernetes restarting it. With
`standby: 1` the standby takes over without waiting for the restart.
[The HA profile](#the-ha-profile) sets every standby, and the database's,
the broker's and the dashboard's counts, at once.

**What CI tests today.** Core's CI installs the chart in both shapes on a
scratch cluster and injects failures, timing each recovery against its
bound:

| Shape | Failures injected | Held to (targets) |
|---|---|---|
| Tolerant, the default | A writer's process killed (the lake, the book); a component cut from its database by a network policy | Back by restart within 2 minutes |
| A warm standby per writer, three zones | A writer's process killed (the lake, the book, the street, the instrument store); a writer's node paused past its lease; a writer cut from the broker and the API server but not its database; a writer's node stopped; a component cut from its database | The book, the street and the instrument store answering again within 10 seconds, the lake's writes within 15 seconds |

## Desktop { #desktop }

The default chart, as `meridian up` installs it: one member of each
component, no standby, the database the first-run wizard brings.

**Tolerates** a pod lost, by Kubernetes restarting it.

**Footprint**, measured on CI's GitHub-hosted Linux runner in a k3s cluster,
the default profile with no plugin, from v29's chart:

| | |
|---|---|
| Pods | 12, and 13 with the database the wizard brings |
| Memory requested | 1216 MiB |
| Memory limits | 6912 MiB |
| CPU requested | 700 millicores |
| Memory at its peak | 162 MiB across the release's pods, in a minute once every workload is ready |
| Disk | 34.9 MiB for its databases |

Every later chart is held to this in CI: no new pod; memory requested and
at its peak at most 15% over; CPU requested at most 15% over; disk at most
10% over. A plugin adds its own pod and sidecar.

## Single node { #single-node }

The default chart on one server, with backups.

**Tolerates** a pod lost, by restart; a lost volume, by restoring the last
backup to a new install.

**Configuration:** schedule backups, sealed to an administrator's key and
written to storage that outlives the machine. See
[Back up and restore a deployment](../how-to/back-up-and-restore.md).

```yaml title="single-node.yaml"
backup:
  schedule: "0 2 * * *"           # cron, in the cluster's time zone
  recipient: age1...              # the public half of `meridian backup key`
  existingClaim: meridian-backups # storage that outlives the machine
```

```bash
meridian upgrade-deployment -f single-node.yaml
```

What is lost in a restore is what changed since the last backup.

## Multi-node { #multi-node }

A warm standby for each writer, on a cluster of several nodes in one site.

**Tolerates** a pod or a node lost: the standby takes the writer's lease and
answers, without waiting for a restart.

**Configuration:** each component's `standby`:

```yaml title="multi-node.yaml"
lake: {standby: 1}
bor: {standby: 1}
street: {standby: 1}
instrument: {standby: 1}
launcher: {standby: 1}
```

```bash
meridian upgrade-deployment -f multi-node.yaml
```

`upgrade-deployment` merges the file over the deployment's own values and
shows what it changes before it asks.

**The conductor's standby needs the deployment's key in a Kubernetes
Secret**, named in `key.existingSecret` with `key.generate=false`. The key
the chart generates lives on a volume one node mounts at a time, so a
standby on another node could not start, and the chart refuses
`conductor.standby: 1` with a generated key. A deployment whose key the
chart generated keeps its conductor without a standby.

The database stays one instance; [the HA profile](#the-ha-profile) adds
its standbys.

## Multi-zone { #multi-zone }

The multi-node configuration, with its members kept within and spread over
three zones.

**Tolerates** a pod or a node lost, as multi-node, and its members are
spread so that one zone holds a writer or its standby, never both.

**Configuration:** the multi-node values, plus the zones, by the nodes'
`topology.kubernetes.io/zone` labels:

```yaml title="multi-zone.yaml"
zones: [zone-a, zone-b, zone-c]
```

```bash
meridian upgrade-deployment -f multi-node.yaml -f multi-zone.yaml
```

The database stays one instance; [the HA profile](#the-ha-profile) adds
its standbys.

## The HA profile { #the-ha-profile }

`resilience.profile` turns every count of the HA configuration on at once,
each still overridable by its own value:

| Value | `tolerant`, the default | `ha` |
|---|---|---|
| `<component>.standby` (`lake`, `bor`, `instrument`, `street`, `conductor`, `launcher`) | 0 | 1 |
| `database.brought.standbys` | 0 | 2, under Patroni |
| `broker.replicas` | 1 | 3 |
| `broker.jetstream.replicas` | 0 | 3, the analytics component's work queue |
| `dashboard.replicaCount` | 1 | 2 |
| `analytics.coordinator.replicaCount`, `analytics.worker.replicaCount` | 1 | 2 |

```bash
meridian upgrade-deployment --set resilience.profile=ha
```

`ha` needs the deployment's key in a Secret named by `key.existingSecret`,
as the conductor's standby does; the chart refuses it without one. See
[To move to the HA profile, and back](../how-to/upgrade-a-deployment.md#to-move-to-the-ha-profile-and-back)
for the two upgrades a brought database takes to move under Patroni.

**The database.** With standbys, the database the chart brings is a primary
and two standbys under Patroni, each on its own volume and node. One standby
is synchronous and strict, so a primary cut off from every standby
acknowledges no commit alone: the book's, the street store's, the
instrument store's and the configuration's commits wait for it, and the
lake's commit locally. The database's Service follows the primary. A
database that has moved under Patroni stays under it, standbys or none.
`meridian status` lists its members, each primary or standby, and how far
each standby is behind.

**The broker.** Three servers, each keeping its JetStream state on a volume
of its own (`broker.jetstream.size`, `1Gi`), so a server restarted rejoins
with what it held. A client moves to another server when its own has not
answered for 2 seconds.

Every count the chart takes is one CI tests, and any other is refused.

## The chart's values { #the-charts-values }

| Value | Default | What it does |
|---|---|---|
| `resilience.profile` | `tolerant` | `tolerant` or `ha`: [the HA profile](#the-ha-profile) |
| `<component>.standby` | by the profile: `0`, `1` in `ha` | A warm standby beside the writer: 0 or 1, for `lake`, `bor`, `street`, `instrument`, `conductor` and `launcher`. Any other count is refused, since CI tests one |
| `<component>.readyLagMs` | `5000` | The lag behind the writer's change log under which a standby is ready |
| `<component>.replicaCount` | `1` | 0 or 1. Above 1 the chart refuses to render, naming the component and pointing at `standby` |
| `leases.renewSeconds` | `2` | How often a writer renews its lease, and a standby looks at it |
| `leases.durationSeconds` | `6` | How long a lease lasts unrenewed before a standby takes it |
| `zones` | `[]` | The zones members are kept within and spread over; empty spreads over nodes only |
| `tolerations` | `[]` | More tolerations, after the chart's own 30-second ones |
| `key.existingSecret` | `""` | The deployment's key as a Secret: required for a conductor standby |
| `dashboard.replicaCount` | by the profile: `1`, `2` in `ha` | Copies of the dashboard, each reading the same sessions from its tables |
| `database.brought.standbys` | by the profile: `0`, `2` in `ha` | The brought database's standbys under Patroni: 0 or 2 |
| `broker.replicas` | by the profile: `1`, `3` in `ha` | The broker's servers: 1 or 3 |

### The hot layer { #the-hot-layer }

The lake, the book and the instrument store answer their most-read reads
from their own memory, the database remaining the record. Each layer is
bounded in MiB, the least recently read evicted first; an evicted key is
answered from the record and loaded again. Only a read of the latest now,
or a listing as of now, is answered from memory, and only when every key it
names is held; any other read goes to the record, never partly from memory.
A restarted store answers from the record until each key is loaded again.

| Value | Default | Passed as | What it holds |
|---|---|---|---|
| `lake.hotLayer.latestMiB` | `64` | `MERIDIAN_LAKE_HOT_LATEST_MIB` | Each dataset's latest rows per subject, what a live page reads |
| `lake.hotLayer.listingsMiB` | `32` | `MERIDIAN_LAKE_HOT_LISTINGS_MIB` | A chain's series per underlying and dataset |
| `bor.hotLayer.booksMiB` | `128` | `MERIDIAN_BOR_HOT_BOOKS_MIB` | Each account's book at its head, within the book's 512 MiB |
| `instrument.hotLayer.recordsMiB` | `32` | `MERIDIAN_INSTRUMENT_HOT_RECORDS_MIB` | Records by ID, and what each became |

A layer that does not fit is given a smaller bound, never more memory: the
lake keeps within its 1 GiB limit.

**`from_memory`.** Each read's timing line in a store's log says
`from_memory`, true when every row the read returned was answered from
memory, and `layer`, which layer answered it, or `record` where any row came
from the database. `meridian logs` shows them.

## Related

- [Plan your deployment](plan-your-deployment.md): what to install where.
- [Back up and restore a deployment](../how-to/back-up-and-restore.md).
- [Upgrade a deployment](../how-to/upgrade-a-deployment.md).
