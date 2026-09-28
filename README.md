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

Pages live under `docs/`, in the sections the navigation in `mkdocs.yml`
names: getting started, concepts, how-to, tutorials, API reference and the
developer guide. The API reference is written from the code of
[meridian-cli](https://github.com/open-meridian/meridian-cli),
[meridian-python](https://github.com/open-meridian/meridian-python) and
[meridian-schema](https://github.com/open-meridian/meridian-schema); when
those change, it changes with them.
