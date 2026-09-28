# `plugin dev` events

`meridian plugin dev --json` writes a stream of JSON objects to stdout, one per line, while it watches a plugin's directory. It is for scripts and AI agents following a live plugin. `meridian plugin events --json` reports the same events on demand. Progress and errors go to stderr, never to stdout.

For the command itself, see [`meridian plugin dev`](cli.md#plugin-dev). For what a development deployment is, see [Development deployments](../concepts/development-deployments.md).

```sh
mkdir -p .meridian
meridian plugin dev --instance my-plugin --yes --json > .meridian/dev.jsonl 2> .meridian/dev.err
```

!!! tip "Write the stream under `.meridian/`"
    `plugin dev` sends every file in the plugin's directory that changes, except `.meridian/` and what `.dockerignore` names. Output written anywhere else in the directory would be sent to the plugin as a change, again and again.

## Revisions

Every change `plugin dev` sends is given a **revision**, a whole number. Revisions count up from 1, and the first run, before anything is sent, is revision 0. Every event carries the revision it is about, so you can tell which save it concerns.

## Where events come from

| Source | Events | How to recognise it |
|---|---|---|
| The `meridian` command line, on your machine | `sent` | Only on the `plugin dev --json` stream. It has no `at` field. |
| The plugin's sidecar | `synced`, `refused` | `"by": "sidecar"` |
| The dev runner in the plugin's container (`meridian-dev run`, from the Python SDK) | `seeded`, `restarted`, `crashed`, `exited` | No `by` field. |
| The Python SDK, inside the plugin's process | `ready` | No `by` field. |

The runner's and the sidecar's events are merged and sorted by `at`. `plugin dev` reports each one once, however many times a poll returns it.

## Events

### `sent`

This process sent a change to the deployment, and the deployment gave it a revision.

| Field | Type | Meaning |
|---|---|---|
| `event` | string | `"sent"` |
| `revision` | integer | The revision the change was given. |
| `files` | integer | How many files were sent, each whole. |
| `deleted` | integer | How many files were sent as deleted. |

```json
{"event": "sent", "revision": 2, "files": 1, "deleted": 0}
```

### `synced`

The sidecar wrote the change into the plugin's live folder. It writes every file first and the revision last, so a change half-written never runs.

| Field | Type | Meaning |
|---|---|---|
| `event` | string | `"synced"` |
| `revision` | integer | The revision written. |
| `files` | integer | Files written. |
| `deleted` | integer | Files deleted. |
| `at` | number | When, in seconds since the Unix epoch. |
| `by` | string | `"sidecar"` |

### `restarted`

The plugin's process was started on this revision. The runner starts the plugin when the container starts, and again on each new revision, stopping the running process first. It sends SIGTERM and waits 5 seconds before killing the process.

| Field | Type | Meaning |
|---|---|---|
| `event` | string | `"restarted"` |
| `revision` | integer | The revision it started on. |
| `pid` | integer | The new process's id. |
| `at` | number | When, in seconds since the Unix epoch. |

### `ready`

The plugin registered with its sidecar again: this revision is running. The SDK writes this from inside `meridian.connect()` once registration is admitted, so `ready` means running, not merely started.

| Field | Type | Meaning |
|---|---|---|
| `event` | string | `"ready"` |
| `revision` | integer | The revision now running. |
| `at` | number | When, in seconds since the Unix epoch. |

### `crashed`

The plugin's process stopped with an error. It is not started again until the next revision, so a plugin that can't start does not restart as fast as it fails.

| Field | Type | Meaning |
|---|---|---|
| `event` | string | `"crashed"` |
| `revision` | integer | The revision that crashed. |
| `exit` | integer or `null` | The process's exit code. `null` when no process was started, because `pyproject.toml` names no usable `[project.scripts]` entry point. |
| `traceback` | string | The last 40 lines the process printed, or why it could not be started. |
| `at` | number | When, in seconds since the Unix epoch. |

### `exited`

The plugin's process stopped by itself, without an error. Like `crashed`, it is not started again until the next revision.

| Field | Type | Meaning |
|---|---|---|
| `event` | string | `"exited"` |
| `revision` | integer | The revision that exited. |
| `exit` | integer | Always `0`. |
| `at` | number | When, in seconds since the Unix epoch. |

### `refused`

The sidecar refused the plugin something it tried to do, for example a typed operation none of its roles grants, or a command for an account outside its write scope. This is the plugin's grants working, not a bug to code around. Changing roles or tags takes a new version, which a person approves. See [Plugins, roles and grants](../concepts/plugins.md).

| Field | Type | Meaning |
|---|---|---|
| `event` | string | `"refused"` |
| `revision` | integer | The revision running when it was refused. |
| `reason` | string | What was refused, and why, in the sidecar's words. |
| `at` | number | When, in seconds since the Unix epoch. |
| `by` | string | `"sidecar"` |

### `seeded`

The runner found a new, empty live folder and filled it from the plugin's image, before starting the plugin for the first time.

| Field | Type | Meaning |
|---|---|---|
| `event` | string | `"seeded"` |
| `revision` | integer | The revision the folder was on, normally `0`. |
| `at` | number | When, in seconds since the Unix epoch. |

!!! note
    `seeded` is written by the runner and returned like any other event, but the event table in the plugin template's `AGENTS.md` doesn't list it. Treat it as informational.

## Following a change

1. Save a file. There is nothing to run: the save is the deploy.
2. Find the `sent` line after your save, and its `revision`, R. Several saves close together can land as one revision, so read the newest `sent`.
3. Wait for `ready` or `crashed` at R. Nothing about R is known before then.
4. On `crashed`, read its `traceback`, fix the cause, and save again. The next revision replaces it.

To check what happened since your change from another terminal, pass the revision before it:

```sh
meridian plugin logs   --instance my-plugin --since <R-1>
meridian plugin events --instance my-plugin --since <R-1> --json
```

`--since N` returns only what belongs to revisions after N.

## `plugin events --json`

Without `--follow`, `meridian plugin events --json` prints one object holding the current revision and every event kept:

```json
{
  "revision": 2,
  "events": [
    {"revision": 1, "event": "synced", "files": 9, "deleted": 0, "at": 1790000000.1, "by": "sidecar"},
    {"revision": 1, "event": "restarted", "pid": 42, "at": 1790000000.4},
    {"revision": 1, "event": "ready", "at": 1790000001.2}
  ]
}
```

With `--follow`, it prints one event object per line, as they happen, like `plugin dev --json` without `sent`.

The runner and the sidecar each keep their latest 2,000 events.

## Text form

Without `--json`, each event is one line with its revision first. A `crashed` event's traceback follows on indented lines:

| Event | Line |
|---|---|
| `sent` | `r2 sent (1 files, 0 deleted)` |
| `synced` | `r2 synced (1 sent, 0 deleted)` |
| `refused` | `r2 refused: <reason>` |
| `crashed` | `r2 crashed, exit 1` then the traceback, indented four spaces |
| `exited` | `r2 exited, exit 0` |
| any other | `r2 <event>` |

!!! note "Events the SDK's documentation mentions but the sidecar does not emit"
    The docstring of the SDK's dev runner (`meridian/dev.py`) says the sidecar's own events include what the instance published and received. The sidecar in this release records only `synced` and `refused`.
