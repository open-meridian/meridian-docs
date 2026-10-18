# Plan your deployment

A firm comes to Open Meridian with a profile: what kind of firm it is, where
it is, and which markets it serves. It asks how to use a deployment as its
books and records, and which plugins it needs for its clients, its
regulators and its reporting. This page answers in the same three layers
every time, says how to read the answer, and works three profiles through
it.

!!! note "A plan, not a promise of dates"
    Each status below is honest for the current release: what exists, what
    is planned and in which release, and what a firm builds itself. The
    releases still to come carry no dates. Where a page elsewhere on this site describes something that is
    specified but not built, it says so too.

## Who checks a plugin

Every table below marks each plugin with its **registry**, which says where
it comes from and what was checked before it reached you:

| Registry | What it is |
|---|---|
| **Local** | Your deployment's own registry, which you or your agent upload to. The platform checks nothing here. Open Meridian's plugins not yet listed in Community are marked Local, as uploaded from their releases |
| **Community** | The platform's shared registry. The platform builds each version itself and runs its automatic checks before listing it. Open to Open Meridian's own plugins first; SnapTrade is listed there. See [Registries](registries.md) |
| **Verified** | The platform's shared registry for plugins that pass the automatic checks and a person's review. Not open yet |
| **Planned** | The plugin does not exist yet |

Whichever registry a plugin comes from, your firm does its own vendor due
diligence: the vendor's terms and licences, its security, and whether the
plugin fits your purpose.

## A deployment in three layers

### Core: the books and records

Every deployment runs the same core, whatever the firm. It is the record,
and nothing in it is specific to one broker, region or market:

- **The firm's [accounts](accounts.md)**, and each external account at a
  broker or custodian linked to one.
- **The street**: what each custodian says an account holds and, from the
  custodian's activity, what happened on it, kept as reported.
- **[The book of record](the-book-of-record.md)**: the firm's own positions,
  opened by an opening balance a person confirms and reconciled with the
  street, each difference a break a person resolves.
- **[Instruments](instruments.md)**: one identity for every instrument.
- **[The order lifecycle](the-order-lifecycle.md)**: every order, placement and execution, its
  state decided by the book, and fills moving the book's positions.
- **[Settlement calendars](settlement-calendars.md)**: a settlement or value date worked out one way
  from the platform's calendars, with its basis.
- **[Access](access.md)**: who signs in, and what each person may reach.
- **Every change its own record**: who changed what, to what, and when, never
  back-dated, kept in the deployment the firm runs in its own environment.

### Plugins, by role

Everything that reaches outside the deployment, or decides something, is a
[plugin](plugins.md), and each plugin holds one or more of fourteen fixed
[roles](roles.md). A plan names, for each need, the role that meets it and a
plugin that holds that role. Each plugin is one of three things:

- **It exists**: you install it.
- **It is planned**, in a named release.
- **You build it**, with an AI agent, against the contract the role already
  has. [Roles](roles.md#method) maps an idea to the least roles it needs.

### Configuration

What makes the same core and plugins fit one firm is configuration, set by
the firm's own admins:

| Setting | What it decides | Today |
|---|---|---|
| **Accounts and account groups** | Which accounts exist, and which groups of them each permission names | Exists |
| **Access** | Who may use which plugin, at `read`, `write` or `admin`, on which accounts | Exists, per role of a plugin: see [Access per role](access.md#access-per-role) |
| **A plugin's settings** | Its keys and secrets, and tables such as code links, each change recorded with who made it | Exists ([Set a plugin's settings](../how-to/set-a-plugins-settings.md)) |
| **Holds** | How long the raw records a plugin received or sent are kept at the least, and whether older ones move to cold storage | Exists, in **the archive**: a deployment admin's hold per edge role or for all, each plugin's archive allowed with a bound, and its windows set by its admin ([The archive](the-archive.md)) |
| **Region** | Where the deployment and its storage run | Yours: the deployment runs where you install it. Showing the storage's region on Settings is planned, not scheduled |
| **Egress** | The address the deployment calls out from, and which outside hosts each plugin calls | Your cluster's network today. A plugin declaring its hosts, and the admin approving them, is planned, not scheduled |
| **Service accounts** | A named account, with an owner, that a plugin's scheduled work runs as | Exists: see [Service accounts](service-accounts.md) |
| **Trading instructions** | Active, pause or stop on an account, every account, a plugin, a person or a service account, which each plugin on the order path honours | Exists: see [Set trading instructions](../how-to/set-trading-instructions.md) |
| **Releases wait for compliance** | Per account, whether an order is released only once every `compliance` plugin covering the account has answered; on by default | Exists: see [Set trading instructions](../how-to/set-trading-instructions.md#whether-an-accounts-releases-wait-for-compliance) |
| **Routing** | Which connectivity plugins each `ems` may place at, who may route through each, and each account's venue account code | Exists: see [Route orders through a connectivity plugin](../how-to/route-orders-through-a-connectivity-plugin.md) |

## How to read a plan

Each profile below is a table, one row per need:

| Column | What it says |
|---|---|
| **Need** | What the firm has to be able to do, in its own words |
| **Role** | The role that meets it, linked to what that role does and does not do |
| **Plugin** | A plugin that exists or is planned, or "yours" where the firm builds it |
| **Registry** | Where the plugin comes from, and so who checks it: see [Who checks a plugin](#who-checks-a-plugin) |
| **Status** | One of the five below |

| Status | Meaning |
|---|---|
| **Exists** | Built and installable today |
| **Planned, in a release** | Accepted, and named for a release still to come, below |
| **Planned, not scheduled** | Accepted, with no release named yet |
| **Build your own** | The contract already carries it: a firm's agent can write the plugin now |
| **Spec to bring** | The contract cannot express it yet. A firm describes it, and it lands as an addition at its turn, with nothing renamed |

Everything marked **Exists** is in the current release; what each release
added is in the [release notes](../api/python-sdk.md#release-notes). Two
releases are still to come by name: **live market data**'s professional
sources, which a fund licenses, following when their keys exist; and **risk
and compliance**, restricted lists and standing limits in a common form.
What comes **after the order path** is said so, row by row.

## A US individual, accounts at Fidelity through SnapTrade

A person keeping their own books: a brokerage account, an IRA and a 401(k)
at Fidelity, reached through SnapTrade, in US dollars. They want their
holdings, what happened on each account, a book that reconciles, and its
value. No trading yet.

| Need | Role | Plugin | Registry | Status |
|---|---|---|---|---|
| Holdings and cash from Fidelity, daily | [`custody`](roles.md#custody) | SnapTrade | Community | Exists |
| Dividends, reinvestments, splits and transfers, back to the start of the history SnapTrade holds | [`custody`](roles.md#custody) | SnapTrade | Community | Exists |
| A 401(k) plan's own fund codes linked to their instruments | [`custody`](roles.md#custody) | SnapTrade, its Plan-code links table | Community | Exists |
| The IRA's core position, an FDIC-insured deposit, counted as cash | [`custody`](roles.md#custody) | SnapTrade, by its own flag or its Cash links table | Community | Exists |
| An opening balance per account, with its lots, and daily reconciliation, each break explained | [`operations`](roles.md#operations) | The sample operations plugin | Local | Exists |
| Daily closes for stocks and ETFs | [`data`](roles.md#data) | Alpaca and Tradier | Local | Exists: see [Using a data plugin](../how-to/using-a-data-plugin.md#alpaca-and-tradier) |
| US dollar exchange rates | [`data`](roles.md#data) | The Federal Reserve's H.10 rates | Local | Exists: see [Using a data plugin](../how-to/using-a-data-plugin.md#the-federal-reserves-h10) |
| A mutual fund's daily NAV | [`data`](roles.md#data) | Tiingo | Local | Exists: see [Using a data plugin](../how-to/using-a-data-plugin.md#tiingo-mutual-funds-daily-navs) |
| The book valued, by account and in total | [`reporting`](roles.md#reporting) | The sample reporting plugin | Local | Exists: see [Value the book](../how-to/value-the-book.md) |
| A plan-only fund valued at the custodian's own mark | [`data`](roles.md#data) | SnapTrade | Community | Planned, not scheduled |
| Trading from the deployment | [`connectivity`](roles.md#connectivity) | SnapTrade | Community | Exists: trading enabled per connection, tested against a simulated brokerage only; see [Trading through SnapTrade](../how-to/using-a-custody-plugin.md#trading-through-snaptrade) |

**Configuration.** The person is their own deployment admin and the only
person with access. SnapTrade's key is a secret setting on its form. Accounts
are named on Settings and linked to Fidelity's on SnapTrade's page. A stable
money market fund is valued at 1.00 by the reporting plugin's named rule,
shown as such. A fund no source prices, such as a plan-only fund, is shown
unvalued with its reason, never as zero. The free data sources here are for
the account holder's own use, which this profile is.

**A spec to bring.** Nothing this profile needs: every row is existing or
planned.

## A small US fund

A fund with accounts at several brokers and a custodian, which values its
book daily, holds itself to concentration and restricted-list limits,
reports to its investors, and trades through the order path.

| Need | Role | Plugin | Registry | Status |
|---|---|---|---|---|
| Holdings, cash and activity from the brokerages SnapTrade reaches | [`custody`](roles.md#custody) | SnapTrade | Community | Exists |
| Holdings, cash and activity from a custodian or prime broker with no plugin | [`custody`](roles.md#custody) | Yours | Local | Build your own |
| Holdings and activity read directly from Alpaca or Tradier | [`custody`](roles.md#custody) | Alpaca, Tradier | Local | Exists: see [Using a custody plugin](../how-to/using-a-custody-plugin.md) |
| Opening balances, daily reconciliation, breaks resolved by people | [`operations`](roles.md#operations) | The sample operations plugin, or yours | Local | Exists |
| Consolidated end-of-day prices under the fund's own licence | [`data`](roles.md#data) | Databento, Massive | Planned | Planned, in live market data |
| Mutual fund NAVs | [`data`](roles.md#data) | Tiingo, under the fund's own licence | Local | Exists: see [Using a data plugin](../how-to/using-a-data-plugin.md#tiingo-mutual-funds-daily-navs) |
| Exchange rates | [`data`](roles.md#data) | The Federal Reserve's H.10 rates | Local | Exists: see [Using a data plugin](../how-to/using-a-data-plugin.md#the-federal-reserves-h10) |
| The book valued daily, consolidated and by account | [`reporting`](roles.md#reporting) | The sample reporting plugin, or yours | Local | Exists: see [Value the book](../how-to/value-the-book.md) |
| Post-trade concentration checks against the book | [`compliance`](roles.md#compliance) | Yours | Local | Build your own: it reads positions and account figures today |
| Restricted lists and standing limits in a common form | [`compliance`](roles.md#compliance) | Yours | Local | Planned, with risk and compliance |
| A verdict on each order before it goes out | [`compliance`](roles.md#compliance) | Yours | Local | Build your own: the contract carries it; see [The order lifecycle](the-order-lifecycle.md) |
| Investor reports, kept as sent | [`reporting`](roles.md#reporting) | Yours | Local | Build your own: it reads positions and the lake's prices today |
| An agent drafting an adjustment that a person makes | any | Any | — | Exists: [Prepared changes](prepared-changes.md) |
| A nightly job running as a named account | any | Any | — | Exists: [Service accounts](service-accounts.md) |
| Orders decided, worked and sent | [`portfolio`](roles.md#portfolio), [`oms`](roles.md#oms), [`ems`](roles.md#ems) | Yours | Local | Build your own: the contract carries it; see [The order lifecycle](the-order-lifecycle.md) |
| Orders placed at a broker | [`connectivity`](roles.md#connectivity) | SnapTrade; Alpaca and Tradier | Community; Local | Exists, each tested against a simulated brokerage only: see [Route orders through a connectivity plugin](../how-to/route-orders-through-a-connectivity-plugin.md) |

**Configuration.** Accounts carry an owner label per fund or sleeve, and
account groups follow them: operations staff hold `write` on the accounts
they reconcile, the portfolio manager `read` on all of them. One plugin's
custody and operations can go to different people, by access per role. A
hold as long as the fund's books-and-records obligations require, set on the
archive. Service accounts for scheduled work, each with an owner.
Data keys are secret settings; the data vendor's licence decides whether
prices may be shown to investors outside the firm.

**A spec to bring.** Fund accounting beyond the book: investor capital
accounts, a NAV per share, fees and allocations between investors. No
release plans it.

## An introducing broker in Singapore, offering US equities and crypto

A firm in Singapore whose clients hold US equities through a carrying broker
and crypto through exchanges. The firm keeps its clients' books in its own
deployment, beside the carrying broker's own system; its clients reach their
accounts through the firm's app, never by signing in to the dashboard. The
carrying broker remains the broker of record and the custodian; the
deployment records and checks, and the firm answers to MAS.

| Need | Role | Plugin | Registry | Status |
|---|---|---|---|---|
| Each client's accounts and positions, reconciled daily with the carrying broker's | core, and [`operations`](roles.md#operations) | The sample operations plugin, or yours | Local | Exists |
| Positions, cash and activity from the carrying broker for US equities | [`custody`](roles.md#custody) | Alpaca, its Broker API | Planned | Planned, not scheduled |
| Spot crypto balances and activity from an exchange | [`custody`](roles.md#custody) | Yours, reading OKX | Local | Build your own |
| Crypto prices | [`data`](roles.md#data) | Coinbase and Kraken; OKX later | Local; planned | Coinbase and Kraken exist: see [Using a data plugin](../how-to/using-a-data-plugin.md#coinbase-and-kraken); OKX planned |
| US equity prices under the firm's licence | [`data`](roles.md#data) | Databento, Massive | Planned | Planned, in live market data |
| Money in, out and between accounts, and journals between the firm's accounts and its clients' | [`custody`](roles.md#custody), or [`settlement`](roles.md#settlement) for a separate payment rail | The carrying broker's plugin | Planned | Planned, after the order path |
| A firm-account mark, and custodial, joint and trust accounts | core | none | — | Planned, after the order path |
| Opening a client's account at the carrying broker | [`custody`](roles.md#custody) | The carrying broker's plugin | Planned | Planned, not scheduled |
| A client's identity checks, the identity data kept in the plugin's storage | to settle in the spec | Yours, for a KYC provider | Local | Spec to bring |
| Statements, confirmations and tax forms a client can list | core, the file in the plugin's storage | The carrying broker's plugin | Planned | Planned, not scheduled |
| Clients reaching their own accounts through the firm's app | [`portfolio`](roles.md#portfolio) and [`reporting`](roles.md#reporting) | Yours, acting as a service account | Local | Build your own |
| The Travel Rule's information on each crypto transfer, and proof a client owns a self-hosted address | [`custody`](roles.md#custody) | Yours | Local | Spec to bring: an on-chain transfer's details are not in the contract yet |
| Orders for US equities and crypto | [`oms`](roles.md#oms), [`connectivity`](roles.md#connectivity) | The carrying broker's and the exchange's | Planned | Planned: the contract carries the order path; these plugins come after it |
| Returns to the regulator, kept as sent | [`reporting`](roles.md#reporting) | Yours | Local | Build your own: a `reporting` plugin reads the orders and executions too |

**Configuration.** A hold of five years on every edge plugin's raw records,
set on the archive; the book
keeps every change as its own record. The deployment and its storage installed in
Singapore. A static egress address, so exchange keys can be bound to it: an
OKX key that trades and is bound to no address expires after 14 days unused. The firm's staff by role, by access per role:
operations staff `write` on operations, client service `read`. The intake
plugin runs as a service account with its own owner, and never holds a
deployment admin's powers. One deployment is one firm: a partner firm that
keeps its own books runs its own deployment.

**A spec to bring.** A client's identity check, and how far its data
reaches; an on-chain transfer's network, hash, addresses and the link
between its two legs, with the Travel Rule's message reference and the
counterparty exchange; crypto beyond spot (perpetuals, funding, staking
income) if the firm offers it; and erasure of a client's personal data once
the hold ends, under Singapore's data protection law.

## If something is missing

A need no row covers is met in one of three ways, in this order:

1. **Configure it.** A regional value is a setting, never a constant in
   core: a hold's length, a window, a region, an egress address, a
   threshold. If the setting exists, set it; if it is planned, the plan says
   in which release.
2. **Build a plugin for it, with an agent.** Where the contract already
   expresses what the need records, a firm's agent writes the plugin against
   it and the instructions every new plugin carries. Start with
   [Your first plugin](../getting-started/first-plugin.md) and
   [Build with an AI agent](../getting-started/build-with-an-ai-agent.md);
   choose its roles with [Roles](roles.md#method); for a connector to a
   broker or custodian, follow
   [Record a holdings statement](../tutorials/record-a-holdings-statement.md),
   [Report the custodian's activity](../how-to/report-the-custodians-activity.md)
   and [Keep what your custody plugin converts](../how-to/keep-what-the-edge-converts.md);
   prove it with
   [Prove a plugin against a released runtime](../how-to/prove-a-plugin-against-a-released-runtime.md),
   and ship it with [Release a plugin version](../how-to/release-a-plugin.md).
3. **Bring a spec.** Where the contract cannot express it, describe it: who
   needs it, what must be recorded, which rule asks for it, and for how
   long. Open an issue with **Suggest an improvement** on
   [meridian-core](https://github.com/open-meridian/meridian-core/issues).
   It lands as an addition to the contract at its turn, with nothing renamed
   or reshaped, as every revision so far has.

## Related

- [Roles](roles.md): what each role does, what it leaves to another, and
  how an idea maps to the least roles.
- [The book of record](the-book-of-record.md): how an account enters the
  book and is reconciled.
- [The custodian's activity](the-custodians-activity.md): what a custody
  plugin reports of what happened on an account.
- [Access](access.md): user groups, account groups and the three levels.
