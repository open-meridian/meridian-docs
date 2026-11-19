# Scale out the lake and the book

The lake and the book each write through one **writer** by default. When one
writer is not enough, you add writers by configuration: **writer groups**,
each owning a share of the store's **partitions**, and, when one database is
not enough either, a **database per writer group**. Then you move
partitions and accounts between them, and split a busy lake range, online,
from the dashboard, the command line or your agent.

This page is for a deployment admin. For what each level of resilience
needs, see [Service levels](../concepts/service-levels.md); for how a
store scales out, see [Scale out the writers](../concepts/service-levels.md#scale-out-the-writers).

## Plan the counts first

- **Keep peak load below about 60 to 70% of what a writer group takes.**
  There, latency stays near its floor. The resilience profile advises a
  writer group more once a group's measured peak passes it (see
  [Read the advice](#read-the-advice)).
- **Start with more partitions than writer groups**, 8 to 16 book
  partitions with 2 groups, say. Scaling out is then adding a group and
  moving partitions to it. A partition is never split between groups, so a
  group added when there are no more partitions than groups finds nothing
  to take.
- **Set the most writer groups ahead of need.** `lake.maxWriterGroups` and
  `bor.maxWriterGroups` (2 by default, at most 64) are the most groups each
  store may run. The database's connections are counted for that many, so
  a change of `writerGroups` within it never restarts the database, and
  raising it restarts the database once.

| Value | Default | What it sets |
|---|---|---|
| `lake.writerGroups`, `bor.writerGroups` | `1` | Writer groups, each owning a share of the store's partitions |
| `lake.maxWriterGroups`, `bor.maxWriterGroups` | `2` | The most writer groups, 1 to 64 |
| `bor.partitions` | `1` | The book's partitions, `P0` to `P<n-1>`, 1 to 64 |
| `lake.databases`, `bor.databases` | `1` | Databases the writer groups spread over |
| `<store>.database.groupSecrets` | `[]` | A database somebody else runs, past the first: one Secret each |
| `moves.holdSeconds`, `moves.switchSeconds` | `5`, `30` | A move's hold on writes, and how long it may take to switch |

## To add writer groups

```bash
meridian upgrade-deployment --set lake.writerGroups=2,bor.writerGroups=2
```

Each group past the first runs as a writer of its own, with its own lease
and, where the store keeps one, its own standby. Every member takes the
store's writes and hands each to the group that owns its partition, so
plugins and pages change nothing. The new group is given its share of the
partitions, which move to it one at a time, each following its writer's
log before it switches (see [To move a partition](#to-move-a-partition)).
A move back to a partition's first group waits until every member runs the
new revision, so a rollout never takes a partition back halfway.

Above `maxWriterGroups`, the upgrade is refused before anything changes.
Raise the most first, which restarts the database once, then the count:

```bash
meridian upgrade-deployment --set bor.maxWriterGroups=4
meridian upgrade-deployment --set bor.writerGroups=4
```

**Raise only, in the HA profile.** With `resilience.profile=ha`, and for
the lake wherever its write-ahead stream runs, the count can be raised and
not lowered: an upgrade that lowers it is refused, says so, and changes
nothing. `meridian rollback-deployment` refuses a rollback that would lower
it, for the same reason.

**Upgrade first.** Moving to the release that brings writer groups, and
changing `writerGroups` or `databases`, are two upgrades. One that does both
is refused: run the upgrade without the count, then change the count.

## To give each writer group its own database

```bash
meridian upgrade-deployment --set bor.writerGroups=2,bor.databases=2
```

Writer group *g* writes to database *g* mod the count. Database 0 keeps
the store's `control` partition and which group owns what. A read that
spans databases is answered from each and merged, and carries a
watermark per partition as every read does.

- **With the database the deployment brought,** the chart brings one more
  for each database past the first, `<release>-<store>-database-<d>`, each
  with the profile's standbys, read replicas and WAL archive.
- **With a database somebody else runs,** name a Secret for each database
  past the first, in order, each read with the store's key:

```yaml title="book-databases.yaml"
bor:
  writerGroups: 2
  databases: 2
  database:
    groupSecrets: [meridian-bor-database-1]
```

```bash
meridian upgrade-deployment -f book-databases.yaml
```

A partition moved to a group on another database is copied there first,
in pages, then follows the source's log until it switches. The move is
recorded as any move is.

`meridian status` lists each group's members, `<store>-group-<g>`, with
its lag and its partitions.

## To add book partitions

```bash
meridian upgrade-deployment --set bor.partitions=8
```

A new account is placed in a partition when it is created, for good: by
its **owner** label where it has one, so a fund's or a household's
accounts land together, and by its ID otherwise. Raising the count places
new accounts only. Existing accounts stay where they are until you move
them ([To move an account](#to-move-an-account)), and editing an account's
owner moves nothing.

Lowering the count is refused while a partition past the new count holds
accounts, naming each and how many it holds. Move them first.

A booking whose allocations fall in other partitions is booked in each, and
posts once every partition has its part. One left incomplete raises the
held-booking alert, as any held booking does (see
[Booking](../concepts/booking.md)).

## To move a partition { #to-move-a-partition }

Move a lake range or a book partition to another writer group:

=== "Dashboard"

    On **Resilience**, under **Deployment** in the dashboard's settings, open
    **Partitions**, and choose **Move** on the partition's row. Give the
    **Writer group** to move it to and a **Note** saying why, then **Move**,
    or **Prepare** to keep it, checked, for someone to make (see
    [Prepared changes](../concepts/prepared-changes.md)).

=== "Command line"

    ```bash
    meridian partition move P3 --to-group 1 --reason "balance the book's groups"
    ```

    ```text
    Begun: bor P3 moves from writer group 0 to 1 (started 2026-11-19T14:02:11Z). Writes to it are held for a moment at the switch, never refused inside the hold.
    Moved: bor P3: group 0 to 1, epoch 4.
    ```

    It follows the move until its record shows, for `--timeout` (2 minutes
    by default); `--no-wait` answers once it has begun. A move still under
    way when the time runs out is left to finish.

=== "Your agent"

    [`dashboard__move_partition`](../api/core-tools.md#dashboard__move_partition),
    with the partition, the target group and a note.

A lake range is named by its dataset's ID, or `<dataset>/<lo>-<hi>` once
split; a book partition is `P0`, `P1` and on. `control` never moves.

**What happens.** The target group follows the partition's log, and the
switch starts once it is within the store's `readyLagMs`. Writes to the
partition are then held for at most `moves.holdSeconds`, never past the
caller's own deadline, while the source closes, the two compare digests
and the target takes over. Past the hold, a write is refused `OVERLOADED`
with a retry-after, which the SDK waits out. Nothing is refused inside the
hold, and nothing is lost or written twice.

**A move that does not switch** leaves the source owning, with the cause in
its record:

| Cause | When |
|---|---|
| `lag` | The target did not come within `readyLagMs` within `moves.switchSeconds`. Nothing was held. |
| `timeout` | The switch began and did not finish within `moves.switchSeconds`. |
| `digest` | The source's and the target's digests differ. It is also an integrity finding. |

Any held writes go to the source. Ask again when you are ready; nothing
needs undoing.

A store runs one move at a time, and a partition being moved or split is
refused a second move or a split until the first ends. Each move, done or
not, is its own record, on the page's **History**.

## To move an account { #to-move-an-account }

Continue an account in another book partition:

=== "Dashboard"

    On **Resilience**, open **Partitions** and choose **Move account**. Give
    the **Account**, the partition it goes **To**, and a **Note**, then
    **Move** or **Prepare**.

=== "Command line"

    ```bash
    meridian account move ACC-01JB8Z3K6Q --to-partition P2 --reason "with its household"
    ```

    ```text
    Moved: account ACC-01JB8Z3K6Q continues in P2, from P0: closed at sequence 48211 there, opened at 1022 here. Its positions, lots and orders read as before.
      by admin@example.com, 2026-11-19T14:05:40Z
      reason: with its household
    ```

=== "Your agent"

    [`dashboard__move_account`](../api/core-tools.md#dashboard__move_account).

The account's chain closes in its partition and continues in the new one,
so its positions, lots and orders read the same before and after. Acts on
it wait while it is between the two. A move that does not switch for `lag`
or `timeout` is refused `OVERLOADED` with a retry-after, and one for
`digest` is refused naming the account; either may be asked again.

## To split a lake range { #to-split-a-lake-range }

A dataset written faster than its group can take is split in two, and a
half moved to another group:

=== "Dashboard"

    On **Resilience**, open **Partitions**, and choose **Split** on the lake
    range's row. Give a **Note**, then **Split** or **Prepare**.

=== "Command line"

    ```bash
    meridian partition split kraken-1:trades --reason "busiest range"
    ```

    ```text
    Split: kraken-1:trades closed at sequence 905113 and continues as kraken-1:trades/0000-7fff and kraken-1:trades/8000-ffff, each with its parent's writer group.
      by admin@example.com, 2026-11-19T14:10:02Z
      reason: busiest range
    ```

=== "Your agent"

    [`dashboard__split_partition`](../api/core-tools.md#dashboard__split_partition).

A split halves the range at its midpoint, by the hash of each row's first
subject, in one commit of its writer. Nothing is copied, so it cannot fail
halfway; writes to the range wait for that one commit. Both halves stay with
the range's group; move one to another group to spread the load. Reads and
`read_after` follow the split with nothing to change: a read covers the
range up to the split, then its halves.

Every row of one subject stays in one range, in order, so one very busy
subject has a ceiling no split lifts. Splitting its range again moves its
neighbours away from it, so they are not slowed by it.

The `control` partition, a book partition, a range not open and a range of
one hash value are refused, naming the partition.

## Read the advice { #read-the-advice }

The resilience profile advises on writer groups and partitions beside its
levels. Read it on the Resilience page's **Profile** tab, with
`meridian status --profile --json` (its `advice`), or through
[`dashboard__read_resilience_profile`](../api/core-tools.md#dashboard__read_resilience_profile).
Each line names its subject, why, and the change to make:

| Line | When | The change it names |
|---|---|---|
| The book's partitions | `bor.partitions` is not more than `bor.writerGroups` | `bor.partitions` at twice the groups |
| The lake's partitions | The lake writes no more ranges than it has writer groups | Split the busiest range |
| A store's writer group *g* | Its commit lane was busy past 70% of a minute at its busiest in the last 15 minutes, or it refused work as overloaded | `<store>.writerGroups` one more |

The profile changes nothing. Make a change it names with
`meridian upgrade-deployment --set`, or move and split on the Partitions
tab.

## To lower a count

- **Writer groups,** in the tolerant profile: lower `writerGroups`. The
  partitions of the groups taken away pass to the groups that stay, and a
  stopping writer keeps answering until another has taken them. In the HA
  profile they are raised only (above).
- **Databases:** move each partition to a writer group whose database stays,
  then lower `<store>.databases`. An upgrade that would leave data in a
  database past the new count is refused, naming the partitions.
- **Book partitions:** move each account out of the partitions past the new
  count, then lower `bor.partitions`.

## Related

- [Service levels](../concepts/service-levels.md): the levels, the HA
  profile and the chart's values.
- [Upgrade a deployment](upgrade-a-deployment.md): `--set` and `-f`.
- [Command line](../api/cli.md#meridian-partition-move): `partition move`,
  `partition split` and `account move`.
