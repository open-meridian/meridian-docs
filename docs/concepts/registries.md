# Registries

A plugin reaches a deployment from a **registry**. There are three, labelled **Local**,
**Community** and **Verified**. Every deployment has its own Local registry, which you upload to
yourself. The platform at open-meridian.com keeps the two shared ones, Community and Verified,
where a plugin built by one organisation is listed for every deployment to find, read and install.

[Who checks a plugin](plan-your-deployment.md#who-checks-a-plugin) says what each registry checks,
and what your firm checks itself.

## The three registries

| | Local | Community | Verified |
|---|---|---|---|
| **Where it is** | Inside your deployment | The platform | The platform |
| **Who puts a plugin there** | A deployment admin, with `meridian plugin upload` | An organisation holding publisher status, from a signed release tag the platform builds | The same, at the verified grade, after a person's review |
| **What is checked** | Nothing, by the platform | The [automatic checks](#the-automatic-checks), at build | The automatic checks, a person's review, and a version floor |
| **Named** | By its bare name, `my-plugin` | `namespace/plugin`, such as `open-meridian/snaptrade` | The same |
| **Open today** | Yes | To Open Meridian's own plugins (Phase 0, below) | Not yet |

A plugin installed from Community or Verified lands in your Local registry under
`plugins/<namespace>/<plugin>`, its version recording the registry it came from and its
listing, so it can never collide with a plugin you uploaded yourself.

## Phases

The shared registries open in phases:

- **Phase 0, now:** Open Meridian's own plugins are listed in Community, under the
  `open-meridian/` namespace, such as
  [`open-meridian/snaptrade`](https://open-meridian.com/plugins/open-meridian/snaptrade), with
  five starter packs (see
  [Install a plugin from a registry](../how-to/install-from-a-registry.md#a-starter-pack)).
- **Outside publishers can't publish yet.** The platform refuses their publish, saying the
  registries are open only to first-party plugins for now.
- **Later phases** open publishing to invited organisations, then the Verified registry, and then
  Community publishing to any organisation.

Open Meridian's own plugins go through Verified's review, as any vendor's do, once Verified opens.

## Who publishes

- **An organisation holding publisher status**, which platform staff grant and revoke, each grant
  its own record. A person publishing alone does so as an organisation of one.
- **A person** who is an Owner or Admin of that organisation, or who holds the plugin's
  **may publish**, which an Owner or Admin grants on the plugin's page.
- **A listing** is `namespace/plugin`: the organisation's **namespace**, which can be changed
  until its first publish and never after, and the plugin's `[project] name`. `open-meridian/` is
  the first-party namespace, reserved for Open Meridian's own plugins.
- **The source repository** is linked to the organisation with **Connect GitHub**, through the
  platform's GitHub App, **Open Meridian Registry**, and fixed for the listing at its first
  publish.
- **Signing keys.** The organisation registers the SSH public keys its release tags are signed
  with, as many as it needs. Any SSH key works: a desktop key with a passphrase is the usual
  choice, and a hardware security key is optional. A signing key stays with a person or a device,
  never in CI. Revoking one records when it stopped being trusted (**not trusted after**), so tags
  it signed before then still verify.

The CLI signs in to the platform in your browser, never with a password, and keeps the sign-in for
30 days; each access token it uses lives ten minutes, and a publish's token is good for one plugin
alone. See [Publish a plugin to a registry](../how-to/publish-a-plugin.md).

## How a version is built

The platform builds every version it lists itself. A publisher never pushes an image.

1. The publisher signs a release tag, `v` and the version's SemVer (`v1.4.0`), in the linked
   repository, and asks for a build with `meridian plugin publish`.
2. The platform's builder, a workflow in its public repository
   [`open-meridian/plugin-builder`](https://github.com/open-meridian/plugin-builder), checks out the
   commit the tag pins, verifies the tag's signature against the organisation's keys, and builds
   the plugin on the SDK's `plugin-python` base image.
3. It runs the automatic checks, below, and attaches the image's **provenance** (the repository,
   the commit, the tag, the signing key's fingerprint and the builder), its **bill of materials**
   and its scan results to the image, each signed by the platform's key.
4. When every check passes, the platform signs a **listing statement** for the version and lists
   it. A Community version is listed then; a Verified one waits for a reviewer.

Community copies are held in the platform's public registry,
`ghcr.io/open-meridian/plugins/<namespace>/<plugin>`, and every reference to one is by digest.
Community build logs are public. A version, once listed, never changes.

### The automatic checks

A version that fails one is refused, naming it; nothing is half-listed. A refused build does not
hold its version: fix what it names, and that version is still free to publish.

- **Signature:** the tag is signed by one of the organisation's registered keys.
- **Base image:** it is built on `plugin-python`.
- **Licences:** the plugin's own dependencies are screened against the plugin's licence. The base
  image's packages are not the plugin's, and are not screened.
- **Vulnerabilities** in the plugin's own dependencies.
- **Secrets** and **malware** in the image.
- **Tests:** the role's conformance suite and the plugin's own tests run inside the built image.
- **Size:** the image stays within the platform's cap.
- **Plugin check:** `meridian plugin check` passes, its documentation with it (see
  [Write a plugin's documentation](../how-to/write-a-plugins-documentation.md)).
- **Attestations:** the provenance, bill of materials and scan results are signed by the
  platform's key.

Each build has a page on the platform: one short line per check, its full text a click away, and a
**Packages** table, the bill of materials.

## Installing, updating and pulls

A deployment admin works with the registries on the dashboard's **Plugins** page,
`/admin/plugins/versions`, and its tabs **Installed**, **Browse** and **Registries**; see
[Install a plugin from a registry](../how-to/install-from-a-registry.md).

- **The catalogue.** Your deployment pulls the platform's catalogue hourly, and on demand with
  **Pull now**: listings, versions, pulls, withdrawals and the status of every signing key. The
  dashboard reads that copy, so the platform is never reached while a page loads.
- **Install** is a deployment admin's act, at a listing's page or through an agent's tool. The
  dashboard checks the version's floor against your deployment first. The conductor then asks the
  platform where to pull the version, pulls the image and its attachments by digest into the Local
  registry, and verifies them. The version is recorded under its listing, `namespace/plugin`,
  so it never collides with a local one, with the install's note. Install launches nothing.
- **Verification** is the conductor's, at download and again at every launch, offline, against
  the platform's keys your chart's values carry (`registries.platformKeys`, the current key and
  the next, so the platform's key can rotate without a gap; with none, nothing is installed from a
  registry and Browse says the deployment reaches none): the digest, the provenance's and the listing statement's
  signatures, the signing key's status at the build, and that the declaration it records is the
  built image's. A version failing any check is refused, naming it. There is no override.
- **Launch** is as for any version, naming it by its listing: you approve the roles it asks
  for. For a Verified version, the roles its review approved, and no more.
- **Updates** are offered from the registry a version came from, never a pre-release over a
  release, and applying one is always a person's act. A version asking for more roles waits for a
  deployment admin's approval, showing the difference; a plugin's admin may update where the roles
  are unchanged. An instance running a local version of the same plugin can be moved to the listed
  one, checked the same way, keeping its state.
- **A pull** removes a version from the catalogue, for a breach of the terms or a copyright
  notice. Installed copies are warned, never removed: the warning heads the instance's Summary and
  the Installed list until a deployment admin stops the instance or keeps it (**Keep or stop**),
  with a note.
- **A withdrawal** is the publisher's own: the version is no longer offered, stays pullable by
  digest, and carries no warning.

### A deployment that reaches nothing

On a connected machine, `meridian plugin download namespace/plugin@version` writes a **plugin
bundle**: the image, its provenance, bill of materials, scan results and listing statement, its
documentation and a dated copy of the signing keys' status, each verified against the platform's
keys that CLI release carries before anything is written. `meridian plugin upload --bundle <file>`
carries it into the air-gapped deployment, which verifies it again. Such a deployment reports
nothing, and learns of a pull only from a later bundle. CLI 0.1.53 carries the platform's
registry-signing key, version 1. See
[Install a plugin from a registry](../how-to/install-from-a-registry.md#a-deployment-that-reaches-nothing).

### What a deployment reaches

A deployment installing from Community reaches the platform, `open-meridian.com`, and the
platform's public registry, `ghcr.io`, with its content host `pkg-containers.githubusercontent.com`.
Community images are pulled anonymously.

## Counts and stars

- **Report plugin usage** is a deployment admin's setting on the **Registries** tab, on by default
  and shown at the first install. While on, the conductor sends the platform a weekly report for
  each installed Community or Verified version: its listing and version, its launched instances,
  how many people hold each level, and daily counts of the operations, pages and tool calls it
  carried. It names no person, account, instrument or local plugin, and each report sent is kept
  and listed on the tab.
- **Installs** are counted when a deployment asks the platform where to pull a version.
- **A count is shown only once three or more deployments contribute**; below that the public
  catalogue shows "<3", and other pages read "Fewer than three deployments". Nobody outside the
  platform's staff sees which deployment installed what.
- **Stars.** An Owner or Admin of an organisation with an enrolled deployment may star a listing
  once, naming the organisation, and take the star back. Who starred is never shown.

## The catalogue on the web, and for agents

[open-meridian.com/plugins](https://open-meridian.com/plugins) lists every listing, readable
without signing in: its **Name**, **Publisher**, **Roles**, **Registry**, **Version**, **Installs**
and **Stars**. One search covers plugin names and their documentation. A listing's page shows its
build, provenance and, for Community, its public build log, and its **Documentation** tab holds
each version's sections and Reference.

An agent reads the catalogue through the platform's MCP, on a delegation you make for the registry
(**Use the plugin registry as you**): `search_plugins`, `get_plugin`, `search_plugin_documentation`
and `read_listing_documentation`, each marking a vendor's text as data, never instructions; and
`star_plugin` and `unstar_plugin`. A publishing organisation's Owners and Admins also reach its
own tools, such as `read_plugin_build`, `list_signing_keys`, `set_plugin_attributes`,
`withdraw_version` and `get_plugin_usage`. Who may publish and which keys
sign are changed only on the organisation's pages or with the CLI, never by a tool.

## Copyright notices

The platform has a takedown process for copyright notices, built and not yet switched on. Until
it is, only Open Meridian's own plugins publish. Acting on a notice is a pull of the versions it
names, under the same rules as any pull: new installs stop, installed deployments are warned, nothing is removed.

## Related

- [Plan your deployment](plan-your-deployment.md): which plugins a firm needs, and each one's
  registry.
- [Publish a plugin to a registry](../how-to/publish-a-plugin.md).
- [Install a plugin from a registry](../how-to/install-from-a-registry.md).
- [Write a plugin's documentation](../how-to/write-a-plugins-documentation.md).
