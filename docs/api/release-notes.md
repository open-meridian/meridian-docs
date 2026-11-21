# Release notes

What each release changed, newest first. The other pages describe the current release.

## The Python SDK { #the-python-sdk }

Each release of the SDK, the interface version it declares, the runtime it needs, and the CLI whose `plugin new` writes a plugin on it. What a plugin's author does to move to it is in [Moving a plugin to a new release](python-sdk.md#moving-a-plugin-to-a-new-release).

!!! note "0.37.1: a fix"
    open-meridian 0.37.1 is a fix: a raw record kept from two threads at
    once waits its turn, so no stream message is dropped. 0.37.0 refused a
    second thread's `RawStore.keep_line` at once, and the message was lost.
    A `keep_line`, `keep` or `tend` while another thread is in `keep_line`
    now waits, the wait for the thread and for another pod's lock sharing
    two seconds, then raises `TimeoutError` with nothing written; `keep`,
    `tend` and `get` never close a file another thread is writing (see
    [`edge.storage_dir()`](python-sdk.md#instance_storage_dir)). Nothing a plugin calls
    changed: `meridian plugin migrate` moves only the pins. Base image
    `ghcr.io/open-meridian/plugin-python:0.37.1`; chart 0.1.632.

!!! note "0.37.0: breaking"
    open-meridian 0.37.0 keeps interface version `"v30"` and runs a plugin
    [as shards or with a standby pod](../how-to/run-a-plugin-as-shards-or-with-a-standby.md).
    [`meridian.run`](python-sdk.md#run) waits for its sidecar for as long as it takes,
    and when the sidecar is lost after the plugin registered, restarted on
    its own or its shard taken over, stops the role classes and waits in the
    same process to be registered again, then starts them afresh. A 0.36
    plugin is never registered again after its sidecar restarts on its own,
    so move every plugin to 0.37.0. Adds storage per shard
    ([`edge.storage_dir()`](python-sdk.md#instance_storage_dir), the shard's own folder
    once registered, and `edge.instance_storage_dir()`, the whole); a
    placement sent at most once across a takeover, each noted as a file of
    its own, `trading/sent/<pid>`; a charge reported under its key
    (`report_charge`'s `idempotency_key`); an archive's bucket asked before
    each registration; and `meridian-storage`, the command the deployment
    copies an instance's storage with, on the base image's `PATH`. Breaking:
    `edge.storage_dir()` read before the plugin registers, on storage an
    instance's pods share, raises `RuntimeError`; a connectivity instance
    run as shards or with a standby pod sends no placement until it is
    granted storage; and a connectivity instance is never rolled back below
    0.37.0, since an earlier release would send again what 0.37.0 noted.
    Base image `ghcr.io/open-meridian/plugin-python:0.37.0`; chart 0.1.632;
    CLI 0.1.61's `plugin new` writes 0.35.0, which `meridian plugin migrate`
    moves to it. See [0.36.3 to 0.37.0](python-sdk.md#0363-to-0370).

!!! note "0.36.3: a fix and an addition"
    open-meridian 0.36.3 makes `option_chains.SeriesTimes` public, the
    holder of each option series' first valid time and first subject that
    `option_chains.Feed` is built on, for a plugin running a chain of its
    own: it decides each series' row and sends the rows in the lake's
    batches, taking a refusal of a series' own valid time as recorded. A
    `Feed` whose calendar names no day keeps New York's. Base image
    `ghcr.io/open-meridian/plugin-python:0.36.3`; chart 0.1.538.

!!! note "0.36.2: fixes"
    open-meridian 0.36.2 keeps each row key's first valid time in the SDK's
    helpers: `helpers.chains.statistic` is valid from the start of the day
    it describes; `helpers.chains.option_series` keeps a series' terms
    under their key's first valid time, an adjustment a new key from its
    date (`adjusted_on`); `option_chains.Feed` holds each series' first
    valid time, in the plugin's storage where it is given `series_path`. An
    event contract's outcome keeps its first determination's valid time,
    and a listings feed's withdrawal of a trade keeps the trade's. Base
    image `ghcr.io/open-meridian/plugin-python:0.36.2`; chart 0.1.538.

!!! note "0.36.1: fixes"
    open-meridian 0.36.1: an event-contract feed states a payout in a
    venue's own token by the token's instrument once its record is held,
    and by its category before then, where 0.36.0 refused it, and states a
    range market's bounds only with their unit. `EventContractsChecks`
    admits a plugin asking for a contract's own event and its series by
    reference. Base image `ghcr.io/open-meridian/plugin-python:0.36.1`;
    chart 0.1.538.

!!! note "0.36.0: breaking"
    open-meridian 0.36.0 declares a new interface version (`SCHEMA_VERSION`
    `"v30"`) and needs chart 0.1.538. Adds
    [standing jobs](../concepts/the-analytics-component.md#a-standing-job)
    (`analytics.job(..., standing=True)`, each measure's `refresh`,
    `analytics.Jobs().standing` answering a `LiveView`); a stream held to
    its far end (`receive.QUIET_SECONDS`); an act or read refused for load
    asked again after its retry-after (`client.load_wait`); a dataset's
    `terms_and_pricing`, `sessions_calendar_id` and `gap_recovery`, and
    `Declaration(most_shards=)`; an event contract's terms and category
    stated at its resolve; a bond's terms offered as a value of its record
    and a quoted yield whose day count is unstated; the `benchmark_yield`
    rate kind; and the source priorities read. `DatasetLicence`,
    `DataEligibility` and `licence_default` are gone. Base image
    `ghcr.io/open-meridian/plugin-python:0.36.0`; CLI 0.1.60's `plugin new`
    writes 0.35.0, which `meridian plugin migrate` moves to it. See
    [0.35.5 to 0.36.0](python-sdk.md#0355-to-0360).

!!! note "0.35.5: additive"
    open-meridian 0.35.5 holds the FX week once:
    [`helpers.sessions.FX_WEEK`](python-sdk.md#helpers), Sunday 17:00 to Friday 17:00
    New York, for wherever sessions are taken and an FX dataset names no
    calendar of its own. The base template links kit 0.16.0 (`pages.KIT`),
    whose `<om-live cells>` draws a page's [live values](python-sdk.md#live-values).
    Base image `ghcr.io/open-meridian/plugin-python:0.35.5`; chart 0.1.408.

!!! note "0.35.4: a fix and an addition"
    A book record's view is keyed by its entity (`views.ENTITY_KEYS`), so an
    order whose venue's ID is set later is held once. A quote stating no
    source time is timed by its `valid_from_ns`, so `ems.ReferenceCheck` no
    longer judges it stale. Adds [live values](python-sdk.md#live-values),
    `pages.live_values` and `LiveValue.of`: a page's values worked out from
    its views, with source, age and staleness counted only in session.

!!! note "0.35.3: a fix"
    A supervised session hands `heard` every message, `[]` for a heartbeat,
    waits at least a failure's `retry_after`, and with
    `reopen_on_want=True` opens a new session for what is wanted. A rate or a
    statistic delivered latest value first no longer fails the hearing
    loop, and a chain's rows are told apart by their series key.
    `RawStore.tend` reads from the settings only what it is not given. A
    pricing plugin declares its models,
    `Declaration(pricing_models=[PricingModelDeclaration(model_id, model_version)])`.

!!! note "0.35.2: a fix"
    A typed delivery of the settings holds every setting delivered in
    `config.values`, the storage kinds' window settings among them, and
    `RawStore.tend(plugin, settings=config, today=...)` reads a kind's
    window from it.

!!! note "0.35.1: a fix"
    An act is made through the role object, never the connection: the pairs
    and event-contract feeds resolve their venue through the feed. The
    suites' `Recorder.plugin` stands in for the connection and makes no act.
    `meridian.run` applies the first settings before any class's `on_start`
    and keeps the settings watch.

!!! note "0.35.0: breaking"
    [Each role is one class](python-sdk.md#role-classes), `meridian.roles.<role>.Role`,
    its acts methods and its events `on_<event>` methods; seven role modules
    added (`compliance`, `confirmation`, `oms`, `portfolio`, `reference`,
    `servicing`, `settlement`). [`meridian.run`](python-sdk.md#run) is the entry point,
    `connect(roles=)` requires the classes, the connection makes no act, and
    `receive` is gone. `connectivity.Trader`, `pricing.Pricer` and the data
    feeds are role classes. Adds `meridian.helpers.sessions` and
    `.calendars`, `data.SentRows`, `Conflator`, `Timetable`, `timeliness`,
    `api_key` and `data.option_chains`. No contract change. See
    [0.34.0 to 0.35.0](python-sdk.md#0340-to-0350).

!!! note "0.34.0: breaking"
    Adds [bonds and fixed income](../concepts/bonds-and-fixed-income.md):
    the money rules, accrual and factors (`helpers.debt`), the bond records
    and servicing's expectations (`helpers.lifecycle`),
    `analytics.DEBT_MEASURES`, a quality assessment's data type and a derived
    value in money. `meridian.roles` holds only roles: `chains`,
    `packages`, `lifecycle` and `debt` moved to [`meridian.helpers`](python-sdk.md#helpers)
    with no shim. See [0.33.5 to 0.34.0](python-sdk.md#0335-to-0340).

!!! note "0.33.2 to 0.33.5: additive"
    Reads ask for what a page shows (`paths`, `fields`, an expiration
    window); `chains.read_expirations` from the typed `list_expirations`;
    `RawStore.keep_line` keeps a stream's memory flat; and
    [views](python-sdk.md#live-values), `plugin.subscribe` and `pages.live`, with each
    dataset's class of source.

!!! note "0.33.1: additive"
    open-meridian 0.33.1 adds an event-contract venue's bars. A `Market`
    answering `bars(contract, interval, first_ns, until_ns)` -- each
    `Candle` of an hour (`HOUR`) or the venue's session day (`DAY`) --
    publishes a third dataset keyed `bars`, of the lake's bar kind, and
    `Feed.keep_bars(declared)` keeps each served contract's closed hours and
    days; a want of `bars` is answered from the venue's history. A `Market`
    without the hook is unchanged, and `EventContractsChecks` refuse any
    third dataset but `bars`. The data suite's feed-delay producer stands
    its want on the quote where the venue's last trade states no time or
    its live dataset declares no prices, and a row's interval and business
    date are part of what makes it a duplicate. Base image
    `ghcr.io/open-meridian/plugin-python:0.33.1`; runtime chart 0.1.313 or
    later.

!!! note "0.33.0"
    Breaking: the typed
    operations take `meridian.SubjectRef` only, which carries its role
    (`role=`), and refuse the wire's; every role's suite holds v28's cases,
    each case about what a plugin's source or work may never present marked
    by its `about`; and the three latency cases are required again.
    `Latency.report` sends `ReportLatency`, and an `ems`'s
    `ReferenceCheck.permitted` reads the stale-reference actions the
    deployment permits. Listed options and futures: chains, lifecycle
    events and package orders (`meridian.roles.chains`, `.lifecycle`,
    `.packages`); a signal's derived series, saved scenarios and a row's
    quality escalated (`meridian.roles.signal`); the filings slice
    (`meridian.roles.data.filings`); quality states at the edge
    (`meridian.roles.data.quality`); a licence's eligibility
    (`DataEligibility`). `meridian plugin migrate` rewrites a wire
    `SubjectRef` handed to the SDK (see [0.32.3 to 0.33.0](python-sdk.md#0323-to-0330)).
    It needs a deployment (chart 0.1.313 or later). CLI 0.1.53's
    `plugin new` writes a plugin on it. Its base image is
    `ghcr.io/open-meridian/plugin-python:0.33.0`.

!!! note "0.32.3: a rate's convention, listings' liveness, the not-affiliated notice"
    open-meridian 0.32.3, released on PyPI on 2026-10-24, needs chart 0.1.309 or later, as 0.32.0 does. `rates.Feed.rate` refuses a rate with no
    convention, an index level taking the convention of the rate it
    compounds, and `Feed.subject` asks a subject missed again the same day,
    after 5, then 15, then every 60 minutes. A listings feed records its
    live dataset's liveness, as a pairs feed does. An event contract's
    `Resolution` carries the venue's deadline to challenge a determination
    (`challenge_ends_at_ns`) to the `Outcome`. `DatasetLicence` writes
    `not_affiliated_notice`. The merged Connection (`connection_pages`)
    draws one group at a time under a tab row of its sections' titles, and
    Raw records' record wraps within its box. Set the licence's attribution
    terms only on chart 0.1.311 or later. Only the pins move, but a rate
    built with no convention now raises (see
    [0.32.2 to 0.32.3](python-sdk.md#0322-to-0323)). CLI 0.1.52's `plugin new` writes a
    plugin on 0.32.1, and `plugin migrate` moves it here. Its base image is
    `ghcr.io/open-meridian/plugin-python:0.32.3`
    (`sha256:596236b9c7e2a2e324f7704df68551a311d1a1ce9387ec6d5bd4d7ba661674f3`).

!!! note "0.32.2: the licence's attribution terms, Sessions only once measured"
    open-meridian 0.32.2, released on PyPI on 2026-10-23, needs chart 0.1.309 or later, as 0.32.0 does. `DatasetLicence` writes the v27 wire's
    `redistribution`, `attribution_required`, `attribution_text`,
    `copyright_class` and `no_more_restrictive_terms`, an answer given by
    its word, with or without its prefix. A data plugin's Connection draws
    **Sessions** only once a session is measured. The testing `Recorder`
    answers `RecordRates` with its count. `RATES_NOT_PRESENTED` no longer
    names `records-a-datasets-liveness`: a polled rates plugin recording
    each poll as its dataset's liveness presents it. Set the licence's new
    terms only on chart 0.1.311 or later: an earlier v27 deployment refuses
    the registration. Only the pins move (see
    [0.32.1 to 0.32.2](python-sdk.md#0321-to-0322)). CLI 0.1.52's `plugin new` writes a
    plugin on 0.32.1, and `plugin migrate` moves it here. Its base image is
    `ghcr.io/open-meridian/plugin-python:0.32.2`
    (`sha256:2235d96dcca58e315dbb9d38fe9dda753d1a4bfbcac67b09f614b07d54020b80`).

!!! note "0.32.1: two data cases about closes"
    open-meridian 0.32.1, released on PyPI on 2026-10-23, needs chart 0.1.309 or later, as 0.32.0 does. The data suite's `an-exact-price` and
    `a-want-recorded-against` are about `closes`, so a data plugin
    recording rates and no prices names them not presented, with why: "it
    records rates, never prices". `meridian.roles.data.testing.RATES_NOT_PRESENTED`
    names every case such a plugin never presents. A plugin recording
    prices maps them as before. Only the pins move (see
    [0.32.0 to 0.32.1](python-sdk.md#0320-to-0321)). CLI 0.1.52's `plugin new` writes a
    plugin on it. Its base image is
    `ghcr.io/open-meridian/plugin-python:0.32.1`
    (`sha256:92f58ed38f475a50a6ca4f28c90e70b30d5f9c4528541d1720045ca09a70db9f`).

!!! note "0.32.0"
    open-meridian 0.32.0, released on PyPI on 2026-10-22, needs chart 0.1.309 or later: the analytics component's `pnl` version 2, realized P&L
    beside unrealized (`analytics.measure("pnl", 2)`), and
    `execution_cost`; a job's business date and reporting currency
    (`analytics.job(..., business_date=, reporting_currency=)`), and a job
    with no account refused as it is built; the reference computations'
    18-place rounding of a quoted price per unit, inverted and crossed fiat
    legs, and each position's input price and each conversion leg in the
    provenance. The lake's rates (`meridian.roles.data.rates`); latency
    recorded (`roles.Latency`) and not yet reported, since core receives
    `ReportLatency`; a dataset's liveness (`Wants.liveness`,
    `roles.Liveness`) and declared delay; the settings for session
    ceilings, dataset thresholds and the stale-reference action; an `ems`'s
    reference check (`roles.ems.ReferenceCheck`) and an RFQ placement's
    quotes (`roles.ems.open_quotes`); a connectivity `Trader`'s placement
    types and RFQs (`VenueQuote`); connectivity's pages declared by the SDK
    (`connectivity.trading_pages`, `connection_pages`, `raw_records_page`);
    and an event-contract venue's events kept (`Feed.keep_events`) with a
    range member's bounds. A `DatasetLicence` writes both `derived_use` and
    `derived_use_terms`. Its typed operations are in
    [RFQ quotes](typed-operations.md#rfq-costs-rates-and-liveness).
    Breaking: every role's suite holds new cases a plugin's suite test must
    map (see [0.31.1 to 0.32.0](python-sdk.md#0311-to-0320)). It needs a runtime on chart 0.1.309 or later. CLI 0.1.51's `plugin new` writes
    a plugin on it. Its base image is
    `ghcr.io/open-meridian/plugin-python:0.32.0`
    (`sha256:8ea1713eb354d7cadcf2f83ee0903d9ed2d157c3f49c1036a65ce7dccd53b5cd`).

!!! note "0.31.1: refused settings, the pricing template without storage"
    open-meridian 0.31.1, released on PyPI on 2026-10-19, needs chart 0.1.308 or later, as 0.31.0 does. A saved setting value that is no longer one of its
    choices, or not of its kind, is delivered unset and listed in
    `Settings.refused` (`meridian.RefusedSetting`), never raised and never
    mapped to another value (see [`Settings`](python-sdk.md#settings)). An
    event-contract venue's contract map keeps a range market's bounds, and
    `event_contracts.Feed.stated_identifiers`, by which
    `EventContractsChecks` holds a record complete, is public. The pricing
    template declares no storage, since `pricing` is no edge role; every
    template's `AGENTS.md` says how a version is published to a registry,
    and its pre-push hook says a tag push runs nothing. Only the pins move
    (see [0.31.0 to 0.31.1](python-sdk.md#0310-to-0311)). CLI 0.1.50's `plugin new`
    writes a plugin on it. Its base image is
    `ghcr.io/open-meridian/plugin-python:0.31.1`
    (`sha256:67781f140800652d7b8052f685355738901cd7f8dab20c13473c2142a3535b39`).

!!! note "0.31.0"
    open-meridian 0.31.0, released on PyPI on 2026-10-19, needs chart 0.1.308 or later: the analytics component, asked through
    `meridian.analytics` (a job's typed builders, its answer and every
    figure with how it was computed, and a job answered later caught up by
    sequence), with the reference computations its engine equals exactly;
    the `pricing` role, `meridian.roles.pricing.Pricer`, and its template;
    event groups (`meridian.EventGroups`, `event_contracts.Feed.report_event`);
    the agents' demo-only guard (`environment(demo="paper")`,
    `reached_environment`, `connection_badge`, `Caller.agent_refused`);
    `plugin.query_lake`, one bounded query of the lake, and
    `plugin.count_model_tokens`. It also carries more of each role's common
    logic: custody's pages (`custody.account_pages`), a broker's listings
    (`roles.data.listings`), and the Trader's stated charges and settlement
    dates. Its typed operations are in
    [The analytics component's operations](typed-operations.md#analytics-and-event-groups).
    Breaking: every role's suite holds new cases a plugin's suite test must
    map (see [0.30.0 to 0.31.0](python-sdk.md#0300-to-0310)). It needs a runtime on chart 0.1.308 or later. CLI 0.1.49's `plugin new` writes
    a plugin on it, `--role pricing` among its templates. Its base image is
    `ghcr.io/open-meridian/plugin-python:0.31.0`
    (`sha256:e041f83c89cfcd020f1406bf918aba88c1ff68978874a5de52399d46824cf5d2`).

!!! note "0.30.0: each role's common logic"
    open-meridian 0.30.0, released on PyPI on 2026-10-18, still needs chart 0.1.306 or later. It carries each role's common logic, generic over the
    venue (see [Each role's common logic](python-sdk.md#each-roles-common-logic)):
    `meridian.roles.data` (`Wants`, `Venue`, the venue's reading,
    `served`, `want_rows`, `VenueConnection`), with
    `meridian.roles.data.pairs` and `.event_contracts` doing a venue's
    whole work by what it lists, and `meridian.roles.data.testing`'s
    checks; `meridian.edge.RawStore`, raw records as files; and
    `meridian.roles.connectivity` (`Trader` over a venue's adapter, its
    **Trading** page and `testing.Rig`), with a connectivity role
    template. The data role's Datasets template pages its wants with the
    kit's `om-pager`. A plugin that copied this middle layer from a
    sibling plugin moves onto the SDK's helpers with
    [`meridian plugin migrate`](cli.md#plugin-migrate) (see
    [0.29.0 to 0.30.0](python-sdk.md#0290-to-0300)). It needs a runtime on chart 0.1.307 or later. CLI 0.1.47's `plugin new`
    writes a plugin on it, `--role connectivity` among its templates. Its base image is
    `ghcr.io/open-meridian/plugin-python:0.30.0`
    (`sha256:a238c6d9292779b4f1df0a06cd30836367c01412a703b559a7414137f3473ed6`).

!!! note "0.29.0"
    open-meridian 0.29.0, released on PyPI on 2026-10-17, needs chart 0.1.306 or later. A version's declaration is the whole of what it says
    about itself (`Declaration(interface=, reads_external_accounts=,
    documentation=)`): its settings, its interface and the tools its
    routes make, and the vendor's documentation, the plugin's `docs/`
    sections named by digest (see
    [Write a plugin's documentation](../how-to/write-a-plugins-documentation.md)).
    `meridian-declaration --documentation` prints the texts the upload
    sends, and a plugin declaring v25 registers exactly the declaration
    its version was uploaded with, or is refused naming the first
    difference. An operations plugin declares its affirmation deadline
    (`Declaration(affirmation_deadline=)`); a break names an unrecognized
    security's identifiers (`record_break(unresolved_identifiers=)`); a
    venue is resolved by its ID (`resolve_venue(venue_id=)`); a
    connectivity plugin no longer reads whether orders may name a local
    record; and the give-up's suite case is about `give-ups`. With it, chart 0.1.306 brings the platform's [registries](../concepts/registries.md)
    (Phase 0: Open Meridian's own plugins in Community), CLI 0.1.46's
    `plugin publish`, `plugin key`, `plugin download`, `upload --bundle`,
    `status` and `logs`, the book's snapshots (`bor.snapshotInterval`), a
    version retired from the catalogue, the licensed schemes declared,
    a listing identifier's trading currency, a give-up naming nothing held
    kept unplaced, and an FX trade after Friday's cut dated Monday.
    [`meridian plugin migrate`](cli.md#plugin-migrate) rewrites what it
    can (see [0.28.0 to 0.29.0](python-sdk.md#0280-to-0290)). It needs a runtime on chart 0.1.306 or later, and CLI 0.1.46's
    `plugin new` writes a plugin on it. Its base image is
    `ghcr.io/open-meridian/plugin-python:0.29.0`
    (`sha256:f3b62d27899acb0c2c9a29f32fdb8d505b1628fbcaadd8a1052ac6af389279f0`).

!!! note "0.28.0"
    open-meridian 0.28.0, released on PyPI on 2026-10-15, needs chart 0.1.305 or later.
    The `oms` [books](../concepts/booking.md) an order's executions to its
    accounts (`book_order`, `hand_off_booking`, `correct_booking`), with
    the block order, the error account, sleeve crosses
    (`record_sleeve_cross`) and give-ups (`report_give_up`); `portfolio` and
    `operations` set an allocation instruction
    (`set_allocation_instruction`); `compliance` raises and acknowledges
    alerts (`raise_alert`, `acknowledge_alert`); and readers list bookings
    and alerts (`list_bookings`, `list_alerts`). Every instrument is named
    by the platform's `INS-` ID, a deployment's local `LCL-` record
    provisional until the platform answers
    (`ResolveIdentifierResult.provisional`; see
    [One ID per instrument](../concepts/one-id.md)); every role hears a
    replacement and catches up with `list_replacements`, the SDK keeping a
    current-ID map from both, and reads the templates (`list_templates`,
    `read_template`); `reference` offers a template's fields
    (`offer_template_fields`); and the order path's roles read whether an
    order may name a local record (`read_local_record_orders`). An
    account's base currency is a balance and every other currency opens
    lots. A data plugin's dataset names the settlement calendar its
    business dates follow (`DatasetDeclaration.calendar_id`).
    `meridian.environment()` defaults to **Sandbox**, **Live** only where a
    person chose it or the plugin's code says `environment(default="live")`.
    The suites gain v24's cases, the SDK answering every suite's two new
    ones for a plugin that maps neither. Every operation it adds is
    `preview`. [`meridian plugin migrate`](cli.md#plugin-migrate) rewrites
    what changed (see [0.27.0 to 0.28.0](python-sdk.md#0270-to-0280)). It needs a
    runtime on chart 0.1.305 or later, and CLI 0.1.45's
    `plugin new` writes a plugin on it. Its base image is
    `ghcr.io/open-meridian/plugin-python:0.28.0`
    (`sha256:ea7720e34c11d40fded19254448317685351b3668eab3bb318e505770f997f5b`).

!!! note "0.27.0"
    open-meridian 0.27.0 needs chart 0.1.303 or later.
    A connectivity plugin reports a
    [venue-originated fill](python-sdk.md#venue-originated-fills) on no placement
    (`report_execution`'s `instrument_id`, `side`, `venue_order_id` and
    `venue_client_order_id`), which waits unmatched (`Execution.state`);
    the `ems` accepts it (`accept_execution`, to an `order_id` or a
    `new_order`) or answers it DK (`dont_know_execution`, with a reason);
    a connectivity plugin hears the executions it reported, and its
    catalogue says which acknowledgement its venue takes
    (`VenueCatalogue.execution_acknowledgement`); `list_orders` takes
    `execution_state`. A connectivity plugin reports a venue's
    [value-date roll](python-sdk.md#a-value-date-roll) (`report_value_date_roll`), a fee
    may be financing or commission, and an FX order names its
    `quote_currency`. A data plugin records an event contract's
    [outcomes](python-sdk.md#outcomes) (`record_outcomes`, `Outcome`), which prices'
    readers and `operations` hear and read (`list_outcomes`); a daily value
    on a closed day carries `ObservationMeta.closed_day`. A plugin whose
    source states no currency declares
    [`meridian.account_currency()`](python-sdk.md#typed-settings). The suites gain v23's
    cases, their [`about` markers](python-sdk.md#a-case-not-presented) and `any_of`.
    Every operation it adds is `preview`. Nothing a plugin calls changed
    shape: `meridian plugin migrate` moves the pins (see
    [0.26.0 to 0.27.0](python-sdk.md#0260-to-0270)). It needs a runtime on chart 0.1.303 or later, and CLI 0.1.43's `plugin new`
    writes a plugin on it. Released 2026-10-14.

!!! warning "Notice: SDK 0.28.0 changes three stable reads"
    The one-ID revision changes
    [`ResolveIdentifier`](typed-operations.md#resolve_identifier),
    [`ResolveInstrument`](typed-operations.md#resolve_instrument) and
    [`ReportMissingInstrument`](typed-operations.md#report_missing_instrument). Every
    instrument comes to be keyed by its platform `INS-` ID: a deployment's
    provisional records stay `LCL-`, resolved to their `INS-` record, and a
    resolved `LCL-` ID is accepted forever. The `open_meridian` identifier
    stops being added to records. Plugins treat IDs as opaque and need no
    change; a plugin that reads the `open_meridian` identifier should stop
    relying on it. A stable row changes only after a version whose notice
    says it will, and SDK 0.27.0 is that version.

!!! note "0.26.0"
    open-meridian 0.26.0 needs chart 0.1.301 or later:
    [the order path](python-sdk.md#the-order-path) and
    [settlement calendars](python-sdk.md#settlement-calendars). Each role on the order
    path does its part through typed operations (`propose_order`,
    `release_order`, `create_placement`, `report_execution` and the rest)
    and hears the book's records (`receive(order_updated=...,
    placement_updated=..., execution_recorded=...,
    trading_instruction_changed=...)`); a refusal by the order's state, a
    claim or a link is a `CommandRefused` with its code, and the order's
    transition table ships as `meridian/transitions.json`. Every role works
    out a date in core (`read_calendar`, `compute_date`). A version declares
    the algorithms its autonomous work may name
    (`Declaration(algorithms=[AlgorithmDeclaration(...)])`), and
    [`runs_as(role, algorithm_id=...)`](python-sdk.md#runs_as) names one; a
    [`Caller`](python-sdk.md#caller) carries `algorithm_id` and, for an `ems`, the
    connectivity plugins the user may route through
    (`connectivity_instance_ids`). A placement carries its own change
    requests (`change_requests`). A connectivity plugin reports fills on
    the `ems`'s placements and records no order and creates no placement. The order path's and the
    calendars' operations are `preview`. At the upgrade to chart 0.1.301 the
    book records that every account it holds waits for compliance, each
    its own entry, and no connectivity plugin is available or linked, each
    recorded so. Nothing a plugin calls changed
    shape: `meridian plugin migrate` moves the pins (see
    [0.25.0 to 0.26.0](python-sdk.md#0250-to-0260)). It needs a runtime on chart 0.1.301 or later, and CLI 0.1.42's `plugin new` writes
    a plugin on it. Released 2026-10-13.

!!! note "0.25.0"
    A plugin's autonomous work -- a scheduled sweep, a strategy, an agent
    inside the plugin -- calls its own acts as the
    [service account](../concepts/service-accounts.md) its role runs as,
    [`meridian.runs_as(role)`](python-sdk.md#runs_as), answered made or prepared; a
    refusal names its field (`NotGranted.fields`, `CallFailed.fields`), and
    a sidecar older than v21 is said to be (`CallFailed`, kind
    `"unimplemented"`). An act's route reached for such a call reads a
    [`Caller`](python-sdk.md#caller) whose `subject_kind` is a service account, naming
    its `owner_subject` (`meridian.SubjectKind`), and acts as for a person;
    `meridian.testing` calls a tool so (`subject_kind=`, `owner_subject=`).
    Nothing a plugin calls changed shape: `meridian plugin migrate` moves
    the pins (see [0.24.0 to 0.25.0](python-sdk.md#0240-to-0250)). It needs a runtime
    runtime on chart 0.1.299 or later, and CLI 0.1.41's
    `plugin new` writes a plugin on it. Released 2026-10-12.

!!! note "0.24.0"
    An act can be [prepared](python-sdk.md#prepared) rather than made (`checked_by=`,
    `accounts=`, `made_on=`, `request.prepared()`); a setting may be
    [each person's own](python-sdk.md#own_settings) (`per_person`,
    `plugin.set_own_settings`, `request.own_settings`); a plugin links only
    to the accounts a deployment admin granted it; a data plugin reads its
    own datasets' licences and backfills a restart's gap
    (`meridian.roles.data.backfill_restart`); the roles `dgm`, `ccm` and
    `match` are named `data`, `connectivity` and `confirmation`; and each
    role's common part is [`meridian.roles`](python-sdk.md#each-roles-common-part), with
    typed settings (`@meridian.settings`, `meridian.environment()`,
    `meridian.sample_data()`) and the kit's macros (`meridian/kit.html`).
    From 0.23.0 `meridian plugin migrate` rewrites the old role names; see
    [0.23.0 to 0.24.0](python-sdk.md#0230-to-0240). It needs a runtime on chart 0.1.298 or later, and CLI 0.1.39's `plugin new` writes a
    plugin on it. Released 2026-10-11.
    At the upgrade to chart 0.1.298 the instrument store opens a pulled
    identifier's window from the start, each record so corrected a version
    of its own naming each window and the date it replaced; a duplicate
    local record minted before it, beside the platform's, by an
    earlier-dated report or a data plugin naming a currency the deployment
    did not hold, is left for a person to merge on the **Instruments** page.
    Each account a plugin had linked is granted to it at the upgrade,
    recorded as made then, so nothing that worked stops.
    A deployment's grants and access entries naming an old role name are
    rewritten once by core at the upgrade.
    At the upgrade every act is "may make", with the second pair of eyes
    off, which is what every delegation could do before, each recorded as
    set then.
    A secret of 16 characters or more shows its last four characters in
    its placeholder once it is set again after the upgrade.

!!! note "0.23.0"
    open-meridian 0.23.0 adds the lake's trades
    and quotes: a data plugin records them in batches, `signal` and `ems` read and
    hear them, every trade in full and caught up after a watermark;
    `reporting` resolves an identifier; the suites' 1b cases and a case
    about a kind of data a plugin never publishes marked not presented. It
    needs a runtime on chart 0.1.294 or later, which
    refuses nothing a plugin on 0.22.0 sends. Released 2026-10-10. See
    [Trades and quotes](python-sdk.md#trades-and-quotes).

!!! note "0.22.0"
    open-meridian 0.22.0 adds [the lake](python-sdk.md#the-lake): a
    `data`'s catalogue, prices and bars recorded in batches, wants, the
    readers, a `Money` naming its instrument and real dates. It needs a
    runtime on chart 0.1.292 or later, which refuses
    nothing a plugin on 0.21.0 sends. See [Plugin manifest](plugin-manifest.md).
    A plugin built before it keeps sending the currency code it always sent,
    and core resolves it to the currency's cash instrument. At the upgrade
    to chart 0.1.292 the street and the book resolve every currency code they
    hold to its cash instrument, once, each resolution its own record saying
    it was filled in then, not when the amount was first recorded; no entry
    or record is rewritten, and a code the instrument store does not answer
    for yet is resolved by a later sweep.

!!! note "0.21.0"
    open-meridian 0.21.0 adds [the archive](python-sdk.md#the-archive):
    a plugin at the edge declares the kinds of raw record it keeps, and past
    each kind's window archives, keeps or deletes them as its admin chose,
    each move reported. It needs a runtime on chart
    0.1.277 or later, and CLI 0.1.36's `plugin new` writes a plugin on it;
    CLI 0.1.36's `meridian up` asks where older records go (`--archive`,
    `--no-archive`). A plugin declaring no kinds keeps one retention, as
    before. **SnapTrade 0.13.0**, the first plugin on it, drops 0.12.0's
    **Keep raw responses for** (`raw_retention_days`) and **Keep activity
    records for** (`activity_retention_days`) and carries neither value
    over: its windows, **Raw responses: window** (`responses_window_days`,
    30 days by default) and **Reported activity: window**
    (`activity_window_days`, 2,555 days), take their place, set once at
    upgrade. Upgrade the deployment first, note what the two old settings
    hold, launch 0.13.0 in place, then set the two windows and what is done
    past each. What 0.12.0 deleted is not brought back; on its first pass
    0.13.0 moves 0.12.0's records into units, keeping their times.

!!! note "0.20.0"
    open-meridian 0.20.0 adds a person's level is granted
    per role of a plugin (see [Access per role](../concepts/access.md#access-per-role)),
    and a page, route, tool and setting names the roles it serves; a custody
    plugin re-resolves an activity once its instrument resolves. It needs a
    runtime on chart 0.1.268 or later, and CLI 0.1.35's
    `plugin new` writes a plugin on it. A runtime serving v14 or earlier
    grants each plugin as a whole. **The upgrade to chart 0.1.268 rewrites
    every grant once**, changing what nobody can do: every access entry on a
    plugin holding exactly one role is rewritten to name it, at the level it
    had, in the group it was in (a plugin's roles being what its sidecar
    last reported, or its latest launch); an entry on a plugin holding no
    role is left naming none; user groups, account groups, permissions and
    links are untouched, and **All plugins (admin)** grants `admin` on every
    role. A delegation covering everything is untouched; each row of a
    narrowed one is rewritten to name the plugin's one role, and a row the
    rewrite cannot name is kept, covers nothing, and is flagged on Connected
    clients. Each group the upgrade rewrote is recorded, made by no person.
    A runtime at chart 0.1.268 keeps no session for a terminal and serves CLI
    0.1.25 or later, which holds a [delegation](../concepts/access.md#delegations-to-the-cli)
    in place of a session.

!!! note "0.19.0"
    open-meridian 0.19.0 needs a newer runtime:
    [the custodian's activity](../concepts/the-custodians-activity.md),
    reported by a custody plugin, and read, heard and linked by
    `operations`, with each sync status the street keeps; and a setting may
    be a table of typed columns. It needs a runtime on chart 0.1.262 or later, and CLI 0.1.34's `plugin new` writes a plugin
    on it. Released 2026-10-05. Every settings change is
    its own record. At the upgrade the deployment redacts the records of
    every setting already secret; a change made before it, recorded with
    who and when and without the value, is filled in from the value the
    setting still holds where its latest change set it, and says so; and
    each setting changed before the upgrade gets one more record saying
    the earlier values are not known before then.

!!! note "The plugin UI kit, by version"
    The kit pages link, at `/.meridian/ui/<version>/`, served by the
    deployment. A 0.x release only adds, and the dashboard serves the newest
    0.x it carries to any 0.x request (see
    [Build a plugin's page](../how-to/build-a-plugin-page.md#the-kits-version)).

    | Version | What it added |
    |---|---|
    | 0.1.0 | The brand's tokens and colour schemes, the platform's CSS classes, and `om-grid` (with its high-rate mode), `om-chart`, `om-asof`, `om-instrument-picker`, `om-live` and `om-panels` |
    | 0.2.0 | The seamless frame: a page the dashboard frames drops its own heading and tab row, and the frame is sized to the page. See [Inside the dashboard's frame](../how-to/build-a-plugin-page.md#inside-the-dashboards-frame). |
    | 0.3.0 | `om-account-map`; `om-moment`; the grid's declared JSON, rich cells and narrow layouts; list rows that wrap; option and field-row styles, and a select as tall as an input |
    | 0.4.0 | Header actions: a framed page's head buttons, drawn by the dashboard in its own header. See [Header actions](../how-to/build-a-plugin-page.md#header-actions). |
    | 0.5.0 | `om-account-map` at scale: a dense table with search, filters, grouping, pages, a chooser found by typing, suggestions, and several links in one form (`link-several`). See [At thousands of accounts](../how-to/build-a-plugin-page.md#at-thousands-of-accounts). |
    | 0.6.0 | `om-status`, a status dot with its note on hover, focus or a tap; and in `om-account-map`, each account's optional `status` and `values`, a Status column and a filter by state |
    | 0.7.0 | Header status: a framed page's head `om-status` marked `data-om-header`, drawn by the dashboard beside the plugin's name. See [Header status](../how-to/build-a-plugin-page.md#header-status). |
    | 0.8.0 | Icon actions: a button marked `data-om-icon="refresh"` is drawn as a circular arrow, in the page and as a header action in the dashboard's header. See [Icon actions](../how-to/build-a-plugin-page.md#icon-actions). |
    | 0.9.0 | `om-entry-grid`: a table of typed inputs a person enters rows in, posted with the page's own form, the server's messages placed on their cells, a spreadsheet's paste and a CSV in a dialog |
    | 0.10.0 | Every page fits one screen: a height budget the dashboard holds to the screen, compact chrome, one-line rows (`table.one-line`, `om-grid`'s `one-line`) with the whole row a click away, `om-pager`, as many rows a page as fit, and the overflow check |
    | 0.11.0 | A search beside the pager, `search` on `om-grid`, `om-pager` and `om-entry-grid`, `search-param` on `om-pager`, and the `om-search` event; and fields gated on a choice, `data-om-applies-when` and `data-om-one-of`. See [To search a list, and show a field only when it applies](../how-to/build-a-plugin-page.md#to-search-a-list-and-show-a-field-only-when-it-applies). Served from chart 0.1.293. |
    | 0.12.0 | An `instrument` column on `om-entry-grid` with its `src`, found as you type; the patterns **Facts**, **Next step** and **Prepare**; and `meridian:open` with `data-om-opens`, a link from a framed page to one of the dashboard's own tabs. See [Role pages, instruments and Prepare](../how-to/build-a-plugin-page.md#role-pages-instruments-and-prepare). Served from chart 0.1.298. |
    | 0.13.0 | `om-sidebar`, a grouped left sidebar of plain links, its groups given as data, collapsing to icons on a desktop and a drawer on a phone, with `.om-shell` and `.om-shell-main` and the kit's stroked icons (`lib/icons.js`). The dashboard's settings are drawn with it. See [A site's sections: `om-sidebar`](../how-to/build-a-plugin-page.md#a-sites-sections-om-sidebar). Served from chart 0.1.309. |

## Upgrading the chart { #upgrading-the-chart }

What an upgrade from an older chart does on the way, beyond what [Upgrade a deployment](../how-to/upgrade-a-deployment.md) says of the current one.

!!! note "Upgrading from a chart before 0.1.408"
    The upgrade to chart 0.1.408 adds each store's change log, the table a
    standby follows, and the stores' hot layers, each bounded within the
    component's memory limit (see
    [Service levels](../concepts/service-levels.md#the-hot-layer)). Every
    `standby` value defaults to 0, so a deployment keeps one member of each
    component until you ask for more. It also brings
    [bonds and fixed income](../concepts/bonds-and-fixed-income.md): the
    debt templates, pools' factors in the lake, and the book's fixed-income
    records. Plugins keep running as they are: one built on an older SDK
    registers and sends what it did; move it with
    [`meridian plugin migrate`](cli.md#plugin-migrate).

!!! note "Upgrading from a chart before 0.1.313"
    The upgrade to chart 0.1.313 migrates the
    instrument store (a listed series' terms, and the company records), the
    conductor (the deployment's settings kept one record each, and starter
    packs) and the dashboard's notices, each adding to what is held. The
    book's snapshots change format, so each account's projection is
    rebuilt from its journal once; the journal is not rewritten. The
    settings home page gains **Series request rule** (series for an order
    asked for, standing wants not, 500 a day) and **Stale reference actions
    permitted** (refuse only); the **Data sources** page its **Age** tab; **Browse** its
    **Starter packs** view. Plugins keep running as they are: one built on
    SDK 0.32 registers and sends what it did, and reports no latency until
    it moves to SDK 0.33.0 (see
    [Moving a plugin to a new release](python-sdk.md#moving-a-plugin-to-a-new-release)).
    An `ems` moved to SDK 0.33.0 reads **Stale reference actions permitted**, so
    a desk whose admin chose **Warn** refuses until a deployment admin
    permits **Refuse or warn**. The options measures price at the US
    Treasury's par yield curve, so a deployment running them launches a
    rates plugin recording it (see [Rates](../concepts/rates.md)).

    Upgrading from a chart before chart 0.1.309 also rebuilds each
    account's projection from its journal once, as the book's snapshots
    change format, so every lot relieved before it gains its
    [proceeds](../concepts/the-book-of-record.md#a-closed-lots-proceeds);
    the journal is not rewritten. The dashboard's settings move from a row
    of tabs to a grouped sidebar, every address unchanged, with **FX pivot
    currencies** under **Deployment**, reading USD, then EUR, until a
    deployment admin sets them. Placements made before it have no type and
    read as DMA. Plugins keep running as they are: one built on an older
    SDK registers and sends what it did, and one moved to SDK 0.32.0 or
    later records and reads [rates](../concepts/rates.md), liveness and
    [execution costs](../concepts/execution-costs.md), and places by
    [type](../concepts/placement-types-and-rfq-quotes.md) (see
    [Moving a plugin to a new release](python-sdk.md#moving-a-plugin-to-a-new-release)).
    From chart 0.1.311 a plugin whose catalogue states the licence's
    attribution terms registers, and rates resolve by their publisher's own
    codes (see
    [The licence list](../concepts/one-id.md#the-licence-list)).
    Upgrading from a chart before chart 0.1.308 also adds
    [the analytics component](../concepts/the-analytics-component.md): two
    Deployments, a coordinator and a worker, on an image of its own,
    `ghcr.io/open-meridian/meridian-analytics`, sized by the chart's
    `analytics.coordinator` and `analytics.worker` values, stateless, with
    no database and no volume, every pricing model built-in until a
    deployment admin routes one; and the book records
    [the agents' guard](../concepts/the-agents-guard.md) on, once, as its
    own entry, a connectivity plugin reporting no environment for its
    session being live for agents. From one before chart 0.1.306, it starts
    the book's snapshots, one every `bor.snapshotInterval` entries (default
    1,000), and gives the **Plugins** page **Browse** and **Registries**
    (see [Registries](../concepts/registries.md)); from one before chart 0.1.305, it runs that release's instrument migration (see
    [Review provisional records and the migration](../how-to/review-provisional-records.md)).
    `meridian status` shows the release, each component and plugin, and the
    book's health after the upgrade.
