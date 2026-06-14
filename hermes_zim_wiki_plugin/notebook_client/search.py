"""Notebook search via Zim Query / SearchSelection API and optional fuzzy matching."""

from __future__ import annotations

import re

from .session import NotebookError, get_notebook, path_to_dict, resolve_path, run_zim_op

_STRUCTURED_KEYWORDS = re.compile(
    r"\b(content|name|namespace|section|contentorname|links|linksfrom|linksto|tag)\s*:",
    re.I,
)
_TAG_IN_QUERY = re.compile(r"(?:^|\s)@\w+", re.U)

_VALID_MODES = frozenset({"exact", "fuzzy", "auto"})
_VALID_SCOPES = frozenset({"names", "content", "both"})
_DEFAULT_LOOKUP_THRESHOLD = 95
_SEPARATOR_RE = re.compile(r"[\s_\-.]+")


def _import_fuzz():
    try:
        from rapidfuzz import fuzz
    except ImportError as exc:
        raise NotebookError(
            "rapidfuzz is required for fuzzy search; install hermes-zim-wiki-plugin with dependencies"
        ) from exc
    return fuzz


def _is_structured_query(query: str) -> bool:
    if _STRUCTURED_KEYWORDS.search(query):
        return True
    return bool(_TAG_IN_QUERY.search(query))


def _validate_mode(mode: str) -> str:
    normalized = (mode or "auto").strip().lower()
    if normalized not in _VALID_MODES:
        raise NotebookError(f"Invalid search mode: {mode!r} (expected exact, fuzzy, or auto)")
    return normalized


def _validate_scope(scope: str) -> str:
    normalized = (scope or "both").strip().lower()
    if normalized not in _VALID_SCOPES:
        raise NotebookError(f"Invalid search scope: {scope!r} (expected names, content, or both)")
    return normalized


def _validate_threshold(threshold: int) -> int:
    try:
        value = int(threshold)
    except (TypeError, ValueError) as exc:
        raise NotebookError("threshold must be an integer between 0 and 100") from exc
    if not 0 <= value <= 100:
        raise NotebookError("threshold must be an integer between 0 and 100")
    return value


def _wiki_body(page) -> str:
    lines = page.dump("wiki")
    return "\n".join(lines) if lines else ""


def _score_text(fuzz, query: str, text: str) -> float:
    q = query.lower()
    t = text.lower()
    return max(
        fuzz.partial_ratio(q, t),
        fuzz.token_set_ratio(q, t),
    )


def _score_name(fuzz, query: str, name: str, basename: str) -> float:
    return max(
        _score_text(fuzz, query, name),
        _score_text(fuzz, query, basename),
        _score_text(fuzz, query, name.replace(":", " ")),
    )


def _normalize_identifier(text: str) -> str:
    normalized = _SEPARATOR_RE.sub(" ", text.lower().strip())
    return " ".join(normalized.split())


def _compact_identifier(text: str) -> str:
    return re.sub(r"[\s_\-.:/]+", "", text.lower())


def _identifier_variants(text: str) -> set[str]:
    stripped = text.strip()
    if not stripped:
        return set()
    variants = {
        stripped.lower(),
        _normalize_identifier(stripped),
        _compact_identifier(stripped),
        stripped.lower().replace(":", " "),
        _normalize_identifier(stripped.replace(":", " ")),
    }
    return {variant for variant in variants if variant}


def _score_identifier(fuzz, query: str, target: str) -> float:
    best = 0.0
    for q in _identifier_variants(query):
        for t in _identifier_variants(target):
            best = max(
                best,
                fuzz.partial_ratio(q, t),
                fuzz.token_set_ratio(q, t),
            )
    return best


def _score_basename(fuzz, term: str, basename: str) -> float:
    return _score_identifier(fuzz, term, basename)


def _validate_terms(terms: list[str]) -> list[str]:
    if not isinstance(terms, list):
        raise NotebookError("terms must be a list of strings")
    cleaned = [term.strip() for term in terms if isinstance(term, str) and term.strip()]
    if not cleaned:
        raise NotebookError("At least one non-empty search term is required")
    return cleaned


def _try_exact_name_lookup(notebook, term: str) -> str | None:
    for variant in _identifier_variants(term):
        try:
            path = notebook.pages.lookup_from_user_input(variant)
            page = notebook.get_page(path)
            if page.exists():
                return path.name
        except (ValueError, Exception):
            continue
    return None


def _find_page(terms: list[str], threshold: int = _DEFAULT_LOOKUP_THRESHOLD) -> dict:
    from .pages import _read_page

    cleaned_terms = _validate_terms(terms)
    threshold = _validate_threshold(threshold)
    notebook = get_notebook()

    hits: dict[str, dict] = {}

    def record_hit(page_name: str, term: str, score: float, mode: str) -> None:
        entry = hits.get(page_name)
        if entry is None:
            hits[page_name] = {
                "matched_terms": {term},
                "score": score,
                "mode": mode,
            }
            return
        entry["matched_terms"].add(term)
        if score > entry["score"]:
            entry["score"] = score
        if mode == "exact":
            entry["mode"] = "exact"

    fuzzy_terms: list[str] = []
    for term in cleaned_terms:
        page_name = _try_exact_name_lookup(notebook, term)
        if page_name:
            record_hit(page_name, term, 100.0, "exact")
        else:
            fuzzy_terms.append(term)

    if fuzzy_terms:
        fuzz = _import_fuzz()
        for record in notebook.pages.walk():
            for term in fuzzy_terms:
                score = _score_basename(fuzz, term, record.basename)
                if score >= threshold:
                    record_hit(record.name, term, round(score, 2), "fuzzy")

    if not hits:
        raise NotebookError(
            f"No page matched {cleaned_terms!r} by basename at threshold {threshold}"
        )

    pages: list[dict] = []
    for page_name in sorted(hits, key=lambda name: (-hits[name]["score"], name.lower())):
        hit = hits[page_name]
        pages.append({
            **_read_page(page_name),
            "matched_terms": sorted(hit["matched_terms"]),
            "score": hit["score"],
            "mode": hit["mode"],
        })

    return {
        "count": len(pages),
        "pages": pages,
        "terms": cleaned_terms,
        "threshold": threshold,
    }


def find_page(terms: list[str], *, threshold: int = _DEFAULT_LOOKUP_THRESHOLD) -> dict:
    return run_zim_op("find_page", _find_page, terms=terms, threshold=threshold)


def _match_kind(name_score: float, content_score: float, scope: str, threshold: int) -> str | None:
    name_hit = name_score >= threshold
    content_hit = content_score >= threshold
    if scope == "names":
        return "name" if name_hit else None
    if scope == "content":
        return "content" if content_hit else None
    if name_hit and content_hit:
        return "both"
    if name_hit:
        return "name"
    if content_hit:
        return "content"
    return None


def _snippet_for_path(notebook, path, query: str) -> str | None:
    """Best-effort snippet when the search API does not provide one."""
    needle = query.strip().lower()
    if not needle or ":" in needle.split()[0]:
        return None
    try:
        page = notebook.get_page(path)
        body = _wiki_body(page)
        idx = body.lower().find(needle)
        if idx < 0:
            return None
        start = max(0, idx - 40)
        end = min(len(body), idx + len(needle) + 40)
        return body[start:end].replace("\n", " ")
    except Exception:
        return None


def _fuzzy_snippet(body: str, query: str, window: int = 80) -> str | None:
    fuzz = _import_fuzz()
    flat = body.replace("\n", " ")
    if not flat.strip():
        return None
    if len(flat) <= window:
        return flat.strip()

    best_score = -1.0
    best_start = 0
    step = max(1, window // 4)
    q = query.lower()
    for start in range(0, len(flat) - window + 1, step):
        chunk = flat[start : start + window]
        score = fuzz.partial_ratio(q, chunk.lower())
        if score > best_score:
            best_score = score
            best_start = start
    return flat[best_start : best_start + window].strip()


def _exact_search_pages(query: str, limit: int) -> list[dict]:
    from zim.search import Query, SearchSelection

    notebook = get_notebook()
    selection = SearchSelection(notebook)
    try:
        selection.search(Query(query.strip()))
    except Exception as exc:
        raise NotebookError(f"Invalid search query: {exc}") from exc

    results: list[dict] = []
    scored = sorted(
        selection,
        key=lambda p: selection.scores.get(p, 0),
        reverse=True,
    )
    for path in scored[: max(1, limit)]:
        entry = {
            **path_to_dict(path),
            "score": selection.scores.get(path, 0),
        }
        snippet = _snippet_for_path(notebook, path, query)
        if snippet:
            entry["snippet"] = snippet
        results.append(entry)
    return results


def _fuzzy_search_pages(
    query: str,
    limit: int,
    threshold: int,
    scope: str,
    prefix: str,
) -> list[dict]:
    if _is_structured_query(query):
        raise NotebookError(
            "Fuzzy search supports plain text only; use mode=exact for structured queries "
            "(Content:, Tag:, LinksTo:, etc.)"
        )

    fuzz = _import_fuzz()
    notebook = get_notebook()
    start = None
    if prefix.strip():
        start = resolve_path(prefix.strip())

    candidates: list[tuple[float, dict]] = []
    for record in notebook.pages.walk(start):
        name_score = 0.0
        content_score = 0.0

        if scope in ("names", "both"):
            name_score = _score_name(fuzz, query, record.name, record.basename)

        body = ""
        if scope in ("content", "both") and record.hascontent:
            try:
                page = notebook.get_page(record)
                body = _wiki_body(page)
                if body:
                    content_score = _score_text(fuzz, query, body)
            except Exception:
                content_score = 0.0

        if scope == "names":
            total_score = name_score
        elif scope == "content":
            total_score = content_score
        else:
            total_score = max(name_score, content_score)

        match = _match_kind(name_score, content_score, scope, threshold)
        if match is None:
            continue

        entry = {
            **path_to_dict(record),
            "score": round(total_score, 2),
            "match": match,
        }
        if match in ("content", "both") and body:
            snippet = _fuzzy_snippet(body, query)
            if snippet:
                entry["snippet"] = snippet
        elif match == "name":
            entry["snippet"] = record.name

        candidates.append((total_score, entry))

    candidates.sort(key=lambda item: item[0], reverse=True)
    return [entry for _, entry in candidates[: max(1, limit)]]


def _search_pages(
    query: str,
    limit: int = 20,
    mode: str = "auto",
    threshold: int = 85,
    scope: str = "both",
    prefix: str = "",
) -> dict:
    if not query.strip():
        raise NotebookError("Search query is empty")

    mode_requested = _validate_mode(mode)
    scope = _validate_scope(scope)
    threshold = _validate_threshold(threshold)

    try:
        limit = int(limit)
    except (TypeError, ValueError) as exc:
        raise NotebookError("limit must be an integer") from exc
    if limit < 1:
        raise NotebookError("limit must be at least 1")

    if mode_requested == "exact":
        results = _exact_search_pages(query, limit)
        return {"mode": "exact", "mode_requested": "exact", "results": results}

    if mode_requested == "fuzzy":
        results = _fuzzy_search_pages(query, limit, threshold, scope, prefix)
        return {"mode": "fuzzy", "mode_requested": "fuzzy", "results": results}

    exact_results = _exact_search_pages(query, limit)
    if exact_results:
        return {"mode": "exact", "mode_requested": "auto", "results": exact_results}

    fuzzy_results = _fuzzy_search_pages(query, limit, threshold, scope, prefix)
    return {"mode": "fuzzy", "mode_requested": "auto", "results": fuzzy_results}


def search_pages(
    query: str,
    limit: int = 20,
    *,
    mode: str = "auto",
    threshold: int = 85,
    scope: str = "both",
    prefix: str = "",
) -> dict:
    return run_zim_op(
        "search_pages",
        _search_pages,
        query=query,
        limit=limit,
        mode=mode,
        threshold=threshold,
        scope=scope,
        prefix=prefix,
    )
