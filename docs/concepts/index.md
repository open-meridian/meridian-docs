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
| [Access](access.md) | How people sign in to a deployment, and how the dashboard decides what each of them may reach, per role of a plugin from contract v15; from contract v20 the access levels and account access, and a person's own settings |
| [Accounts](accounts.md) | The firm's accounts, how an account at a broker or custodian is tied to one, and from contract v20 the accounts a plugin may link to and each account's attributes in the book |
| [The book of record](the-book-of-record.md) | The firm's own record of what each account holds, how it differs from the street and the edge, and how operations opens and reconciles it |
| [The custodian's activity](the-custodians-activity.md) | What a custody plugin reports of what happened on an account, and how operations explains a break and proposes its entry from it |
| [The archive](the-archive.md) | An edge plugin's raw records: each kind's window, archived, kept or deleted past it, the deployment admin's archive, bound and holds, restore, and the record every move leaves. |
| [Instruments](instruments.md) | Instrument identity, the security master, and the copy a deployment keeps of it; from contract v19 each identifier's window, binary event contracts, and an ID never reused |
| [The lake](the-lake.md) | Where a deployment keeps what its data sources say, prices and bars, by dataset: versions, reads as of a recorded time, the source priority, wants, kept or served (contract v18); trades and quotes, streamed, caught up after a watermark, and who reads them (contract v19) |
| [Licences and entitlements](licences-and-entitlements.md) | The terms a dataset is kept on, the one-person warning, which plugins may read it and which fields, and who changed what |
| [Money and instruments](money-and-instruments.md) | Why every amount names a cash instrument, fiat and tokens alike, a code resolved by core, and the records filled in at upgrade |
| [Venues](venues.md) | The platform's venue master: a venue ID, its MIC and vendors' codes, pulled one at a time, and where a deployment names a venue |
| [Dates and time](dates-and-time.md) | Moments and plain dates, a daily price keyed by its business date, a dataset's day, and a date checked at both ends |
| [Tickets and the inbox](tickets-and-the-inbox.md) | How a problem someone sees reaches the people who can act on it: who sees a ticket, advice that changes nothing, the acts only a person takes, and the inbox |
| [Prepared changes](prepared-changes.md) | An agent or a person prepares a change and a person makes it; what agents may do with each act, set by the deployment admin and a plugin's admin; the second pair of eyes; lapse (contract v20) |
| [Service accounts](service-accounts.md) | A user of the deployment that is not a person, which a plugin's autonomous work runs as: its owner, prepare only or act, granted per role, what binds it and what is recorded (contract v21) |
| [The order lifecycle](the-order-lifecycle.md) | How an order reaches a venue through the book: who does what by role, the states and the transition table, child orders, the release gate and waiting for compliance, connectivity plugins linked to an `ems`, fills moving positions, and trading instructions (contract v22) |
| [Settlement calendars](settlement-calendars.md) | Business-day calendars and date rules the platform keeps and a deployment pulls; a settlement, spot or tenor date worked out one way in core, with its basis; coverage, and the Calendars tab (contract v22) |
| [Development deployments](development-deployments.md) | A deployment installed for writing plugins, and why a firm's own deployment is never one |

!!! note "What Open Meridian does today"
    A deployment today signs people in, administers who may reach what,
    catalogues and runs plugins, resolves instruments, records what
    custodians say is held and what happened on each account, keeps the
    firm's own book of record, reconciled with it, and takes a problem someone sees to the people who
    can act on it. From contract v18 it keeps the lake: prices and bars from data
    plugins, licensed and entitled per dataset, and the book valued from them.
    From contract v19 it adds trades and quotes, streamed, for `signal` and
    `ems` plugins. From contract v20 it adds prepared
    changes, which keep a person in the loop of an agent's work, the
    accounts a deployment admin grants each plugin, and one first-use path
    per role. From contract v21 it adds service
    accounts, which a plugin's autonomous work runs as, preparing by
    default. From contract v22 it adds the order path
    -- orders proposed, released, placed at a venue through a connectivity
    plugin and filled, their state decided by the book -- and settlement
    calendars; SnapTrade is the first connectivity plugin a deployment can
    launch, tested against a simulated brokerage only. Contract v23 adds
    venue-originated fills, which the `ems` accepts or answers DK, a
    venue's value-date roll, an event contract's outcome in the lake, and
    the lake's flag on a daily value dated on a closed day. Where a page describes something that is specified
    but not built, it says so.
