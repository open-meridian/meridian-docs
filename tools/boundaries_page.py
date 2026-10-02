"""The roles page and llms.txt, generated from meridian-schema's boundaries.

meridian-schema publishes the roles a plugin may hold, the principles a
request must fit, the method that maps a request to the least roles and the
worked examples, as boundaries/roles.json, with each file's digest in
boundaries/SHA256SUMS. This repository keeps a copy in boundaries/, and the
schema revision and contract version it describes in boundaries/vendored.json.

As an MkDocs hook (mkdocs.yml, `hooks:`), at every build it

- checks the copy against its SHA256SUMS, so the copy is the schema's, unedited;
- adds concepts/roles.md and llms.txt to the site, both generated from the copy,
  so neither is written by hand and neither can say what the other does not;
- after the build, checks llms.txt against the built site: every link resolves
  to a page and an anchor the site publishes, and every role and operation the
  site publishes is linked, nothing missing and nothing extra; then proves, by
  a self-test, that the check fails on a missing link, an extra one and a
  tampered copy.

From the command line, it refreshes the copy:

    python tools/boundaries_page.py refresh --rev <sha or branch> --contract <n>

taking boundaries/ from meridian-schema at that revision (--repo names another
clone, a URL or a local path), checking its digests, and recording the
revision and the contract version these docs describe.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENDORED = ROOT / "boundaries"
SCHEMA_REPO = "https://github.com/open-meridian/meridian-schema.git"
SCHEMA_WEB = "https://github.com/open-meridian/meridian-schema"

ROLES_PAGE = "concepts/roles.md"
INDEX = "llms.txt"
TYPED_OPERATIONS = "api/typed-operations.md"
SDK = "api/python-sdk.md"

# The SDK section that makes each call every plugin makes, whatever its roles.
# A new call fails the build here until it is given its section.
EVERY_PLUGIN_SECTIONS = {
    "Register": "connect",
    "Heartbeat": "report",
    "Leave": "leave",
    "WatchSettings": "settings",
    "PluginAccess": "access",
    "WatchAccountScope": "account_scope",
}

# The pages llms.txt sends an agent to beside the roles and the operations.
GUIDES = [
    (TYPED_OPERATIONS, "Typed operations",
     "every operation a plugin's roles let it take, with its arguments, what it returns and its errors"),
    (SDK, "Python SDK",
     "connecting to the sidecar, settings, access, figures, receiving what a plugin's roles hear, and pages"),
    ("how-to/prove-a-plugin-against-a-released-runtime.md", "Prove a plugin against a released runtime",
     "an end-to-end check of what a plugin records, on core's plugin harness: a real sidecar, street store and book"),
    ("how-to/build-a-plugin-page.md", "Build a plugin's page",
     "declaring a plugin's pages and the levels they serve, and building them on the plugin UI kit"),
]

# How llms.txt says which roles hold an operation.
BY = {"publishes": "published by", "reads": "read by", "hears": "heard by"}

# Holders a role leaves work to that are not roles.
HOLDER_NAMES = {"bor": "the book", "platform": "the platform"}


# The copy -------------------------------------------------------------------

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_digests(directory: Path) -> list[str]:
    """What is wrong with a copy of boundaries/: empty when it is the schema's."""
    sums = directory / "SHA256SUMS"
    if not sums.is_file():
        return [f"{directory.name}/SHA256SUMS is missing"]
    listed: dict[str, str] = {}
    for line in sums.read_text().splitlines():
        if line.strip():
            value, name = line.split(maxsplit=1)
            listed[name.lstrip("*")] = value
    errors = []
    if "roles.json" not in listed:
        errors.append(f"{directory.name}/SHA256SUMS does not list roles.json")
    for name, value in sorted(listed.items()):
        path = directory / name
        if not path.is_file():
            errors.append(f"{directory.name}/{name} is listed in SHA256SUMS and missing")
        elif digest(path.read_bytes()) != value:
            errors.append(f"{directory.name}/{name} is not what SHA256SUMS says: edited by hand, "
                          "or copied wrongly; refresh it (tools/boundaries_page.py refresh)")
    for path in sorted(directory.iterdir()):
        if path.name not in listed and path.name not in ("SHA256SUMS", "vendored.json"):
            errors.append(f"{directory.name}/{path.name} is not in SHA256SUMS")
    return errors


def load(directory: Path = VENDORED) -> tuple[dict, dict]:
    roles = json.loads((directory / "roles.json").read_text())
    vendored = json.loads((directory / "vendored.json").read_text())
    return roles, vendored


# Generating -----------------------------------------------------------------

def snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def step_key(step: str) -> tuple:
    return tuple(int(part) for part in re.findall(r"\d+", step))


def prose(text: str) -> str:
    return text.replace(" -- ", " — ")


def operation_target(op: dict) -> tuple[str, str, str]:
    """(page, anchor, the name the page gives it) for an operation of roles.json."""
    roles = op.get("roles", {})
    if roles.get("publishes") or roles.get("reads"):
        return TYPED_OPERATIONS, snake(op["name"]), snake(op["name"])
    return SDK, "receive", op["name"]


def every_plugin_target(call: dict) -> tuple[str, str, str]:
    if call["name"] not in EVERY_PLUGIN_SECTIONS:
        raise ValueError(f"roles.json names {call['name']}, a call every plugin makes, and "
                         "tools/boundaries_page.py gives it no SDK section (EVERY_PLUGIN_SECTIONS)")
    return SDK, EVERY_PLUGIN_SECTIONS[call["name"]], call["name"]


def relative(page: str, anchor: str = "") -> str:
    """A link from the roles page, in concepts/, to another page of the site."""
    link = "../" + page
    return f"{link}#{anchor}" if anchor else link


def url(site_url: str, page: str, anchor: str = "", directory_urls: bool = True) -> str:
    """A page's address on the site, as llms.txt links it."""
    path = page[: -len(".md")]
    if not directory_urls:
        path += ".html"
    elif path == "index" or path.endswith("/index"):
        path = path[: -len("index")]
    else:
        path += "/"
    address = site_url.rstrip("/") + "/" + path.lstrip("/")
    return f"{address}#{anchor}" if anchor else address


def role_link(name: str, names: set[str]) -> str:
    if name in names:
        return f"[`{name}`](#{name})"
    return HOLDER_NAMES.get(name, f"`{name}`")


def cite(text: str, items: list[str] | None) -> str:
    """Text with where it is decided in brackets, before its last full stop."""
    text = prose(text)
    if not items:
        return text
    stop = "." if text.endswith(".") else ""
    return f"{text[: len(text) - len(stop)]} ({', '.join(items)}){stop}"


def scope_line(role: dict, by_name: dict[str, dict]) -> list[str]:
    parts = []
    for kind in ("publishes", "reads", "hears"):
        names = role["scope"].get(kind, [])
        if names:
            links = []
            for name in names:
                page, anchor, shown = operation_target(by_name[name])
                links.append(f"[`{shown}`]({relative(page, anchor)})")
            parts.append(f"{kind} {', '.join(links)}")
    return parts


def roles_page(roles: dict, vendored: dict) -> str:
    contract = f"v{vendored['contract']}"
    rev = vendored["schema_rev"]
    entries = roles["roles"]
    names = {r["name"] for r in entries}
    by_name = {op["name"]: op for op in roles["operations"]}
    out: list[str] = []
    add = out.append

    add("# Roles\n")
    add("A plugin's **roles** decide what it may do on the bus: the operations it may call, the "
        "queries it may ask and the deliveries it hears. This page is each role's entry: the person "
        "or desk whose job it does (its persona), its function and duties, what it leaves to which other role, and "
        f"what it holds at contract {contract}. Then the principles a plugin must fit, and the method "
        "that turns an idea for a plugin into the least roles it needs, with worked examples.\n")
    add("**Roles are fixed, and nobody can change a role's grants, not even for one plugin.** So an "
        "idea is mapped to the least roles that hold what it needs, or reshaped until it fits. "
        "What a plugin is and how its grants are made is in "
        "[Plugins, roles and grants](plugins.md).\n")
    add("Every part of this page is generated from `boundaries/roles.json` in "
        f"[meridian-schema]({SCHEMA_WEB}), which an agent can read as it is; "
        f"[`/llms.txt`](../{INDEX}) lists this page's sections and every operation, for an agent "
        "to start from.\n")

    proposed = [r["name"] for r in entries if r.get("status") == "proposed"]
    if proposed:
        which = ("Every role's entry is proposed" if len(proposed) == len(entries) else
                 "The entries for " + ", ".join(f"`{n}`" for n in proposed) + " are proposed")
        add('!!! note "Proposed entries"')
        add(f"    {which}: its persona, function, duties and what it leaves to others may still be "
            "revised. Its scope is generated from the contract, and is exact.\n")

    add("## The thirteen roles { #the-roles }\n" if len(entries) == 13 else
        f"## The {len(entries)} roles {{ #the-roles }}\n")
    add(f"| Role | Function | Persona | At contract {contract} |")
    add("|---|---|---|---|")
    for r in entries:
        counts = [f"{kind} {len(r['scope'].get(kind, []))}"
                  for kind in ("publishes", "reads", "hears") if r["scope"].get(kind)]
        held = ", ".join(counts).capitalize() if counts else "Nothing yet"
        add(f"| [`{r['name']}`](#{r['name']}) | {prose(r['archetype'])} | {prose(r['persona'])} | {held} |")
    add("")
    add("**An edge role** connects the deployment to something outside it, and may keep that outside "
        "party's raw records in storage of its own, to reconnect and rebuild from. Every other role "
        "keeps nothing it cannot lose. No plugin's storage is a channel to another plugin.\n")

    for r in entries:
        add(f"### `{r['name']}` {{ #{r['name']} }}\n")
        add(f"**{prose(r['archetype'])}.** {prose(r['summary'])}\n")
        add(f"- **Persona:** {prose(r['persona'])}.")
        add("- **Duties:**")
        for duty in r["duties"]:
            add(f"    - {cite(duty['duty'], duty.get('basis'))}")
        add("- **Leaves to others:**")
        for item in r["leaves_to"]:
            add(f"    - {prose(item['what'])}: {', '.join(role_link(t, names) for t in item['to'])}")
        add("- **Storage:** " + ("an edge role; it may keep its raw external records in storage of its own."
                                 if r["edge"] else "none; it keeps nothing it cannot lose."))
        parts = scope_line(r, by_name)
        if parts:
            add(f"- **At contract {contract}:** " + "; ".join(parts) + ".")
        else:
            add(f"- **At contract {contract}:** nothing yet. No workflow names this role, so a plugin "
                "holding only it is admitted with no topics; it can still serve a page.")
        add("")

    add("## Roles held together { #combinations }\n")
    add("A plugin may hold several roles. It has one sidecar and one credential, and holds the union "
        "of their grants; the duties stay separate in the records. Sets a plugin commonly holds:\n")
    for c in roles["combinations"]:
        add(cite(f"- {c['name']}: {', '.join(role_link(n, names) for n in c['roles'])}", c.get("basis")))
    add("")

    people = roles["people"]
    add("## Who may use a plugin { #people }\n")
    add(f"{cite(people['says'], people.get('basis'))} The levels, the same for every plugin:\n")
    for level in people["levels"]:
        add(f"- **`{level['level']}`**: {prose(level['says'])}")
    add("")
    add("How a deployment admin grants them is in [Access](access.md); what each opens is in "
        "[Who may use a plugin](plugins.md#who-may-use-a-plugin-admin-read-or-write).\n")

    add("## What every plugin does { #every-plugin }\n")
    add("Whatever its roles, every plugin makes these calls to its sidecar, through the SDK:\n")
    for call in roles["every_plugin"]:
        page, anchor, shown = every_plugin_target(call)
        title = f": {call['title']}" if call["title"] != shown else ""
        add(f"- [`{shown}`]({relative(page, anchor)}), {call['step']}{title}")
    add("")

    add("## Principles { #principles }\n")
    add("These are Open Meridian's design philosophy. A request must fit them before any role is "
        "chosen.\n")
    for p in roles["philosophy"]:
        add(f"{p['number']}. **{prose(p['principle'])}** {cite(p['says'], p.get('basis'))}")
    add("")

    add("## From an idea to the least roles { #method }\n")
    add("Because roles are fixed and their grants generated, an idea for a plugin is mapped to the "
        "roles it needs, the fewest that will do, or reshaped. An agent building a plugin follows "
        "these steps, and says what it found at each:\n")
    for m in roles["method"]:
        add(f"{m['number']}. **{prose(m['step'])}** {prose(m['says'])}")
    add("")
    held = {r["name"] for r in entries if any(r["scope"].values())}
    example = next((e for e in roles["examples"]
                    if e["least_roles"] and set(e["least_roles"]) <= held), None)
    if example:
        add("The roles found go in the plugin's `pyproject.toml`, and a deployment admin approves them "
            f"when it is launched. For the worked example “{prose(example['request'])}”, below:\n")
        add("```toml\n[tool.meridian]\nroles = [" + ", ".join(f'"{n}"' for n in example["least_roles"])
            + "]\n```\n")
        add("See [Plugin manifest](../api/plugin-manifest.md#roles).\n")

    add("## Worked examples { #examples }\n")
    add("Each names what it needs and the contract version that grants it. Where a request breaks a "
        "principle, it says which, and the shape that fits.\n")
    for e in roles["examples"]:
        add(f"### “{prose(e['request'])}”\n")
        if e["reshaped"]:
            numbers = [str(n) for n in e.get("breaks", [])]
            broken = (f"principle {numbers[0]}" if len(numbers) == 1 else
                      f"principles {', '.join(numbers[:-1])} and {numbers[-1]}")
            add(f"- **Reshaped:** it breaks [{broken}](#principles). "
                f"{prose(e['why'])}")
            add(f"- **Instead:** {prose(e['reshaped_to'])}")
        else:
            add(f"- **Least roles:** {', '.join(role_link(n, names) for n in e['least_roles'])}")
            add(f"- **Why:** {prose(e['why'])}")
        if e.get("deployment_needs"):
            add(f"- **The deployment also runs:** {prose(e['deployment_needs'])}")
        if e.get("people"):
            add(f"- **People:** `{e['people']}`")
        if e.get("needs"):
            add("- **Needs:**")
            for need in e["needs"]:
                who = role_link(need["role"], names)
                if "row" in need:
                    page, anchor, shown = operation_target(by_name[need["row"]])
                    add(f"    - {who} {need['as']} [`{shown}`]({relative(page, anchor)}): "
                        f"from contract {need['granted']}")
                else:
                    add(f"    - {who}, {prose(need['what'])}: not yet; {prose(need['pending'])}")
        add(f"- **Available:** {prose(e['available'])}")
        add("")

    add("---\n")
    add(f"Generated from [`boundaries/roles.json`]({SCHEMA_WEB}/blob/{rev}/boundaries/roles.json) "
        f"in meridian-schema at `{rev[:7]}`, contract {contract}.")
    return "\n".join(out) + "\n"


def index_entries(roles: dict, vendored: dict, site_url: str, directory_urls: bool = True) -> dict:
    """The sections of llms.txt: each a list of (text, address, description)."""
    def at(page: str, anchor: str = "") -> str:
        return url(site_url, page, anchor, directory_urls)

    contract = f"v{vendored['contract']}"
    entries = roles["roles"]
    sections: dict[str, list[tuple[str, str, str]]] = {}
    sections["Roles"] = [
        ("Roles", at(ROLES_PAGE),
         f"each role's persona, function, duties, what it leaves to another role and what it holds at contract {contract}"),
        ("Principles", at(ROLES_PAGE, "principles"),
         f"the {len(roles['philosophy'])} principles a request must fit before any role is chosen"),
        ("From an idea to the least roles", at(ROLES_PAGE, "method"),
         f"the method, in {len(roles['method'])} steps, including when a request must be reshaped"),
        ("Worked examples", at(ROLES_PAGE, "examples"),
         f"{len(roles['examples'])} requests mapped to their least roles, or reshaped"),
    ] + [(r["name"], at(ROLES_PAGE, r["name"]), prose(r["summary"])) for r in entries]

    ops = []
    for op in sorted(roles["operations"], key=lambda o: step_key(o["step"])):
        page, anchor, shown = operation_target(op)
        holders = "; ".join(f"{BY[kind]} {', '.join(who)}" for kind, who in op["roles"].items())
        how = ", with receive" if page == SDK else ""
        article = "an" if op["kind"][0] in "aeiou" else "a"
        ops.append((shown, at(page, anchor),
                    f"{op['name']}, {op['step']} {op['title']}: {article} {op['kind']}, {holders}{how}"))
    sections[f"Operations at contract {contract}"] = ops

    sections["What every plugin does"] = [
        (shown, at(page, anchor), f"{call['step']} {call['title']}, through the SDK")
        for call in roles["every_plugin"]
        for page, anchor, shown in [every_plugin_target(call)]
    ]
    sections["Building a plugin"] = [(title, at(page), description) for page, title, description in GUIDES]
    return sections


def index(roles: dict, vendored: dict, site_name: str, site_url: str, directory_urls: bool = True) -> str:
    contract = f"v{vendored['contract']}"
    out = [
        f"# {site_name}",
        "",
        f"> {site_name} is the open-source OEMS you run yourself and build on with plugins. A plugin "
        "talks only to its own sidecar, and the roles it holds, from a fixed list, decide what it may "
        "do. This index is for an agent building a plugin: the roles, the principles a plugin must fit, "
        f"the method that maps a request to the least roles, and every operation a plugin may take at contract {contract}.",
        "",
        "Roles are fixed and their grants generated: nobody can change a role's grants, not even for "
        "one plugin. Map an idea to the least roles that hold what it needs, or reshape it until it "
        "fits. Who may use a plugin is a person's read, write or admin on it, granted by a deployment "
        "admin, never a role.",
    ]
    for heading, items in index_entries(roles, vendored, site_url, directory_urls).items():
        out += ["", f"## {heading}", ""]
        out += [f"- [{text}]({address}): {description}" for text, address, description in items]
    return "\n".join(out) + "\n"


# Checking llms.txt against the built site -----------------------------------

class _Page(HTMLParser):
    """The ids a built page has, and its headings that begin with code."""

    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.code_headings: dict[str, set[str]] = {}
        self._heading: tuple[str, str] | None = None
        self._first = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag in ("h2", "h3") and attrs.get("id"):
            self._heading, self._first = (tag, attrs["id"]), True
        elif self._heading and self._first:
            if tag == "code":
                self.code_headings.setdefault(self._heading[0], set()).add(self._heading[1])
            self._first = False

    def handle_data(self, data):
        if self._heading and self._first and data.strip():
            self._first = False

    def handle_endtag(self, tag):
        if self._heading and tag == self._heading[0]:
            self._heading = None


def _built(site_dir: Path, path: str) -> Path:
    target = site_dir / path
    return target / "index.html" if path == "" or path.endswith("/") else target


LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


def check_index(text: str, site_dir: Path, site_url: str, roles: dict,
                directory_urls: bool = True) -> list[str]:
    """What is wrong with llms.txt against the built site: empty when nothing is."""
    base = site_url.rstrip("/") + "/"
    pages: dict[str, _Page | None] = {}

    def page(path: str) -> _Page | None:
        if path not in pages:
            built = _built(site_dir, path)
            if built.is_file():
                parsed = _Page()
                parsed.feed(built.read_text(encoding="utf-8"))
                pages[path] = parsed
            else:
                pages[path] = None
        return pages[path]

    errors = []
    linked: set[str] = set()
    for _, address in LINK.findall(text):
        linked.add(address)
        if not address.startswith(base):
            errors.append(f"llms.txt links {address}, which is not on {base}")
            continue
        path, _, anchor = address[len(base):].partition("#")
        built = page(path)
        if built is None:
            errors.append(f"llms.txt links {address}, a page the site does not publish")
        elif anchor and anchor not in built.ids:
            errors.append(f"llms.txt links {address}, an anchor its page does not have")

    def must_link(address: str, what: str) -> None:
        if address not in linked:
            errors.append(f"llms.txt omits {what}, published at {address}")

    roles_path = url(base, ROLES_PAGE, directory_urls=directory_urls)[len(base):]
    must_link(base + roles_path, "the roles page")
    for anchor in ("principles", "method", "examples"):
        must_link(f"{base}{roles_path}#{anchor}", f"the roles page's {anchor}")
    built_roles = page(roles_path)
    published_roles = set(built_roles.code_headings.get("h3", set())) if built_roles else set()
    for name in sorted(published_roles | {r["name"] for r in roles["roles"]}):
        must_link(f"{base}{roles_path}#{name}", f"the role {name}")

    ops_path = url(base, TYPED_OPERATIONS, directory_urls=directory_urls)[len(base):]
    built_ops = page(ops_path)
    published_ops = set(built_ops.code_headings.get("h2", set())) if built_ops else set()
    for anchor in sorted(published_ops):
        must_link(f"{base}{ops_path}#{anchor}", f"the operation {anchor}")
    for op in roles["operations"]:
        p, anchor, shown = operation_target(op)
        must_link(url(base, p, anchor, directory_urls=directory_urls), f"the operation {op['name']}")
    for call in roles["every_plugin"]:
        p, anchor, shown = every_plugin_target(call)
        must_link(url(base, p, anchor, directory_urls=directory_urls), f"{call['name']}, which every plugin makes")
    for p, title, _ in GUIDES:
        must_link(url(base, p, directory_urls=directory_urls), title)

    expected = {address for _, items in index_entries(roles, {"contract": 0}, base, directory_urls).items()
                for _, address, _ in items}
    for address in sorted(set(linked) - expected):
        errors.append(f"llms.txt links {address}, which the index does not list")
    return errors


def self_test(text: str, site_dir: Path, site_url: str, roles: dict, directory: Path,
              directory_urls: bool = True) -> list[str]:
    """Proves check_index and check_digests fail where they must."""
    failures = []
    base = site_url.rstrip("/") + "/"
    if check_index(text, site_dir, site_url, roles, directory_urls):
        failures.append("the generated llms.txt does not pass its own check")
    lines = text.splitlines()
    first_role = url(base, ROLES_PAGE, roles["roles"][0]["name"], directory_urls)
    first_op = url(base, TYPED_OPERATIONS, snake(next(
        op["name"] for op in roles["operations"] if operation_target(op)[0] == TYPED_OPERATIONS)), directory_urls)
    cases = {
        "a missing role": "\n".join(l for l in lines if f"({first_role})" not in l),
        "a missing operation": "\n".join(l for l in lines if f"({first_op})" not in l),
        "an extra link to an anchor nobody publishes":
            text + f"- [nothing]({url(base, ROLES_PAGE, 'no-such-role', directory_urls)}): nothing\n",
        "an extra link to a page nobody publishes":
            text + f"- [nothing]({url(base, 'no-such-page.md', directory_urls=directory_urls)}): nothing\n",
        "an extra link to a page the index does not list":
            text + f"- [Access]({url(base, 'concepts/access.md', directory_urls=directory_urls)}): access\n",
    }
    for case, mutated in cases.items():
        if not check_index(mutated, site_dir, site_url, roles, directory_urls):
            failures.append(f"the llms.txt check passes {case}")
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / "boundaries"
        shutil.copytree(directory, copy)
        if check_digests(copy):
            failures.append("the digest check fails the copy as it is")
        with open(copy / "roles.json", "ab") as handle:
            handle.write(b" ")
        if not check_digests(copy):
            failures.append("the digest check passes a roles.json edited by hand")
    return failures


# The MkDocs hook ------------------------------------------------------------

_state: dict = {}


def on_config(config, **kwargs):
    from mkdocs.exceptions import PluginError

    errors = check_digests(VENDORED)
    if errors:
        raise PluginError("boundaries/: " + "; ".join(errors))
    _state["roles"], _state["vendored"] = load()
    return config


def on_files(files, config, **kwargs):
    from mkdocs.exceptions import PluginError
    from mkdocs.structure.files import File

    for generated in (ROLES_PAGE, INDEX):
        if files.get_file_from_path(generated) is not None:
            raise PluginError(f"docs/{generated} is generated from boundaries/; remove the file")
    roles, vendored = _state["roles"], _state["vendored"]
    try:
        page = roles_page(roles, vendored)
        text = index(roles, vendored, config["site_name"], config["site_url"], config["use_directory_urls"])
    except (KeyError, ValueError) as err:
        raise PluginError(f"boundaries/roles.json: {err}") from err
    files.append(File.generated(config, ROLES_PAGE, content=page))
    files.append(File.generated(config, INDEX, content=text))
    return files


def on_post_build(config, **kwargs):
    from mkdocs.exceptions import PluginError

    site_dir = Path(config["site_dir"])
    text = (site_dir / INDEX).read_text(encoding="utf-8")
    roles = _state["roles"]
    directory_urls = config["use_directory_urls"]
    errors = check_index(text, site_dir, config["site_url"], roles, directory_urls)
    if not errors:
        errors = [f"self-test: {failure}" for failure in
                  self_test(text, site_dir, config["site_url"], roles, VENDORED, directory_urls)]
    if errors:
        raise PluginError("llms.txt: " + "; ".join(errors))


def on_serve(server, config, builder, **kwargs):
    server.watch(str(VENDORED))
    return server


# Refreshing the copy --------------------------------------------------------

def refresh(rev: str, contract: int, repo: str) -> None:
    if Path(repo).exists():
        repo = str(Path(repo).resolve())
    with tempfile.TemporaryDirectory() as tmp:
        def git(*args: str) -> str:
            return subprocess.run(["git", "-C", tmp, *args], check=True,
                                  capture_output=True, text=True).stdout

        git("init", "-q")
        try:
            git("fetch", "-q", "--depth", "1", repo, rev)
        except subprocess.CalledProcessError as err:
            sys.exit(f"refresh: could not fetch {rev} from {repo}: {err.stderr.strip()}")
        full = git("rev-parse", "FETCH_HEAD").strip()
        staged = Path(tmp) / "staged"
        staged.mkdir()
        for name in git("ls-tree", "--name-only", "FETCH_HEAD", "boundaries/").split():
            (staged / Path(name).name).write_bytes(subprocess.run(
                ["git", "-C", tmp, "show", f"FETCH_HEAD:{name}"], check=True, capture_output=True).stdout)
        errors = check_digests(staged)
        if errors:
            sys.exit("refresh: meridian-schema's boundaries/ at " + full + ": " + "; ".join(errors))
        VENDORED.mkdir(exist_ok=True)
        for old in VENDORED.iterdir():
            old.unlink()
        for new in staged.iterdir():
            shutil.copyfile(new, VENDORED / new.name)
        (VENDORED / "vendored.json").write_text(
            json.dumps({"schema_rev": full, "contract": contract}, indent=2) + "\n")
    print(f"boundaries/ is meridian-schema's at {full}, describing contract v{contract}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    take = commands.add_parser("refresh", help="take boundaries/ from meridian-schema at a revision")
    take.add_argument("--rev", required=True, help="a full commit or a branch of meridian-schema")
    take.add_argument("--contract", required=True, type=int,
                      help="the contract version these docs describe, as a number")
    take.add_argument("--repo", default=SCHEMA_REPO, help="meridian-schema: a URL or a local clone")
    args = parser.parse_args()
    if args.command == "refresh":
        refresh(args.rev, args.contract, args.repo)


if __name__ == "__main__":
    main()
