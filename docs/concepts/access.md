# Access

Two questions decide what somebody can do in a deployment, and Open Meridian
answers them in different places.

- **Who is this?** Answered by signing in, against your firm's directory or
  against accounts the deployment holds itself.
- **What may they reach?** Answered by the deployment's own records, which a
  deployment admin authors in the dashboard.

A directory establishes who a person is and which groups they belong to.
Nothing in what it returns decides what they may do: no permission, account
or access level is ever read from a token. That is always the deployment's
records.

The steps for granting access are in
[Give people access](../how-to/administer-access.md).

## Signing in

The dashboard signs people in one of three ways, chosen in the first-run
wizard. The deployment runs no identity server of its own in any of them.

| How | What happens | Choose it when |
|---|---|---|
| **Your OpenID Connect provider** | The dashboard federates to your provider. Nothing of Open Meridian's authenticates anybody, and multi-factor authentication is whatever your provider requires | Your firm has single sign-on: Microsoft Entra ID, Okta, Ping and the like |
| **Your LDAP or Active Directory** | The dashboard binds to your directory directly. It forwards a person's password once, stores none, and reads their groups from the directory (`memberOf` on most) | Your firm has a directory but no OpenID Connect provider |
| **Accounts the deployment holds** | The dashboard keeps the accounts, with Argon2id-hashed passwords and a lockout | Your firm has no directory of its own |

### OpenID Connect, and `auth_time`

The dashboard uses the authorisation-code flow with PKCE. Every sign-in asks
the provider to authenticate the person anew — it sends `prompt=login` and
`max_age=0` — requests no refresh token, and refuses an ID token whose
`auth_time` is earlier than the sign-in it started.

That check is what makes withdrawn access go away. A provider with a session
of its own can hand out a token without asking the person anything, carrying
groups your directory has since removed; `auth_time` is the only thing that
says when they really authenticated. So **your provider must return
`auth_time`**. Okta does when asked this way; Microsoft Entra ID sends it only
once it is added as an optional claim on the app registration; dex does not
implement it and cannot be used.

Open Meridian does not speak SAML. A firm whose single sign-on speaks only
SAML needs a broker in front that presents OpenID Connect to the dashboard —
and returns `auth_time`.

### LDAP

A person types their directory password into the dashboard's own sign-in
form, and the dashboard checks it by binding to your directory as them. Two
things are refused before anything is sent: an empty password, which LDAP
would otherwise treat as an unauthenticated bind that succeeds, and a
username that is not escaped before it reaches a search filter.

With an `ldap://` address, tick **StartTLS** in the wizard, or every password
crosses your network as it was typed. An `ldaps://` address is encrypted
already.

### Accounts the deployment holds

For a firm with no directory, the wizard creates one account, which becomes
the deployment's administrator. Its login, as permissions name it, is
`local|<name>`.

- **Lockout.** Five failed attempts lock the username for 15 minutes.
- **A warning before the lock.** From the third failed attempt, the sign-in
  page says how many attempts are left. It says the same for every username
  typed, whether or not an account has it, so the page cannot be used to ask
  who works at the firm.
- **A lost password** is reset with a password-reset code from the platform;
  see [Reset a lost password](../how-to/reset-a-lost-password.md). Resetting
  clears the lock, ends every session the account held, and revokes its
  delegations.

There is no multi-factor authentication on this route. A firm that needs it
signs in through a provider that has it.

## Sessions

A session is held by the dashboard, keyed by an opaque, HTTP-only cookie, and
records who the person is and the directory groups they presented. It records
nothing about what they may do: access is evaluated from the records on every
request. Opening a plugin starts a session on that plugin's own host, which
ends with the dashboard session and carries the one level it was opened at,
and from contract v15 the person's level on each of the plugin's roles within
it; see [One level per session](#one-level-per-session-manage-open-and-view).

Sessions end after **30 minutes idle** and **12 hours** at most. Both are fixed
by Open Meridian's contract rather than configuration. A browser's session is
held in the dashboard's memory, so restarting the dashboard signs browsers out.

Directory groups are read at sign-in and never copied or synchronised into the
deployment. So a person removed from a directory group keeps access in a
browser until their session ends — at most 12 hours — and no longer. That is
the price of never holding a copy of your firm's staff, and it is a stated
number. A delegation, which outlasts a session, has bounds of its own.

### Delegations to the CLI

From CLI 0.1.25 and chart 0.1.223, the CLI holds no session. `meridian
connect`, given the deployment's address unless it is the local one, opens the
deployment's own sign-in in a browser, always as a fresh sign-in, and then
asks the person to let the CLI on that computer act as them: a
**delegation**, their own access or a narrower part of it, lent to that one
client for 7, 30 or 90 days. It never takes a password.

The page, **Allow a client to act as you**, names the client (`meridian on`
and the computer's host name) and offers **everything you hold, as that
changes**, or only what the person ticks from what they hold: plugins at their
levels, from contract v15 a level on each of a plugin's roles, the account
groups their permissions name, and the deployment admin's
capabilities, which never include changing who holds access. For the CLI it
starts at everything and 90 days. A narrowed delegation never grows; to widen
it, connect again.

The CLI then holds a ten-minute access token, accepted only on the CLI's own
paths and never where a browser's cookie is, and a single-use refresh token,
which it spends for the next pair without asking anybody. Presenting a spent
refresh token revokes the delegation. The deployment keeps a one-way
fingerprint of each token, never the token, in the dashboard's own tables in
the deployment's database, so a delegation survives the dashboard restarting
or being upgraded.

A delegation grants nothing beyond what the person holds. Every request reads
it and evaluates the person's access as for a browser, cut to what the
delegation covers, so revoking it stops the client at its next request, and
withdrawing the person's access reaches it within 30 seconds. Its directory
groups are kept as fresh as the deployment can keep them without the person:

- **LDAP:** read again, as the account the deployment searches as, whenever
  an access token is issued. A person the directory no longer finds has their
  delegations revoked.
- **Accounts the deployment holds:** looked up whenever an access token is
  issued. An account the deployment no longer holds has its delegations
  revoked, and so does one whose password is reset.
- **Your provider:** the groups of the person's latest fresh sign-in, in a
  browser or by `meridian connect`. A delegation whose groups are more than 7
  days old is refused, not revoked, until the person signs in again.

The person is told a week before a delegation lapses, on their dashboard's
home and by the CLI on every command. Connecting again renews it.

**Connected clients**, in the menu under the person's name at the top right of
the dashboard, lists each client acting for them: what it covers, when it was
made, until when, when it was last used and last refused, each with
**Revoke**. A deployment admin sees who has delegated in the **Connected
clients** tab of Settings, and revokes one of a person's delegations or all of
them; that person's browser sessions are left alone. `meridian sign-out`
revokes one's own.

A deployment at contract v15 keeps no session for a terminal. The sessions a
CLI from before delegations kept, 0.1.24 or earlier, are retired with the
**Terminal sessions** tab of Settings that ended them: the dashboard serves
CLI 0.1.25 or later, tells an older one so, and takes nothing on the CLI's
paths but an access token on a delegation. Up to contract v14 such a session
was accepted until it lapsed, with a browser session's bounds.

## The access model

Access is built from four records, all held in the conductor's configuration
store and authored in the dashboard's **Settings**.

| Record | What it is |
|---|---|
| **User group** | A set of directory groups and individual logins. A person belongs to it when their login is listed, or when, at sign-in, their directory says they are in one of its groups |
| **Account group** | An explicit list of the firm's [accounts](accounts.md), with no nesting; an empty group reaches nothing. One is built in, **All accounts** |
| **Access group** | A list of entries, each naming one plugin instance, from contract v15 one of the roles it holds, and a level: `admin`, `read` or `write`. The levels are the same for every plugin and role; a plugin names no parts of itself |
| **Permission** | Joins one user group, one account group and one access group: *these people* may use *these plugins* on *these accounts* |

A person's access is the union of every permission whose user group they
belong to. There are no deny rules: access only adds up.

### Three levels

| Level | What it gives on the plugin |
|---|---|
| `admin` | Its configuration: its settings, and its own pages at `admin`, such as connections and account links. **No account's data**, and no account group |
| `read` | What the plugin shows, on the accounts the person may read |
| `write` | `read`, and acting through the plugin, on the accounts the person may write |

`write` includes `read`. `admin` includes neither, and neither includes
`admin`: it is configuration, kept apart from the data. A person may hold
`admin` on a plugin's role and, beside it, one data level, `read` or `write`,
the higher one granted. An access group may name a plugin's role at `admin`
and at one data level; naming it at both `read` and `write` is refused, since
`write` already includes `read`.

`read` covers queries and receiving events; `write` covers commands. Each
access entry names a single plugin, and from contract v15 one of its roles,
so each plugin's access is granted, and can be counted, on its own. A plugin
holding one role, which is every plugin today, is granted exactly as before:
see [Access per role](#access-per-role).

The data levels are combined **permission by permission**, never dimension by
dimension. For each plugin and role, a person holds a set of accounts they may
read and a set they may write, and each permission contributes only its own accounts
at its own level. Write on one account group through one permission and read
on another through a second is write on the first and read on the second —
never write on both.

A permission to an access group that gives only `admin` names no account
group: configuring a plugin is not an act on an account. One with a `read` or
`write` entry names one.

### One level per session: Manage, Open and View

A person opens a plugin at one of the levels they hold, by a button on the
dashboard's home: **Manage** for `admin`, **Open** for `write`, **View** for
`read`. A writer is offered View too. See
[Manage, Open and View](plugins.md#manage-open-and-view).

A plugin's session carries only the level it was opened at, and what the
dashboard tells the plugin about the person is cut to it:

| Button | The plugin is told | The person may |
|---|---|---|
| **Manage** | `admin`, and no account | Configure the plugin. The plugin's sidecar refuses every read and command sent for them but two: reading the deployment's accounts, answered with their identities alone (name, state, custodian, type, owner and note, never holdings or balances), and linking an external account |
| **Open** | `write`, every account they may read, and the accounts they may write | See every account they may read, and act on those their `write` grants name |
| **View** | `read`, and every account they may read | See every account they may read, and act on nothing |

From contract v15 the plugin is also told, beside these, the person's level
on each of its roles within the button, and the accounts each reaches: under
Open a role held at `write` is at `write` and one held at `read` at `read`,
under View each at `read`, under Manage each role they administer at `admin`
with no account. What the table says stays the union over those roles, so a
plugin that reads no role is told what it was told before.

The dashboard opens nothing at a level the person does not hold. Nothing
conflicts between the levels, so no grant is refused for giving a person a
second one: separation of duties is per session. A firm that needs it per
person grants nobody both.

A plugin holds data as itself, and nothing technical stops it showing that on
a page at `admin`. That is the trust already placed in a plugin to cut what
it shows under Open and View. The SDK's test client fails a plugin's tests
when a page at `admin` shows account data; see
[Python SDK](../api/python-sdk.md#testing).

### A plugin's admins

A person holding `admin` on a plugin is one of its **admins**. They configure
it: its settings, in the dashboard's admin view of the plugin, and its own
pages at `admin`, under Manage. A plugin admin is **account agnostic**: they
see every account's identity, and link the plugin's external accounts to any
existing account, but reach no account's data. The barrier between business
lines is the `read` and `write` levels', and their account groups. Only a
deployment admin names a new account, and only a deployment admin grants.

From contract v15 `admin` is held on a role of a plugin: a role's admin
administers that role's side of it, its pages at `admin` and the settings
serving only roles they administer. See [Admin per role](#admin-per-role).

### Access per role

!!! note "Contract v15"
    This section describes a runtime serving contract v15 (chart 0.1.268 or
    later) and open-meridian 0.20.0. A runtime serving v14 or earlier grants
    each plugin as a whole.

A plugin may hold several roles: an order and execution management system is
`oms` and `ems`, and a vendor's turnkey plugin may hold `portfolio`, `oms`
and `ems` behind one interface. Granted per plugin, a person with `write` on
such a plugin would write in every one of its roles, so a portfolio manager
who proposes and a trader who releases would be one person by accident of a
vendor's packaging. From contract v15 a person's level is granted **per role
of a plugin**: an access entry names a plugin, one role it holds, and a
level.

Roles are not a plugin's parts. They are the deployment's fixed list of
thirteen, approved when the plugin is launched (see
[Plugins, roles and grants](plugins.md#roles-what-a-plugin-is-for)), so a
grant naming one keeps access decided by the deployment, never by the plugin.

**A plugin holding one role changes nothing.** Every plugin today holds one
role or none: SnapTrade holds `custody`, the sample operations plugin
`operations`. Each entry on such a plugin names its one role, the Access
editor fills it in, and nobody sees a role named anywhere else. A plugin
holding no role is granted as a whole, its entries naming none.

#### A plugin holding two roles

Take a plugin launched holding `custody` and `operations`, and two people:

| Person | Granted | Offered | Under Open |
|---|---|---|---|
| Ada | `write` on `operations`, `read` on `custody` | Open and View | Records an opening balance, an `operations` command. Shown `custody`'s pages that serve `read`. A holdings statement the plugin sends for her is refused by the sidecar: *RecordHoldingsStatement is custody's, and Ada Park holds read on custody* |
| Ben | `write` on `custody`, `read` on `operations` | Open and View | Records the holdings statement. Refused the opening balance, the refusal naming `operations` and his `read` on it |

Under View neither sends anything. Each grant reaches its own accounts, as
permissions always have: `write` on `operations` through one permission and
`read` on `custody` through another is exactly that, never `write` on
`custody`.

- **One home entry per plugin, three buttons.** The home offers the plugin
  once, with **Manage**, **Open** or **View** for each level the person holds
  on any of its roles. On a plugin holding several roles, each button's
  title names the roles it reaches at their levels, such as *Open:
  operations write, custody read*. A session spans every role the person
  holds within its button.
- **The tab row by role.** A plugin holding several roles names the roles
  each of its pages serves. A page is shown, and served, when the person's
  level on one of its roles within the button is one of the page's levels.
- **The sidecar decides every act.** It admits a command sent for a person
  only when they hold `write` on a role whose generated grants include that
  command, with the account among that role's write accounts and in the
  plugin's write scope, and otherwise refuses it, naming each role that
  holds the command and what the person holds on it. It works the role out
  from the contract; the plugin names none on what it sends. A page's
  declared roles decide what is shown, never what is admitted.
- **One account scope per plugin.** What a plugin may read and write as
  itself is the union over its roles, and its links and storage stay one
  per plugin. A plugin that reads no role shows a person the union of their
  roles' read accounts; cutting per role is the plugin's, as cutting per
  person is (see [Reads and writes on behalf of people](plugins.md#reads-and-writes-on-behalf-of-people)).

#### Admin per role

- A role's admin configures that role's side of the plugin: its pages at
  `admin` and the settings serving only roles they administer.
- A setting serving several roles needs `admin` on every role it serves,
  today the one act on a plugin as a whole. On the Settings form such a setting
  is shown to an admin of any role it serves, read-only, with *Serves custody
  and operations: set by an admin of every one*, and the dashboard refuses a
  change to it from anyone who does not administer them all.
- Linking an external account is an admin's of a role whose grants include
  the link: `custody` today.
- **All plugins (admin)** holds `admin` on every role of every plugin,
  plugins launched later and roles gained later included.

#### A role a plugin gains, and entries that no longer match

A role a plugin gains when a new version is launched starts ungranted:
nobody but **All plugins (admin)** holds anything on it until a deployment
admin grants it. Nothing widens on an upgrade or a new role.

An entry naming a role the plugin no longer holds, or naming no role on a
plugin that now holds some, holds nothing. It is kept as the deployment
admin wrote it, never read as every role, and flagged on the Access editor
as **not held now**, naming the roles the plugin holds. A role restored at a
later launch makes it hold again.

#### Delegations and agents

A delegation narrowed to part of what a person holds names, from contract
v15, a level on each of a plugin's roles. The consent page lists a row per
plugin role at each level the person holds, each with the tools it reaches,
and a narrowed delegation never grows. One covering **everything you hold,
as that changes** follows the person's grants per role, a role granted later
included. An agent's tools at the dashboard's `/mcp` follow the same rows:
a tool is listed when the person holds one of its levels on one of its
roles; see
[Offer your plugin's pages to agents](../how-to/offer-your-pages-to-agents.md#tools-by-role).
From contract v17 (built, not released), everything a person can see or do
in a plugin's area, an agent can through their delegation, at the same role
and level, with two exceptions: no agent reads or types a secret setting's
value, and none changes who holds access; see
[Core's tools](../api/core-tools.md).

#### On upgrading to contract v15

The upgrade rewrites every grant once, and changes what nobody can do:

- **Every access entry on a plugin holding exactly one role is rewritten to
  name it**, at the level it had, in the group it was in: on a deployment
  running SnapTrade and the sample operations plugin, every entry on
  SnapTrade becomes a `custody` entry and every one on the operations plugin
  an `operations` entry. A plugin's roles are what its sidecar last reported
  it was launched as, or its latest launch where it has not reported. An
  entry on a plugin holding no role is left naming none.
- **Nothing else moves.** User groups, account groups, permissions and links
  are untouched. **All plugins (admin)** now grants `admin` on every role,
  which is everything it granted.
- **Delegations.** One covering everything is untouched. Each row of a
  narrowed one is rewritten to name the plugin's one role, so none covers
  more or less. A row the rewrite cannot name, on a plugin with several
  roles or none known, is kept, covers nothing, and is flagged on Connected
  clients.
- **What a person sees:** the same home, the same buttons, tabs, pages,
  settings and links, and on the Access editor and each plugin's **Access**
  tab a **Role** column holding each plugin's one role.

From contract v15 every change to a grant is its own record in the
deployment's configuration: an access group defined or changed, a
permission granted or withdrawn, what it was, what it became, who, through
which delegation where they used one, and when. Each group the upgrade
rewrote is recorded too, made by no person, and every access group has one
record saying its history is not known before the upgrade, by the
deployment's clock. No page shows these records yet.

### Deployment admin

**Deployment admin** is a built-in access group. It holds the deployment's
own capabilities — accounts, account and user groups, access groups,
permissions, the deployment's settings, and bringing plugins in — and reaches
no account's data, so a permission to it names no account group. Being a
deployment admin makes nobody admin on a plugin, and lets nobody read or act
through one: that takes a grant, as it does for anybody. A deployment admin
who also works in a plugin is granted `read` or `write` on it, on the record.

It cannot be edited or deleted, and the last permission to it cannot be
withdrawn: a deployment is never left without an administrator.

The first administrators are named in the first-run wizard: a directory group,
whose members hold deployment admin from their first sign-in, or the local
account the wizard creates. A deployment that somehow has none gets one back
with a first-admin code from the platform, redeemed at `/claim`.

### All plugins (admin)

**All plugins (admin)** is a second built-in access group. It gives `admin` on
every plugin, those launched later included, and from contract v15 on every
role of each, those it gains later included; it names no account group.
First run links the user group holding deployment admin to it, and so does a
first-admin code, so a deployment's administrators start as admins of every
plugin. The link is an ordinary permission, and may be withdrawn, for a firm
that keeps configuring plugins apart from administering the deployment.
Deployments installed before levels gained it when they were upgraded: every
user group holding deployment admin was linked to it then.

### All accounts

**All accounts** is a built-in account group. It holds every account, those
no other group lists and those opened later included, and a permission may
name it like any other: a compliance plugin's scope can cover accounts nobody
has grouped. It cannot be edited or deleted.

An account no account group lists is reached only through a permission naming
All accounts, or by a plugin whose link names it. Nobody reaches it by being
an admin.

### How fast a change applies

A change to any of these records reaches every live session within **30
seconds**. A dashboard that has not been able to read the records for **10
minutes** refuses every request rather than serving what it last knew. Plugins'
sidecars keep the same two bounds for what they are told.

### What leaves the deployment

None of these records, at any time, for any purpose. The platform never holds
your firm's staff, your groups or your permissions.
