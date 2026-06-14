# hermes-zim-wiki-plugin

Hermes Agent plugin for reading and writing [Zim Desktop Wiki](https://zim-wiki.org/) notebooks via the **Zim Python API**.

**Version:** `2026.06.14.0` — see [VERSIONING.md](VERSIONING.md) for the release scheme. Release history: [CHANGELOG.md](CHANGELOG.md).

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
| `zim_search` | Search pages (default `mode=auto`: exact Zim query, then fuzzy fallback; also `mode=exact` / `mode=fuzzy`, `threshold`, `scope`, `prefix`) |
| `zim_lookup_page` | Find best page by title or tag (OR terms, 95% fuzzy) and return full body in one call |
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

### Hermes CLI or dashboard (recommended)

Install from GitHub with Hermes built-in plugin manager. The repo root is the plugin directory (`plugin.yaml` and `__init__.py` at the top level), so Hermes keeps the full git checkout and `hermes plugins update` works.

**CLI:**

```bash
hermes plugins install MarkoPaasila/hermes-zim-wiki-plugin --enable
```

Hermes clones the repo, prompts for `ZIM_NOTEBOOK_PATH` if it is not already set (saved to `~/.hermes/.env`), and enables the plugin. Update later with:

```bash
hermes plugins update zim-wiki
```

**Dashboard:**

1. Start the web UI: `hermes dashboard` (requires `pip install 'hermes-agent[web]'`).
2. Open **Plugins** in the sidebar.
3. Under **Install from GitHub / Git URL**, paste:
   `MarkoPaasila/hermes-zim-wiki-plugin`
4. Leave **Enable after install** on and click **Install**.
5. If the dashboard reports missing env vars, set `ZIM_NOTEBOOK_PATH` on the **Keys** page.

See [Hermes plugins](https://hermes-agent.nousresearch.com/docs/user-guide/features/plugins) for the full plugin manager reference.

### Symlink (development)

```bash
ln -s "$(pwd)" ~/.hermes/plugins/zim-wiki
hermes plugins enable zim-wiki
```

### Rsync (local)

Copy the plugin into your Hermes plugins directory (flat layout for manual deploy — no repo docs or tests). Skip Python cache files:

```bash
mkdir -p ~/.hermes/plugins/zim-wiki
rsync -av --delete \
  --exclude '__pycache__/' \
  --exclude '*.py[cod]' \
  --exclude '.pytest_cache/' \
  --exclude '.mypy_cache/' \
  --exclude '.ruff_cache/' \
  hermes_zim_wiki_plugin/ ~/.hermes/plugins/zim-wiki/
cp plugin.yaml ~/.hermes/plugins/zim-wiki/
hermes plugins enable zim-wiki
```

Re-run after pulling updates. The same layout is used in [`scripts/build-plugin.sh`](scripts/build-plugin.sh) for the directory tarball.

### Rsync (remote)

Deploy to another machine over SSH (Hermes and Zim must already be installed there):

```bash
REMOTE=user@host   # adjust
ssh "$REMOTE" 'mkdir -p ~/.hermes/plugins/zim-wiki'
rsync -av --delete \
  --exclude '__pycache__/' \
  --exclude '*.py[cod]' \
  --exclude '.pytest_cache/' \
  --exclude '.mypy_cache/' \
  --exclude '.ruff_cache/' \
  hermes_zim_wiki_plugin/ "$REMOTE:~/.hermes/plugins/zim-wiki/"
rsync -av plugin.yaml "$REMOTE:~/.hermes/plugins/zim-wiki/"
ssh "$REMOTE" 'hermes plugins enable zim-wiki'
```

Set `ZIM_NOTEBOOK_PATH` on the remote as well (for example in `~/.hermes/.env` or the remote shell profile) so it points at a notebook on that machine.

### Pip

```bash
python -m venv .venv
.venv/bin/pip install -e .
```

Zim itself must still be installed on the system; pip only installs this plugin.

### Project-local

```bash
mkdir -p .hermes/plugins
ln -s "$(pwd)" .hermes/plugins/zim-wiki
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
plugin.yaml               # Hermes manifest (repo root — git install)
__init__.py               # register(ctx) shim for git install
hermes_zim_wiki_plugin/   # implementation package
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

## License

[GNU General Public License v2.0](LICENSE) (GPL-2.0-only), the same license as [Zim Desktop Wiki](https://zim-wiki.org/).
