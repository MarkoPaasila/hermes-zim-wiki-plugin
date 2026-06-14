# Page lookup matches basenames only

`zim_lookup_page` resolves human-ish titles to notebook pages in one tool call so Hermes Agent avoids search-then-read round trips. We match lookup terms against **page basenames** (the leaf segment after the last colon), not namespace prefixes, tags, or body content. Fuzzy hits at or above a configurable threshold (default 95) qualify; exact Zim resolution via `lookup_from_user_input` still accepts full colon-notation paths at score 100. All qualifying pages are returned in one `{ count, pages[] }` response.

**Considered Options**

- **Full page name** — matching `Notes:Meeting Notes`, basename, and colon-as-space variants. Rejected: a term like `Meeting` still collides across namespaces, but matching namespace segments (e.g. `Notes`) pollutes results when the agent only knows a leaf title.
- **Tags** — fallback when no title matches. Rejected: shared tags (e.g. `@todo` on many pages) fight the single-call efficiency goal and belong on `zim_list_tags` / `zim_search`.
- **Single winner** — pick one best page. Rejected: agents pass synonymous terms (Finnish/Latin names) or hit multiple same-basename pages; returning all matches is more honest and still one round trip.

**Consequences**

- `terms=["Meeting"]` may return every `*:Meeting` page; agents disambiguate with exact paths (`Notes:Meeting`) or switch to `zim_search`.
- Tag-based discovery is no longer part of lookup; skill and tool docs must steer agents to `zim_list_tags`.
- Response shape is always an array envelope — a breaking change from the earlier flat single-page object.
