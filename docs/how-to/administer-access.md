# Give people access

Who may do what in a deployment is set on the dashboard's **Administer this deployment** page. Only
a deployment admin can open it.

A **permission** joins three things:

| Part | Answers | Made of |
|---|---|---|
| User group | Who | Directory groups, or logins |
| Account group | On which accounts | The firm's accounts |
| Access group | Using what | Plugins' parts, at `read` or `write` |

So a permission reads: *the people in this user group, using these plugins' parts, on these
accounts.* See [Access](../concepts/access.md) and [Accounts](../concepts/accounts.md) for the model.

## To open the Administer page

1. Sign in to the dashboard.
2. On the home page, choose **administer this deployment**. It is at `/admin`.

The page has seven tabs: **Permissions**, **User groups**, **Account groups**, **Access groups**,
**Accounts**, **External accounts** and **Terminal sessions**. Every change is recorded with who made
it. If a change is refused, the page says why; choose **Back** to return to what you typed.

## To add an account

1. Open the **Accounts** tab and choose **New account**.
2. Enter a **Name** and choose **Create**.

To rename one, choose **Rename** on its row. To close one, choose **Close**. A closed account is kept,
and nobody works in it. Accounts are never deleted.

## To group accounts

1. Open **Account groups** and choose **New account group**.
2. Enter a **Name** and tick the accounts it holds.
3. Choose **Create**.

To change it later, choose **Edit** on its row.

## To say who: make a user group

1. Open **User groups** and choose **New user group**.
2. Enter a **Name**.
3. Fill in one or both:
    - **Directory groups, one per line.** Someone is in the user group when their directory says they
      are in one of these. An LDAP group is a full distinguished name, such as
      `cn=traders,ou=groups,dc=firm,dc=internal`.
    - **Logins, one per line.** For an account the deployment holds itself, a login is
      `local|name`.
4. Choose **Create**.

!!! note
    A directory states a person's groups when they sign in. A change in your directory reaches Open
    Meridian at that person's next sign-in.

## To say what: make an access group

An access group lists parts of plugins, each at `read` or `write`. A part is one of a plugin's roles
or one of its tags, as its `pyproject.toml` declares them.

1. Open **Access groups** and choose **New access group**.
2. Enter a **Name**.
3. Under **Entries, one per line**, write each as `<plugin instance> <part> read` or
   `<plugin instance> <part> write`. For example:

    ```text
    snaptrade-1 holdings read
    my-plugin reports write
    ```

4. Choose **Create**.

The plugin instance must be running and have reported to the deployment, and it must carry the part
you name. If not, the page says so, for example that the plugin does not carry the part and lists
what it does carry.

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

1. Open **External accounts** and choose **Link an external account**.
2. Enter the **Plugin instance**, for example `snaptrade-1`. It must be running and have reported.
3. Enter the **External account**, as the plugin names it.
4. Choose the **Account** it is. **None (unlink)** removes a link.
5. Choose **Link**.

## To end someone's terminal sessions

The **Terminal sessions** tab lists who is signed in from a terminal with `meridian connect`. Choose
**End them** on a person's row and confirm. Their CLI has to sign in again.

## What people see

On the dashboard's home page, each person sees the plugins they hold a part of. A deployment admin
sees every launched plugin. A plugin page opens only for someone with access to at least one
account through it, or a deployment admin.

## Related

- [Plugins, roles and grants](../concepts/plugins.md): roles, tags and what a plugin may do.
- [Recover administration](recover-administration.md): if nobody can open this page.
