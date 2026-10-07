# Install a deployment

This page takes you from nothing to a running Open Meridian deployment that people sign in to. It
assumes you have never installed one. Budget half an hour.

You move between two places:

- **The platform**, at <https://open-meridian.com>. You register deployments and issue one-time codes
  there.
- **The deployment**, which you install into your own Kubernetes cluster. Your data lives here.

The two are separate on purpose. The platform never holds your positions, and it never holds a
private key. See [Projects and deployments](../concepts/projects-and-deployments.md) for more.

## Before you start

You need:

- A Kubernetes cluster, with `kubectl` already pointing at it. A laptop cluster (k3s, Rancher
  Desktop, kind, Docker Desktop) is fine for trying Open Meridian.
- `helm` 3.12 or newer. The CLI drives your own `helm` and `kubectl`; you do not run them yourself.
- An account on the platform, in a project where you are an **Owner** or **Admin**. Signing up and
  creating a project is free. In someone else's project, its owner can make you an admin.

You do **not** need to make a key or create a Kubernetes Secret. The deployment makes its own key,
and the set-up wizard writes its own Secrets.

### Install the CLI

On macOS (Apple silicon or Intel) or Linux (x86_64 or arm64):

```bash
curl -fsSL https://raw.githubusercontent.com/open-meridian/meridian-cli/main/install.sh | sh
```

It checks the download against its published checksum and puts `meridian` in `~/.local/bin`. No
`sudo` is needed. Check it:

```bash
meridian --version
```

!!! note
    `meridian` never checks for a newer release by itself. Run `meridian upgrade` when you want the
    latest. See the [command line reference](../api/cli.md) for every command.

## 1. Check your machine and cluster

```bash
meridian doctor
```

It checks the cluster and your rights in it, Helm's version, a storage class for the deployment's
key, that no node is short of disk, that the runtime image can be pulled, that the platform answers,
and this machine's clock. It changes nothing. Each problem it finds comes with its fix.

The output looks something like this:

```text
  ok       a cluster is reachable
  ok       helm 3.14 is recent enough
  ok       this account may create deployments in meridian
  ok       this account may create secrets in meridian
  ok       this account may create jobs in meridian
  ok       1 storage class(es) for the key's volume
  ok       node lima-rancher-desktop is not under disk pressure
  ok       the platform at https://open-meridian.com answers
  ok       this machine's clock is within 1s of the platform's
  …

doctor: nothing here would stop an install
```

If a line says `stops`, do what it says and run `meridian doctor` again.

!!! tip "Why the clock matters"
    The deployment proves who it is with signed, time-limited assertions. A skewed clock fails in a
    way that looks exactly like a bad key. `doctor` is the easy way to catch it.

## 2. Make three decisions

Each is easier to make now than after the install.

**Where the database lives.**

| Choice | Use it when | What you agree to |
|---|---|---|
| One the deployment brings | Trying Open Meridian, or developing against it | It runs in your cluster and its roles and passwords are made for you. It survives `meridian down`. It is lost with the cluster, and **nobody backs it up**. |
| One you already run | Anything you depend on | Your own Postgres, in Docker or managed by your cloud. You make two roles first. |

If you use your own Postgres, create two roles now. The **migrating** role may create tables; the
**serving** role must not:

```sql
CREATE DATABASE meridian;
CREATE ROLE meridian_migrate LOGIN PASSWORD 'a-password-you-choose';
CREATE ROLE meridian_app LOGIN PASSWORD 'another-password-you-choose';
GRANT ALL ON DATABASE meridian TO meridian_migrate;
```

The wizard tests both roles and names the statement that fixes anything missing.

**How people reach it.**

| Choice | Use it when | What you pass to `meridian up` |
|---|---|---|
| Your own name, through the cluster's ingress | Your firm's cluster | `--host meridian.firm.example` and a values file naming your certificates |
| `meridian.localhost` | A laptop cluster with an ingress controller (Rancher Desktop, Docker Desktop, k3s) | Nothing extra |
| A port-forward | A cluster with no ingress controller | Nothing extra. `meridian up` forwards a port when it finds no controller. `--no-ingress` asks for one anyway. |

It must be a **name**, not an IP address. Each plugin's page is served on its own name below the
dashboard's, `<instance>.plugins.<host>`, so one plugin's page can never act as you on another. For
your own name you need DNS for the name and for the wildcard `*.plugins.<host>`, both pointing at
your ingress controller. On a laptop, any name ending in `.localhost` needs neither.

**How people sign in.** Your OpenID Connect provider, your LDAP, or accounts the deployment holds
itself. You answer this in the wizard, not at install. See
[Choose how people sign in](../how-to/choose-sign-in.md) before you get there.

## 3. Register the deployment

On the platform:

1. Sign in and open your project.
2. Open **Deployments** and choose **Register deployment**.
3. Give it a name you will recognise in a year, such as `production` or `uat`, and choose
   **Register**.

The deployment now has an identifier that starts `DEP-`. Copy it with the **Copy** button beside it.
Every step below needs it.

## 4. Issue an enrolment code

On the deployment you just registered, open its menu and choose **Issue enrolment code**.

The code is shown once and lasts a day. Copy it now.

This code is what the install carries instead of a key. The deployment makes its own keypair inside
your cluster, registers the public half with this code, and the code is spent.

!!! note
    Issuing a second code expires the first. A deployment that already has a key is not offered a
    code at all, and a retired deployment is refused one.

## 5. Install

Put the enrolment code in the environment, not on the command line, so your shell history does not
keep it. Then run `meridian up` with your identifier exactly as the platform shows it, `DEP-`
included.

=== "Laptop"

    ```bash
    export MERIDIAN_ENROLMENT_CODE=ENR-XXXX-XXXX-XXXX
    meridian up --id DEP-XXXXXXXXXXXXXXXXXXXXXXXXXX
    ```

    It is reached at `http://meridian.localhost`. That needs no certificate and no DNS.

=== "Your firm's cluster"

    Write a values file naming the Secrets that hold your certificates. Leave out
    `pluginsSecretName` if the first certificate covers both names.

    ```yaml title="ingress.yaml"
    ingress:
      tls:
        secretName: meridian-tls                 # for the name
        pluginsSecretName: meridian-plugins-tls  # for *.plugins.<the name>
    ```

    ```bash
    export MERIDIAN_ENROLMENT_CODE=ENR-XXXX-XXXX-XXXX
    meridian up --id DEP-XXXXXXXXXXXXXXXXXXXXXXXXXX --host meridian.firm.example -f ingress.yaml
    ```

=== "No ingress controller"

    ```bash
    export MERIDIAN_ENROLMENT_CODE=ENR-XXXX-XXXX-XXXX
    meridian up --id DEP-XXXXXXXXXXXXXXXXXXXXXXXXXX --no-ingress
    ```

    `meridian up` holds a port-forward on `http://127.0.0.1:8443` until you press Ctrl-C. Use
    `--port` for another port.

`meridian up` runs `meridian doctor` first, then installs, waits for the dashboard, and prints the
wizard's address. It prints the Helm command it ran, so you can see exactly what it did. The
namespace is `meridian`; `-n` picks another.

!!! note "Where older records go: CLI 0.1.36"
    From CLI 0.1.36, `meridian up` asks one more question before it installs:
    where plugins at the edge move their older records, an archive on a directory of the
    cluster's node, such as a NAS export or a second disk, or none. Answer it with
    `--archive <path>` or `--no-archive`; pressing Enter is none. Naming one allows no plugin an
    archive by itself. See
    [Keep older records in the archive](../how-to/keep-older-records-in-the-archive.md#name-the-archive-at-install).

!!! warning "Development deployments"
    Add `--development` to make a sandbox for writing plugins. It may then run plugin code as it is
    being written, which nobody has reviewed, and every page says so. It is set at install and
    nowhere else. **Never** use it on a deployment your firm depends on. See
    [Development deployments](../concepts/development-deployments.md).

### What a correct install looks like

If you watch the pods while it comes up (`kubectl --namespace meridian get pods`), some sit in an
error. That is expected at this point.

| Pods | Expect |
|---|---|
| `broker`, `conductor`, `dashboard`, `first-run` | **1/1**. These serve you the wizard. |
| `key` | **Completed**. The deployment has made its own keypair. |
| `street`, `instrument`, `migrate` | **`CreateContainerConfigError`**, and they stay there. |

The last row is not a failure. Those three wait for a database, which the wizard sets up. They retry
by themselves and come up a minute or two after you apply the wizard. Nothing needs restarting or
deleting.

## 6. Check the deployment enrolled

On the platform, the deployment now shows **Connected** and lists a key with a **fingerprint**.
Keep that page open. You compare the fingerprint in step 8.

## 7. Issue a first-run code

On the same deployment's menu, choose **Issue first-run code**. It is offered once the deployment
shows **Connected**.

The code is single use and lasts a day. It opens the wizard.

## 8. Open the wizard

Open the address `meridian up` printed: `https://<your name>/first-run`, or
`http://meridian.localhost/first-run` on a laptop.

1. **Compare the fingerprints.** The page shows the deployment's identifier and its key's
   fingerprint. It must match what the platform shows. If it does not, someone else spent your
   enrolment code: stop, revoke that key on the platform, and start again at step 4.
2. Enter the first-run code and choose **Continue**.

## 9. Answer the wizard

The wizard has five steps: **Database**, **Signing in**, **Administrators**, **Address**, and
**Review and apply**. Nothing is written until you choose **Apply**.

1. **Database.** Choose *Start one inside this cluster*, or *Use a Postgres you already run* and fill
   in the host, port, database, TLS mode and both roles.
2. **Signing in.** Choose one of three and answer only that part. See
   [Choose how people sign in](../how-to/choose-sign-in.md).
3. **Administrators.** With a directory, name the directory group whose members run this deployment.
   Spell it exactly: it is not checked. With no directory, the account you just made is the
   administrator.
4. **Address.** The name your staff will use to reach the dashboard, such as
   `https://meridian.firm.example`. Not a `127.0.0.1` port-forward.
5. **Review and apply.** Choose **Test**. It checks every answer the way Apply will, and names what
   to fix. Fix it and test again. When it is clean, choose **Apply**.

Applying takes a couple of minutes and restarts what changed.

## 10. Sign in

1. If you used a port-forward, stop it with Ctrl-C.
2. Open the dashboard at the address you gave it and sign in. The administrators you named hold
   deployment admin from their first sign-in, and `admin` on every plugin through **All plugins
   (admin)**: configuring plugins, not reading their data. See [Access](../concepts/access.md).
3. Sign the CLI in as yourself, so you can bring in plugins from a terminal:

    ```bash
    meridian connect https://meridian.firm.example
    ```

    On a laptop, just `meridian connect`: with no address it signs in to
    `http://meridian.localhost`, where `meridian up` puts a deployment. It opens the deployment's own sign-in
    in your browser and never takes a password. From CLI 0.1.25 it then asks you to let the CLI on
    this computer act as you: choose **Allow**. That is a delegation of everything you hold, for 90
    days unless you choose less, and the CLI keeps its access fresh by itself until then. See
    [`meridian connect`](../api/cli.md#meridian-connect).

That is the install finished.

!!! tip "Answering the wizard from a file"
    For a scripted install, `meridian up --params first-run.yaml` posts the same answers to the
    wizard, behind the same first-run code. The file holds no password: each one is read from a
    `MERIDIAN_<FIELD>` variable instead. See [Choose how people sign in](../how-to/choose-sign-in.md)
    and the [command line reference](../api/cli.md).

## Next steps

- [Your first plugin](first-plugin.md): put a plugin in your deployment.
- [Give people access](../how-to/administer-access.md): let the rest of your firm in.
- [Troubleshoot an install](../how-to/troubleshoot-install.md): if something above did not go as
  described.
