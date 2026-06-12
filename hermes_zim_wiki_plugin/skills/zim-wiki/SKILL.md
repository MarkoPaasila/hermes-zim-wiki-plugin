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
| Read content | `zim_read_page` |
| Find notes | `zim_search` |
| Update existing page | `zim_write_page` |
| Create new page | `zim_create_page` |
| Outbound / inbound links | `zim_get_links` |
| Tags on page / pages with tag | `zim_list_tags` |

## Page names

Use Zim **colon notation**: `Home`, `Notes:Meeting`, `Projects:Dev:Design`.

The plugin resolves names via `notebook.pages.lookup_from_user_input()` — not filesystem paths.

## Search query examples

- Plain text: `meeting notes` (searches content and names)
- `Content:python`
- `Name:Home`
- `Tag:todo` or `@todo` in query
- `LinksTo:Home` (backlinks)
- `LinksFrom:Home` (outbound)
- `Content:api AND Tag:work`

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
