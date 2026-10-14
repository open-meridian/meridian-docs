"""The Integrations page's table, from integrations/, checked against each
plugin's release.

integrations/integrations.yaml holds the page's rows by hand, one per released
plugin: the service it works with, its repository, roles, asset classes,
environments, status, version, contract and guide (status only ever
`released`: the page lists released plugins alone, and shows no status). integrations/released.json
is a snapshot of each of those plugins' main pyproject.toml -- its [project]
version, its [tool.meridian] roles and its pin of the SDK, with the contract
that SDK release declares -- and the commit each was read at.

As an MkDocs hook (mkdocs.yml, `hooks:`), at every build it

- checks every row: its fields, their allowed values, its status `released`
  and nothing else, so an unreleased plugin is never listed, and its roles, version and contract against the
  snapshot, so a row that drifts from its plugin's release fails the build;
  then proves, by a self-test, that the check fails on any other status and on
  a drifted version;
- writes the table and its filters into how-to/integrations.md where the page
  says `<!-- integrations -->`, each row's guide linking its how-to page in
  these docs or, without one, its repository's README;
- after the build, checks that every guide's anchor is on its page.

The build reads nothing from the network. From the command line, it refreshes
the snapshot:

    python tools/integrations_page.py refresh

reading each row's repository's main pyproject.toml, and the SDK's declared
contract (meridian.SCHEMA_VERSION) at the tag of each release pinned (--org
names another place the repositories are, a URL or a local directory).
"""

from __future__ import annotations

import argparse
import copy
import html
import json
import re
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "integrations"
ROWS = DATA / "integrations.yaml"
RELEASED = DATA / "released.json"
ORG = "https://github.com/open-meridian"
SDK_REPO = "meridian-python"
SDK_PACKAGE = "open-meridian"
SDK_CONSTANT = "src/meridian/client.py"

PAGE = "how-to/integrations.md"
MARKER = "<!-- integrations -->"

# Each filter group's values, in the order the page shows them, with their
# labels. A value outside its group fails the build.
ROLES = {r: r for r in ("data", "custody", "connectivity", "confirmation", "operations", "reporting")}
ASSETS = {
    "equity": "Equity",
    "fund": "Fund",
    "debt": "Debt",
    "derivative": "Derivative",
    "crypto": "Crypto",
    "event-contract": "Event contract",
    "fx": "FX",
    "cash": "Cash",
}
ENVIRONMENTS = {"sandbox": "Sandbox", "live": "Live", "sample-data": "Sample data"}
# The page lists released plugins only (the product owner, 2026-10-14), so a
# row's status must be `released` and the page shows no status column.
STATUSES = {"released": "released"}

# The page's filter groups: the query key, its legend, its values, the row
# field it reads, and whether a value no row has is left out.
GROUPS = (
    ("role", "Role", ROLES, "roles", True),
    ("asset", "Asset class", ASSETS, "assets", False),
    ("environment", "Environment", ENVIRONMENTS, "environments", True),
)

LISTS = {"roles": ROLES, "assets": ASSETS, "environments": ENVIRONMENTS}
REQUIRED = ("service", "plugin", "roles", "assets", "environments", "status", "version", "contract")
OPTIONAL = ("guide",)
PLUGIN_NAME = re.compile(r"^plugin-[a-z0-9]+(?:-[a-z0-9]+)*$")
VERSION = re.compile(r"^\d+\.\d+\.\d+$")


def repository(plugin: str) -> str:
    return f"{ORG}/{plugin}"


def load_rows(path: Path = ROWS) -> list:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or []


def load_released(path: Path = RELEASED) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# Checking the rows ----------------------------------------------------------

def check_rows(rows: list, released: dict) -> list[str]:
    """Every error in the rows, as `row: what is wrong`; none when they are
    whole and each matches its plugin's release."""
    errors: list[str] = []
    if not isinstance(rows, list) or not rows:
        return ["integrations.yaml holds no rows"]
    plugins = released.get("plugins", {})
    seen: set[str] = set()
    for number, row in enumerate(rows, 1):
        name = row.get("plugin") if isinstance(row, dict) else None
        where = f"row {number}" + (f" ({name})" if name else "")
        if not isinstance(row, dict):
            errors.append(f"{where}: not a mapping")
            continue
        for key in REQUIRED:
            if key not in row:
                errors.append(f"{where}: no {key}")
        for key in row:
            if key not in REQUIRED and key not in OPTIONAL:
                errors.append(f"{where}: unknown field {key!r}")
        if not isinstance(row.get("service", ""), str) or not str(row.get("service", "")).strip():
            errors.append(f"{where}: service must be a name")
        if name is not None:
            if not isinstance(name, str) or not PLUGIN_NAME.match(name):
                errors.append(f"{where}: plugin {name!r} is not a repository named plugin-<name>")
            elif name in seen:
                errors.append(f"{where}: {name} has a row already")
            else:
                seen.add(name)
        for key, allowed in LISTS.items():
            values = row.get(key)
            if key not in row:
                continue
            if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
                errors.append(f"{where}: {key} must be a list of names")
                continue
            if key != "assets" and not values:
                errors.append(f"{where}: {key} is empty")
            for value in values:
                if value not in allowed:
                    errors.append(f"{where}: {key} {value!r} is not one of {', '.join(allowed)}")
            if len(set(values)) != len(values):
                errors.append(f"{where}: {key} names a value twice")
        if "status" in row and row["status"] not in STATUSES:
            errors.append(f"{where}: status {row['status']!r} is not released: the page lists released plugins only")
        version = row.get("version")
        if "version" in row and not (isinstance(version, str) and VERSION.match(version)):
            errors.append(f"{where}: version {version!r} is not a quoted MAJOR.MINOR.PATCH")
        contract = row.get("contract")
        if "contract" in row and (not isinstance(contract, int) or isinstance(contract, bool)):
            errors.append(f"{where}: contract {contract!r} is not a number")
        guide = row.get("guide")
        if guide is not None and not (isinstance(guide, str) and guide.split("#")[0].endswith(".md")):
            errors.append(f"{where}: guide {guide!r} is not a page under docs/")

        # Against the plugin's release.
        if not isinstance(name, str):
            continue
        release = plugins.get(name)
        if release is None:
            errors.append(f"{where}: not in released.json; run `python tools/integrations_page.py refresh`")
            continue
        if isinstance(row.get("roles"), list) and set(row["roles"]) != set(release["roles"]):
            errors.append(f"{where}: roles {row['roles']} are not the release's {release['roles']} "
                          f"([tool.meridian] roles at {release['commit'][:7]})")
        if "version" in row and version != release["version"]:
            errors.append(f"{where}: version {version} is not the release's {release['version']} "
                          f"([project] version at {release['commit'][:7]})")
        if "contract" in row and contract != release["contract"]:
            errors.append(f"{where}: contract {contract} is not the release's {release['contract']} "
                          f"(the contract {SDK_PACKAGE}=={release['sdk']} declares)")
    for name in plugins:
        if name not in seen:
            errors.append(f"{name}: in released.json with no row; add its row, or refresh")
    return errors


def self_test(rows: list, released: dict) -> list[str]:
    """That the check fails where it must: on a status other than released,
    and on a version that is not the release's."""
    failures = []
    bad_status = copy.deepcopy(rows)
    bad_status[0]["status"] = "preview"
    if not any("status" in e for e in check_rows(bad_status, released)):
        failures.append("a status of 'preview' passed")
    drifted = copy.deepcopy(rows)
    drifted[0]["version"] = "999.0.0"
    if not any("version" in e for e in check_rows(drifted, released)):
        failures.append("a version the release does not have passed")
    return failures


# Writing the table ----------------------------------------------------------

def _e(text: str) -> str:
    return html.escape(str(text), quote=True)


def filters(rows: list) -> str:
    groups = []
    for key, legend, values, field, only_present in GROUPS:
        present = set()
        for row in rows:
            held = row[field]
            present.update(held if isinstance(held, list) else [held])
        boxes = "".join(
            f'<label class="om-filter"><input type="checkbox" name="{key}" value="{_e(value)}">'
            f"<span>{_e(label)}</span></label>"
            for value, label in values.items() if value in present or not only_present)
        groups.append(f'<fieldset class="om-integrations__group"><legend>{_e(legend)}</legend>'
                      f"{boxes}</fieldset>")
    return (
        '<form class="om-integrations__filters" aria-label="Filter the plugins" hidden>'
        + "".join(groups)
        + '<div class="om-integrations__summary">'
        '<p class="om-integrations__count" role="status" aria-live="polite"></p>'
        '<button type="button" class="md-button om-integrations__clear">Clear filters</button>'
        "</div></form>"
    )


def guide_link(row: dict, page_file, files) -> str:
    guide = row.get("guide")
    if guide is None:
        return f'<a href="{_e(repository(row["plugin"]))}#readme">README</a>'
    path, _, anchor = guide.partition("#")
    target = files.get_file_from_path(path)
    href = target.url_relative_to(page_file) + (f"#{anchor}" if anchor else "")
    return f'<a href="{_e(href)}">Guide</a>'


def table(rows: list, page_file, files) -> str:
    head = ("Works with", "Plugin", "Roles", "Asset classes", "Environments", "Version",
            "Guide")
    body = []
    for row in sorted(rows, key=lambda r: r["service"].casefold()):
        roles = [r for r in ROLES if r in row["roles"]]
        assets = [a for a in ASSETS if a in row["assets"]]
        environments = [e for e in ENVIRONMENTS if e in row["environments"]]
        data = (f' data-role="{_e(" ".join(roles))}" data-asset="{_e(" ".join(assets))}"'
                f' data-environment="{_e(" ".join(environments))}"')
        cells = (
            _e(row["service"]),
            f'<a class="om-nowrap" href="{_e(repository(row["plugin"]))}">{_e(row["plugin"])}</a>',
            " ".join(f"<code>{_e(r)}</code>" for r in roles),
            _e(", ".join(ASSETS[a] for a in assets)) or "&mdash;",
            _e(", ".join(ENVIRONMENTS[e] for e in environments)),
            f'<span class="om-nowrap">{_e(row["version"])}</span> '
            f'<span class="om-nowrap">on v{_e(row["contract"])}</span>',
            guide_link(row, page_file, files),
        )
        body.append(f"<tr{data}>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
    return (
        '<div class="om-integrations__table"><table>'
        "<thead><tr>" + "".join(f"<th>{_e(h)}</th>" for h in head) + "</tr></thead>"
        "<tbody>" + "".join(body) + "</tbody></table></div>"
    )


def block(rows: list, page_file, files) -> str:
    return (
        f'<div class="om-integrations" id="om-integrations" data-total="{len(rows)}">'
        + filters(rows)
        + table(rows, page_file, files)
        + '<p class="om-integrations__empty" hidden>No plugin matches all of these filters. '
        'Clear one, or request a plugin below.</p>'
        "</div>"
    )


# The MkDocs hook ------------------------------------------------------------

_state: dict = {}


def on_config(config, **kwargs):
    from mkdocs.exceptions import PluginError

    try:
        rows, released = load_rows(), load_released()
    except (OSError, ValueError, yaml.YAMLError) as err:
        raise PluginError(f"integrations/: {err}") from err
    errors = check_rows(rows, released)
    if not errors:
        errors = [f"self-test: {failure}" for failure in self_test(rows, released)]
    if errors:
        raise PluginError("integrations/: " + "; ".join(errors))
    _state["rows"] = rows
    return config


def on_files(files, config, **kwargs):
    from mkdocs.exceptions import PluginError

    errors = []
    if files.get_file_from_path(PAGE) is None:
        errors.append(f"docs/{PAGE} is missing")
    for row in _state["rows"]:
        guide = row.get("guide")
        if guide is not None and files.get_file_from_path(guide.split("#")[0]) is None:
            errors.append(f"{row['plugin']}: guide docs/{guide.split('#')[0]} is not a page")
    if errors:
        raise PluginError("integrations/: " + "; ".join(errors))
    return files


def on_page_markdown(markdown, page, config, files, **kwargs):
    from mkdocs.exceptions import PluginError

    if page.file.src_uri != PAGE:
        if MARKER in markdown:
            raise PluginError(f"docs/{page.file.src_uri}: {MARKER} belongs on docs/{PAGE} alone")
        return markdown
    if markdown.count(MARKER) != 1:
        raise PluginError(f"docs/{PAGE}: says {MARKER} {markdown.count(MARKER)} times, not once")
    return markdown.replace(MARKER, block(_state["rows"], page.file, files))


def on_post_build(config, **kwargs):
    from mkdocs.exceptions import PluginError
    from mkdocs.structure.files import File

    site_dir = Path(config["site_dir"])
    errors = []
    for row in _state["rows"]:
        path, _, anchor = (row.get("guide") or "").partition("#")
        if not anchor:
            continue
        built = File(path, config["docs_dir"], config["site_dir"], config["use_directory_urls"])
        text = (site_dir / built.dest_uri).read_text(encoding="utf-8")
        if f'id="{anchor}"' not in text:
            errors.append(f"{row['plugin']}: docs/{path} has no #{anchor}")
    if errors:
        raise PluginError("integrations/: " + "; ".join(errors))


def on_serve(server, config, builder, **kwargs):
    server.watch(str(DATA))
    return server


# Refreshing the snapshot ----------------------------------------------------

def _source(org: str, name: str) -> str:
    local = Path(org) / name
    if local.exists():
        return str(local.resolve())
    return f"{org.rstrip('/')}/{name}.git"


def _sdk_pin(dependencies: list[str], plugin: str) -> str:
    for dependency in dependencies:
        match = re.fullmatch(rf"\s*{re.escape(SDK_PACKAGE)}\s*==\s*(\d+\.\d+\.\d+)\s*", dependency)
        if match:
            return match.group(1)
    sys.exit(f"refresh: {plugin}'s main pins no {SDK_PACKAGE}==<version>")


def refresh(org: str) -> None:
    plugins: dict[str, dict] = {}
    sdks: dict[str, dict] = {}
    with tempfile.TemporaryDirectory() as tmp:
        def git(*args: str) -> str:
            return subprocess.run(["git", "-C", tmp, *args], check=True,
                                  capture_output=True, text=True).stdout

        def fetch(source: str, ref: str, what: str) -> tuple[str, str]:
            try:
                git("fetch", "-q", "--depth", "1", source, ref)
            except subprocess.CalledProcessError as err:
                sys.exit(f"refresh: could not fetch {ref} of {source}: {err.stderr.strip()}")
            return git("rev-parse", "FETCH_HEAD^{commit}").strip(), git("show", f"FETCH_HEAD:{what}")

        git("init", "-q")
        for row in load_rows():
            name = row["plugin"]
            commit, text = fetch(_source(org, name), "main", "pyproject.toml")
            project = tomllib.loads(text)
            meridian = project.get("tool", {}).get("meridian", {})
            plugins[name] = {
                "commit": commit,
                "version": project["project"]["version"],
                "roles": list(meridian.get("roles", [])),
                "sdk": _sdk_pin(project["project"].get("dependencies", []), name),
            }
        for pin in sorted({p["sdk"] for p in plugins.values()}, key=lambda v: tuple(map(int, v.split(".")))):
            commit, text = fetch(_source(org, SDK_REPO), f"refs/tags/v{pin}", SDK_CONSTANT)
            match = re.search(r'^SCHEMA_VERSION\s*=\s*"v(\d+)"', text, re.MULTILINE)
            if not match:
                sys.exit(f"refresh: {SDK_REPO} v{pin}'s {SDK_CONSTANT} declares no SCHEMA_VERSION")
            sdks[pin] = {"commit": commit, "contract": int(match.group(1))}
    for release in plugins.values():
        release["contract"] = sdks[release["sdk"]]["contract"]
    RELEASED.write_text(json.dumps({
        "refreshed_by": "python tools/integrations_page.py refresh",
        "plugins": plugins,
        "sdk": sdks,
    }, indent=2) + "\n", encoding="utf-8")
    for name, release in plugins.items():
        print(f"{name} {release['version']} at {release['commit'][:7]}: "
              f"{', '.join(release['roles'])}; {SDK_PACKAGE}=={release['sdk']}, contract v{release['contract']}")
    errors = check_rows(load_rows(), load_released())
    if errors:
        print("integrations.yaml now differs from the releases:\n  " + "\n  ".join(errors))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    take = commands.add_parser("refresh", help="read each row's plugin release into integrations/released.json")
    take.add_argument("--org", default=ORG,
                      help="where the repositories are: a URL, or a local directory of clones")
    args = parser.parse_args()
    if args.command == "refresh":
        refresh(args.org)


if __name__ == "__main__":
    main()
