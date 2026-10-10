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
| [Plan your deployment](plan-your-deployment.md) | A firm's profile answered in three layers — core as its books and records, plugins by role, configuration — with what exists, what is planned and what to build, worked for three firms |
| [Projects and deployments](projects-and-deployments.md) | How a deployment is registered on the platform, how it proves who it is, and the one-time codes it is set up with |
| [Plugins, roles and grants](plugins.md) | What a plugin is, what it may do on the bus, how that is decided, and how people reach its pages, by Manage, Open and View |
| [Roles](roles.md) | Each of the thirteen roles: its persona, duties, what it leaves to another role and what it holds; the principles a plugin must fit, and how an idea maps to the least roles |
| [Access](access.md) | How people sign in to a deployment, and how the dashboard decides what each of them may reach, per role of a plugin from contract v15 |
| [Accounts](accounts.md) | The firm's accounts, and how an account at a broker or custodian is tied to one |
| [The book of record](the-book-of-record.md) | The firm's own record of what each account holds, how it differs from the street and the edge, and how operations opens and reconciles it |
| [The custodian's activity](the-custodians-activity.md) | What a custody plugin reports of what happened on an account, and how operations explains a break and proposes its entry from it |
| [The archive](the-archive.md) | An edge plugin's raw records: each kind's window, archived, kept or deleted past it, the deployment admin's archive, bound and holds, restore, and the record every move leaves. |
| [Instruments](instruments.md) | Instrument identity, the security master, and the copy a deployment keeps of it |
| [The lake](the-lake.md) | Where a deployment keeps what its data sources say, prices and bars, by dataset: versions, reads as of a recorded time, the source priority, wants, kept or served (contract v18, built, not released) |
| [Licences and entitlements](licences-and-entitlements.md) | The terms a dataset is kept on, the one-person warning, which plugins may read it and which fields, and who changed what |
| [Money and instruments](money-and-instruments.md) | Why every amount names a cash instrument, fiat and tokens alike, a code resolved by core, and the records filled in at upgrade |
| [Venues](venues.md) | The platform's venue master: a venue ID, its MIC and vendors' codes, pulled one at a time, and where a deployment names a venue |
| [Dates and time](dates-and-time.md) | Moments and plain dates, a daily price keyed by its business date, a dataset's day, and a date checked at both ends |
| [Tickets and the inbox](tickets-and-the-inbox.md) | How a problem someone sees reaches the people who can act on it: who sees a ticket, advice that changes nothing, the acts only a person takes, and the inbox |
| [Development deployments](development-deployments.md) | A deployment installed for writing plugins, and why a firm's own deployment is never one |

!!! note "What Open Meridian does today"
    A deployment today signs people in, administers who may reach what,
    catalogues and runs plugins, resolves instruments, records what
    custodians say is held and what happened on each account, keeps the
    firm's own book of record, reconciled with it, and takes a problem someone sees to the people who
    can act on it. Contract v18, built and not yet released, adds the lake: prices and bars from data
    plugins, licensed and entitled per dataset. Order routing and execution are on the roadmap and
    are not available yet. Where a page describes something that is specified
    but not built, it says so.
