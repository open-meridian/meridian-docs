# Registries

A plugin reaches a deployment from a **registry**. Every deployment has its own, the **local**
registry, which you upload to yourself. The platform at open-meridian.com keeps two shared ones,
**community** and **verified**, where a plugin built by one organisation is listed for every
deployment to find, read and install.

Naming a plugin in any registry is not an endorsement. Read
[Who checks a plugin](plan-your-deployment.md#who-checks-a-plugin) before you install one: it says
what each registry checks, and what your firm checks itself.

## The three registries

| | Local | Community | Verified |
|---|---|---|---|
| **Where it is** | Inside your deployment | The platform | The platform |
| **Who puts a plugin there** | A deployment admin, with `meridian plugin upload` | An organisation holding publisher status, from a signed release tag the platform builds | The same, at the verified grade, after a person's review |
| **What is checked** | Nothing | The [automatic checks](#the-automatic-checks), at build. Labelled **Unsupervised** wherever it appears | The automatic checks, a person's review at best effort, and a version floor |
| **Named** | By its bare name, `my-plugin` | `organisation/plugin`, such as `open-meridian/snaptrade` | The same |
| **Open today** | Yes | To Open Meridian's own plugins (Phase 0, below) | Not yet |

A plugin installed from community or verified lands in your local registry under
`plugins/<organisation>/<plugin>`, its version recording the registry it came from and its
listing, so it can never collide with a plugin you uploaded yourself.

## Phases

The shared registries open in phases:

- **Phase 0, now:** Open Meridian's own plugins are listed in community, under the
  `open-meridian` organisation.
- **Phase 1:** invited outside organisations publish. The tools for it are built: publisher
  status, the per-plugin publishing permission, linked repositories, the builder, review, and the
  copyright process. An outside organisation can publish only once the platform's copyright
  process is switched on; until then the platform refuses its publish, saying the registries are
  open only to first-party plugins for now.
- **Later phases** open the verified registry, and then community publishing to any organisation.

No phase has a date. Open Meridian's own plugins go through verified's review, as any vendor's
do, once verified opens.

## Who publishes

- **An organisation holding publisher status**, which platform staff grant and revoke, each grant
  its own record. A person publishing alone does so as an organisation of one.
- **A person** who is an Owner or Admin of that organisation, or who holds the plugin's
  **may publish**, which an Owner or Admin grants on the plugin's page.
- **A listing** is `organisation/plugin`: the organisation's slug, which can be changed until its
  first publish and never after, and the plugin's `[project] name`. `open-meridian` is reserved
  for Open Meridian's own plugins.
- **The source repository** is linked to the organisation through the platform's GitHub App,
  **Open Meridian Registry**, and fixed for the listing at its first publish.
- **Signing keys.** The organisation registers the SSH public keys its release tags are signed
  with. Revoking one records when it stopped being trusted (**not trusted after**), so tags it
  signed before then still verify.

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
3. It runs the automatic checks, below, and writes the image's **provenance** (an in-toto
   statement in SLSA's form, naming the repository, the commit, the tag, the signing key's
   fingerprint and the builder), its **bill of materials** (SPDX) and its scan results, each
   attached to the image.
4. When every check passes, the platform signs a **listing statement** for the version and lists
   it. A community version is listed then; a verified one waits for a reviewer.

Community copies are held in the platform's public registry,
`ghcr.io/open-meridian/plugins/<organisation>/<plugin>`, and every reference to one is by digest.
Community build logs are public. A version, once listed, never changes.

### The automatic checks

A version that fails one is refused, naming it; nothing is half-listed.

- The tag is signed by a registered key of the organisation, active at the build.
- The repository is the listing's. For community it is public, and the plugin's own code is under
  the platform's licence for it, Apache-2.0.
- It is built on `plugin-python`.
- The bill of materials' dependencies are screened; strong copyleft is flagged, and does not
  block.
- Trivy scans for vulnerabilities and secrets, ClamAV for malware. A secret, malware, a
  vulnerability on CISA's Known Exploited Vulnerabilities list, or a critical one with a fix
  blocks; any other finding is a warning shown with the version.
- The role's conformance suite runs.
- Caps: an image of at most 1 GiB, at most 20 publishes per organisation a day, and two builds
  per organisation at once.
- Its roles are the contract's, the version floor is present, and the version is higher than
  every listed one.
- Its documentation's digests match its texts, and pass `documentation-sections` and
  `documentation-safe` (see [Write a plugin's documentation](../how-to/write-a-plugins-documentation.md)).

What these checks are, and are not, is in
[the notice](plan-your-deployment.md#who-checks-a-plugin).

## Installing, updating and pulls

!!! note "TODO: core, not built yet"
    Core's v25 branch has not landed the Plugins page's **Browse**, **Installed** and
    **Registries** tabs, install and update, the conductor's verification, or the usage report.
    This section is written from the accepted spec; check each sentence against core as built.

- **The catalogue.** Your deployment pulls the platform's catalogue hourly, and on demand from
  **Browse**: listings, versions, pulls, withdrawals and the status of every signing key. The
  dashboard reads that copy, so the platform is never reached while a page loads.
- **Install** is a deployment admin's act, at **Browse** or through an agent's tool. The dashboard
  checks the version's floor against your deployment's components first. The conductor then asks
  the platform where to pull the version, pulls the image and its attachments by digest into the
  local registry, and verifies them. Install launches nothing.
- **Verification** is the conductor's, at download and again at every launch, offline, against
  the platform's keys your chart carries: the digest, the provenance's and the listing statement's
  signatures, the signing key's status at the build, and that the declaration it records is the
  built image's. A version failing any check is refused, naming it. There is no override.
- **Launch** is as for any version: it shows the notice and the roles the version asks for, which
  you approve. For a verified version, the roles its review approved, and no more.
- **Updates** are offered from the registry a version came from, and applying one is always a
  person's act. A version asking for more roles or scope waits for your approval, showing the
  difference. An instance running a local version of the same plugin can be moved to the listed
  one, checked the same way, keeping its state.
- **A pull** removes a version from the catalogue, for a breach of the terms or a copyright
  notice. Installed copies are warned, never removed: the warning heads the instance's Summary and
  the Installed list until a deployment admin stops the instance or keeps it, with a note.
- **A withdrawal** is the publisher's own: the version is no longer offered, stays pullable by
  digest, and carries no warning.

### A deployment that reaches nothing

On a connected machine, `meridian plugin download organisation/plugin@version` writes a **plugin
bundle**: the image, its provenance, bill of materials, scan results and listing statement, its
documentation and a dated copy of the signing keys' status, each verified against the platform's
keys that CLI release carries before anything is written. `meridian plugin upload --bundle <file>`
carries it into the air-gapped deployment, which verifies it again. Such a deployment reports
nothing, and learns of a pull only from a later bundle. See
[Install a plugin from a registry](../how-to/install-from-a-registry.md#a-deployment-that-reaches-nothing).

### What a deployment reaches

A deployment installing from community reaches the platform, `open-meridian.com`, and the
platform's public registry, `ghcr.io`, with its content host `pkg-containers.githubusercontent.com`.
Community images are pulled anonymously.

## Counts and stars

- **Report plugin usage** is a deployment admin's setting on the **Registries** tab, on by default
  and shown at the first install. While on, the conductor sends the platform a weekly report for
  each installed community or verified version: its listing and version, its launched instances,
  how many people hold each level, and daily counts of the operations, pages and tool calls it
  carried. It names no person, account, instrument or local plugin, and each report sent is kept
  and listed on the tab.
- **Installs** are counted when a deployment asks the platform where to pull a version.
- **A count is shown only once three or more deployments contribute**; below that it reads "Fewer
  than three deployments". Nobody outside the platform's staff sees which deployment installed
  what.
- **Stars.** An Owner or Admin of an organisation with an enrolled deployment may star a listing
  once, naming the organisation, and take the star back. Who starred is never shown.

## The catalogue on the web, and for agents

`open-meridian.com/plugins` lists every listing, readable without signing in, with each version's
build, provenance and, for community, its public build log. Its **Documentation** tab is the index
of every listed version's documentation sections and Reference. The notice is in full on every
listing page, and its title heads every list.

An agent reads the catalogue through the platform's MCP, on a delegation you make for the registry
(**Use the plugin registry as you**): `search_plugins`, `get_plugin`, `search_plugin_documentation`
and `read_listing_documentation`, each answering the notice verbatim and marking a vendor's text
as data, never instructions; and `star_plugin` and `unstar_plugin`. A publishing organisation's
Owners and Admins also reach its own tools, such as `read_plugin_build`, `list_signing_keys`,
`set_plugin_attributes`, `withdraw_version` and `get_plugin_usage`. Who may publish and which keys
sign are changed only on the organisation's pages or with the CLI, never by a tool.

## Copyright notices

The platform has a takedown process for copyright notices, built and switched off until its
designated agent is filed. While it is off, only Open Meridian's own plugins publish, and its
policy page is not published. Acting on a notice is a pull of the versions it names, under the
same rules as any pull: new installs stop, installed deployments are warned, nothing is removed.

## Related

- [Plan your deployment](plan-your-deployment.md): which plugins a firm needs, and each one's
  registry.
- [Publish a plugin to a registry](../how-to/publish-a-plugin.md).
- [Install a plugin from a registry](../how-to/install-from-a-registry.md).
- [Write a plugin's documentation](../how-to/write-a-plugins-documentation.md).
