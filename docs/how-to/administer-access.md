# Give people access

Who may do what in a deployment is set in the dashboard's **Settings**. Only a deployment admin can
open it.

A **permission** joins three things:

| Part | Answers | Made of |
|---|---|---|
| User group | Who | Directory groups, or logins |
| Account group | On which accounts | The firm's accounts |
| Access group | Using what | Plugins, each at `admin`, `read` or `write` |

So a permission reads: *the people in this user group, using these plugins, on these accounts.* See [Access](../concepts/access.md) and [Accounts](../concepts/accounts.md) for the model.

## To open Settings

1. Sign in to the dashboard.
2. Choose the gear at the top right, named **Settings**. It is at `/admin`.

Only a deployment admin sees the button. In Settings it is a house, named **Home**, and takes you
back to your plugins. The breadcrumb beside the mark reads **Settings**, and in a plugin's view
**Settings / Plugins /** and the plugin's name.

Settings' tabs include **Plugins**, **Permissions**, **User groups**, **Account groups**,
**Access groups**, **Accounts**, **Connected clients** and **Terminal sessions**. Each lists its
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

To change one, choose **Edit** on its row. What you save replaces all four, so a field you empty is
cleared. To close one, choose **Close**. A closed account is kept, and nobody works in it. Accounts
are never deleted.

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
      group, people holding a terminal session, and the accounts the deployment holds itself.
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

An access group lists plugins, each at a level. It is the same three levels for every plugin:

- `admin`: the person configures the plugin, its settings and its own pages at `admin`, and sees no
  account's data. See [A plugin's admins](../concepts/access.md#a-plugins-admins).
- `read`: the plugin may show the person what it reads, on the accounts they may read.
- `write`, which includes `read`: the plugin may also act for the person, on the accounts they may
  write.

A plugin names no parts of itself. Which topics it may publish and read is its roles', and has
nothing to do with who may use it.

1. Open **Access groups** and choose **+ Add**. The dialog is headed **New access group**.
2. Enter a **Name**.
3. Under **Plugins**, choose each plugin the group gives, from the searchable list of the
   deployment's plugin instances, and beside each choose one of:
    - **Read**
    - **Write (includes read)**
    - **Admin (configures it, no account)**
    - **Admin and read**
    - **Admin and write**
4. Choose **Create**.

The plugin instance must be running and have reported to the deployment. If not, the page says so.

Two access groups are built in, and neither can be edited:

- **Deployment admin** gives the deployment's own capabilities, and no plugin and no account.
- **All plugins (admin)** gives `admin` on every plugin, those launched later included, and no
  account.

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
would need one: the page says which permission to withdraw, or give the data level in another group.

## To make someone a deployment admin

Grant a permission with **Access** set to **Deployment admin** and **On accounts** set to **None**,
to a user group they are in.

With a directory, the simpler route is usually the group you named in the wizard: add the person to
it in your directory. The wizard made a user group called **Deployment admins** for it, and linked
it to **All plugins (admin)** as well.

## To make someone a plugin's admin

1. Make an access group giving the plugin at **Admin (configures it, no account)**, or at **Admin
   and read** or **Admin and write** if they also work in it.
2. Grant it to a user group they are in: on **None** for admin alone, or on an account group for a
   data level beside it.

They find the plugin on their home with **Manage**, which opens on its **Summary**, its status and
the figures it reports, with its **Settings** and its pages at `admin` after it. Its settings are
also in the dashboard's admin view of the plugin, at `/admin/plugins/<instance>`, which shows them
the tabs **Overview**, **Settings** and **Access**; they read **Access** and change nothing there,
since only a deployment admin grants.

To make every plugin's admins one group, grant **All plugins (admin)** on **None**. To keep
configuring plugins apart from administering the deployment, withdraw the permission first run made
from **Deployment admins** to **All plugins (admin)**: deployment admins then configure no plugin
unless granted.

## To withdraw a permission

On the **Permissions** tab, choose **Withdraw** on its row and confirm. The people in the user group
lose what it gave them.

## To link an external account

A plugin that reads a broker or custodian names accounts as that source does. Linking tells the
deployment which of your accounts that is. Until a source's account is linked, the deployment
refuses the plugin's rows for it.

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

## To end someone's terminal sessions

The **Terminal sessions** tab lists who is signed in from a terminal by a CLI from before
delegations, 0.1.24 or earlier, each session honoured until it lapses. Choose **End them** on a
person's row and confirm. Their CLI has to sign in again.

## What people see

On the dashboard's home, each person sees the plugins they hold a level on, with a button for each:
**Manage** for `admin`, **Open** for `write`, **View** for `read` (a writer gets View too). A
deployment admin linked to **All plugins (admin)** sees every launched plugin, with **Manage**, and
**Open** or **View** only where a permission gives them `write` or `read`. A plugin opens only at a
level the person holds. See [Manage, Open and View](../concepts/plugins.md#manage-open-and-view).

## Related

- [Plugins, roles and grants](../concepts/plugins.md): roles, and what a plugin may do.
- [Recover administration](recover-administration.md): if nobody can open Settings.
