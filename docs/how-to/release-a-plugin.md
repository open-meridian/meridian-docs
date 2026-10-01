# Release a plugin version

A plugin reaches a deployment as a **version**: the `version` in its `pyproject.toml`, uploaded to
the deployment's catalogue. A version is never replaced. To ship a change, raise the version and
upload again.

A new version is also the only way to change what a plugin **may** do, or what it **depends on**:

- New roles in `[tool.meridian]`. The person launching it approves them again.
- New packages in `dependencies`. Live code runs on the image it was launched from.

## To release from a development deployment

Use this when the plugin is running live under `meridian plugin dev`.

1. Run `meridian plugin check --run-tests`, and fix what it names until it passes.
2. Raise `version` in `pyproject.toml`, for example from `0.1.0` to `0.2.0`.
3. From the plugin's directory, run:

    ```bash
    meridian plugin dev --release --instance my-plugin
    ```

4. Read the roles it shows, and answer `y` to approve.

It uploads the directory as it is now, as that version, stops the live instance and launches the
version in its place:

```text
Released my-plugin 0.2.0 as sha256:…, and launched it as my-plugin.
```

It is now an ordinary version in the catalogue, launched the ordinary way.

!!! note
    If you forget step 2, the release is refused: the version is recorded already, and a version is
    never replaced. Raise it and release again.

## To release to any deployment

Use this for a deployment that is not for development, or when the plugin is not live.

1. Run `meridian plugin check --run-tests`, and raise `version` in `pyproject.toml`.
2. Upload it:

    ```bash
    meridian plugin upload
    ```

3. Stop the running instance:

    ```bash
    meridian plugin stop my-plugin
    ```

4. Launch the new version under the same instance name, and approve what it asks for:

    ```bash
    meridian plugin launch my-plugin 0.2.0 --instance my-plugin
    ```

5. Check it:

    ```bash
    meridian plugin list
    ```

Keeping the instance name keeps what was granted against it: access groups and external account
links name the instance, not the version.

## To move a plugin to a newer SDK

A plugin pins one release of the SDK, in `pyproject.toml` and in its `Dockerfile`. To move it to a
newer one, from its directory, with its changes committed:

```bash
meridian plugin migrate
```

It moves both pins, rewrites what each release in between changed, runs `meridian plugin check`, and
lists what is left to do by hand, with the file and line. Review the diff, then release as above.
See [`meridian plugin migrate`](../api/cli.md#plugin-migrate).

## To move a plugin to another deployment

Each deployment has its own catalogue. To take a plugin from your development deployment to your
firm's:

1. Sign in to the other deployment too:

    ```bash
    meridian connect https://meridian.firm.example
    ```

2. With more than one session held, name the deployment on each command:

    ```bash
    meridian plugin upload --deployment https://meridian.firm.example
    meridian plugin launch my-plugin 0.2.0 --instance my-plugin --deployment https://meridian.firm.example
    ```

The firm's deployment admin approves the roles at launch.

## Related

- [Plugin manifest](../api/plugin-manifest.md): the keys in `[tool.meridian]`.
- [Command line](../api/cli.md): every `meridian plugin` flag.
- [Build with an AI agent](../getting-started/build-with-an-ai-agent.md): the live loop.
- [Prove your plugin against a released runtime](prove-a-plugin-against-a-released-runtime.md):
  an e2e check of the version before you release it.
