# Change your plugin's page, live

In this tutorial you make a plugin, run it live on a development deployment, change its page and see
the change in about a second. Then you break it on purpose, read the crash, fix it, and release the
result as a version.

This is the same loop a coding agent follows from `AGENTS.md`. Doing it once by hand shows you what
your agent is doing. Allow 15 minutes.

## What you need

- A deployment installed with `meridian up --development`. See
  [Install a deployment](../getting-started/installation.md).
- You are a deployment admin on it, and so an admin of every plugin through **All plugins (admin)**.
- The `meridian` CLI, 0.1.36 (`meridian --version`; `meridian upgrade` updates it), whose scaffold
  this page shows, on SDK 0.21.0 (0.22.0 from CLI 0.1.37 and 0.23.0 from CLI 0.1.38, with the
  same pages). Its pages and `--level` came with 0.1.21.
- Docker on this machine.
- Two terminals.

The examples use `https://meridian.localhost`, the deployment on this machine. For another, give
its address to `meridian connect`.

## 1. Sign in and make the plugin

```bash
meridian connect
meridian plugin new live-demo
cd live-demo
```

## 2. Start the live loop

In the first terminal, from `live-demo/`:

```bash
meridian plugin dev --instance live-demo
```

The first time, it builds and uploads the plugin, which takes a minute or two. Then it asks you to
approve what the plugin asks for. The reference plugin asks for nothing:

```text
live-demo 0.1.0 asks for
  roles: none
Launch it live as live-demo, with these? [y/N] y
Launched live-demo: live-demo 0.1.0.
Its page, if it serves one: https://meridian.localhost/plugins/live-demo
Watching . for live-demo. Ctrl-C stops watching; the instance keeps running.
r1 sent (10 files, 0 deleted)
r1 synced (10 sent, 0 deleted)
r1 restarted
r1 ready
```

Each line is an event with its **revision**, `r1`. `ready` means that revision is running and
connected to its sidecar. The file count depends on what is in the directory.

Leave this terminal running.

## 3. Look at the page

The reference plugin has two pages: **Setup**, at `/setup`, under Manage, and **Accounts**, at `/`,
under Open and View. You hold `admin` on it, so you look at Setup, at Manage.

In the second terminal, from `live-demo/`:

```bash
meridian plugin open --instance live-demo --level manage --print /setup
```

This prints the page at `/setup` exactly as you are served it in a Manage session. Among the HTML you
should see:

```html
<div><h1>Reference plugin</h1></div>
```

`--print` needs no browser and gives the same answer every time, so it is the best way to check a
change. Name the level: without `--level` it asks at the first level you hold, and a page serves
only the levels it is declared with, so `--print /` at Manage is refused with 403.

## 4. Change the page

Open `src/live_demo/page.py` and change the title, which the kit's base template draws as every
page's heading:

```python title="src/live_demo/page.py"
TITLE = "My live page"
```

Save the file. There is nothing to run: the save is the deploy. The first terminal shows:

```text
r2 sent (1 files, 0 deleted)
r2 synced (1 sent, 0 deleted)
r2 restarted
r2 ready
```

Print the page again:

```bash
meridian plugin open --instance live-demo --level manage --print /setup
```

```html
<div><h1>My live page</h1></div>
```

!!! tip
    Several saves close together can land as one revision. Always read the newest `sent` line.

## 5. Break it on purpose

In the same file, change the title line to use a name that does not exist:

```python title="src/live_demo/page.py"
TITLE = "My live page" + missing_name
```

Save. The first terminal shows the crash, with the end of the traceback:

```text
r3 sent (1 files, 0 deleted)
r3 synced (1 sent, 0 deleted)
r3 restarted
r3 crashed, exit 1
    Traceback (most recent call last):
    …
    NameError: name 'missing_name' is not defined
```

You can ask for the same from the second terminal. Both take the revision to start **after**:

```bash
meridian plugin events --instance live-demo --since 2
meridian plugin logs --instance live-demo --since 2
```

`events` shows what happened to revision 3. `logs` shows what the plugin printed after revision 2.

## 6. Fix it

Put the line back:

```python title="src/live_demo/page.py"
TITLE = "My live page"
```

Save. The next revision replaces the broken one. Nothing needs restarting:

```text
r4 sent (1 files, 0 deleted)
r4 synced (1 sent, 0 deleted)
r4 restarted
r4 ready
```

## 7. Open it in a browser

```bash
meridian plugin open --instance live-demo
```

It prints a link. Open it within a minute; it works once and signs that one browser in to this
plugin's page alone, at the first level you hold, Manage. The link lands on the plugin's `/`, which
the reference plugin serves only under Open and View, so the browser says
`/ is not served under Manage; it is for Open and View.` Go to `/setup` on the same address,
`https://live-demo.plugins.meridian.localhost/setup`, and reload as often as you like. The
dashboard's home opens the plugin with **Manage** onto its **Summary**, with its **Setup** tab after
**Summary** and **Settings**.

## 8. Release it

1. In the first terminal, press Ctrl-C. The instance keeps running:

    ```text
    Stopped watching. live-demo runs on, live: `meridian plugin stop live-demo` stops it.
    ```

2. In `pyproject.toml`, raise the version:

    ```toml title="pyproject.toml"
    version = "0.1.1"
    ```

3. Release:

    ```bash
    meridian plugin dev --release --instance live-demo
    ```

    Approve the roles when asked. It ends with:

    ```text
    Released live-demo 0.1.1 as sha256:…, and launched it as live-demo.
    ```

`live-demo 0.1.1` is now an ordinary version in the catalogue, running in place of the live
instance. `meridian plugin list` shows it.

## 9. Clean up

```bash
meridian plugin stop live-demo
```

## What you learned

- A save changes what the plugin does, in about a second, on the same pod and sidecar.
- `open --print`, `logs` and `events` answer "did my change work?" without a browser.
- A crash is just a revision. The next save replaces it.
- A release turns the directory into a version that is never replaced.

Next, [Record a holdings statement](record-a-holdings-statement.md) gives a plugin a role, so it
can write to the deployment. For the event format see
[plugin dev events](../api/plugin-dev-events.md).
