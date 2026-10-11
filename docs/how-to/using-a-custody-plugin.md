# Using a custody plugin

A **custody plugin** (the role `custody`) reads what a broker or custodian
says your accounts hold, and records it as the custodian's view in the
deployment: statements, holdings, cash and each account's activity. Every
custody plugin has the same first-use path, the same pages in the same
order, and the same "not set up yet" states naming the next step. This page
is that path, valid for every custody plugin. Today there is one,
[plugin-snaptrade](https://github.com/open-meridian/plugin-snaptrade), so
where this page names a setting or a page only SnapTrade has, it says so.

!!! note "Contract v20"
    The common part is in open-meridian 0.24.0 (contract v20), the kit
    0.12.0 and core's **Setting up**, and the account grants in core,
    released 2026-10-12 in chart 0.1.298. SnapTrade 0.14.0, released
    2026-10-12, is built on open-meridian 0.24.0 and runs on chart
    0.1.298 or later. It takes the common part: its **Raw responses**
    page titled **Raw records**, its **+ Add** reading **Connect**, and its
    `synthetic` setting renamed `sample_data`; it links only to the accounts
    granted to it, and every act names its check tool. SnapTrade 0.13.1 is
    built on contract v18.

## The first-use path

| # | Step | Whose | Where |
|---|---|---|---|
| 1 | **Enter the credentials** | the plugin's admin | the plugin's **Settings**, under Manage |
| 2 | **Connect** | the plugin's admin | the plugin's **Connections** page: connect the custodian, through the vendor's own portal where it has one |
| 3 | **Have accounts granted** | a deployment admin | the plugin's **Accounts** tab in the dashboard's admin view: the firm's accounts this plugin may link to. See [To grant a plugin accounts to link](administer-access.md#to-grant-a-plugin-accounts-to-link). |
| 4 | **Link accounts** | the plugin's admin | the plugin's **Account links** page: each of the custodian's accounts to one of those granted |
| 5 | **See statements** | people with `read` or `write` on the accounts | the plugin's **Statements** page, under Open or View |

### Setting up, on the Summary

From contract v20 core draws **Setting up** on the
plugin's **Summary**, first under its status while any step is undone, each
step linking to where it is done, from core's own records:

- **Enter the credentials**: every required secret is set.
- **Connect**: core has heard an external account's sync state.
- **Have accounts granted**: at least one account is granted to the
  instance. To anyone but a deployment admin it reads "Ask a deployment
  admin to have accounts granted".
- **Link accounts**: no external account the plugin reported is unlinked.

Seeing statements is the Statements page's own to say. When every step is
done the part folds to **Set up**. See
[Using a data plugin](using-a-data-plugin.md#setting-up-on-the-summary) for
how the part reads.

## Its settings

In this order on every custody plugin: the credentials, each a secret
labelled in the vendor's own words (SnapTrade's **Client ID**, **Consumer
key** and **User secret**); where the custodian is read on a schedule, **Read
every** (`poll_seconds`) and **Stale after** (`stale_after_hours`); the
vendor's own settings (SnapTrade's **Key type**, with **User ID** shown for
the key type that needs it, and its **Plan-code links** and **Cash links**
tables); its raw records' windows; and **Sample data**, on a development
deployment only. A secret's field says where it stands, never its value:
see [Set a plugin's settings](set-a-plugins-settings.md#a-secret).

## Its pages

Under **Manage**, in first-use order:

- **Connections** (`read_connections`): a row each, the connection, its
  state and whose fix it is, the accounts it reaches and when it was last
  read, with **Refresh** and **Reconnect** on a row where the vendor allows,
  and **Connect** in the section's head where the vendor connects through a
  portal of its own. Before any credential: "No credentials yet: enter them
  in Settings".
- **Account links** (`read_account_links`, linking with `link_account`): the
  custodian's accounts beside the accounts granted to the plugin, each
  linked with **Link**. Before any grant: "No accounts granted yet: a
  deployment admin grants this plugin the accounts it may link to". See
  [To link an external account](administer-access.md#to-link-an-external-account).

Under **Open** and **View**, the page you return to daily first:

- **Statements** (`read_statements`): a row for each account you may read,
  its custodian, as of, and its state (open, closed, or withheld, with why),
  each row naming its raw record. Before any link: "No statements yet: an
  account appears once it is linked, under Account links".
- **History** (`read_account_activities`): the custodian's activity per
  account, as reported: account, trade date, settlement date, kind,
  instrument, units, amount and description. "No activity yet" before any.
- **Raw records**: each kind of raw record kept, its window and the
  archive, and a raw record followed from a row's reference. See
  [Keep older records in the archive](keep-older-records-in-the-archive.md).

## Its figures

**Connections** (how many, a warning when any needs attention), **Accounts
reached** and **Last read** (an error, with the reason, when the last read
failed): SnapTrade's three, now every custody plugin's.

## For an agent

Each page is a tool under the role's name, so an agent that knows one
custody plugin knows the next: `<instance>__read_connections`,
`read_account_links`, `link_account`, `read_statements` and
`read_account_activities`. Linking is an act: from contract v20 the
deployment admin and the plugin's admin set whether a person's agent may
make it, only prepare it, or not reach it; see
[Prepared changes](../concepts/prepared-changes.md). From SnapTrade 0.14.0
each of its acts names its check tool (`check_link_account`,
`check_open_connection_portal`, `check_refresh_connection`,
`check_reconnect_connection` and `check_snaptrade_now`), so each can be
prepared; under an act's second pair of eyes its button prepares it.
SnapTrade 0.13.1's acts name no check tool, so they can be left at "may
make" or set to "may not", not prepared.

## Related

- [Accounts](../concepts/accounts.md): the firm's accounts, external
  accounts, and the accounts a plugin may link to.
- [The custodian's activity](../concepts/the-custodians-activity.md).
- [Report the custodian's activity](report-the-custodians-activity.md).
- [Keep what your custody plugin converts](keep-what-the-edge-converts.md):
  writing one.
