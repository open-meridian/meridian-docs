# Plugin manifest

A plugin describes itself to an Open Meridian deployment in its own `pyproject.toml`, under `[tool.meridian]`. `meridian plugin upload` reads it and sends it with the plugin's image, and the deployment records it with the version.

These are **declarations, not grants**. What a plugin may do comes from the roles a deployment admin approves when a version is launched, never from the plugin's code. See [Plugins, roles and grants](../concepts/plugins.md).

## The template's manifest

`meridian plugin new` writes this. The names shown are the reference plugin's.

```toml title="pyproject.toml"
[project]
name = "reference-plugin"
version = "0.1.0"
description = "A Meridian plugin"
requires-python = ">=3.11"
dependencies = ["open-meridian==0.20.0"]

[project.scripts]
reference-plugin = "reference_plugin.__main__:main"

[tool.meridian]
roles = []
interface = true
```

## `[tool.meridian]`

The table must be present: an upload without it is refused. The command line reads these two keys, and refuses `tags` (below).

| Key | Type | Default when absent | Meaning |
|---|---|---|---|
| `roles` | list of strings | `[]` | The roles the plugin asks for, from the deployment's fixed list (below). Its grants on the bus are the union of its roles' grants. Empty is a plugin admitted with no topics, as the reference plugin is. |
| `interface` | boolean | `false` | Whether the plugin serves a page through its sidecar. It is shown in the catalogue (`page: yes` or `no` in `meridian plugin list`). |

### Rules

The command line checks these before anything is built or sent:

- `roles` is a list, and every item in it is a string.
- Every role is a name: 1 to 63 characters of lowercase letters, digits and single hyphens, starting with a letter and not ending with a hyphen.
- There is no `tags` key. A `[tool.meridian]` that declares one, even `tags = []`, is refused (from CLI 0.1.14; see below).

The deployment checks these again when it records the version, and also refuses:

- a role that is not on the deployment's list;
- a role that is one of the deployment's own components, which no plugin may declare: `conductor`, `dashboard`, `street`, `instrument`, `first-run`, `launcher`, `sidecar`;
- a role declared twice.

### Roles

A plugin's roles come from this list, from the deployment's contract. The template's comment gives the same thirteen.

| Role | For |
|---|---|
| `ccm` | broker and venue connectivity |
| `compliance` | pre- and post-trade compliance rules |
| `custody` | custodian, prime broker and broker positions and reconciliation |
| `dgm` | external data ingress |
| `ems` | execution management |
| `match` | confirmation with external matching services |
| `oms` | order management, including tax-lot selection |
| `operations` | the post-trade pipeline: matching, servicing, reconciliation, settlement |
| `portfolio` | portfolio construction |
| `reporting` | reporting, analytics and valuation |
| `servicing` | non-trading transactions: corporate actions, lifecycle events, coupons |
| `settlement` | external settlement rails |
| `signal` | signal generation |

A role's topics are exactly the rows of the contract that name it. A role that no row names yet holds nothing. In this release, `custody`, `operations`, `portfolio`, `reporting`, `compliance` and `oms` hold [typed operations](typed-operations.md): `operations` from contract v7, and from contract v8 the book of record's, which `operations` writes and the other four read.

## Keys outside `[tool.meridian]`

The command line also reads these, and refuses an upload without them.

| Key | Type | Meaning |
|---|---|---|
| `[project] name` | string | The plugin's name. The same form as a role: lowercase letters, digits and single hyphens, starting with a letter. It names its image and its repository in the deployment's registry, `plugins/<name>`. |
| `[project] version` | string | The version. It must not be empty. The deployment takes 1 to 64 characters of letters, digits, `.`, `_`, `+` and `-`. A version is recorded once and never replaced. |
| `[project] dependencies` | list of strings | Must pin the SDK exactly, as `open-meridian==<version>`. That version is recorded as the plugin's SDK version, so an admin can see which plugins stand on a base that needs a fix. A range is refused. |
| `[project.scripts]` | table | On a development deployment, the live runner starts the first entry point named here, as `module:function`. |

!!! note "Settings are not declared here"
    A plugin's settings, and the pages it serves with the levels each serves, are declared in code when it connects, through `meridian.connect(settings=..., interface=...)`. See the [Python SDK](python-sdk.md#connect). The manifest's `interface` flag and the `interface=` argument are separate: nothing in the command line or the recording checks that they agree.

## Changing the manifest

!!! warning "Roles and dependencies take a new version, which a person approves"
    A save changes what a plugin does, never what it is allowed to do. Adding a role to `pyproject.toml` changes nothing on a running instance, live or not. A new dependency does nothing either: the live code runs on the image the instance was launched from.

    To change any of them:

    1. Raise `version` in `[project]`. A version is never replaced, so uploading one that is already recorded is refused.
    2. Upload it with `meridian plugin upload`, or `meridian plugin dev --release`.
    3. Launch it. The launch shows the roles the version declares, and runs it only once a person approves them.

    The deployment runs a launched version with exactly the roles it declares. An approval that names anything else is refused.

`--yes` on `meridian plugin launch` and `meridian plugin dev` approves without asking. It is for a script that has already shown the roles to a person and got their yes, never for getting past a question nobody has answered. See the [command line reference](cli.md).

## Who may use a plugin is not declared here

A plugin declares no `tags`, and nothing else in the manifest says who may use it. A person's level on a plugin, from contract v15 on each of its roles, is `admin`, `read` or `write`, the same for every plugin, granted by a deployment admin in the deployment's access groups; the plugin reads the session's level, and the accounts it reaches, from [`Caller`](python-sdk.md#caller). Which levels each page serves is declared in code, with [`meridian.Pages`](python-sdk.md#pages). See [Access](../concepts/access.md).

A manifest written for an earlier release, with `tags = [...]` in `[tool.meridian]`, needs that line removed. `meridian plugin upload` from CLI 0.1.14 refuses it, citing the reason, before anything is built.
