# How-to guides

Short recipes for one task each. They assume you have a deployment; if not, start with
[Install a deployment](../getting-started/installation.md).

| Guide | Use it to |
|---|---|
| [Integrations](integrations.md) | See which plugins are released, the service each works with, and filter them by role, asset class, environment or status. |
| [Choose how people sign in](choose-sign-in.md) | Pick OpenID Connect, LDAP or accounts the deployment holds, and answer the wizard for it. |
| [Give people access](administer-access.md) | Set up accounts, their attributes in the book, groups and permissions in the dashboard's Settings, make a plugin's admins, grant a plugin the accounts it may link to, and give a plugin's work a service account. |
| [Reset a lost password](reset-a-lost-password.md) | Get a local administrator back in with a code from the platform. |
| [Recover administration](recover-administration.md) | Get back in when nobody can administer the deployment. |
| [Set a plugin's settings](set-a-plugins-settings.md) | Fill a plugin's Settings form and each table's own tab, see who changed what, and declare a table setting and read its rows from code. |
| [Build a plugin's page](build-a-plugin-page.md) | Declare each page with the levels it serves, link the plugin UI kit, link external accounts with `om-account-map` at any scale, fit a page to a phone, search a list and show a field only when it applies, and sit well in the dashboard's frame, with header actions and status. |
| [Prove your plugin against a released runtime](prove-a-plugin-against-a-released-runtime.md) | Run your plugin, and any plugins it needs beside it, on the plugin harness image published with a pinned runtime, from `make e2e` and CI, and compare the street store and the book with what you expect. |
| [Report the custodian's activity](report-the-custodians-activity.md) | Report each activity on an account from a custody plugin, once, back to the history's first date, and read it from an operations plugin to explain a break. |
| [Keep older records in the archive](keep-older-records-in-the-archive.md) | Name the archive at install, allow a plugin its archive with a bound, set holds and a plugin's windows, and restore archived records. |
| [License and entitle a dataset](license-and-entitle-a-dataset.md) | Confirm a dataset's licence, entitle the plugins that read it, and set the source priority, on the Data sources page or through its tools. |
| [Using a data plugin](using-a-data-plugin.md) | Set up any data plugin by its one first-use path (enter the key, check Connection, license and entitle its datasets, see data arrive), read its common pages, and see what Alpaca, Tradier, Tiingo, Coinbase, Kraken, the Federal Reserve Board, the New York Fed, US Treasury, FRED and the ECB each serve, with their terms, summarised. |
| [Using a custody plugin](using-a-custody-plugin.md) | Set up any custody plugin: enter its credentials, connect, have accounts granted, link them, and see statements, and trade through SnapTrade. |
| [Using an operations plugin](using-an-operations-plugin.md) | Set up any operations plugin: its settings, access and a street source, opening balances, reconciliation and breaks. |
| [Using a reporting plugin](using-a-reporting-plugin.md) | Set up any reporting plugin: its settings, its entitlements to the data it reads, people's access, and each person's own views. |
| [Add a prediction-market plugin](add-a-prediction-market-plugin.md) | Launch Kalshi or Polymarket, which need no key, and complete their contracts' records as binary event contracts, their outcomes, and Polymarket US. |
| [Write a data plugin against its suite](write-a-data-plugin.md) | Start a data plugin from `plugin new --role data`, declare its catalogue, convert at the edge, answer wants, record trades and quotes, backfill a restart's gap, keep the role's common pages, and pass the data suite, marking what your source never publishes. |
| [Write a pricing plugin](write-a-pricing-plugin.md) | Start a pricing plugin from `plugin new --role pricing`, write a model over a batch's market objects, pass the pricing suite, and have a deployment admin route a model id to it. |
| [Record rates in a data plugin](record-rates.md) | Record a rates publisher's fixings, averages, index levels and curves with `meridian.roles.data.rates`, and pass the data suite's rates cases. |
| [Record and read an option chain](record-and-read-an-option-chain.md) | Record an underlying's listed series, open interest and chain quotes from a data plugin, read the chain from a reading plugin, ask for a series' record before an order, and run the options measures over it. |
| [Set staleness thresholds and the stale-reference action](set-staleness-thresholds.md) | Set each dataset's **Stale after**, whether the deployment permits a desk to warn, an `ems`'s own ceiling and whether it refuses or warns, and record liveness and check the reference price in a plugin. |
| [Set the FX pivot currencies](set-the-fx-pivot-currencies.md) | Order the fiat currencies a valuation crosses through, at the dashboard or through its tool. |
| [Run a TCA job and read its costs](read-execution-costs.md) | Measure an account's fills against the standard benchmarks with an `execution_cost` job, and read the costs back from a plugin or through an agent. |
| [Read trades and quotes in a `signal` or `ems` plugin](read-trades-and-quotes.md) | Read a day's trades, hear each new one, catch up after a watermark, read the latest quotes, and pass the `signal` or `ems` suite. |
| [Value the book](value-the-book.md) | Set up the sample reporting plugin, which values the book at a date's prices, consolidated and by account, in any reporting currency, and read how it prices each position; or build your own. |
| [Watch the market on the Board](watch-the-board.md) | Set the sample reporting plugin's watchlist and read its Board, a calm view of the latest prices from every source side by side, on the page or through `read_board`. |
| [Offer your pages to agents](offer-your-pages-to-agents.md) | Declare a route's inputs as one typed record so the SDK derives its tool on the deployment's MCP surface, answer typed data, refuse by path, and test it as an agent calls it. |
| [Let your agent manage a plugin's settings and archive](let-your-agent-manage-a-plugin.md) | Connect an agent that reads a plugin's Summary and settings, sets a value with a note, allows its archive, and launches and stops it, as you; or prepares the change for you to make. |
| [Run a plugin's autonomous work as a service account](run-a-plugins-work-as-a-service-account.md) | Create a service account with its owner and setting, grant it on a plugin's role, choose what the role runs as, and watch it and stop it as its owner. |
| [Route orders through a connectivity plugin](route-orders-through-a-connectivity-plugin.md) | Make a connectivity plugin available, grant an `ems` its accounts, link the plugin to the `ems` and choose who may route through it, and map each account to its venue account code. |
| [Answer a venue-originated fill](answer-a-venue-originated-fill.md) | Accept a fill the venue reports on no order to an order or a new one, or answer it DK with a reason, at the `ems` plugin's page or through its tools; and report and answer one in a plugin. |
| [Place manually or by RFQ](place-manually-or-by-rfq.md) | Place a trade agreed by phone as a manual placement with its evidence, and work an order by RFQ, picking a dealer's quote. |
| [Net FX orders](net-fx-orders.md) | Propose a net of opposite FX orders on one pair and value date from an `oms`, record the offset as internal crosses, and book it. |
| [Set trading instructions and whether releases wait](set-trading-instructions.md) | Set active, pause or stop on an account, every account, a plugin, a person or a service account, and say whether an account's releases wait for compliance, at the page or through their tools; and allow or refuse orders on local records. |
| [Advising on tickets](advise-on-tickets.md) | Run an agent on a schedule that adds advice to open tickets, with the deployment's connector and nothing else, and the prompt to paste. |
| [Working your tickets](work-your-tickets.md) | Run an agent on a schedule that reads your inbox, advises where a change needs it, and tells you what waits for you, and the prompt to paste. |
| [Write a plugin's documentation](write-a-plugins-documentation.md) | The sections a deployment admin reads before launching a plugin, declared with the version, checked by `plugin check` and uploaded with it. |
| [Release a plugin version](release-a-plugin.md) | Ship a change to a plugin as a new version. |
| [Publish a plugin to a registry](publish-a-plugin.md) | Sign a release tag, and have the platform build, check and list it in the Community registry as `namespace/plugin`. |
| [Install a plugin from a registry](install-from-a-registry.md) | Find a listed plugin, install it by digest at the dashboard or with `meridian plugin install`, install and keep a starter pack from Browse or with `meridian plugin pack`, update it, and carry one into a deployment that reaches nothing. |
| [Upgrade a deployment](upgrade-a-deployment.md) | Move a deployment to a newer chart, with the command line or your own pipeline. |
| [Review provisional records and the migration](review-provisional-records.md) | See each provisional record and why it waits on the Instruments page's Provisional tab, apply the upgrade's migration and hold a line back, and set the usage report. |
| [Back up and restore a deployment](back-up-and-restore.md) | Make the identity backups are sealed to, back up on a schedule or now, and restore a backup into an empty namespace. |
| [Remove or start over](remove-or-start-over.md) | Uninstall, reinstall, or retire a deployment. |
| [Troubleshoot an install](troubleshoot-install.md) | Match what you see to what it means and what to do. |
