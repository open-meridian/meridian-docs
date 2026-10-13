# Give people access

Who may do what in a deployment is set in the dashboard's **Settings**. Only a deployment admin can
open it.

A **permission** joins three things:

| Part | Answers | Made of |
|---|---|---|
| User group | Who | Directory groups, or logins |
| Account group | On which accounts | The firm's accounts |
| Access group | Using what | Plugins, each role of each at `admin`, `read` or `write` |

So a permission reads: *the people in this user group, using these plugins, on these accounts.* See [Access](../concepts/access.md) and [Accounts](../concepts/accounts.md) for the model.

`admin`, `write` and `read` are the **access levels**; `read` or `write`, the levels that reach
accounts, are a person's **account access**.

!!! note "Contract v20"
    From contract v20 the **Books** tab is merged into **Accounts** (see
    [To set an account's attributes in the book](#to-set-an-accounts-attributes-in-the-book)),
    a deployment admin grants each plugin the accounts it may link to (see
    [To grant a plugin accounts to link](#to-grant-a-plugin-accounts-to-link)), and the **Agents**
    tab sets what people's agents may do with each act (see
    [Prepared changes](../concepts/prepared-changes.md#what-agents-may-do)). Released 2026-10-12 in chart 0.1.298.

!!! note "Contract v21"
    From contract v21 Settings gains a **Service accounts** tab, where a
    deployment admin creates the users a plugin's autonomous work runs as,
    and a plugin's **Access** tab gains **Runs as** (see
    [To give a plugin's work a service account](#to-give-a-plugins-work-a-service-account)).
    Released 2026-10-12 in chart 0.1.299.

## To open Settings

1. Sign in to the dashboard.
2. Choose the gear at the top right, named **Settings**. It is at `/admin`.

Only a deployment admin sees the button. In Settings it is a house, named **Home**, and takes you
back to your plugins. The breadcrumb beside the mark reads **Settings**, and in a plugin's view
**Settings / Plugins /** and the plugin's name.

Settings' tabs are **Plugins**, **Permissions**, **User groups**, **Account groups**,
**Access groups**, **Accounts**, **Holds**, **Agents**, from contract v21
**Service accounts**, and **Connected clients** (before contract v20, **Books** in place of
**Agents**). Each lists its
records in a table with a search box above it, which keeps the rows holding every word you type,
and headings that sort it. On the three group tabs the section is headed **User**, **Account** or
**Access**. Where a tab makes records, **+ Add** beside its heading opens a dialog headed with what it makes, such as **New
account**. A record is changed with **Edit** on its own row, in a dialog that already holds it;
nobody types an identifier. Every change is recorded with who made it. If a change is refused, the
page says why; choose **Back** to return to what you typed.

## To add an account

1. Open the **Accounts** tab and choose **+ Add**. The dialog is headed **New account**.
2. Enter a **Name**. Optionally, describe it:
    - **Custodian:** where it is held, such as `Fidelity`.
    - **Type:** what it is, such as `Roth IRA`.
    - **Owner:** one ownership or grouping label, such as `Fund I`.
    - **Note:** anything else worth knowing about it.
3. Choose **Create**.

All four are free text. The custodian, type and owner hold up to 200 characters each, and the note
up to 2,000; a longer one is refused, naming the field. The tab shows each account's custodian, type
and owner in columns. An account with a note has a marker beside its name: point at the row, or
focus the marker, and the note shows whole in a bubble.

To find an account, type in the search box above the table: it keeps the rows whose name,
identifier, custodian, type, owner or note hold every word you type.

To change one, choose **Edit** on its row. What you save under **Account** replaces all four, so a
field you empty is cleared. To close one, choose **Close**. A closed account is kept, and nobody
works in it. Accounts are never deleted.

## To set an account's attributes in the book

From contract v20 the tab's **Base currency** and **Lot relief** columns are
each account's attributes in the [book of record](../concepts/the-book-of-record.md). To change
them:

1. Choose **Edit** on the account's row. The dialog has two sections, **Account** and **In the
   book**, each with its own save.
2. Under **In the book**, which says since when the account is in the book, set the **Base
   currency**, three capital letters, and **Lot relief, when a sale names none**; and from
   contract v22 (built, not released) **Releases**, **Wait for compliance** (every new account's)
   or **Do not wait** (see
   [Whether an account's releases wait for compliance](set-trading-instructions.md#whether-an-accounts-releases-wait-for-compliance)).
3. Enter a **Reason**, and choose **Save**.

Each attribute you change is its own entry in the account's journal, with your reason. **In the
book** is shown only for an account that already exists. Before v20 this was the **Books** tab.

## To group accounts

1. Open **Account groups** and choose **+ Add**. The dialog is headed **New account group**.
2. Enter a **Name**, and under **Accounts** choose the accounts it holds. The picker is searchable,
   by name, identifier, custodian, type or owner.
3. Choose **Create**.

To change it later, choose **Edit** on its row, and **Save**.

**All accounts** is built in, and marked **built in** on its row. It holds every account, those
opened later included, so a permission naming it covers accounts nobody has grouped. It cannot be
edited.

## To say who: make a user group

1. Open **User groups** and choose **+ Add**. The dialog is headed **New user group**.
2. Enter a **Name**.
3. Say who is in it, in any of three ways:
    - **People.** Choose them from the searchable list, which names each person by their user ID,
      then their login ID. It lists everybody the dashboard can name: people already in a user
      group, people holding a delegation, and the accounts the deployment holds itself; from
      contract v21 also each service account, by its `SA-` ID, named
      such as *The sweep (service account)*.
    - **Other logins, one per line.** For somebody not listed yet, such as a person from your
      directory who has never been named here. For an account the deployment holds itself, a login
      is `local|name`.
    - **Directory groups, one per line.** Someone is in the user group when their directory says they
      are in one of these. An LDAP group is a full distinguished name, such as
      `cn=traders,ou=groups,dc=firm,dc=internal`.
4. Choose **Create**.

A person's **login ID** is the login exactly as sign-in presents it, and what every grant names:
`local|ada` for an account the deployment holds. Their **user ID** is the part of it they are known
by in their own directory: a local account's name, the `sub` claim for OpenID Connect, or for LDAP
the first part of their entry's name (`ada` of `uid=ada,ou=people,…`).

!!! note
    A directory states a person's groups when they sign in. A change in your directory reaches Open
    Meridian at that person's next sign-in.

## To say what: make an access group

An access group lists plugins, and from contract v15 each role of each, at a level. It is the same
three levels for every plugin and role:

- `admin`: the person configures the plugin's role, its settings and its own pages at `admin`, and
  sees no account's data. See [A plugin's admins](../concepts/access.md#a-plugins-admins).
- `read`: the plugin may show the person what it reads, on the accounts they may read.
- `write`, which includes `read`: the plugin may also act for the person, on the accounts they may
  write.

A plugin names no parts of itself. Which topics it may publish and read is its roles', and has
nothing to do with who may use it; from contract v15 a person is granted a level on each role of a
plugin, so a grant on one role reaches nothing of another. See
[Access per role](../concepts/access.md#access-per-role).

1. Open **Access groups** and choose **+ Add**. The dialog is headed **New access group**.
2. Enter a **Name**.
3. Under **Plugins, a row for each role**, the table lists every plugin the deployment knows, one
   line for each role it holds, with the columns **Plugin**, **Role** and **Level**. A plugin
   holding one role has one row, its role filled in; one holding none has one row reading **no
   role**. It is paged, six rows at a time. In **Level**, choose one of:
    - **None**: the group gives nothing on that row
    - **Read**
    - **Write**, which includes read
    - **Admin**, which configures that role's side and reaches no account
    - **Admin, read**
    - **Admin, write**
4. Choose **Create**.

The plugin must have reported to the deployment, whether or not it runs now. If not, the page says
so. An entry naming a role the plugin does not hold is refused, naming the roles it does.

An entry kept on a role the plugin no longer holds, after a version without that role was launched,
holds nothing. Its row stays in the editor, flagged **not held now**, naming the roles the plugin
holds now, and saving the group keeps it as written. Grant the role the plugin holds instead, or
choose **None** on the flagged row to drop it.

Before contract v15 the editor listed plugins without roles, each chosen from a searchable list,
with **Read**, **Write (includes read)**, **Admin (configures it, no account)**, **Admin and read**
and **Admin and write**.

Two access groups are built in, and neither can be edited:

- **Deployment admin** gives the deployment's own capabilities, and no plugin and no account.
- **All plugins (admin)** gives `admin` on every plugin, those launched later included, on every
  role of each, and no account.

## To grant a permission

1. Open **Permissions** and choose **+ Add**. The dialog is headed **Grant a permission**.
2. Choose the **User group**.
3. Choose **On accounts**: an account group, **All accounts** among them, or **None (admin only, and
   the built-in access groups)**.
4. Choose the **Access** group.
5. Choose **Grant**.

A permission to **Deployment admin**, to **All plugins (admin)**, or to an access group that gives
only `admin`, is granted on no account group: configuring is not an act on an account. Any other
access group is granted on an account group. The same permission cannot be granted twice.

An access group already granted on no account group cannot gain a `read` or `write` entry, which
would need one: the page says which permission to withdraw, or give the account access in another
group.

## To make someone a deployment admin

Grant a permission with **Access** set to **Deployment admin** and **On accounts** set to **None**,
to a user group they are in.

With a directory, the simpler route is usually the group you named in the wizard: add the person to
it in your directory. The wizard made a user group called **Deployment admins** for it, and linked
it to **All plugins (admin)** as well.

## To make someone a plugin's admin

1. Make an access group giving the plugin's role at **Admin**, or at **Admin, read** or **Admin,
   write** if they also work in it. On a plugin holding several roles, give each role they are to
   administer its own row: a setting serving several roles is set only by an admin of every one.
2. Grant it to a user group they are in: on **None** for admin alone, or on an account group for
   account access beside it.

They find the plugin on their home with **Manage**, which opens on its **Summary**, its status and
the figures it reports, with its **Settings** and its pages at `admin` after it. Its settings are
also in the dashboard's admin view of the plugin, at `/admin/plugins/<instance>`, which shows them
the tabs **Overview**, **Settings** and **Access**, and from contract v20 **Accounts**; they read
who holds access on **Access** and the accounts granted on **Accounts**, and change neither, since
only a deployment admin grants. From contract v15 **Access** lists each grant with its **Role**:
the user group, the role, the level and the accounts, a grant holding nothing flagged with the
plugin's roles, paged. From contract v20 it also lists the plugin's acts under
**What agents may do**: who may make each by hand, what their agents may (May make, Prepare only
or May not, capped where the deployment's ceiling is stricter) and whether it needs a second pair
of eyes, which an admin of the act's role sets with **Edit** on its row (see
[Prepared changes](../concepts/prepared-changes.md#what-agents-may-do)). From contract v21 it also shows, under **Runs as**, the service account each role's autonomous work
runs as, which an admin of the role chooses (see
[To give a plugin's work a service account](#to-give-a-plugins-work-a-service-account)), and its
dialogs open, **What agents may do**'s **Edit** among them, which on chart 0.1.298 opened none.
How they fill the form is in [Set a plugin's settings](set-a-plugins-settings.md).

To make every plugin's admins one group, grant **All plugins (admin)** on **None**. To keep
configuring plugins apart from administering the deployment, withdraw the permission first run made
from **Deployment admins** to **All plugins (admin)**: deployment admins then configure no plugin
unless granted.

## To withdraw a permission

On the **Permissions** tab, choose **Withdraw** on its row and confirm. The people in the user group
lose what it gave them.

## To grant a plugin accounts to link

From contract v20 a plugin that links external accounts links them only to
the accounts a deployment admin granted it, and a new plugin instance is granted none. To grant
some:

1. On the **Plugins** tab, open the plugin, then its **Accounts** tab, **Accounts it may link to**.
2. Under **Grant**, choose an account, say why, and choose **Grant**. Grant each account its admins
   may link one of the source's accounts to.
3. To take one back, choose **Withdraw** on its row and confirm. Its link, if one was made, is kept;
   no new link can name it.

The tab says, for each account granted, whether the plugin has linked it yet, and who last changed
the grant and when. A grant lets the plugin's admins link; it gives nobody anything to read or
write, which is still a permission. At the upgrade to v20 each plugin is granted the accounts its
links already named. See [Accounts a plugin may link to](../concepts/accounts.md#accounts-a-plugin-may-link-to).

From contract v22 (built, not released) an `ems` is granted here the accounts its admins may map to
venue account codes, nothing by default; see
[Route orders through a connectivity plugin](route-orders-through-a-connectivity-plugin.md).

## To give a plugin's work a service account

From contract v21 a plugin's autonomous work, such as the sample operations
plugin's sweep, changes something only as a
[service account](../concepts/service-accounts.md), a user of the deployment that is not a person:

1. On the **Service accounts** tab, choose **+ Add**: its name, purpose, owner (a person who
   answers for it) and setting, **Prepare only** (the default) or **Act**.
2. Grant it `write` on the plugin's role, over the account groups it is to act on, as anyone is
   granted: its `SA-` ID in a user group's logins, that user group granted an access group.
3. An admin of the plugin's role chooses it on the plugin's **Access** tab, under **Runs as**.

The tab lists each account on one line: name, owner, setting, state, **Runs for**, last used and
last refusal, with **What it did**, **Edit**, **Disable**, **Re-enable** and **Remove**. Each
change is its own record. See
[Run a plugin's autonomous work as a service account](run-a-plugins-work-as-a-service-account.md).

## To link an external account

A plugin that reads a broker or custodian names accounts as that source does. Linking tells the
deployment which of your accounts that is. Until a source's account is linked, the deployment
refuses the plugin's rows for it. From contract v20 the plugin offers only the accounts granted
to it (above).

Each plugin links its own external accounts, on its own pages at `admin`, because only the plugin
knows what its accounts mean. An admin of the plugin links them, under **Manage**. For SnapTrade:

1. On the dashboard's home, choose **Manage** on the plugin, and open its **Account links** tab.
2. The table opens on the accounts not yet linked. Search it by name, number, custodian or type,
   or group it by connection.
3. On an account's row, choose **Link…**. Link it to an existing account, found by typing its name.
   A deployment admin may instead create a new account for it and link it in one step. A linked
   account offers **Change…**, and **Unlink**.

Where an account's name or number matches exactly one of yours, the row suggests it: **Link**
takes it, and **Other…** opens the same choices. **Link N suggested…** reviews every suggestion the
search finds, and links those you keep in one go.

A new account's custodian starts as the connection's brokerage and its type as the account type
SnapTrade reports; change or clear either before you create it. Give it an owner or a note
afterwards, with **Edit** on the **Accounts** tab.

The plugin sends the link for you. The deployment checks that you opened the plugin by **Manage**,
that the plugin reported that account, and, for a new account, that you are a deployment admin.
Under Manage the plugin reads your accounts' identities only: their names, custodians and types,
never their holdings. The **Plugins** tab of Settings counts, for each plugin, the accounts it
reaches that nothing links.

## To revoke someone's connected clients

The **Connected clients** tab lists everybody who has delegated to a client, such as the `meridian`
command on one of their computers, with how many clients each has. To revoke all of a person's
delegations, choose **Revoke them all** on their row and confirm. To revoke one, choose **See them**:
the page lists each client with what it covers, when it was made, until when, and when it was last
used and last refused. Choose **Revoke** on its row. Each client stops at its next request, and the
person's browser sessions are untouched. Their CLI has to connect again.

A person revokes their own the same way, from **Connected clients** in the menu under their name.
See [Delegations to the CLI](../concepts/access.md#delegations-to-the-cli).

## What people see

On the dashboard's home, each person sees the plugins they hold a level on, with a button for each:
**Manage** for `admin`, **Open** for `write`, **View** for `read` (a writer gets View too). A
deployment admin linked to **All plugins (admin)** sees every launched plugin, with **Manage**, and
**Open** or **View** only where a permission gives them `write` or `read`. A plugin opens only at a
level the person holds. On a plugin holding several roles, a person holding a level on any of its
roles sees it, and each button's title names the roles it reaches at their levels, such as *Open:
operations write, custody read*. See [Manage, Open and View](../concepts/plugins.md#manage-open-and-view).

## Related

- [Plugins, roles and grants](../concepts/plugins.md): roles, and what a plugin may do.
- [Recover administration](recover-administration.md): if nobody can open Settings.
- [Service accounts](../concepts/service-accounts.md): the users a plugin's autonomous work runs
  as (contract v21).
