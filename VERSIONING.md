# Versioning

This project uses **calendar versioning** with a daily build suffix:

```text
YYYY.MM.DD.N
```

| Part | Meaning |
|------|---------|
| `YYYY.MM.DD` | Release date (UTC), zero-padded |
| `N` | Release number for that date, starting at `0` |

## Examples

- `2026.06.13.0` — first release on 2026-06-13
- `2026.06.13.1` — second release on the same day (bugfix, republish)
- `2026.06.14.0` — first release on the next day

## When to bump

- **New date, `N = 0`:** normal releases shipped on a new calendar day.
- **Same date, increment `N`:** hotfix or re-release on the same day without waiting for the next day.

Breaking changes, features, and fixes are not encoded in the number — use git tags, changelog entries, and release notes for that detail.

## Where the version lives

Canonical value: [`hermes_zim_wiki_plugin/_version.py`](hermes_zim_wiki_plugin/_version.py) (`__version__`).

Also update these when releasing (must match):

- [`hermes_zim_wiki_plugin/plugin.yaml`](hermes_zim_wiki_plugin/plugin.yaml) — Hermes plugin manifest
- [`pyproject.toml`](pyproject.toml) — reads `__version__` dynamically at build time

After changing the version, run tests and verify with:

```bash
python -c "from hermes_zim_wiki_plugin import __version__; print(__version__)"
HERMES_PLUGINS_DEBUG=1 hermes plugins list
```
