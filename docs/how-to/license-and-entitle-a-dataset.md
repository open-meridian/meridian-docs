# License and entitle a dataset

A data plugin (one holding `dgm`) puts its vendor's prices into the
deployment's [lake](../concepts/the-lake.md), each in a dataset its catalogue
declares. Before another plugin can read a dataset, a deployment admin
entitles it; and the admin confirms or changes the terms the lake keeps it
on, its licence. Both are on the dashboard's **Data sources** page, and
through its tools for an agent. What each term means is in
[Licences and entitlements](../concepts/licences-and-entitlements.md).

!!! note "Contract v18"
    This page describes contract v18, core's lake and the Data sources page,
    from chart 0.1.292.

You need the deployment admin's capabilities, and a data plugin launched:
its datasets are listed from the moment it runs. See
[Add a data plugin's key](add-a-data-plugins-key.md).

## Open the page

In the dashboard, open **Settings**, then **Data sources**, beside
**Instruments**. It has three tabs, each a page of one-line rows:

| Tab | One row per |
|---|---|
| **Datasets** | dataset a launched data plugin's catalogue declares: its ID (`alpaca-1:daily`), its vendor (and aggregator), what it serves, the licence enforced, how many plugins are entitled to it, how many of its values were left unconverted, and how many identifiers and venues its plugin reported missing |
| **Entitlements** | plugin entitled to a dataset, with the fields it may read, who set it and when |
| **Priority** | data type and price kind, with the datasets a default read takes first to last |

The page shows no price: prices are read by the plugins entitled to them, on
their own pages.

## Confirm or change a dataset's licence

Until you set one, a dataset is on its catalogue's default, the vendor's
standard terms as its plugin declares them, and the **Licence** column says
so on hover. To set the deployment's own:

1. On the dataset's row, select **Licence**.
2. Tick or clear each term: **The lake may keep its rows** (cleared, they
   are served, not kept), **Derived data may be made**, **It may be shown**,
   and **Its terms are one person's**.
3. **Kept for, in days**: 0 keeps rows with no limit set; at most 36,500.
4. **Fields readable by default**: leave it empty for every field, or list
   dictionary entries, such as `meridian.v1.Bar.vwap`.
5. Add a **Note** saying why, and **Save**.

The licence replaces the one before it whole, and is its own record naming
you. It records what you entered; it does not say the deployment meets the
vendor's terms.

A dataset whose terms are one person's shows **one person's** beside its
licence when more than one person holds `read` or `write` on a plugin
entitled to it; hover it for their names. It warns and refuses nothing: to
clear it, narrow who holds access to the entitled plugins (see
[Give people access](administer-access.md)), or withdraw an entitlement.

## Entitle a plugin

1. On the dataset's row, select **Entitle**.
2. **Plugin instance**: the running instance that may read it, such as
   `my-report-1`.
3. Keep **It may read the dataset** ticked.
4. **Fields**: leave it empty for every field, or list dictionary entries of
   the dataset's types, such as `meridian.v1.Price.price`.
5. Add a **Note**, and **Save**.

Its deliveries follow at once. To change the fields, select **Edit** on its
row in **Entitlements**; to withdraw it, **Withdraw**, and its deliveries
stop.

## Set a source priority

A reader that names no dataset reads the deployment's default for the data
type and, for prices, the kind. With none set, it takes the datasets in the
order the lake lists them.

1. On **Priority**, select **+ Add**, or a row's **Edit** to change one.
2. **Data type**: Price or Bar. **Kind, for prices**: Close, Last, NAV or
   Settlement; none for bars.
3. **Datasets, first to last, one a line**: at most 16, each declaring the
   data type.
4. Add a **Note**, and **Set**.

The priority is replaced whole. If someone changed it after you opened the
dialog, it is refused: read it again and redo the change.

## Or ask your agent

The same acts are five tools on the deployment's MCP surface, listed to a
delegation covering the deployment admin's capabilities. Each change needs a
note. See [Core's tools](../api/core-tools.md#the-data-sources-page).

| To | Tool |
|---|---|
| Read the datasets, their licences, entitlements, counts and warnings | `dashboard__list_datasets` |
| Set a licence | `dashboard__set_dataset_licence` |
| Entitle a plugin, or withdraw it | `dashboard__set_dataset_entitlement` |
| Read the priorities | `dashboard__list_source_priorities` |
| Set a priority, against its `updated_at_ns` as read | `dashboard__set_source_priority` |

A delegation covering the deployment admin's capabilities reaches all five.
One narrowed before contract v18 keeps, from its first use after the
upgrade, every tool it reaches then, these among them; from then on, a tool
that changes something and arrives later waits until you consent again from
that client.

## Related

- [Licences and entitlements](../concepts/licences-and-entitlements.md).
- [The lake](../concepts/the-lake.md): datasets, default reads and wants.
- [Add a data plugin's key](add-a-data-plugins-key.md): Alpaca and Tradier.
