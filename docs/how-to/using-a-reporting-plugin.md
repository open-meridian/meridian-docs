# Using a reporting plugin

A **reporting plugin** (the role `reporting`) reads what the deployment
holds, the book's positions and the lake's prices, and shows it: a
valuation, a board, a report. It records nothing in core. Every reporting
plugin has the same first-use path, the same Datasets page under Manage,
and the same "not set up yet" states; its reports, its whole value, are its
own. This page is that path, valid for every reporting plugin. Today there
is one, the sample reporting plugin (plugin-sample-reporting): see
[Value the book](value-the-book.md) and
[Watch the market on the Board](watch-the-board.md) for its pages.

The sample reporting plugin takes the common part: a Datasets page under
Manage, and the figures "Last valued" and "Not priced". Each person with
`write` saves their own Board, its watchlist and charts, as their own (see
[Your own Board](watch-the-board.md#your-own-board)). An **Orders** tab
under Open and View (`read_orders`) lists the orders in the accounts you may
read, newest first, one line each: account, instrument, side, ordered,
filled, state, and who decided and who executed it. An order opens to its
history (`read_order_history`), each step with who took it and when. It
records nothing. Its suite's two calendar cases are not presented, with
why: it values at a business date's prices as the lake holds them, and
never reads a settlement calendar or asks for a settlement date.

## The first-use path

| # | Step | Whose | Where |
|---|---|---|---|
| 1 | **Choose its settings** | the plugin's admin | the plugin's **Settings**, under Manage |
| 2 | **Have it entitled to the data it reads** | a deployment admin | **Settings**, **Data sources**: entitle the plugin to the datasets it reads. See [License and entitle a dataset](license-and-entitle-a-dataset.md). |
| 3 | **Grant people read** | a deployment admin | access: a group holding `read` or `write` on the plugin over accounts. See [Give people access](administer-access.md). |
| 4 | **Read its reports** | people with `read` or `write` | its report pages, under Open or View |

Core's **Setting up**, on the plugin's **Summary**, judges the first three from its own records: every
required setting set; the plugin entitled to at least one dataset, linking
a deployment admin to Data sources; and a group holding `read` or `write`
on it over an account group, linking to its **Access** tab. To anyone but a
deployment admin the last two read "Ask a deployment admin to ...". See
[Using a data plugin](using-a-data-plugin.md#setting-up-on-the-summary) for
how the part reads.

## Its settings

**Reporting currency** (`reporting_currency`), the ISO 4217 code its reports
value in: every reporting plugin values what the firm holds, so in a
currency. Then the plugin's own.

## Each person's own views

A reporting plugin may declare settings that are **each person's own** (`per_person`), such as a watchlist
or a saved chart, so the three access levels read:

| Level | What the person does |
|---|---|
| `admin` | Chooses the data and accounts the plugin may use, within the deployment admin's grant, and designs the shared dashboards, on its **Settings** |
| `write` | Builds and saves their own views, per person, on the plugin's pages under **Open** |
| `read` | Sees the admin's shared dashboards, under **View** |

A person's own views are not on the Settings form. They save them on the
plugin's pages; the dashboard keeps them under that person, hands them back
with each of their requests, and records each change, shown to them alone.
No other person reads them, a deployment admin included, and no tool does.
An agent a person has delegated to saves the person's own views through the
plugin's own tool for that page, within what the deployment lets agents do
with it. See [Access](../concepts/access.md#admin-shares-write-keeps-ones-own-read-sees-what-is-shared).

## Its pages

Under **Manage**:

- **Datasets** (`read_datasets`): each dataset it reads, whether it is
  entitled to it and to which fields, the priority a default read takes,
  and its misses. Before any entitlement: "Not entitled yet: a deployment
  admin entitles this plugin on Data sources".

Under **Open** and **View**, its main report first, then its others, each
with its tool, each following the common states: an as-of control where a
report is as of a day, "Nothing here for you" to someone who may read no
account, and the reporting currency named. A reporting plugin that sends
reports out adds **Sent**, what it sent as sent.

## Its figures

**Last valued** (a time; an error, with why, when the last valuation
failed) and **Not priced** (positions valued without a price, a warning
when any), then the plugin's own.

## Related

- [Value the book](value-the-book.md): the sample reporting plugin, and
  building your own.
- [Watch the market on the Board](watch-the-board.md).
- [Licences and entitlements](../concepts/licences-and-entitlements.md).
