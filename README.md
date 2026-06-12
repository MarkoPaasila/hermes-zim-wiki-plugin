# hermes-zim-wiki-plugin

Hermes Agent plugin for reading and writing [Zim Desktop Wiki](https://zim-wiki.org/) notebooks via the **Zim Python API**.

**Version:** `2026.06.13.0` — see [VERSIONING.md](VERSIONING.md) for the release scheme. Release history: [CHANGELOG.md](CHANGELOG.md).

## Goal

Enable Hermes Agent to interact with a Zim Desktop Wiki repository through **non-LLM tools** — deterministic handlers that query, search, and read notebook contents, and modify or write pages in a way that respects the Zim on-disk format (headers, paths, and wiki structure). The agent should rely on these tools for notebook I/O instead of ad-hoc file edits or model-generated guesses about Zim conventions.

## Prerequisites

1. **Zim Desktop Wiki** installed system-wide (not on PyPI):
   - Arch: `pacman -S zim`
   - Debian/Ubuntu: `apt install zim`
2. **`ZIM_NOTEBOOK_PATH`** set to your notebook root (must contain `notebook.zim`).

The plugin imports Zim's Python modules at runtime. Zim is licensed under **GPL-2.0**; this plugin is also GPL-2.0 (see [LICENSE](LICENSE)).

## Tools

| Tool | Description |
|------|-------------|
| `zim_list_pages` | List pages via Zim index (optional namespace prefix) |
| `zim_read_page` | Read page wiki markup |
| `zim_search` | Search with Zim query language (Content:, Tag:, LinksTo:, …) |
| `zim_write_page` | Replace body of an existing page |
| `zim_get_links` | Forward, backward, or bidirectional links |
| `zim_list_tags` | Tags on a page, pages with a tag, or all tags |
| `zim_create_page` | Create a new page (or append if `append=true`) |

Slash command: `/zim` — show notebook path and page count.

Bundled skill: `zim-wiki:zim-wiki` (load with `skill_view`).

## Install

```bash
export ZIM_NOTEBOOK_PATH=/path/to/your/notebook
```

### Symlink (development)

```bash
ln -s "$(pwd)/hermes_zim_wiki_plugin" ~/.hermes/plugins/zim-wiki
hermes plugins enable zim-wiki
```

### Pip

```bash
python -m venv .venv
.venv/bin/pip install -e .
```

Zim itself must still be installed on the system; pip only installs this plugin.

### Project-local

```bash
mkdir -p .hermes/plugins
ln -s "$(pwd)/hermes_zim_wiki_plugin" .hermes/plugins/zim-wiki
```

## Test

```bash
export ZIM_NOTEBOOK_PATH=/path/to/notebook
HERMES_PLUGINS_DEBUG=1 hermes plugins list
hermes
```

Run unit tests (requires Zim installed):

```bash
pytest
```

## Layout

```
hermes_zim_wiki_plugin/
├── plugin.yaml
├── __init__.py           # register(ctx)
├── schemas.py
├── tools.py
├── notebook_client/      # Zim API backend
│   ├── session.py
│   ├── pages.py
│   ├── search.py
│   ├── links.py
│   └── tags.py
└── skills/zim-wiki/
```

See [Build a Hermes Plugin](https://hermes-agent.nousresearch.com/docs/guides/build-a-hermes-plugin).
