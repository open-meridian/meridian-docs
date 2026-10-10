# How-to guides

Short recipes for one task each. They assume you have a deployment; if not, start with
[Install a deployment](../getting-started/installation.md).

| Guide | Use it to |
|---|---|
| [Choose how people sign in](choose-sign-in.md) | Pick OpenID Connect, LDAP or accounts the deployment holds, and answer the wizard for it. |
| [Give people access](administer-access.md) | Set up accounts, groups and permissions in the dashboard's Settings, and make a plugin's admins. |
| [Reset a lost password](reset-a-lost-password.md) | Get a local administrator back in with a code from the platform. |
| [Recover administration](recover-administration.md) | Get back in when nobody can administer the deployment. |
| [Set a plugin's settings](set-a-plugins-settings.md) | Fill a plugin's Settings form and each table's own tab, see who changed what, and declare a table setting and read its rows from code. |
| [Build a plugin's page](build-a-plugin-page.md) | Declare each page with the levels it serves, link the plugin UI kit, link external accounts with `om-account-map` at any scale, fit a page to a phone, and sit well in the dashboard's frame, with header actions and status. |
| [Prove your plugin against a released runtime](prove-a-plugin-against-a-released-runtime.md) | Run your plugin, and any plugins it needs beside it, on the plugin harness image published with a pinned runtime, from `make e2e` and CI, and compare the street store and the book with what you expect. |
| [Report the custodian's activity](report-the-custodians-activity.md) | Report each activity on an account from a custody plugin, once, back to the history's first date, and read it from an operations plugin to explain a break. |
| [Keep older records in the archive](keep-older-records-in-the-archive.md) | Name the archive at install, allow a plugin its archive with a bound, set holds and a plugin's windows, restore archived records, and upgrade SnapTrade to 0.13.0. |
| [Offer your pages to agents](offer-your-pages-to-agents.md) | Declare a route's inputs as one typed record so the SDK derives its tool on the deployment's MCP surface, answer typed data, refuse by path, and test it as an agent calls it. |
| [Let your agent manage a plugin's settings and archive](let-your-agent-manage-a-plugin.md) | Connect an agent that reads a plugin's Summary and settings, sets a value with a note, allows its archive, and launches and stops it, as you. |
| [Advising on tickets](advise-on-tickets.md) | Run an agent on a schedule that adds advice to open tickets, with the deployment's connector and nothing else, and the prompt to paste. |
| [Working your tickets](work-your-tickets.md) | Run an agent on a schedule that reads your inbox, advises where a change needs it, and tells you what waits for you, and the prompt to paste. |
| [Release a plugin version](release-a-plugin.md) | Ship a change to a plugin as a new version. |
| [Upgrade a deployment](upgrade-a-deployment.md) | Move a deployment to a newer chart, with the command line or your own pipeline. |
| [Remove or start over](remove-or-start-over.md) | Uninstall, reinstall, or retire a deployment. |
| [Troubleshoot an install](troubleshoot-install.md) | Match what you see to what it means and what to do. |
