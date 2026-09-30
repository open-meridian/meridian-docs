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
  clears the lock and ends every session the account held.

There is no multi-factor authentication on this route. A firm that needs it
signs in through a provider that has it.

## Sessions

A session is held by the dashboard, keyed by an opaque, HTTP-only cookie, and
records who the person is and the directory groups they presented. It records
nothing about what they may do: access is evaluated from the records on every
request.

Sessions end after **30 minutes idle** and **12 hours** at most. Both are fixed
by Open Meridian's contract rather than configuration. A browser's session is
held in the dashboard's memory, so restarting the dashboard signs browsers out.
A terminal's session (`meridian connect`) is kept, by a hash of its token, in
the dashboard's own table in the deployment's database, so it survives the
dashboard restarting or being upgraded.

Directory groups are read at sign-in and never copied or synchronised into the
deployment. So a person removed from a directory group keeps access until
their session ends — at most 12 hours — and no longer. That is the price of
never holding a copy of your firm's staff, and it is a stated number.

### Terminal sessions

The CLI signs in with `meridian connect`, given the deployment's address unless it is the local one. It opens the deployment's
own sign-in in a browser, always as a fresh sign-in, and receives a session of
its own through a one-time code on a loopback address. It never takes a
password. A terminal session has the same bounds as a browser's, and grants
nothing beyond what the person holds: access is evaluated per request, exactly
as for a browser.

A deployment admin can end a person's terminal sessions, all at once, from the
**Terminal sessions** tab of the administration page; that person's browser
sessions are left alone. `meridian sign-out` ends one's own.

## The access model

Access is built from four records, all held in the conductor's configuration
store and authored on the dashboard's administration page.

| Record | What it is |
|---|---|
| **User group** | A set of directory groups and individual logins. A person belongs to it when their login is listed, or when, at sign-in, their directory says they are in one of its groups |
| **Account group** | An explicit list of the firm's [accounts](accounts.md). There is no "all accounts" group and no nesting, and an empty group reaches nothing |
| **Access group** | A list of entries, each naming one plugin instance and a level: `read` or `write`. `write` includes `read`. The levels are the same for every plugin; a plugin names no parts of itself |
| **Permission** | Joins one user group, one account group and one access group: *these people* may use *these plugins* on *these accounts* |

A person's access is the union of every permission whose user group they
belong to. There are no deny rules: access only adds up.

Access is combined **permission by permission**, never dimension by dimension.
For each plugin, a person holds a set of accounts they may read and a set they
may write, and each permission contributes only its own accounts at
its own level. Write on one account group through one permission and read on
another through a second is write on the first and read on the second — never
write on both.

`read` covers queries and receiving events; `write` covers commands. Each
access entry names a single plugin, so each plugin's access is granted, and
can be counted, on its own.

### Deployment admin

**Deployment admin** is a built-in access group. It holds the dashboard's own
capabilities — accounts, groups, permissions, and bringing plugins in — and
reaches every account, including accounts in no account group, so a permission
to it names no account group. It cannot be edited or deleted, and the last
permission to it cannot be withdrawn: a deployment is never left without an
administrator.

The first administrators are named in the first-run wizard: a directory group,
whose members hold deployment admin from their first sign-in, or the local
account the wizard creates. A deployment that somehow has none gets one back
with a first-admin code from the platform, redeemed at `/claim`.

An account in no account group is visible to deployment admins and to nobody
else.

### How fast a change applies

A change to any of these records reaches every live session within **30
seconds**. A dashboard that has not been able to read the records for **10
minutes** refuses every request rather than serving what it last knew. Plugins'
sidecars keep the same two bounds for what they are told.

### What leaves the deployment

None of these records, at any time, for any purpose. The platform never holds
your firm's staff, your groups or your permissions.
