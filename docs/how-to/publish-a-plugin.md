# Publish a plugin to a registry

Publishing lists a version of your plugin in the platform's community registry, as
`organisation/plugin`, for any deployment to find and install. You never build or push an image:
you sign a release tag, and the platform builds it, checks it and lists it. What the registries
are, and what each checks, is in [Registries](../concepts/registries.md).

!!! note "Who can publish today"
    The registries are in Phase 0: only Open Meridian's own plugins, under `open-meridian`, are
    published. An outside organisation's publish is refused, saying so, until the platform's
    copyright process is switched on. The verified registry is not open.

## Before you start

- CLI 0.1.46, and git 2.34 or later, which signs tags with SSH keys.
- The plugin passes `meridian plugin check`, with its documentation (see
  [Write a plugin's documentation](write-a-plugins-documentation.md)).
- Its repository is on GitHub and public, and the plugin's own code is under Apache-2.0.
- Your organisation on open-meridian.com holds **publisher status**, which platform staff grant,
  and you are its Owner or Admin, or hold the plugin's **may publish**.

## 1. Set the organisation's slug

On your organisation's **Plugins** tab, **Set the slug**: lower-case letters, digits and hyphens,
at most 39 characters. It is the first half of every listing's name, and it is fixed at the first
publish.

## 2. Link the repository

On the **Repositories** tab, **Link repositories on GitHub** installs the platform's GitHub App,
**Open Meridian Registry**, on the repositories you choose. The first publish fixes the listing's
repository.

## 3. Register a signing key

Make an SSH key for signing releases, if you have none, and register its public half:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/release -C "acme release signing"
meridian plugin key register ~/.ssh/release.pub --organisation acme
```

The first command that needs the platform signs you in in your browser; the sign-in is kept 30
days. Registering a key on the **Signing keys** tab, **Register a key**, does the same. The platform
holds public halves only. `meridian plugin key list --organisation acme` reads them.

`--organisation` defaults to the organisation the plugin's git remote names, where the platform
knows it; otherwise the command says to name it.

## 4. Sign and push a release tag

Raise `version` in `pyproject.toml`, commit, then tag that version, `v` and its SemVer, signed with
the key you registered, and push the tag:

```bash
git -c gpg.format=ssh -c user.signingkey="$HOME/.ssh/release.pub" tag -s v0.18.0 -m "venue-desk 0.18.0"
git push origin v0.18.0
```

GitHub shows the same signature as verified.

## 5. Publish

From the plugin's directory:

```bash
meridian plugin publish --registry community --tag v0.18.0
```

Before it asks for anything, it refuses here what the builder would refuse: a tag that is not `v`
and the version `pyproject.toml` holds, a tag not signed with an SSH key, an `origin` that is not a
GitHub repository, or a plugin failing `meridian plugin check`. Then it asks the platform to build
the tag, with a token good for that one plugin, and follows the build, printing each check as the
platform names it, until the version is listed or refused:

```text
acme/venue-desk 0.18.0 (community): listed
  image: sha256:…
  ok    tag signature: …
  ok    repository and licence: …
  ok    base image: …
  warn  vulnerabilities: …
  ok    conformance: …
  …
  log: https://github.com/open-meridian/plugin-builder/actions/runs/…
```

`--timeout` sets how long it follows the build (default 30 minutes); the build carries on either
way. A refused version lists nothing: fix what it names, raise the version and tag again.

The version's page, under your organisation's **Plugins** tab, shows each build with its
provenance, bill of materials and findings. An agent you connect reads the same with
`read_plugin_build`.

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

If a key may have leaked, revoke it, saying when it stopped being trusted:

```bash
meridian plugin key revoke SGK-01JB8Z3K6Q --organisation acme \
  --reason "copied from a build machine" --not-trusted-after 2026-10-16T12:00Z
```

`--not-trusted-after` defaults to now. A tag the key signed before that time still verifies; a
build after it, of a tag it signed, is refused. Deployments learn of the revocation with their next
catalogue pull.

## Related

- [Registries](../concepts/registries.md): the phases, the checks and what a deployment verifies.
- [Command line](../api/cli.md#meridian-plugin-publish): `plugin publish` and `plugin key`.
- [Release a plugin version](release-a-plugin.md): to your own deployment.
