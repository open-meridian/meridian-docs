# Plan your deployment

A firm comes to Open Meridian with a profile: what kind of firm it is, where
it is, and which markets it serves. It asks how to use a deployment as its
books and records, and which plugins it needs for its clients, its
regulators and its reporting. This page answers in the same three layers
every time, says how to read the answer, and works three profiles through
it.

!!! note "A plan, not a promise of dates"
    Each status below is honest as of October 2026: what exists today, what
    is planned and in which release, and what a firm builds itself. The
    releases come in the order this page gives, one at a time; they carry no
    dates. Where a page elsewhere on this site describes something that is
    specified but not built, it says so too.

<!-- DRAFT for the product owner's review (2026-10-05): the wording of
"Who checks a plugin" and the Registry column. Published 2026-10-05 without a section number; when the Terms' plugins section (meridian-platform branch terms-third-party-plugins) goes live, name it here. Not to be rephrased elsewhere
until reviewed. -->

## Who checks a plugin

!!! warning "Naming a plugin here is not an endorsement"
    **Local and community plugins are completely unsupervised.** The platform
    checks nothing about them, and whoever installs one carries its risk.

    **Verified plugins are checked at best effort**: the platform's review and a
    version floor. That is not an audit, a warranty, or due diligence on the vendor.

    **In every case the firm carries its own vendor due diligence**: the
    vendor's terms and licences, its security, its regulatory status, and
    whether the plugin is fit for the firm's purpose.

    This is a summary. The [Platform Terms](https://open-meridian.com/terms)
    govern.

Every table below marks each plugin with its **registry**:

| Registry | What it is |
|---|---|
| **Local** | Your deployment's own registry, which you or your agent upload to. Unsupervised. Every plugin installed today is local, SnapTrade and the sample operations plugin included |
| **Community** | The platform's shared registry, for anyone's plugins. Unsupervised. Not open yet |
| **Verified** | The platform's registry of plugins checked at best effort, as above. Not open yet |
| **Planned** | The plugin does not exist yet |

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
- **[Access](access.md)**: who signs in, and what each person may reach.
- **Every change its own record**: who changed what, to what, and when, never
  back-dated, kept in the deployment the firm runs in its own environment.

### Plugins, by role

Everything that reaches outside the deployment, or decides something, is a
[plugin](plugins.md), and each plugin holds one or more of thirteen fixed
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
| **Access** | Who may use which plugin, at `read`, `write` or `admin`, on which accounts | Exists, per plugin; per role within a plugin is planned, in **access per role** |
| **A plugin's settings** | Its keys and secrets, and tables such as code links, each change recorded with who made it | Exists ([Set a plugin's settings](../how-to/set-a-plugins-settings.md)) |
| **Holds** | How long the raw records a plugin received or sent are kept at the least, and whether older ones move to cold storage | A plugin's version sets how long it keeps them today; the admin's hold and the archive are planned, in **the archive** |
| **Region** | Where the deployment and its storage run | Yours: the deployment runs where you install it. Showing the storage's region on Settings is planned, not scheduled |
| **Egress** | The address the deployment calls out from, and which outside hosts each plugin calls | Your cluster's network today. A plugin declaring its hosts, and the admin approving them, is planned, not scheduled |
| **Service accounts** | A named account, with an owner, that a plugin's scheduled work runs as | Planned, in **service accounts** |

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
| **Planned, in a release** | Accepted, with its place in the order below |
| **Planned, not scheduled** | Accepted, with no place in the order yet |
| **Build your own** | The contract already carries it: a firm's agent can write the plugin now |
| **Spec to bring** | The contract cannot express it yet. A firm describes it, and it lands as an addition at its turn, with nothing renamed |

The releases, in their order:

1. **The custodian's activity**: what happened on an account, explaining a
   break. Released 2026-10-05.
2. **Access per role**: a person granted a level on one role of a plugin, so
   one plugin's custody and operations can be given to different people.
3. **The archive**: an admin's hold on a plugin's raw records, older ones
   moved to cold storage, restored on request, each move recorded.
4. **Valuation**: prices and daily bars in the deployment's market-data
   store, and the book valued from them.
5. **Live market data**: trades, quotes and streaming prices, and the
   professional data sources a fund licenses.
6. **Prepared changes**: an agent prepares a change, and a person makes it.
7. **Service accounts**: a plugin's scheduled work runs as a named account.
8. **The order path**: orders, their state decided by the book, sent to
   venues and filled.

What comes **after the order path** is said so, row by row.

## A US individual, accounts at Fidelity through SnapTrade

A person keeping their own books: a brokerage account, an IRA and a 401(k)
at Fidelity, reached through SnapTrade, in US dollars. They want their
holdings, what happened on each account, a book that reconciles, and its
value. No trading yet.

| Need | Role | Plugin | Registry | Status |
|---|---|---|---|---|
| Holdings and cash from Fidelity, daily | [`custody`](roles.md#custody) | SnapTrade | Local | Exists |
| Dividends, reinvestments, splits and transfers, back to the start of the history SnapTrade holds | [`custody`](roles.md#custody) | SnapTrade | Local | Exists |
| A 401(k) plan's own fund codes linked to their instruments | [`custody`](roles.md#custody) | SnapTrade, its Plan-code links table | Local | Exists |
| The IRA's core position, an FDIC-insured deposit, counted as cash | [`custody`](roles.md#custody) | SnapTrade, by its own flag or its Cash links table | Local | Exists |
| An opening balance per account, with its lots, and daily reconciliation, each break explained | [`operations`](roles.md#operations) | The sample operations plugin | Local | Exists |
| Daily closes for stocks and ETFs | [`dgm`](roles.md#dgm) | Alpaca and Tradier | Planned | Planned, in valuation |
| US dollar exchange rates | [`dgm`](roles.md#dgm) | The Federal Reserve's H.10 rates | Planned | Planned, in valuation |
| A mutual fund's daily NAV | [`dgm`](roles.md#dgm) | Tiingo | Planned | Planned, after valuation's equity sources |
| The book valued, by account and in total | [`reporting`](roles.md#reporting) | The sample reporting plugin | Planned | Planned, in valuation |
| A plan-only fund valued at the custodian's own mark | [`dgm`](roles.md#dgm) | SnapTrade | Local | Planned, not scheduled |
| Trading from the deployment | [`ccm`](roles.md#ccm) | SnapTrade | Local | Planned, in the order path |

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
reports to its investors, and trades once the order path is built.

| Need | Role | Plugin | Registry | Status |
|---|---|---|---|---|
| Holdings, cash and activity from the brokerages SnapTrade reaches | [`custody`](roles.md#custody) | SnapTrade | Local | Exists |
| Holdings, cash and activity from a custodian or prime broker with no plugin | [`custody`](roles.md#custody) | Yours | Local | Build your own |
| Holdings and activity read directly from Alpaca or Tradier | [`custody`](roles.md#custody) | Alpaca, Tradier | Planned | Planned, not scheduled |
| Opening balances, daily reconciliation, breaks resolved by people | [`operations`](roles.md#operations) | The sample operations plugin, or yours | Local | Exists |
| Consolidated end-of-day prices under the fund's own licence | [`dgm`](roles.md#dgm) | Databento, Massive | Planned | Planned, in live market data |
| Mutual fund NAVs | [`dgm`](roles.md#dgm) | Tiingo, under the fund's own licence | Planned | Planned, after valuation's equity sources |
| Exchange rates | [`dgm`](roles.md#dgm) | The Federal Reserve's H.10 rates | Planned | Planned, in valuation |
| The book valued daily, consolidated and by account | [`reporting`](roles.md#reporting) | The sample reporting plugin, or yours | Planned | Planned, in valuation |
| Post-trade concentration checks against the book | [`compliance`](roles.md#compliance) | Yours | Local | Build your own: it reads positions and account figures today |
| Restricted lists and standing limits in a common form | [`compliance`](roles.md#compliance) | Yours | Local | Planned, with the order path |
| A verdict on each order before it goes out | [`compliance`](roles.md#compliance) | Yours | Local | Planned, in the order path |
| Investor reports, kept as sent | [`reporting`](roles.md#reporting) | Yours | Local | Build your own; valued figures wait for valuation |
| An agent drafting an adjustment that a person makes | any | Any | — | Planned, in prepared changes |
| A nightly job running as a named account | any | Any | — | Planned, in service accounts |
| Orders decided, worked and sent | [`portfolio`](roles.md#portfolio), [`oms`](roles.md#oms), [`ems`](roles.md#ems) | Yours | Local | Planned, in the order path |
| Orders placed at a broker | [`ccm`](roles.md#ccm) | SnapTrade; Alpaca and Tradier | Local; planned | Planned: SnapTrade in the order path, Alpaca and Tradier after it |

**Configuration.** Accounts carry an owner label per fund or sleeve, and
account groups follow them: operations staff hold `write` on the accounts
they reconcile, the portfolio manager `read` on all of them. Once access per
role lands, one plugin's custody and operations can go to different people.
A hold as long as the fund's books-and-records obligations require, set once
the archive lands. Service accounts for scheduled work, each with an owner.
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
| Crypto prices | [`dgm`](roles.md#dgm) | Coinbase and Kraken in valuation; OKX later | Planned | Planned, in valuation |
| US equity prices under the firm's licence | [`dgm`](roles.md#dgm) | Databento, Massive | Planned | Planned, in live market data |
| Money in, out and between accounts, and journals between the firm's accounts and its clients' | [`custody`](roles.md#custody), or [`settlement`](roles.md#settlement) for a separate payment rail | The carrying broker's plugin | Planned | Planned, after the order path |
| A firm-account mark, and custodial, joint and trust accounts | core | none | — | Planned, after the order path |
| Opening a client's account at the carrying broker | [`custody`](roles.md#custody) | The carrying broker's plugin | Planned | Planned, not scheduled |
| A client's identity checks, the identity data kept in the plugin's storage | to settle in the spec | Yours, for a KYC provider | Local | Spec to bring |
| Statements, confirmations and tax forms a client can list | core, the file in the plugin's storage | The carrying broker's plugin | Planned | Planned, not scheduled |
| Clients reaching their own accounts through the firm's app | [`portfolio`](roles.md#portfolio) and [`reporting`](roles.md#reporting) | Yours, acting as a service account | Local | Build your own, after service accounts |
| The Travel Rule's information on each crypto transfer, and proof a client owns a self-hosted address | [`custody`](roles.md#custody) | Yours | Local | Spec to bring: an on-chain transfer's details are not in the contract yet |
| Orders for US equities and crypto | [`oms`](roles.md#oms), [`ccm`](roles.md#ccm) | The carrying broker's and the exchange's | Planned | Planned: the contract in the order path, these plugins after it |
| Returns to MAS, kept as sent | [`reporting`](roles.md#reporting) | Yours | Local | Build your own; returns built from trades wait for the order path |

**Configuration.** A hold of five years on every edge plugin's raw records,
for MAS's record-keeping rules, set once the archive lands; the book already
keeps every change as its own record. The deployment and its storage installed in
Singapore. A static egress address, so exchange keys can be bound to it: an
OKX key that trades and is bound to no address expires after 14 days unused. The firm's staff by role once access per role lands:
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
