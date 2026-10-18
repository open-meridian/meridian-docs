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
- The `meridian` CLI 0.1.46 (`meridian --version`; update with `meridian upgrade`). Its
  `plugin new` writes a plugin on SDK 0.29.0, so the deployment must serve contract 25. SDK
  0.30.0, the latest, declares the same contract; `meridian plugin migrate` moves a plugin to it.
- Docker on this machine. `meridian plugin upload` builds the plugin's image here, from its own
  `Dockerfile`.

## 1. Sign the CLI in

```bash
meridian connect
```

With no address it signs in to the deployment on this machine, `https://meridian.localhost`. For any
other, give its address: `meridian connect https://meridian.firm.example`. Your browser opens the
deployment's sign-in. It then asks you to let the CLI on this computer act as you; choose
**Allow**. The CLI holds that delegation for up to 90 days, and nothing asks for a browser again
until it lapses.

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
| `src/my_plugin/declaration.py` | The version's declaration: its pages, whether it reads external accounts, and its documentation in `docs/`. `[tool.meridian]` names it, `meridian plugin upload` reads it from the built image, and the plugin registers with exactly this one. |
| `docs/` | Its documentation, one Markdown file per section, `overview.md`, `setup.md`, `troubleshooting.md`, `terms.md` and `pages.md`, each a short prompt to replace with your own words. A deployment admin reads it before launching the plugin. See [Write a plugin's documentation](../how-to/write-a-plugins-documentation.md). |
| `src/my_plugin/__main__.py` | Connects to the sidecar with its declaration, logs who it was launched as and what it may do, serves the pages, and reports itself healthy. |
| `src/my_plugin/page.py` | The pages people see through the dashboard, each a view function declared with the levels it serves: **Setup** (`/setup`), at `admin`, says what the plugin is and what the deployment lets it do, shows no account's data, and is where an admin links the external account the plugin reports to one of the deployment's accounts; **Accounts** (`/`), at `write` and `read`, shows the accounts the person may read and write through the plugin, and under Open an **Open a statement** button, in the page's header (its `head_actions` block) above the table. |
| `src/my_plugin/templates/` | The pages' Jinja2 templates, `setup.html` and `accounts.html`, each extending the kit's base template. |
| `pyproject.toml` | The package, pinned exactly to the SDK, `open-meridian==0.29.0`. Its `[tool.meridian]` table declares the plugin's `roles`, whether it serves a page, and names its `declaration`. |
| `Dockerfile` | Builds on the SDK's base image of the same version, `ghcr.io/open-meridian/plugin-python:0.29.0`. |
| `tests/test_page.py` | Tests of the pages, run by `meridian plugin check --run-tests`: each page under each level, no account data under Manage, linking on Setup, and the statement button under Open, including what the page says while nothing is linked. |
| `.github/workflows/check.yaml` | A CI workflow that runs `meridian plugin check --run-tests` on a push to `main`, on each pull request, and when run by hand (`workflow_dispatch`). |
| `hooks/pre-push` | A pre-push hook, CI-first: a branch's push runs nothing, its pull request's CI being the gate, and a push straight to `main` runs `meridian plugin check --run-tests` first. Turn it on with `git config core.hooksPath hooks`. |
| `AGENTS.md`, `CLAUDE.md`, `.claude/skills/develop-live/` | Instructions for coding agents: building pages with the kit, the live loop, and `meridian plugin check`. `.dockerignore` keeps them out of the image. |
| `README.md`, `.gitignore`, `.dockerignore` | The usual. |

**Link, then record.** The new plugin reports the external account its connection reaches
(`report_external_accounts`, in `__main__.py`). An admin of the plugin links it to one of the
deployment's accounts on **Setup**, under Manage. Only then is what the plugin records for that
external account taken, and for that account. **Open a statement** opens an empty holdings statement
for the linked external account, sent for the person asking, so the sidecar decides whether they may;
an agent the person connected can do the same through the tool the SDK derives from the route. While
nothing is linked there is nothing to record for: the sidecar refuses a statement naming no linked
external account, and the page says "Link an account first", and where. `tests/test_page.py` holds
the page to each of these.

`meridian plugin check` holds the plugin to the rules every plugin is built to, and a new plugin keeps
them all. Run it after each change; see [the command line](../api/cli.md#plugin-check). To run the
plugin's tests with it, install the plugin and pytest first, in a virtual environment of the
plugin's own:

```bash
cd my-plugin
python3 -m venv .venv && . .venv/bin/activate
pip install -e . pytest
meridian plugin check --run-tests
```

A bare `pip install` outside a virtual environment is refused by some Pythons, such as Homebrew's on
macOS (`externally-managed-environment`). `--run-tests` runs the tests with `.venv/bin/python` when
the plugin has a `.venv`, and `.dockerignore` keeps the `.venv` out of the image.

The reference plugin asks for no roles:

```toml title="pyproject.toml"
[tool.meridian]
roles = []
interface = true
```

That is a plugin admitted with no topics. It can serve pages and read who is asking, and nothing
more. Who may use it is not declared here: a person's level on each of a plugin's roles is `admin`, `read` or `write`, the same for every plugin, and a deployment admin grants it (see
[Give people access](../how-to/administer-access.md)). See [Plugin manifest](../api/plugin-manifest.md) for every key.

## 4. Upload it

In the plugin's directory (`cd my-plugin`, if you did not run its tests above):

```bash
meridian plugin upload
```

It builds the image with Docker and sends its layers to the deployment's own catalogue. Layers the
deployment already holds are not sent again. It ends with a line like:

```text
Uploaded to https://meridian.localhost, as sha256:….
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
Its page, if it serves one: https://meridian.localhost/plugins/my-plugin
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
  my-plugin 0.1.0  roles: none  page: yes  SDK 0.29.0
    documentation: https://meridian.localhost/admin/plugins/versions/my-plugin/0.1.0/documentation
Launches:
  my-plugin  my-plugin 0.1.0  launched
```

## 7. Open its page

In the dashboard, the home page, **Your plugins**, lists it with a **Manage** button. A deployment's
administrators are admins of every plugin, through **All plugins (admin)**, so that is the level you
hold on it; see [Manage, Open and View](../concepts/plugins.md#manage-open-and-view).

Choose **Manage**. The plugin's area opens, at `https://meridian.localhost/plugins/my-plugin?level=admin`,
on its **Summary**, which the dashboard draws: the plugin's status, its version and its contract.
The reference plugin reports no figures, so there are no tiles below it. After **Summary** and
**Settings** come its pages at `admin`: here one, **Setup**, served from the plugin's own name,
`https://my-plugin.plugins.meridian.localhost/`. It shows who you are signed in as, the instance, its
roles, and what it may publish and subscribe to. Manage is configuration, so it shows no account's
data.

The **Accounts** page is at `write` and `read`, for the people who work in the plugin. To see it,
give yourself `write` on `my-plugin` in an access group, on an account group holding an account (see
[Give people access](../how-to/administer-access.md)). The home then offers **Open** and **View**
beside **Manage**, and **Open** shows a table headed **What you may see here**: the accounts you may
read through the plugin, and which of them you may write.

From a terminal you can also run:

```bash
meridian plugin open --instance my-plugin
```

It prints a link that signs one browser in to this plugin's page alone, at the first level you hold.
The link works once, within a minute, and lands on the plugin's `/`: at Manage, that is the
Accounts page refusing you, so go to `/setup` on the same address. `--level open` or `--level view`
opens it at another level you hold, and `--print <path>` prints a page instead:

```bash
meridian plugin open --instance my-plugin --level manage --print /setup
```

## 8. Stop it

```bash
meridian plugin stop my-plugin
```

The version stays in the catalogue. Launch it again whenever you like.

## Next steps

- [Build with an AI agent](build-with-an-ai-agent.md): change the plugin with a coding agent, live.
- [Give people access](../how-to/administer-access.md): give your firm's people admin, read or write on a plugin.
- [Prove your plugin against a released runtime](../how-to/prove-a-plugin-against-a-released-runtime.md):
  run it on the plugin harness of a pinned runtime from `make e2e` and CI, and check what reached the street store and the book.
- [Release a plugin version](../how-to/release-a-plugin.md): ship a change as a new version.
- [Python SDK](../api/python-sdk.md): what a plugin can call.
