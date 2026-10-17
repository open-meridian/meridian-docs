---
hide:
  - toc
---

# Integrations

The plugins released for Open Meridian, and the service each one works with.
Filter them by role, asset class or environment: the page's address
keeps your choice, so a link such as
[`?asset=fx&role=connectivity`](?asset=fx&role=connectivity){ .om-nowrap } opens on the FX
plugins that place orders.

!!! info "What a deployment can hold"
    From day one a deployment's instruments are every security eligible for a
    FIGI, an open identifier, plus currencies by their ISO 4217 code, crypto
    assets by their CAIP-19 identifier, and binary event contracts. Anything
    outside that universe still shows in a deployment, as a local record with
    no price.

Each plugin works with a third-party service. You bring your own account
with that service, and your own key where it asks for one, and the
service's own terms apply. Open Meridian is not affiliated with or endorsed
by any service listed here.

<!-- integrations -->

Only released plugins are listed. **Sample data** is a developer's setting,
offered on a development deployment. **Version** is the plugin's release and
the contract it is built on. Most are on contract 25. OANDA stays on its
current release until it moves to contract 25; Kalshi, Polymarket and
Polymarket US stay on contract 23 and move with contract 26, once core's
plugin harness mints event contracts. A deployment on contract 25 runs
plugins built on earlier contracts.

**Request a plugin.** For a service not listed here, open an issue with
**Suggest an improvement** on
[meridian-core](https://github.com/open-meridian/meridian-core/issues), or
build the plugin yourself, starting with
[Your first plugin](../getting-started/first-plugin.md).

## Related

- [Plugins, roles and grants](../concepts/plugins.md): what a plugin is, and
  the roles it may hold.
- [Using a data plugin](using-a-data-plugin.md), [Using a custody
  plugin](using-a-custody-plugin.md) and [Route orders through a
  connectivity plugin](route-orders-through-a-connectivity-plugin.md): setting
  each kind up.
- [Instruments](../concepts/instruments.md): how a deployment names what it
  holds.
