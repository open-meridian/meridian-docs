# meridian-docs

The documentation for [Open Meridian](https://open-meridian.com), the
open-source OEMS, published at [open-meridian.dev](https://open-meridian.dev).

A [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) site.
Every push builds it with `mkdocs build --strict`, so a broken link fails the
build; a push to `main` publishes it to GitHub Pages.

## Working on it

```sh
pip install -r requirements.txt
mkdocs serve        # http://127.0.0.1:8000, reloading as you save
mkdocs build --strict
```

`mkdocs build --strict` is the whole gate: there is no Makefile here. To run it
as CI does, with nothing installed but Docker:

```sh
docker run --rm -v "$PWD":/docs -w /docs python:3.12-slim \
  sh -c "pip install -q -r requirements.txt && mkdocs build --strict -d /tmp/site"
```

Pages live under `docs/`, in the sections the navigation in `mkdocs.yml`
names: getting started, concepts, how-to, tutorials, API reference and the
developer guide. They are written from the code of
[meridian-core](https://github.com/open-meridian/meridian-core),
[meridian-cli](https://github.com/open-meridian/meridian-cli),
[meridian-python](https://github.com/open-meridian/meridian-python),
[meridian-schema](https://github.com/open-meridian/meridian-schema) and
[meridian-ui](https://github.com/open-meridian/meridian-ui); when those
change, the pages change with them. Today they describe CLI 0.1.21, SDK
0.10.0 (contract v5) and kit 0.7.0. A page describes what is built, and says so where
something is specified and not built yet.
