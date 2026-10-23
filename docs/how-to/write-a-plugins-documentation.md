# Write a plugin's documentation

A deployment admin decides whether to launch a plugin before it has ever run. What they read is
its **documentation**: a few sections of plain Markdown you write in the plugin's `docs/` folder,
carried with each version you upload, and a **Reference** the deployment draws from the version's
declaration, so it always says what the version really asks for.

You need CLI 0.1.52 and SDK 0.32.1 or later (contract 27). `meridian plugin new` writes a plugin with a
`docs/` folder already in it, one short prompt in each section for you to replace.

## The sections

One Markdown file per section, each with a fixed name:

| File | Required | What it holds |
|---|---|---|
| `docs/overview.md` | yes | What the plugin does, for whom, and what it does not do. |
| `docs/setup.md` | yes | What to arrange with the vendor before launching, and the steps after: the settings it asks for, accounts to link, how to tell it is healthy. |
| `docs/troubleshooting.md` | prompted | What goes wrong most often and how a person puts it right, one heading per problem, in the words its Summary or its pages show. |
| `docs/terms.md` | prompted | The terms the plugin is offered under and the vendor's terms a deployment accepts by using it: link the vendor's own terms, or say plainly that the plugin calls no vendor. |
| `docs/pages.md` | no | One sentence per page: who opens it (Manage, Open or View) and what it is for. |

`meridian plugin check` fails a plugin without `overview.md` or `setup.md`, and advises, failing
nothing, when `troubleshooting.md` or `terms.md` is missing. A Verified plugin needs all four (see
[Registries](../concepts/registries.md)). Any other file in `docs/`, such as a `README.md` index
for the repository, is the repository's own: it is not uploaded, and the check says so.

Leave out what the Reference already says. It lists every role and what it reads and publishes,
every setting with its type, label, description and default, every page with its levels, every
tool for agents, the storage the plugin asks for and, for a data plugin, its datasets. Your
sections say why and how; the Reference says what.

## Declare it

The documentation travels in the version's declaration, which from contract 25 is the whole of
what the version says about itself: its settings, its interface (its pages, and the tools their
typed routes make), whether it reads external accounts, and its documentation.

```python title="src/my_plugin/declaration.py"
import meridian

from .page import TITLE, pages


@meridian.settings
class Config:
    api_key: str = meridian.setting("API key", required=True, secret=True)


DECLARATION = meridian.Declaration(
    settings=Config,
    interface=meridian.Interface(port=8000, title=TITLE, pages=pages),
    reads_external_accounts=True,
    documentation="docs",   # relative to where the plugin runs: /plugin/docs in its image
)
```

```toml title="pyproject.toml"
[tool.meridian]
roles = ["custody"]
interface = true
declaration = "my_plugin.declaration:DECLARATION"
```

The plugin connects with the same declaration, `meridian.connect(declaration=DECLARATION)`. The SDK
reads each section, and puts its name, its `sha256:` digest and its size in the declaration. It
parses no Markdown.

Two things follow from registration being held to the version (see
[`meridian.connect`](../api/python-sdk.md#connect)): the interface's port is fixed in the
declaration, never read from the environment, and the module naming the declaration imports every
module that declares a page or a route.

## What the tab shows as written

Write plain Markdown: headings, paragraphs, emphasis, inline code and code blocks, lists, tables,
block quotes and rules. The deployment draws exactly that subset. Raw HTML is shown as the literal
text it is; an image is never fetched, its alt text marked "image not shown"; a link is kept only
to `https:`, `http:` or `mailto:`, drawn with its host and a mark that it leaves the deployment, or
to another section of the bundle by its file name (`setup.md`, `setup.md#before-launching`).
`meridian plugin check`'s `documentation-safe` holds each section to it, and fails:

- a section that is not UTF-8, is empty, or is over 64 KiB, or sections over 256 KiB in all;
- raw HTML, and any image, local or remote;
- a `javascript:`, `vbscript:`, `data:` or `file:` link;
- a link whose text names one host and whose target another;
- a character that hides text, such as a Unicode tag or a bidirectional control;
- text the screen refuses: override, acting for the reader, a claim of endorsement, verification
  or regulatory readiness, posing as Open Meridian, exfiltration, concealment, and claiming
  authority. The deployment refuses such an upload, and the platform such a build, naming where
  and the rule, wherever it is in the documentation or the declaration's text.

It advises, failing nothing, on:

- a level-two heading whose text is longer than one screen of the tab shows (about 200 words):
  split it under more `##` headings;
- a link the tab will show as plain text;
- text matching the screen's shape rules: chat markup, answer-shaped text, instruction words
  (beyond the contract's own allocation, trading, settlement, execution and handling
  instructions), text addressed to the reader (`you need to ...`, which setup steps often say), a
  tool's name, a role marker such as `system:`, or talk of an agent's prompt. The deployment and
  the platform keep such a section, show it to people marked **Screened**, and withhold it from
  agents.

A plugin on an SDK before 0.29.0 cannot declare its documentation, so what these rules find on one
is advice.

## Upload it

```bash
meridian plugin check
meridian plugin upload
```

`plugin upload` reads the declaration from the built image with `meridian-declaration`, and the
texts beside it with `meridian-declaration --documentation`, holds each text to the digest the
declaration names, and sends them with the version. The deployment checks them again, as above,
and keeps them with the version, never replaced. The upload prints where the version's
documentation is read, and `meridian plugin list` prints the same for each version that carries
documentation.

A version's documentation is as fixed as its declaration. To correct a typo, raise the version and
upload again: what a deployment admin read before approving a launch is what runs.

## Where people and agents read it

- **Before launch.** The dashboard's **Plugins** page, `/admin/plugins/versions`, lists each
  version on its **Installed** tab, one line each, and each links its **Documentation** page,
  `/admin/plugins/versions/<name>/<version>/documentation`, a deployment admin's: the address
  `plugin upload` and `plugin list` print. A version installed from a registry is at
  `/admin/plugins/versions/<namespace>/<plugin>/<version>/documentation`. The page says who
  uploaded or installed the version, and their note.
- **A launched or stopped instance.** The **Documentation** tab, last in the plugin's area at
  every level, `/plugins/<instance>?tab=documentation`, for anyone holding a level on the plugin.
  Its sections are tabs, each cut at its level-two headings into one part shown at a time with its
  contents beside it, and the **Reference** last, drawn by the deployment from the declaration.
  A section the screen keeps but
  withholds from agents is shown under a warning saying so. A stopped instance keeps its
  **Summary**, **Settings** and **Documentation**.
- **Through an agent.** `dashboard__read_plugin_documentation` answers each section as
  `vendor_markdown`, the vendor's text, data and never instructions, or withheld, naming the rules
  it matched; and the Reference as the declaration. A person reads a withheld section
  on the tab.
- **In the platform's catalogue.** Once a version is listed in a registry, its sections and its
  Reference are on its listing page's **Documentation** tab at open-meridian.com, and the
  catalogue's one search covers them (see [Registries](../concepts/registries.md)). Agents
  search and read them through the platform's MCP, `search_plugin_documentation` and
  `read_listing_documentation`; a section marked **Screened** is withheld from them.

The plugin's **Summary** keeps the deployment's own facts: its status, warnings, figures and
counts. What the version declares and its tools for agents are on the Reference.

## Writing it well

- Write for the person setting the plugin up, in the words its pages and Summary use.
- Claim nothing the plugin is not: no endorsement, no verification beyond what was done, no
  regulatory readiness. The deployment and the platform refuse such claims.
- In `terms.md`, link the vendor's terms; for a plugin that calls no vendor, say so, and that the
  firm using it does its own due diligence.
- Nothing in a section is a setting or a secret. Settings are declared in code and set on the
  plugin's **Settings** form.

## Related

- [Plugins, roles and grants](../concepts/plugins.md): uploading, launching and approval.
- [Command line](../api/cli.md#plugin-check): `documentation-sections` and `documentation-safe`.
- [Python SDK](../api/python-sdk.md#the-whole-declaration): `Declaration(documentation=...)`.
- [Publish a plugin to a registry](publish-a-plugin.md): where the same documentation is listed.
