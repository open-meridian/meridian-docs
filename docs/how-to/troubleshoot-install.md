# Troubleshoot an install

Find what you see in the left column. Each row says what it means and what to do.

## Before and during `meridian up`

| What you see | What it means | What to do |
|---|---|---|
| `meridian doctor` shows `stops`, or `meridian up` stops with "Nothing was installed" | Something it checked would stop the install | Do what the line under it says, and run it again. Nothing was installed. |
| `meridian up` refuses `--id` | The identifier is not in the platform's shape | Copy it from the platform with its **Copy** button, `DEP-` included. |
| The clock line says this machine is some seconds from the platform's | A skewed clock fails sign-in in a way that looks like a bad key | Fix this machine's time sync and run `meridian doctor` again. |
| The disk line says a node is under disk pressure, or pods sit in `Pending` | Kubernetes evicts a node's pods when it runs short of disk, and schedules none there | Free disk on the node and wait a few minutes. On a laptop VM such as Rancher Desktop's, Docker's build cache is often most of it: `docker builder prune -a`. |
| The chart refuses the host | You gave an IP address | Use a name. On a laptop, any name ending in `.localhost` works. |
| `street`, `instrument` and `migrate` pods in `CreateContainerConfigError` before the wizard | Expected. They wait for the database the wizard sets up | Nothing. They start a minute or two after **Apply**. |

## Enrolling and opening the wizard

| What you see | What it means | What to do |
|---|---|---|
| **Issue first-run code** is not in the deployment's menu | The deployment has not connected yet | Wait for **Connected** on the platform. If it stays **Not connected**, see the next row. |
| The wizard asks for an **Enrolment code**, not a first-run code | The deployment could not enrol, usually because the code was spent or expired | Issue a fresh enrolment code on the platform, enter it on that page and choose **Enrol**. Nothing needs reinstalling. |
| The fingerprint on the wizard differs from the platform's | Someone else spent your enrolment code | Stop. Revoke that key on the platform, issue a new enrolment code, and enrol again. |
| **Issue enrolment code** is missing from the menu | The deployment already holds a key | If the cluster still has its key, it needs no code. To add another key, use **Add a key**. If you deleted the namespace, see [Remove or start over](remove-or-start-over.md). |
| "this deployment is retired" | It was taken out of service on the platform | Choose **Return to service** there. Codes are refused while it is retired. |

## In the wizard

| What you see | What it means | What to do |
|---|---|---|
| **Test** names a missing database grant | Your roles need it | Run the statement it names, then **Test** again. |
| **Test** finds fault with the issuer | The issuer is not exactly what your provider states | Copy it from your provider's discovery document, trailing slash and all. |
| Every OpenID Connect sign-in is refused | Your provider puts another audience in its tokens | Add it under *Other audiences a token may name*. |
| The address step warns about an IP address | A plugin's page needs a name below the dashboard's | Give the dashboard a name. |

## After applying

| What you see | What it means | What to do |
|---|---|---|
| `street`, `instrument` or `migrate` still in error | They may not have retried yet | Give them two minutes. If they stay, read the message: a key still missing there means the apply did not write the database Secret. |
| "the directory did not say when this person authenticated" | Your OpenID Connect provider returned no `auth_time` | See [Choose how people sign in](choose-sign-in.md). On Entra ID, add `auth_time` as an optional claim. Nothing in the deployment changes. |
| You sign in but see no gear (**Settings**) at the top right | You are not in the administrators' group, or it was misspelt | See [Recover administration](recover-administration.md). |
| The only administrator lost their password | Nobody else can sign in to reset it | See [Reset a lost password](reset-a-lost-password.md). |

## From the CLI, after installing

Every `meridian plugin` command exits with a code that says what kind of failure it was.

| Exit | Means | What to do |
|---|---|---|
| 1 | Refused or failed | Read the message. It names the cause. |
| 2 | Asked wrongly | Check the command and its flags against `meridian --help`. |
| 3 | Not connected, or the delegation was revoked or has lapsed | Run the `meridian connect` it prints. A delegation lasts up to 90 days, and a session an earlier CLI kept 12 hours at most. |

| What you see | What to do |
|---|---|
| "not connected to …: `meridian connect …` first" | Run that command. With several deployments connected, add `--deployment <address>`. |
| `plugin dev` is refused | The deployment was not installed with `--development`. Nothing is wrong with the plugin. Use `plugin upload` and `plugin launch` instead. |
| "… runs … as a version, not live" | The instance runs an ordinary version. `meridian plugin stop <instance>` first, or choose another `--instance`. |
| "… is recorded already, and a version is never replaced" | Raise `version` in `pyproject.toml` and release again. |
| "not approved, so not launched" | You did not answer `y`, or there was no terminal to ask at. In a script that has shown a person the roles, pass `--yes`. |

## Still stuck

- [Remove or start over](remove-or-start-over.md) if you want a clean slate.
- [Command line](../api/cli.md) for every command and flag.
