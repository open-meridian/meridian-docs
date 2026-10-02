# Upgrade a deployment

A deployment is a Helm release of the `meridian-runtime` chart. Upgrading it moves the release to a
newer version of that chart, in place: the database migrates, every component restarts on the new
image, and the data, the key and the configuration stay.

What people notice:

- **The CLI stays connected.** A delegation from `meridian connect`, and a session an earlier CLI
  kept, are kept in the deployment's database, so they survive the dashboard restarting, and nobody
  reconnects a terminal.
- **CLI 0.1.25 needs chart 0.1.223 or later.** Against an older dashboard, `meridian connect`
  says it does not take delegations yet. Upgrade the deployment, or connect with CLI 0.1.24 until you
  do.
- **Browsers sign in again.** A browser's session is held in the dashboard's memory, so the
  dashboard's restart ends it.
- **The database stays up.** A database the deployment brought, and its plugin registry, run images
  of their own, and an upgrade that only moves the version does not restart them. The first upgrade
  from a chart that still labelled their pods with its version restarts them once more.
  The migration waits for the database to answer, up to five minutes, rather than failing at once.
- **Launched plugins keep their sidecar.** A plugin keeps the sidecar image it was launched with
  until it is launched again. See [after an upgrade](#after-an-upgrade-relaunch-plugins).

You apply an upgrade with your own cluster rights. Nothing in a deployment holds a right to change
the cluster, and the dashboard does not upgrade itself.

| To | Run or do |
|---|---|
| Upgrade to the latest published chart | `meridian upgrade-deployment` |
| Upgrade to a particular version | `meridian upgrade-deployment --chart-version <v>` |
| Upgrade from your own pipeline | Plain Helm, Argo CD or Flux, below |
| Upgrade the command line itself | `meridian upgrade`, which is a different thing |

## To upgrade with the command line

```bash
meridian upgrade-deployment
```

It checks first, and changes nothing if a check fails:

- the cluster is reachable, and you may patch Deployments and create and delete Jobs in the
  namespace;
- your `helm` is 3.14 or newer, which an upgrade needs (see [why](#why-not-reuse-values));
- no node is under disk pressure. An upgrade pulls new images onto the node, which would take more
  of the disk it is short of, and its new pods would be scheduled nowhere. Free disk and wait for the
  pressure to lift; on a laptop VM, `docker builder prune -a` often does it. Low free disk is only
  reported, as `worth`, and does not stop it;
- the release exists and Helm holds it as `deployed`, not `failed` or `pending-…`;
- the version you are moving to is published, and is not older than the one installed.

If the release is at that version already, it says so and exits 0.

Then it shows what it will do, and asks:

```text
Upgrading meridian in meridian:
  from  meridian-runtime 0.1.180 (revision 7), running ghcr.io/open-meridian/meridian-runtime:845bd06
  to    meridian-runtime 0.1.182, running ghcr.io/open-meridian/meridian-runtime:9c5d480

  helm upgrade meridian oci://ghcr.io/open-meridian/charts/meridian-runtime --version 0.1.182 --namespace meridian --reset-then-reuse-values --timeout 10m

Upgrade it? [y/N]
```

If a node restart has left pods behind, the plan names them too, and the same answer covers removing
them (see [pods left over from a restart](#pods-left-over-from-a-restart)):

```text
  Then it will remove 7 pods left over from a restart, which serve nothing:
    pod/meridian-meridian-runtime-broker-6d9c7b5f4-x2x8q
    ...
```

Answer `y`. It runs that `helm upgrade`, then waits, up to `--timeout`, for:

1. the new revision's migration Job to complete;
2. every Deployment and StatefulSet of the release to roll out;
3. every pod of theirs to run the image its template now names.

While it waits it shows where it is (see [while it runs](#while-it-runs)). When they have, it
deletes the finished Jobs the release ran at earlier revisions and the pods left over from a restart,
and reports:

```text
Upgraded meridian in meridian: meridian-runtime 0.1.180 -> meridian-runtime 0.1.182, now revision 8.
Migrated: job/meridian-meridian-runtime-migrate-8 completed.

Every component on its new template, and ready:
  conductor  1/1  ghcr.io/open-meridian/meridian-runtime:9c5d480
  dashboard  1/1  ghcr.io/open-meridian/meridian-runtime:9c5d480
  ...

Cleaned up 2 finished Job(s) of earlier revisions: job/meridian-meridian-runtime-migrate-7, ...
Removed 7 pods left over from a restart: pod/meridian-meridian-runtime-broker-6d9c7b5f4-x2x8q, ...
Old ReplicaSets are left to the chart's revisionHistoryLimit.
```

A container that restarted while the upgrade ran is listed with the reason Kubernetes gives and the
`kubectl logs … --previous` that shows why. That is worth reading, and it is not a failure: a
component that starts before its migration has finished exits and is restarted.

### While it runs

On a terminal, a block below what it has said is redrawn in place every half second: each step with
its time, the total time, how many components are ready, and what it waits on now, and why.

```text
Upgrading meridian in meridian  1m 04s
  ✓ checks                     3s
  ✓ plan and confirmation     12s
  ✓ apply                      8s
  ⠹ migration                 41s
  ⠹ components                41s  ready 4 of 7  ███████████░░░░░░░░░
  · cleanup
  waiting on conductor: 0 of 1 ready, waiting for its migration
```

A step is pending (`·`), in progress (a spinner), done (`✓`) or failed (`✗`). The migration and the
components are waited for together: a component that starts before its migration has finished exits
and is restarted, so while the migration runs, that is the reason given. Once the upgrade ends, the
block stays with every step's time, above the report.

Piped to a file or run in CI, it writes a line as each step starts and ends, and every 20 seconds a
line saying what it still waits for, so a log never looks stalled:

```text
[3s] apply: started
[11s] apply: done in 8s
[11s] migration: started
[11s] components: started
[31s] still waiting, 4 of 7 components ready: conductor: 0 of 1 ready, waiting for its migration
[45s] migration: done in 34s
[1m 02s] components: done in 51s
```

Set `NO_COLOR` to turn the colour off.

### Pods left over from a restart

When a node restarts, as a laptop's Kubernetes does when the laptop does, each pod it ran can be left
behind stopped, as `Failed` or `Succeeded`, on the image it had then. Its Deployment has already
started a new pod in its place, and nothing restarts or removes the old one. It serves nothing.

The command does not wait for such a pod: one stopped for good and made by a ReplicaSet its
Deployment has since replaced. Waiting for it to run the new image would last until the timeout,
since it never changes. It says so as it waits, and removes it in the cleanup, by name, with the
release's other leftovers. A plugin's pods are treated the same way: a launched plugin carries the
release's labels. A pod still pending, running or terminating on the old image is waited for.

`--yes` answers the question for a script that has already read the plan. `--release`, `-n`,
`--chart` and `--timeout` are as for `meridian up`; see the
[command line reference](../api/cli.md#meridian-upgrade-deployment).

### After an upgrade: relaunch plugins

A launched plugin keeps the sidecar it was launched with until it is launched again, so after an
upgrade it may still run beside the old version's sidecar. From CLI 0.1.19 the report ends by naming
each such plugin, and each plugin whose pod started while the upgrade was under way, when the old
launcher may have launched it. For each it prints the commands that move it:

```text
meridian plugin stop snaptrade
meridian plugin launch snaptrade <version> --instance snaptrade
```

For a plugin running live it prints `meridian plugin dev --instance <instance>` instead. The version
is left as `<version>`: `meridian plugin list` gives it. It relaunches nothing itself.
`meridian doctor` warns about the same plugins, as `worth`, at any time.

### If it stops

| It says | What to do |
|---|---|
| a check `stops` | Nothing was changed. Each one says what to do. |
| the release is `failed` | `helm history meridian -n meridian` says why. Fix the cause, then `helm rollback meridian -n meridian` returns it to its last deployed revision, and you can upgrade again. |
| the release is `pending-upgrade` or `pending-install` | Another Helm operation is running, or one was interrupted. If none is running, `helm rollback meridian -n meridian` clears it. |
| the migration failed | It names the Job. Read its log with `kubectl logs -n meridian job/<name> --all-containers`. The new revision stays applied. Read the log before rolling back: a migration that got part of the way may have changed what the older version reads. |
| still waiting after the timeout | It lists what it was waiting for, each with why. Nothing is rolled back. Run it again with a longer `--timeout`: it is at the new version already, so it only waits. |

!!! note "Not checked yet"
    Two checks are planned and not built, and the command says so each time rather than passing
    them: whether an upgrade skips more versions than is supported, and whether every installed
    plugin runs on the new version. Neither has anything to check against yet.

## To upgrade from your own pipeline

Firms usually apply an upgrade through their own change control: a reviewed version bump, applied by
a pipeline. The chart is the same one the command line applies, and it works that way too. Whatever
applies it, do what the command line does:

**Before:** the release is `deployed`; the new version is published and is newer than the one
installed.

**The upgrade:** the new chart's defaults, with the deployment's own values over them.

**After:**

1. Wait for the migration Job of the new revision, `<release>-meridian-runtime-migrate-<revision>`,
   to complete. If it fails, stop and read its log.
2. Wait for every Deployment and StatefulSet with the label
   `app.kubernetes.io/instance=<release>` to roll out.
3. Delete the finished Jobs of earlier revisions. Their names end with the revision that ran them.
   The Job ending in `-key` is kept: it runs once, at install.

`kubectl rollout status` does not wait for [pods left over from a
restart](#pods-left-over-from-a-restart), so a pipeline is not held up by them. Deleting them is
tidying, and optional.

### Plain Helm

```bash
helm upgrade meridian oci://ghcr.io/open-meridian/charts/meridian-runtime \
  --version 0.1.182 --namespace meridian --reset-then-reuse-values

kubectl wait -n meridian --for=condition=complete --timeout=10m \
  job/meridian-meridian-runtime-migrate-8
kubectl rollout status -n meridian deployment -l app.kubernetes.io/instance=meridian --timeout=10m
kubectl rollout status -n meridian statefulset -l app.kubernetes.io/instance=meridian --timeout=10m
```

`helm history meridian -n meridian` gives the new revision, the number the migration Job ends with.

Do not add `--wait`. Charts up to 0.1.182 mark an upgrade failed under `--wait` on one of their own
setup resources, although the upgrade worked. Wait with `kubectl` as above.

### Flux

A `HelmRelease` runs Helm itself. The values it holds are the deployment's own, and on each upgrade
it applies them over the new chart's defaults, which is what `--reset-then-reuse-values` does. To
upgrade, change the version in Git:

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: OCIRepository
metadata:
  name: meridian-runtime
  namespace: meridian
spec:
  interval: 1h
  url: oci://ghcr.io/open-meridian/charts/meridian-runtime
  ref:
    tag: 0.1.182          # the version; change this to upgrade
  layerSelector:
    mediaType: application/vnd.cncf.helm.chart.content.v1.tar+gzip
    operation: copy
---
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: meridian
  namespace: meridian
spec:
  interval: 10m
  chartRef:
    kind: OCIRepository
    name: meridian-runtime
  upgrade:
    disableWait: true     # see Plain Helm: wait for the migration yourself
  values: {}              # the deployment's own values
```

Flux waits for the resources by default, which fails as `--wait` does on charts up to 0.1.182;
`disableWait` turns that off. Check the migration Job and the rollouts afterwards, as above.

### Argo CD

Argo CD renders the chart with `helm template` and applies what it renders. Its Application holds the
deployment's own values, so there is nothing to reuse: each sync renders the new chart's defaults
with those values. To upgrade, change `targetRevision` in Git to the new chart version.

!!! warning "Jobs named by revision"
    `helm template` renders every release as revision 1. The chart names its migration Job and its
    other per-revision Jobs by Helm's revision, so under Argo CD each upgrade renders a Job with the
    same name as the last one, and Kubernetes refuses to change a Job's template. Delete the
    finished migration Job before syncing an upgrade. Nothing else depends on it.

## Why not `--reuse-values`

`helm upgrade --reuse-values` reuses the previous release's values, the old chart's defaults among
them. The image tag is one of those defaults, so the upgrade applies the new chart's templates and
keeps the old image: every pod restarts, and nothing changes version.

`--reset-then-reuse-values` starts from the new chart's defaults, the new image among them, and
applies only the values the deployment was given over them. It needs Helm 3.14 or newer.

If the deployment's own values set `image.tag`, as `meridian up --image` does, that tag is one of
its own values and an upgrade keeps it. `meridian upgrade-deployment` says so before it asks. Remove
`image.tag` from the deployment's values if it should move with the chart.

## Related

- [Install a deployment](../getting-started/installation.md)
- [Remove or start over](remove-or-start-over.md)
- [Command line reference](../api/cli.md)
