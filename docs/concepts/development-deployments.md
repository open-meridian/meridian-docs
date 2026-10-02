# Development deployments

A **development deployment** is a deployment installed for writing plugins. It
may run a plugin's code *as it is being written*: each save reaches the
running plugin in about a second, and its page, its output and its traffic on
the bus are there to look at. That loop is what makes it practical to build a
plugin by hand or with an AI coding agent.

It is also code that nobody has reviewed, running on purpose. So it is a
property of the whole deployment, chosen when it is installed, and it is never
a property of a firm's real one.

## Installing one

```bash
meridian up --id DEP-… --development
```

`--development` sets the chart's `development` value. It is an install choice
and nothing else: there is no switch for it in the dashboard. Turning it off is
a change to the install too, and it stops every plugin running live.

## What it says about itself

Every dashboard page on a development deployment carries a banner:

> **Development deployment.** It runs plugin code as it is being written,
> which nobody has reviewed. Nothing here is for real use.

Its health check answers `serving, for development`, so the fact is visible
to anything that monitors it, not only to people looking at a page.

## What it allows

On any deployment, only a recorded version of a plugin runs: one uploaded to
the catalogue and approved at launch. A development deployment adds one thing,
the **live shape**.

A live instance runs the SDK's development runner in the plugin's container,
against a folder the plugin shares with its sidecar. A change to that folder
restarts the plugin's process within a second; the pod, the sidecar and its
broker credential stay as they are. The sidecar gains a development endpoint,
behind the same front door as the plugin's page, that writes files into the
folder and reads back the plugin's output and its traffic.

From a terminal signed in with `meridian connect`:

| Command | What it does |
|---|---|
| `meridian plugin dev --instance <id>` | Uploads the plugin if its version is not uploaded yet, launches it live once you approve its roles, then sends each save and reports what happens — `synced`, `restarted`, `ready`, `crashed` with the traceback — each with a revision number |
| `meridian plugin logs` | What the plugin printed, since a revision |
| `meridian plugin events` | Its traffic as it happens: what it published and received, and what its sidecar refused it |
| `meridian plugin open` | A one-time link to its page for one browser, or with `--print <path>`, the page itself as you are served it, at the level `--level` names: `manage`, `open` or `view` |
| `meridian plugin dev --release` | Turns the code as it is into an ordinary recorded version, uploaded and launched the ordinary way |

Every one of these takes `--json` and exits non-zero on failure, so a coding
agent reads results rather than scraping them. `meridian plugin new` writes an
`AGENTS.md` into each plugin that teaches any agent this loop. See
[the CLI reference](../api/cli.md).

## What it does not change

- **Grants.** A live plugin may do exactly what its roles allow, approved at
  launch and enforced by its sidecar. Live code changes what a plugin does
  within its grants, never the grants.
- **Who may do it.** Developing live is launching, so it is for whoever may
  launch plugins on that deployment — today, a deployment admin — on their own
  delegation to the CLI, with its usual bounds. When it lapses or is revoked,
  the CLI says so and what to run.
- **The way in.** Code reaches the pod only through the dashboard, on that
  person's delegation. Nobody needs a credential for the cluster.
- **Dependencies.** Live code runs on the image the plugin was launched from.
  A change to a plugin's dependencies needs a new version.

Anywhere else, the live shape does not exist: the launcher refuses to create
it on a deployment not installed for development, and a sidecar not in the
live shape has no development endpoint at all.

!!! danger "Never for a firm's real deployment"
    A development deployment runs unreviewed code by design. Install one as a
    sandbox, on a laptop or in a cluster of its own, and never install a
    deployment your firm depends on with `--development`. Because the choice
    is made at install, a firm's deployment cannot become one without being
    installed again as one.

## Not built yet

- **Following a repository.** Having a development deployment follow a
  branch, so that each push is running within seconds without anybody's
  terminal, is specified and not built.
- **Agents without a person.** The loop runs on a person's own delegation,
  made by signing in through a browser on the same machine as the CLI. A coding agent running
  in the cloud, with no browser beside it, cannot sign in yet.
