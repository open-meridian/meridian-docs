# Tutorials

A guided path, each step a walkthrough you run yourself with the output you should expect. Start
with [Your first plugin](../getting-started/first-plugin.md), then follow the steps in order. The
first two need a deployment installed with `--development`; see
[Build with an AI agent](../getting-started/build-with-an-ai-agent.md). Each needs SDK 0.35.5,
CLI 0.1.58 and a deployment on chart 0.1.408.

| Step | Tutorial | What you learn |
|---|---|---|
| 1 | [Change your plugin's page, live](change-the-page-live.md) | Edit the reference plugin's pages, watch each save run, break it on purpose, fix it, and release. |
| 2 | [Record a holdings statement](record-a-holdings-statement.md) | A plugin with the `custody` role that records a holdings statement and a holding against one of your accounts. |
| 3 | [Structure a plugin](structure-a-plugin.md) | One class per role, the SDK's helpers for what every plugin of a role does alike, settings and secrets declared once, and tests that hold each class to its role's suite. |
| 4 | [Fast data retrieval](fast-data-retrieval.md) | Subscriptions instead of polling, the lake's hot layer and `from_memory`, latest and listing reads, asking only for what a page shows, batching, and never reading again per request. |
| 5 | [Build a live page](live-pages.md) | Values worked out from views with `pages.live_values` and `LiveValue`: source, age, staleness counted only in session with `FX_WEEK`, a bounded update rate, and never a blank cell. |
| 6 | [Analytics](analytics.md) | The engine's measures rather than your own, worked out on change or on a cadence, kept per key, and off the request path. |
