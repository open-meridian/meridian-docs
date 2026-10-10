# Build with an AI agent

Open Meridian is built so a coding agent can write your plugin while you watch. On a development
deployment, `meridian plugin dev` runs your plugin as you write it: each save is running in about a
second, in the same pod, with the same sidecar and the same grants.

Every plugin made by `meridian plugin new` carries the instructions an agent needs:

| File | For |
|---|---|
| `AGENTS.md` | Any coding agent. It teaches building pages with the plugin UI kit, holding the plugin to `meridian plugin check`, and the live loop: start it, change something, check the result, release. |
| `CLAUDE.md` | Claude Code. It points to `AGENTS.md`. |
| `.claude/skills/develop-live/SKILL.md` | Claude Code. A skill that also leads to `AGENTS.md`. |

`CLAUDE.md` and the skill come with CLI v0.1.8 and later. Commit all three with the plugin, so
whoever works on it next has them too. `.dockerignore` keeps them out of the plugin's image.

## Before you start

- A deployment installed **for development**. Development deployments run unreviewed code, so
  never use one your firm depends on. See
  [Development deployments](../concepts/development-deployments.md).
- The `meridian` CLI, 0.1.36, whose `plugin new` builds on SDK 0.21.0 (0.22.0 from CLI
  0.1.37): 0.1.15 brought
  `plugin check`, which `AGENTS.md` asks for, and 0.1.21 `plugin open --level`, which the checks
  below use. Check with `meridian --version`; update with `meridian upgrade`.
- Docker on this machine. The first run builds the plugin's image.
- A coding agent that can run shell commands in the plugin's directory.

## 1. Install a development deployment

Follow [Install a deployment](installation.md), adding `--development` to `meridian up`:

```bash
export MERIDIAN_ENROLMENT_CODE=ENR-XXXX-XXXX-XXXX
meridian up --id DEP-XXXXXXXXXXXXXXXXXXXXXXXXXX --development
```

Every page of this deployment says **Development deployment**.

## 2. Sign in yourself

```bash
meridian connect
```

Only you can do this. It signs in through your browser, so an agent cannot run it for you. From CLI
0.1.25 it then asks you to let the CLI on this computer act as you; choose **Allow**. Every command
the agent runs later acts on this delegation, recorded as yours, through the CLI. It lasts up to 90
days and the CLI keeps its access fresh by itself, so the agent can work overnight; an earlier CLI's
session lasts 12 hours at most.

## 3. Make the plugin

```bash
meridian plugin new my-plugin
cd my-plugin
```

If you already have a plugin made by an older CLI, it may lack `CLAUDE.md` and the skill. Its
`AGENTS.md` still works for any agent.

## 4. Start your agent in the plugin's directory

Start your coding agent with `my-plugin` as its working directory. Then ask for what you want, and
say you want to see it running. For example:

```text
Read AGENTS.md. Start the live loop for the instance my-plugin, then add a
section to the Setup page that shows today's date. Check the page with
`meridian plugin open --instance my-plugin --level manage --print /setup`
and tell me when it is running.
```

Name the level the page is for. A session on a plugin carries one level, as the dashboard's
**Manage**, **Open** and **View** do, and a page serves only the levels it is declared with. As a
deployment admin you are an admin of every plugin, so without `--level` the CLI asks at Manage, and
the scaffold's Accounts page at `/`, which is for Open and View, is refused. See
[Manage, Open and View](../concepts/plugins.md#manage-open-and-view).

Claude Code reads `CLAUDE.md` by itself. Other agents need to be told to read `AGENTS.md`, or pick
it up by their own convention.

### When the plugin does more than serve a page

If the plugin is to record, read or hear anything in the deployment, ask the agent first which roles
it needs. Roles are fixed, and nobody can change what a role is granted, not even for one plugin. So
the agent maps your idea to the least roles that hold what it needs, from [Roles](../concepts/roles.md),
or tells you how to reshape the idea to fit. For example:

```text
Read https://open-meridian.dev/llms.txt and the roles page it links. Following
the method there, map this to the least roles, and tell me what the contract
version this plugin's SDK pins already grants: a page that shows each
account's latest broker statement.
```

`llms.txt` is an index for agents: the roles, the principles a plugin must fit, the method, and
every operation a plugin may take, each linked to its page here.

## 5. Approve what the plugin asks for

The first launch of an instance needs your yes. `AGENTS.md` tells the agent to show you the `roles`
in `pyproject.toml` and ask. Only after you say yes does it pass `--yes`. An instance
that is already live asks nothing.

!!! warning
    Approving roles decides what the plugin may do in your deployment. Read them: each is described
    on [Roles](../concepts/roles.md). If an agent passes `--yes` without asking you, stop it.

## 6. Watch it work

The agent runs `plugin dev` in the background and writes its output under `.meridian/`:

```bash
mkdir -p .meridian
meridian plugin dev --instance my-plugin --yes --json > .meridian/dev.jsonl 2> .meridian/dev.err
```

The first run uploads the plugin and launches it live. That takes a minute or two. After that, each
save is a new **revision**, and the agent waits for that revision to be `ready` or `crashed`. The
events are:

| Event | Means |
|---|---|
| `seeded` | The live folder was filled from the plugin's image, the first time it runs live |
| `sent` | A change was sent, and given a revision number |
| `synced` | The sidecar wrote it |
| `restarted` | The plugin's process started on that revision |
| `ready` | It connected to its sidecar again: that revision is running |
| `crashed` | It stopped with an error. `traceback` has the last of what it printed |
| `exited` | It stopped by itself, without an error |
| `refused` | The sidecar refused it something. `reason` says what |

The agent checks its work with the command that answers the question:

| To know | It runs |
|---|---|
| What a page shows | `meridian plugin open --instance my-plugin --level manage --print /setup`, or `--level open --print /` for a page at `write` |
| What the plugin printed | `meridian plugin logs --instance my-plugin --since <revision>` |
| What was refused | `meridian plugin events --instance my-plugin --since <revision> --json` |
| What you see in a browser | `meridian plugin open --instance my-plugin`, a link for one browser |

You can run any of these yourself from another terminal. See
[Change your plugin's page, live](../tutorials/change-the-page-live.md) for the same loop by hand,
and [plugin dev events](../api/plugin-dev-events.md) for the event format.

## What a save cannot change

A save changes what the plugin **does**, never what it is **allowed** to do.

- **Roles.** Adding one to `pyproject.toml` changes nothing live. It needs a new version, and you
  approve it.
- **Dependencies.** The live code runs on the image the instance was launched from. A new package
  needs a new version.

A `refused` event is the plugin's grants working, not a bug. A good agent tells you when a change
needs either of these, rather than looking for a way round.

## When the delegation lapses

Every command exits with a code an agent can act on:

| Exit | Means |
|---|---|
| 0 | Done |
| 1 | Refused or failed |
| 2 | Asked wrongly |
| 3 | Not connected, or the delegation was revoked or has lapsed |

On exit 3 the agent should stop and ask you to run the `meridian connect` the command printed. There
is no `meridian status`; `meridian plugin list` shows whether you are connected. Within a week of the
lapse, every command says when; `meridian connect` renews it.

## 7. Release it

When you are happy, ask the agent to release. It runs `meridian plugin check --run-tests` and fixes
what fails, raises `version` in `pyproject.toml`, shows you the roles again, and then runs:

```bash
meridian plugin dev --release --instance my-plugin --yes
```

That uploads the directory as the new version and runs it in place of the live instance. It is then
an ordinary version in the catalogue. See [Release a plugin version](../how-to/release-a-plugin.md).

## 8. Stop

Stopping the background `plugin dev` leaves the instance running as it was. To end it:

```bash
meridian plugin stop my-plugin
```

## Next steps

- [Roles](../concepts/roles.md): which roles a plugin needs, and why an idea is sometimes reshaped
  to fit them.
- [Record a holdings statement](../tutorials/record-a-holdings-statement.md): a plugin that writes
  to the deployment, with the roles and grants that takes.
- [Typed operations](../api/typed-operations.md): what a plugin's roles let it do.
- [Prove your plugin against a released runtime](../how-to/prove-a-plugin-against-a-released-runtime.md):
  an e2e check the agent can run with `make e2e`.
