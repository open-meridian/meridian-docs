# Contributing

This page is for working on Open Meridian's public repositories: meridian-core,
meridian-cli, meridian-python, meridian-schema, meridian-ui, meridian-snaptrade and meridian-docs. It
covers how each is checked, the rules every change keeps, and how to raise a bug or an idea.

!!! note "Issues, not pull requests"
    Open Meridian is open source, and built by its team: we don't merge pull
    requests from outside it. To help, open an issue on the repository --
    **Report a bug** or **Suggest an improvement** -- and describe the problem
    or the idea rather than pasting code; we build every change ourselves.
    Opening an issue gives Societal Lab Inc. a perpetual, irrevocable,
    royalty-free licence to use what you suggest, as each repository's
    `CONTRIBUTING.md` says. Plugins, which live in your own repositories, are
    the way to build on Open Meridian.

## The gate: `make ci-local`

Every public code repository has one command that runs every check it has:

```bash
make ci-local
```

This site, meridian-docs, is checked by `mkdocs build --strict`, which fails on a broken link.

**A green local run is the completion signal.** CI is confirmation, not the
place a failure is first discovered: every job CI runs is reachable from
`ci-local`, so nothing fails there that could not have failed on your machine.

On a fresh clone, run this once:

```bash
make install-hooks
```

It points git at the repository's hooks, so `git push` runs `make ci-local`
first. Without it the gate exists and does not run. In meridian-core, a change
touching a Dockerfile, a lock file, a CI workflow or a `.proto` is promoted to
the longer `ci-local-deep` automatically.

The toolchains are pinned inside containers, so Docker is the only thing the
host needs. A host `protoc` or Rust toolchain at a different version would
produce subtly different output, so the host is never asked to have one.

| Repository | Also useful |
|---|---|
| meridian-core | `docker compose up` runs every component locally, with a database and a broker |
| meridian-schema | `make codegen` regenerates the Rust and Python bindings, in a pinned container |
| meridian-python | Conformance tests assert against the same pinned message bytes as the Rust runtime, so the two agree with the contract rather than with each other |
| meridian-ui | `make serve` serves the kit's gallery, every component light and dark, in each scheme |
| meridian-snaptrade | `make preview` writes each of its pages on synthetic data |

## Rules every change keeps

These are enforced in review, and several by the gate.

**Exact decimal for money.** Never floating point for a quantity, a price or a
balance, at any layer — including an adapter reading a third-party API.
Quantities and money cross the wire as an integer and the scale they were
stated with; in the Python SDK they are `Decimal`, and a value that cannot be
carried exactly is refused rather than rounded. Convert once, at the boundary, on the way in. This is the
class of code where a rounding error becomes a reconciliation break.

**Plugins hold no state.** No local database, no file a plugin expects to find
again. A plugin can be killed and replaced at any moment and seeds from the
deployment when it starts.

**A plugin talks only to its sidecar.** Access control, encoding, health and
lifecycle live in the sidecar, once. The SDK is a thin client for it: anything
added to the SDK must be a convenience, never a decision, because a decision
made in the SDK is made once per plugin and wrong in a different way each
time.

**Typed operations are generated, never hand-written.** The typed methods a
plugin's roles may call are derived from Open Meridian's contract. Generate
them, or do not have them yet.

**Generated files are never edited by hand.** They are committed and reviewed
like any other code, and `make check-codegen` regenerates them into a scratch
directory and fails on any difference.

**No third-party data models in the kernel.** The deployment's own core defines
its own types. External standards are translated at the plugin boundary.

**A plugin never creates reference data.** When an instrument does not
resolve, a plugin reports the miss and moves on; it does not block, retry in a
loop, or mint an instrument. See [Instruments](../concepts/instruments.md).

**Resolution is dated.** Ask what an identifier meant on a date. An undated
lookup is a bug waiting for the day an identifier is reassigned.

**Credentials come from the environment.** Never a literal, never a fixture,
never a committed configuration file.

## The contract changes only when a workflow demands it

Every message in meridian-schema, and every domain message in meridian-core's
`proto/`, exists because a written workflow step needs it. Nothing enters the
contract ahead of that, and the gates fail a message that nothing justifies.

So a change to a `.proto`, or anything that would change what a plugin may
send or receive, is not an ordinary pull request. Open an issue describing
what a plugin or a person needs to do and cannot; the contract follows from
that, not the other way round.

## Licences, and why a plugin stays yours

meridian-core and meridian-cli are AGPL-3.0-or-later. meridian-python,
meridian-schema and meridian-ui are **Apache-2.0**. A plugin links only the SDK and the
contract — it talks to nothing but its sidecar — so a plugin you write on them
stays yours, whatever licence you choose for it. Keep that line where it is: a
change that would make a plugin link anything AGPL is a change to that promise.
See [Repositories](repositories.md).

## Review

Every pull request gets the same review passes in the same order, whether a
person or an AI agent wrote it: correctness first, then security, then whether
it respects the contract, then whether it matches what it set out to do.
Formatting, link checks and code generation are left to `make ci-local`, not to
reviewers; a thing a reviewer catches that a gate could have caught is a
missing gate.
