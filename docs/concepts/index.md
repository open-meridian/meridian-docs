# Concepts

These pages explain how Open Meridian is put together and why. They are not
step-by-step instructions: for those, start with
[installing a deployment](../getting-started/installation.md) and
[your first plugin](../getting-started/first-plugin.md). Read the concepts when
you want to know what a step is doing, what a setting protects, or where a
piece of data lives.

| Page | What it explains |
|---|---|
| [Architecture](architecture.md) | The two halves of Open Meridian — the platform and your deployment — what runs in each, and what crosses between them |
| [Projects and deployments](projects-and-deployments.md) | How a deployment is registered on the platform, how it proves who it is, and the one-time codes it is set up with |
| [Plugins, roles and grants](plugins.md) | What a plugin is, what it may do on the bus, how that is decided, and how people reach its pages, by Manage, Open and View |
| [Access](access.md) | How people sign in to a deployment, and how the dashboard decides what each of them may reach |
| [Accounts](accounts.md) | The firm's accounts, and how an account at a broker or custodian is tied to one |
| [Instruments](instruments.md) | Instrument identity, the security master, and the copy a deployment keeps of it |
| [Development deployments](development-deployments.md) | A deployment installed for writing plugins, and why a firm's own deployment is never one |

!!! note "What Open Meridian does today"
    A deployment today signs people in, administers who may reach what,
    catalogues and runs plugins, resolves instruments, and records what
    custodians say is held. Order routing and execution are on the roadmap and
    are not available yet. Where a page describes something that is specified
    but not built, it says so.
