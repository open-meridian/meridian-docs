# How-to guides

Short recipes for one task each. They assume you have a deployment; if not, start with
[Install a deployment](../getting-started/installation.md).

| Guide | Use it to |
|---|---|
| [Choose how people sign in](choose-sign-in.md) | Pick OpenID Connect, LDAP or accounts the deployment holds, and answer the wizard for it. |
| [Give people access](administer-access.md) | Set up accounts, groups and permissions in the dashboard's Settings, and make a plugin's admins. |
| [Reset a lost password](reset-a-lost-password.md) | Get a local administrator back in with a code from the platform. |
| [Recover administration](recover-administration.md) | Get back in when nobody can administer the deployment. |
| [Build a plugin's page](build-a-plugin-page.md) | Declare each page with the levels it serves, link the plugin UI kit, link external accounts with `om-account-map` at any scale, fit a page to a phone, and sit well in the dashboard's frame, with header actions and status. |
| [Prove your plugin against a released runtime](prove-a-plugin-against-a-released-runtime.md) | Run your plugin on the plugin harness of a pinned runtime image, from `make e2e` and CI, and compare the street store with what you expect. |
| [Release a plugin version](release-a-plugin.md) | Ship a change to a plugin as a new version. |
| [Upgrade a deployment](upgrade-a-deployment.md) | Move a deployment to a newer chart, with the command line or your own pipeline. |
| [Remove or start over](remove-or-start-over.md) | Uninstall, reinstall, or retire a deployment. |
| [Troubleshoot an install](troubleshoot-install.md) | Match what you see to what it means and what to do. |
