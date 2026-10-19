# Publish a plugin to a registry

Publishing lists a version of your plugin in the platform's Community registry, as
`namespace/plugin`, for any deployment to find and install. You never build or push an image:
you sign a release tag, and the platform builds it, checks it and lists it. What the registries
are, and what each checks, is in [Registries](../concepts/registries.md).

In short:

- **Once:** `meridian plugin key setup`.
- **Each release:** raise the version in the change's own pull request, merge it, then
  `meridian plugin release X.Y.Z`.

Signing the tag yourself and running `meridian plugin publish` is the other way,
[below](#or-tag-and-publish-by-hand).

!!! note "Who can publish today"
    The registries are in Phase 0: only Open Meridian's own plugins, under the `open-meridian/`
    namespace, are published. Outside publishers can't publish yet: the platform refuses their
    publish, saying so. The Verified registry is not open.

## Before you start

- CLI 0.1.50, and git 2.34 or later, which signs tags with SSH keys.
- To release in one command, your GitHub sign-in: `GH_TOKEN` or `GITHUB_TOKEN`, or the credential
  git keeps for github.com (`gh auth setup-git` gives git one). It must be able to read checks on
  the plugin's repository.
- The plugin passes `meridian plugin check`, with its documentation (see
  [Write a plugin's documentation](write-a-plugins-documentation.md)).
- Its repository is on GitHub and public, and the plugin's own code is under Apache-2.0.
- Your organisation on open-meridian.com holds **publisher status**, which platform staff grant.
- You are an Owner or Admin of the organisation. A member who is not needs **may publish** on the
  plugin's **Publishers** tab, which an Owner or Admin grants.

Until your organisation's first publish, its **Plugins** page shows a **To your first publish**
checklist: each step below, ticked as it is done.

## Set up once, on the platform

An Owner or Admin does these on the organisation's publishing pages at open-meridian.com.

1. **Set the namespace.** On the **Plugins** page, **Set the namespace**: lower-case letters,
   digits and hyphens, at most 39 characters. It is the first half of every listing's name, and it
   is fixed at the first publish.
2. **Connect GitHub.** On the **Repositories** page, **Connect GitHub** signs you in with GitHub,
   then links the platform's GitHub App, **Open Meridian Registry**, or installs it on the
   repositories you choose. The first publish fixes the listing's repository.
3. **Register a signing key.** `meridian plugin key setup`, below, does it from your computer. Or,
   on the **Signing keys** page, **Register a key**, and paste the public half of the key you will
   sign release tags with. The platform holds public halves only.

### The signing key

Once, from the plugin's directory:

```bash
meridian plugin key setup
```

It makes the key ready in one step:

- **The key.** Where git already signs with an SSH key, that key is used. Otherwise `ssh-keygen`
  makes one on your computer, `~/.ssh/id_ed25519_meridian` (`ed25519`), and asks you for its
  passphrase itself. With `--hardware`, the key is held on a FIDO security key instead
  (`ed25519-sk`), and `ssh-keygen` asks you to touch it.
- **git** is set to sign with it (`gpg.format ssh`, `user.signingkey`). Where git already signs
  with a GPG key, only in the plugin's repository.
- **The platform.** If you are an Owner or Admin, it registers the public half on the
  organisation. If you are not, it tells you to ask one, with the line to give them.

The first command that needs the platform signs you in in your browser; the sign-in is kept 30
days. `--organisation` takes the organisation's namespace. It defaults to the organisation the
plugin's git remote names, where the platform knows it; otherwise the command says to name it.
`meridian plugin new` offers `key setup` where git has no SSH signing key yet.

A signing key stays with a person or a device. Never put it in CI. An organisation can register
several keys, one for each person or device that signs releases.

To register a key you already have, or to list the organisation's keys:

```bash
meridian plugin key register ~/.ssh/release.pub --organisation acme
meridian plugin key list --organisation acme
```

## Each release

The version goes up in the change itself. The pull request that makes the change also raises
`version` in `pyproject.toml` and adds the change to `CHANGELOG.md` under a heading for that
version, with no date and no "(unreleased)": the date lives on the tag and the listing.

```markdown
## 0.18.0

- The Statements page pages by month.
```

Once that pull request is merged and main's CI is green, from the plugin's directory, on main,
clean and up to date:

```bash
meridian plugin release 0.18.0
```

It checks, signs and publishes. It opens no pull request and changes no file:

1. **Checks.** The checkout is on the default branch, clean and up to date with `origin`; the
   version is higher than the last release tag; `pyproject.toml` says `0.18.0`; `CHANGELOG.md`
   has the heading `## 0.18.0`, undated; and main's last CI run is green. Each refusal says what
   to do next: a version not yet raised, for example, is raised in a pull request, merged, and the
   command run again.
2. **The tag.** It signs `v0.18.0` on main's head with your key, and pushes it.
3. **Publishing.** It asks the platform to build the tag, and follows the build, as
   `meridian plugin publish` does.

If it stops following after `--timeout` (default 30 minutes), the build carries on. Running the
same command again finds the tag on `origin` and publishes it.

While the build runs it prints one line a check, cut to your terminal's width, until the version is
listed or refused, then the listing's address:

```text
acme/venue-desk 0.18.0 (community): listed
  image: sha256:…
  ok    <check>: <what it found>
  warn  <check>: <what it found>
  …
  (--details prints each check's full text)
  log: https://github.com/open-meridian/plugin-builder/actions/runs/…
  listing: https://open-meridian.com/plugins/acme/venue-desk
```

`--details` prints each check's full text. The build carries on if you stop following it.

### Or tag and publish by hand

The same release, step by step. Any SSH key registered on the organisation signs it. Point git at
it once, if `meridian plugin key setup` has not:

```bash
git config gpg.format ssh
git config user.signingkey ~/.ssh/release.pub
```

Then, for each release:

1. Raise `version` in `pyproject.toml` and merge the change, through its pull request as usual.
2. Tag the merged release commit with that version, `v` and its SemVer, signed with your key:

    ```bash
    git switch main && git pull
    git tag -s v0.18.0 -m "venue-desk 0.18.0"
    git push origin v0.18.0
    ```

3. From the plugin's directory, ask the platform to build it:

    ```bash
    meridian plugin publish --registry community --tag v0.18.0
    ```

The tag's version must equal the `version` in `pyproject.toml`. Before it asks for anything,
`plugin publish` refuses here what the builder would refuse: a tag that is not `v` and that
version, a tag not signed with an SSH key, an `origin` that is not a GitHub repository, or a
plugin failing `meridian plugin check`. Then it asks the platform to build the tag, with a token
good for that one plugin, and follows the build, printing its report as above. `--timeout` sets
how long it follows the build (default 30 minutes).

## What the platform checks

In short: the tag's signature against your organisation's keys; that it is built on
`plugin-python`; the plugin's own dependencies, screened against its licence and for
vulnerabilities; secrets and malware; the role's conformance suite and the plugin's own tests, run
inside the built image; the image's size; `meridian plugin check`; and the attestations, signed by
the platform's key. See [The automatic checks](../concepts/registries.md#the-automatic-checks).

Each build has its own page, reached from the plugin's **Versions** tab: one short line per check, with its full text a click away, and a **Packages** table, the image's bill of
materials. An agent you connect reads the same with `read_plugin_build`.

A refused build does not hold its version: once you have fixed what it names, that version is
still free to publish.

## Look after a listing

- **Withdraw a version** on the plugin's **Versions** tab, **Withdraw**. It is no longer offered for
  install or update and stays pullable by digest, with no warning to those who installed it.
- **Attributes and support contact** on the **Attributes** tab: the regions (ISO 3166 country
  codes) and asset classes the plugin serves, and how to reach you. Each is shown as the vendor's.
- **Who may publish it**, on the **Publishers** tab: an Owner or Admin grants and revokes **may
  publish** for a member. That is a page act, never an agent's.
- **Usage**, on the **Usage** tab: totals per version and week, once three or more deployments
  contribute.

## Revoke a signing key

If a key may have leaked, revoke it on the **Signing keys** page, or with the CLI, saying when it
stopped being trusted:

```bash
meridian plugin key revoke SGK-01JB8Z3K6Q --organisation acme \
  --reason "laptop lost" --not-trusted-after 2026-10-16T12:00Z
```

`--not-trusted-after` defaults to now. A tag the key signed before that time still verifies; a
build after it, of a tag it signed, is refused. Deployments learn of the revocation with their next
catalogue pull.

## Related

- [Registries](../concepts/registries.md): the phases, the checks and what a deployment verifies.
- [Command line](../api/cli.md#meridian-plugin-release): `plugin release`, `plugin publish` and `plugin key`.
- [Release a plugin version](release-a-plugin.md): to your own deployment.
