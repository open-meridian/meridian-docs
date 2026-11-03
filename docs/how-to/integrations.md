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
the contract it is built on: every one is. The Federal Reserve
Bank of New York, US Treasury and FRED plugins record rates, which belong to
none of the asset classes, so an asset filter leaves them out; so are Pyth
Network's metals and commodities.

**Fixed income.** Terrapin's plugin records government par yield curves,
inflation index levels and municipal bonds' prints, and offers bonds' and
CDs' terms to their records. OpenYield's records its ATS's firm quotes, mids
and Treasury benchmark curve, and the TRACE and MSRB prints it resells. 9fin's,
listed as `ninefin`, offers bonds' terms and issuers and records their
new-issue prices. The Fannie Mae and Freddie Mac disclosures plugin
(`gse-disclosures`) and the Ginnie Mae disclosures plugin (`ginnie-mae`) record
each held pool's and REMIC class's monthly factor and offer the terms the same
files state, read from a location the deployment admin names, since the
agencies publish their files to registered users. Pyth Network's plugin records
composite prices with their confidence intervals and US Treasury par yields.
Each needs your own access with its service. See
[Bonds and fixed income](../concepts/bonds-and-fixed-income.md).

Each is listed in the platform's Community registry, and the five starter
packs, equities and options, FX, crypto, event contracts and multi-asset,
install several at once, from the dashboard's Browse or with one command: see
[Install a plugin from a registry](install-from-a-registry.md#a-starter-pack).

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
