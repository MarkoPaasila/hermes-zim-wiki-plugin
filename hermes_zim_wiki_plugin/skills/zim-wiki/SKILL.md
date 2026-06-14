---
name: zim-wiki
description: >-
  Zim Desktop Wiki notebook format and zim-wiki plugin tools. Use when reading,
  searching, linking, tagging, or writing Zim pages via Hermes tools.
---

# Zim Desktop Wiki (Hermes plugin)

## Requirements

- **Zim Desktop Wiki** installed on the system (`pacman -S zim`, `apt install zim`, …)
- **`ZIM_NOTEBOOK_PATH`** pointing at a notebook directory with `notebook.zim`

Always use the `zim_*` tools for notebook I/O. Do **not** use generic `read_file` / `write_file` / `patch` on notebook pages.

## Tool selection

| Goal | Tool |
|------|------|
| Explore structure | `zim_list_pages` |
| Read content (known page name) | `zim_read_page` |
| Find and read page(s) by basename | `zim_lookup_page` |
| Find notes (many results, content search) | `zim_search` |
| Update existing page | `zim_write_page` |
| Create new page | `zim_create_page` |
| Outbound / inbound links | `zim_get_links` |
| Tags on page / pages with tag | `zim_list_tags` |

## Page names

Use Zim **colon notation**: `Home`, `Notes:Meeting`, `Projects:Dev:Design`.

The plugin resolves names via `notebook.pages.lookup_from_user_input()` — not filesystem paths.

## Search query examples

Default search uses **mode=auto** (exact Zim search first, fuzzy typo fallback if empty).

- Plain text: `meeting notes` (searches content and names)
- Typo-tolerant plain text: `meating notes` (auto falls back to fuzzy when exact finds nothing)
- Structured queries (use **mode=exact** for precision): `Content:python`, `Name:Home`, `Tag:todo`, `LinksTo:Home`, `LinksFrom:Home`, `Content:api AND Tag:work`
- Fuzzy-only plain text: set `mode=fuzzy` with optional `scope` (`names`, `content`, `both`) and `threshold` (default 85)

## Lookup page(s) by basename

Use `zim_lookup_page` when you know roughly which page title you want and need full body content in one call:

- Single term: `terms=["Home"]`
- OR semantics: `terms=["Koiruusu", "Rosa canina"]` — returns every page whose basename matches any term
- Dead terms are ignored; not found only when no term matches
- Handles case, underscores, dashes, and spaces as equivalent (default threshold 95; override with `threshold`)
- Matches page **basenames** only (leaf title, not namespace prefix); exact colon-notation paths also work (`terms=["Notes:Meeting"]`)
- Does **not** match tags or body content — use `zim_list_tags` or `zim_search` for those
- Response: `{ "count", "pages": [...], "terms", "threshold" }` — each page includes `matched_terms`, `score`, `mode`, and full body

## Wiki markup (common)

- **Bold** `''text''`, *italic* `//text//`
- Headings: `====== H1 ======` down to `=== H5 ===`
- Links: `[[+Subpage]]`, `[[OtherPage]]`, `[[path:Page|label]]`
- Tags: `@tagname` at start of line or after space
- Lists: `* item`, `1. item`

## Editing rules

1. `zim_read_page` before `zim_write_page` on unfamiliar content.
2. `zim_write_page` only updates **existing** pages.
3. `zim_create_page` for new pages; set `append=true` to add to an existing page.
4. Preserve links and tags unless the user asks to change them.
5. Content is parsed/stored through Zim's wiki format — do not hand-edit raw `.txt` headers.

Load explicitly: `skill_view("zim-wiki:zim-wiki")`.
