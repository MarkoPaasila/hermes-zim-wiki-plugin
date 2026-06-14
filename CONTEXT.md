# Zim Wiki Plugin

Hermes Agent tools for reading and writing Zim Desktop Wiki notebooks via the Zim Python API.

## Language

**Page lookup**:
Resolving a human-ish page title to notebook page bodies in a single tool call. Returns full page content when a term matches a page basename at or above the lookup threshold (default 95); otherwise reports not found. Basename only — not namespace prefixes, not tags, not body content.
_Avoid_: Search-and-read, find page, tag lookup

**Lookup term**:
One string in the `terms` array used to fuzzy-match page basenames. Multiple terms are disjunctive: each term is evaluated independently; every page whose basename matches any term at or above the lookup threshold is included (deduplicated).
_Avoid_: Query, keyword (when meaning a lookup term specifically)

**Dead lookup term**:
A term in the `terms` array that matches no page basename. Ignored when at least one other term qualifies; the overall lookup fails only when every term is dead.
_Avoid_: Failed term, unmatched query, warning

**Lookup failure**:
When every lookup term is dead at the configured threshold. The tool returns an error and stops — no prescribed follow-up actions from the plugin.
_Avoid_: Fallback, retry, escalation

**Tag exclusion**:
Lookup never interprets `@tag` syntax as a tag search. A tag-shaped term is matched as a basename like any other string; if nothing qualifies, the generic lookup failure applies.
_Avoid_: Tag fallback, tag lookup, tag error

**Lookup threshold**:
Minimum fuzzy match score (0–100) for a term to qualify against a page basename. Configurable on the tool; default 95 — stricter than notebook search's fuzzy default because lookup returns full page bodies where false positives are costly.
_Avoid_: Confidence, similarity (when meaning the lookup cutoff specifically)

**Identifier normalization**:
Case-insensitive matching with equivalent separators (spaces, underscores, dashes, dots) when comparing a lookup term to a page basename.
_Avoid_: Fuzzy matching (when meaning normalization specifically)

**Exact name match**:
A page that Zim resolves unambiguously via `lookup_from_user_input` — including full colon-notation paths — qualifies immediately at score 100 without fuzzy scoring.
_Avoid_: Direct hit, precise match

**Page basename**:
The leaf segment of a notebook page name — the part after the last colon (e.g. `Meeting Notes` in `Notes:Meeting Notes`). Lookup fuzzy-matches terms against basenames only, not namespace prefixes.
_Avoid_: Title, page name (when meaning the full colon-notation path)

**Basename collision**:
Multiple notebook pages sharing the same leaf title in different namespaces (e.g. `Notes:Meeting` and `Projects:Meeting`). Lookup returns every qualifying collision with full bodies; the agent disambiguates with exact colon-notation paths or notebook search.
_Avoid_: Ambiguity resolution (as a plugin responsibility), single winner, best match

**Lookup resolution**:
Exact name matches qualify first (score 100); remaining terms are fuzzy-scored against page basenames at or above the lookup threshold, across the entire notebook. One qualifying page returns its full body; several qualifying pages (including when different terms match different pages) return all their bodies in one response. Terms with no match are ignored; not found only when no term matches any page name. No tag fallback, no namespace prefix filter.
_Avoid_: Best match, tag fallback, conjunctive terms, all-or-nothing, prefix scoping

**Whole-notebook lookup**:
Lookup always evaluates terms against every page in the notebook. Namespace disambiguation belongs in the term itself (e.g. `Notes:Meeting`), not a separate prefix filter.
_Avoid_: Prefix scoping, namespace filter, subtree lookup

**Lookup response**:
Always `{ "count": N, "pages": [...], "terms": [...], "threshold": T }`. Pages sorted by `score` descending, then page name alphabetically. Each page entry includes `read_page` fields plus match provenance: `matched_terms` (all terms that hit this page), `score` (best score), `mode` (`exact` or `fuzzy`). Not found uses `{"error": "..."}` like other tools.
_Avoid_: Flat single-page object, concatenated bodies, matched_term (singular)

**Notebook page**:
A wiki article in a Zim notebook, addressed by colon notation (e.g. `Notes:Meeting`).
_Avoid_: File, document, note (when meaning a Zim page specifically)

**Direct page read**:
Fetching a notebook page's full content when the agent already knows its exact colon-notation name. No title resolution or fuzzy matching.
_Avoid_: Lookup, find page (when the name is already known)

**Notebook search**:
Discovery across page names, body content, tags, and structured queries (`Content:`, `Tag:`, `LinksTo:`, etc.). Returns ranked matches with snippets only — never full page bodies; agents follow up with `zim_read_page` or `zim_lookup_page`.
_Avoid_: Lookup, search-and-read, title resolution (when meaning basename matching specifically)
