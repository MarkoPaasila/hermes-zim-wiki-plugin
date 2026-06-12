# Changelog

All notable changes to this project are documented here. Newest entries appear first.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Version numbers follow [VERSIONING.md](VERSIONING.md) (`YYYY.MM.DD.N`).

## [2026.06.13.1] - 2026-06-13

### Fixed

- Zim API unavailable when Hermes runs on a different Python than the system Zim package (e.g. Hermes 3.11 vs Arch Zim on 3.14): notebook operations now fall back to a discovered Zim-capable interpreter via `zim_worker.py`
- `/zim` status and tool errors now report the active Python interpreter, import error, and optional `ZIM_PYTHON` override instead of a generic install hint

## [2026.06.13.0] - 2026-06-13

### Added

- Hermes plugin scaffold with `plugin.yaml`, tool registration, and bundled skill `zim-wiki:zim-wiki`
- Seven non-LLM tools backed by the Zim Desktop Wiki Python API:
  - `zim_list_pages` — index-backed page listing with optional namespace prefix
  - `zim_read_page` — read wiki markup via `Page.dump('wiki')`
  - `zim_search` — Zim query language (Content:, Name:, Tag:, LinksTo:, …)
  - `zim_write_page` — update existing pages via `parse` + `store_page`
  - `zim_get_links` — forward, backward, and bidirectional link queries
  - `zim_list_tags` — tags on a page, pages with a tag, or all tags
  - `zim_create_page` — create pages or append to existing ones
- `notebook_client/` package: session management, index sync, pages, search, links, tags
- `/zim` slash command for notebook status
- Calendar versioning scheme (`YYYY.MM.DD.N`) and `hermes_zim_wiki_plugin/_version.py` as canonical version
- Integration tests (pytest) and version consistency checks
- GPL-2.0 license
- `scripts/build-plugin.sh` — build installable packages (pip wheel/sdist and directory tarball for `~/.hermes/plugins/`)

### Changed

- Replaced hand-rolled filesystem I/O with full Zim API integration (`build_notebook`, index views, `NotebookState`)
- Renamed internal package from `zim/` to `notebook_client/` to avoid clashing with Zim's top-level `zim` module
- GPL-2.0-only license: copyright header on `LICENSE`, v2-only wording (aligned with Zim), SPDX metadata and `license-files` in `pyproject.toml`

### Documentation

- README with prerequisites (system Zim install, `ZIM_NOTEBOOK_PATH`), install paths, and tool overview
- README rsync install instructions for local and remote deployment
- README rsync excludes for Python cache and dev artifacts (aligned with `scripts/build-plugin.sh`)
- README Hermes CLI and dashboard install via `hermes plugins install` (GitHub subdirectory path)
- README License section linking to `LICENSE`
- [VERSIONING.md](VERSIONING.md) describing release numbering and where to bump versions

[2026.06.13.1]: https://github.com/MarkoPaasila/hermes-zim-wiki-plugin/releases/tag/2026.06.13.1
[2026.06.13.0]: https://github.com/MarkoPaasila/hermes-zim-wiki-plugin/releases/tag/2026.06.13.0
