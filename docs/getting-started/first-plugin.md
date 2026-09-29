# Your first plugin

A plugin is your own code running inside your deployment: a tool, a bot, an analytic, a connector.
It runs beside a **sidecar** and reaches nothing else. What it may do comes from the roles it asks
for, once a deployment admin approves them. See [Plugins, roles and grants](../concepts/plugins.md).

This page makes a plugin from the reference plugin, puts it in your deployment and opens its page.
It works on any deployment. For the faster loop where each save runs at once, see
[Build with an AI agent](build-with-an-ai-agent.md).

## Before you start

- A deployment you installed with [Install a deployment](installation.md).
- You hold **deployment admin** on it. Only a deployment admin brings plugins in.
- Docker on this machine. `meridian plugin upload` builds the plugin's image here, from its own
  `Dockerfile`.

## 1. Sign the CLI in

```bash
meridian connect
```

With no address it signs in to the deployment on this machine, `http://meridian.localhost`. For any
other, give its address: `meridian connect https://meridian.firm.example`. Your browser opens the
deployment's sign-in. The CLI keeps the session: 30 minutes idle, 12 hours at most.

## 2. Make the plugin

```bash
meridian plugin new my-plugin
```

Expected output:

```text
Made my-plugin in my-plugin, on the Python SDK (open-meridian).

  cd my-plugin
  meridian plugin upload
  meridian plugin launch my-plugin 0.1.0 --instance my-plugin

Upload builds its image here and puts it in the catalogue of the deployment
`meridian connect` signed you in to; launch shows the roles its
pyproject.toml asks for, and runs it once you approve them. It reaches its
sidecar and nothing else.

On a deployment installed for development, run it as you write it instead:

  meridian plugin dev --instance my-plugin

AGENTS.md teaches your coding agent that loop, whichever agent it is;
CLAUDE.md and the develop-live skill lead Claude Code to it. Commit them
with the plugin, so whoever works on it next has them too.
```

A plugin name is lowercase letters, digits and single hyphens, starting with a letter. `--into <dir>`
writes it somewhere other than `./my-plugin`. It never writes over a directory that exists.

## 3. Look at what you got

| File | What it is |
|---|---|
| `src/my_plugin/__main__.py` | Connects to the sidecar, logs who it was launched as and what it may do, serves the page, and reports itself healthy. |
| `src/my_plugin/page.py` | The page people see through the dashboard. It shows who is asking, and the accounts they may read or write through the plugin. |
| `pyproject.toml` | The package, pinned to the SDK (`open-meridian`). Its `[tool.meridian]` table declares the plugin's `roles` and whether it serves a page. |
| `Dockerfile` | Builds on the SDK's base image. |
| `AGENTS.md`, `CLAUDE.md`, `.claude/skills/develop-live/` | Instructions for coding agents. `.dockerignore` keeps them out of the image. |
| `README.md`, `.gitignore`, `.dockerignore` | The usual. |

The reference plugin asks for no roles:

```toml title="pyproject.toml"
[tool.meridian]
roles = []
interface = true
```

That is a plugin admitted with no topics. It can serve a page and read who is asking, and nothing
more. Who may use it is not declared here: a person's access to a plugin is `read` or `write`, the
same for every plugin, and a deployment admin grants it (see
[Give people access](../how-to/administer-access.md)). See [Plugin manifest](../api/plugin-manifest.md) for every key.

## 4. Upload it

```bash
cd my-plugin
meridian plugin upload
```

It builds the image with Docker and sends its layers to the deployment's own catalogue. Layers the
deployment already holds are not sent again. It ends with a line like:

```text
Uploaded to http://meridian.localhost, as sha256:….
```

## 5. Launch it

```bash
meridian plugin launch my-plugin 0.1.0 --instance my-plugin
```

The CLI shows what this version asks for and waits for your answer:

```text
my-plugin 0.1.0 asks for
  roles: none
Launch it as my-plugin, with these? [y/N]
```

Type `y`. Anything else is no.

```text
Launched my-plugin: my-plugin 0.1.0.
Its page, if it serves one: http://meridian.localhost/plugins/my-plugin
```

`--instance` names this running copy. You use the same name to open, stop and grant access to it.

!!! note
    `--yes` approves without asking. It is for a script that has already shown a person the
    roles. Do not use it to skip a question nobody has answered.

## 6. Check what is running

```bash
meridian plugin list
```

```text
Versions:
  my-plugin 0.1.0  roles: none  page: yes  SDK 0.3.0
Launches:
  my-plugin  my-plugin 0.1.0  launched
```

## 7. Open its page

In the dashboard, the home page lists **Plugins**. Choose `my-plugin`. Its page opens on its own
name, `http://my-plugin.plugins.meridian.localhost/`.

The page shows who you are signed in as and a table headed **What you may see here**. It is empty
because nobody has been granted any part of this plugin yet.

From a terminal you can also run:

```bash
meridian plugin open --instance my-plugin
```

It prints a link that signs one browser in to this plugin's page alone. The link works once, within
a minute.

## 8. Stop it

```bash
meridian plugin stop my-plugin
```

The version stays in the catalogue. Launch it again whenever you like.

## Next steps

- [Build with an AI agent](build-with-an-ai-agent.md): change the plugin with a coding agent, live.
- [Give people access](../how-to/administer-access.md): give your firm's people read or write on a plugin.
- [Release a plugin version](../how-to/release-a-plugin.md): ship a change as a new version.
- [Python SDK](../api/python-sdk.md): what a plugin can call.
