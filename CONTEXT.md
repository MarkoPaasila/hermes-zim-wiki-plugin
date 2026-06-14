# Zim Wiki Plugin

Hermes Agent tools for reading and writing Zim Desktop Wiki notebooks via the Zim Python API.

## Language

**Page lookup**:
Resolving a human-ish page title to notebook page bodies in a single tool call. Returns full page content when a term matches a page basename at or above the lookup threshold (default 95); otherwise reports not found. Basename only — not namespace prefixes, not tags, not body content.
_Avoid_: Search-and-read, find page, tag lookup

**Lookup term**:
One string in the `terms` array used to fuzzy-match page basenames. Multiple terms are disjunctive: each term is evaluated independently; every page whose basename matches any term at or above the lookup threshold is included (deduplicated).
_Avoid_: Query, keyword (when meaning a lookup term specifically)

**Lookup threshold**:
Minimum fuzzy match score (0–100) for a term to qualify against a page basename. Configurable on the tool; default 95.
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

**Lookup resolution**:
Exact name matches qualify first (score 100); remaining terms are fuzzy-scored against page basenames at or above the lookup threshold, across the entire notebook. One qualifying page returns its full body; several qualifying pages (including when different terms match different pages) return all their bodies in one response. Terms with no match are ignored; not found only when no term matches any page name. No tag fallback, no namespace prefix filter.
_Avoid_: Best match, tag fallback, conjunctive terms, all-or-nothing, prefix scoping

**Lookup response**:
Always `{ "count": N, "pages": [...], "terms": [...], "threshold": T }`. Pages sorted by `score` descending, then page name alphabetically. Each page entry includes `read_page` fields plus match provenance: `matched_terms` (all terms that hit this page), `score` (best score), `mode` (`exact` or `fuzzy`). Not found uses `{"error": "..."}` like other tools.
_Avoid_: Flat single-page object, concatenated bodies, matched_term (singular)

**Notebook page**:
A wiki article in a Zim notebook, addressed by colon notation (e.g. `Notes:Meeting`).
_Avoid_: File, document, note (when meaning a Zim page specifically)
