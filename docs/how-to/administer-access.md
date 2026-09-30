# Give people access

Who may do what in a deployment is set in the dashboard's **Settings**. Only a deployment admin can
open it.

A **permission** joins three things:

| Part | Answers | Made of |
|---|---|---|
| User group | Who | Directory groups, or logins |
| Account group | On which accounts | The firm's accounts |
| Access group | Using what | Plugins, each at `read` or `write` |

So a permission reads: *the people in this user group, using these plugins, on these accounts.* See [Access](../concepts/access.md) and [Accounts](../concepts/accounts.md) for the model.

## To open Settings

1. Sign in to the dashboard.
2. Choose the gear at the top right, named **Settings**. It is at `/admin`.

Only a deployment admin sees the button. In Settings it is a house, named **Dashboard**, and takes
you back to your plugins. The breadcrumb beside the mark reads **Settings**, and in a plugin's view
**Settings / Plugins /** and the plugin's name.

Settings has seven tabs: **Plugins**, **Permissions**, **User groups**, **Account groups**,
**Access groups**, **Accounts** and **Terminal sessions**. Each lists its records in a table with a
search box above it, which keeps the rows holding every word you type, and headings that sort it. A
record is changed with **Edit** on its own row, in a dialog that already holds it; nobody types an
identifier. Every change is recorded with who made it. If a change is refused, the page says why;
choose **Back** to return to what you typed.

## To add an account

1. Open the **Accounts** tab and choose **New account**.
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

1. Open **Account groups** and choose **New account group**.
2. Enter a **Name**, and under **Accounts** choose the accounts it holds. The picker is searchable,
   by name, identifier, custodian, type or owner.
3. Choose **Create**.

To change it later, choose **Edit** on its row, and **Save**.

## To say who: make a user group

1. Open **User groups** and choose **New user group**.
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

An access group lists plugins, each at `read` or `write`. It is the same two levels for every
plugin:

- `read`: the plugin may show the person what it reads, on the accounts they may read.
- `write`, which includes `read`: the plugin may also act for the person, on the accounts they may
  write.

A plugin names no parts of itself. Which topics it may publish and read is its roles', and has
nothing to do with who may use it.

1. Open **Access groups** and choose **New access group**.
2. Enter a **Name**.
3. Under **Plugins**, choose each plugin the group gives, from the searchable list of the
   deployment's plugin instances, and beside each choose its one level: **Read**, or **Write
   (includes read)**.
4. Choose **Create**.

The plugin instance must be running and have reported to the deployment. If not, the page says so.

**Deployment admin** is a built-in access group. It gives the dashboard and every account, and it
cannot be edited.

## To grant a permission

1. Open **Permissions** and choose **Grant a permission**.
2. Choose the **User group**.
3. Choose **On accounts**: an account group, or **Every account (deployment admin only)**.
4. Choose the **Access** group.
5. Choose **Grant**.

Deployment admin is granted on every account. Any other access group is granted on an account group.
The same permission cannot be granted twice.

## To make someone a deployment admin

Grant a permission with **Access** set to **Deployment admin** and **On accounts** set to
**Every account (deployment admin only)**, to a user group they are in.

With a directory, the simpler route is usually the group you named in the wizard: add the person to
it in your directory. The wizard made a user group called **Deployment admins** for it.

## To withdraw a permission

On the **Permissions** tab, choose **Withdraw** on its row and confirm. The people in the user group
lose what it gave them.

## To link an external account

A plugin that reads a broker or custodian names accounts as that source does. Linking tells the
deployment which of your accounts that is. Until a source's account is linked, the deployment
refuses the plugin's rows for it.

Each plugin links its own external accounts, on its own admin pages, because only the plugin
knows what its accounts mean. For SnapTrade:

1. Open **Plugins**, choose **Manage** on the plugin's row, and open its **Account links** tab.
2. The table opens on the accounts not yet linked. Search it by name, number, custodian or type,
   or group it by connection.
3. On an account's row, choose **Link…**. Link it to an existing account, found by typing its name,
   or create a new account for it and link it in one step. A linked account offers **Change…**,
   and **Unlink**.

Where an account's name or number matches exactly one of yours, the row suggests it: **Link**
takes it, and **Other…** opens the same choices. **Link N suggested…** reviews every suggestion the search finds, and links those you keep
in one go.

A new account's custodian starts as the connection's brokerage and its type as the account type
SnapTrade reports; change or clear either before you create it. Give it an owner or a note
afterwards, with **Edit** on the **Accounts** tab.

The plugin sends the link for you, and the deployment checks you are a deployment admin and that
the plugin reported that account. A plugin's health on the **Plugins** tab counts the accounts it
reaches that nothing links.

## To end someone's terminal sessions

The **Terminal sessions** tab lists who is signed in from a terminal with `meridian connect`. Choose
**End them** on a person's row and confirm. Their CLI has to sign in again.

## What people see

On the dashboard's home page, each person sees the plugins they hold access to. A deployment admin
sees every launched plugin. A plugin page opens only for someone with access to at least one
account through it, or a deployment admin.

## Related

- [Plugins, roles and grants](../concepts/plugins.md): roles, and what a plugin may do.
- [Recover administration](recover-administration.md): if nobody can open Settings.
