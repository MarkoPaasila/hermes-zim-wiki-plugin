#!/usr/bin/env bash
# Build installable Hermes Agent plugin packages.
#
# Outputs (under dist/):
#   - hermes_zim_wiki_plugin-<version>-py3-none-any.whl   pip install (entry-point discovery)
#   - hermes_zim_wiki_plugin-<version>.tar.gz              pip install from sdist
#   - zim-wiki-<version>.tar.gz                            directory plugin for ~/.hermes/plugins/
#
# Usage:
#   ./scripts/build-plugin.sh              # check versions, then build all artifacts
#   ./scripts/build-plugin.sh --skip-tests # build without version checks
#   ./scripts/build-plugin.sh --pip-only   # wheel + sdist only (no directory tarball)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

SKIP_TESTS=0
PIP_ONLY=0

usage() {
    sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --skip-tests)
            SKIP_TESTS=1
            shift
            ;;
        --pip-only)
            PIP_ONLY=1
            shift
            ;;
        -h | --help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is required" >&2
    exit 1
fi

PYTHON="${PYTHON:-python3}"

echo "==> Resolving version"
VERSION="$("$PYTHON" -c 'from hermes_zim_wiki_plugin import __version__; print(__version__)')"
PLUGIN_NAME="$("$PYTHON" -c "
import re
from pathlib import Path
text = Path('plugin.yaml').read_text(encoding='utf-8')
match = re.search(r'^name:\\s*(\\S+)\\s*$', text, re.MULTILINE)
if not match:
    raise SystemExit('plugin.yaml: missing name field')
print(match.group(1))
")"
echo "    plugin: $PLUGIN_NAME"
echo "    version: $VERSION"

if [[ "$SKIP_TESTS" -eq 0 ]]; then
    echo "==> Checking version consistency"
    "$PYTHON" - <<'PY'
import re
import sys
from pathlib import Path

from hermes_zim_wiki_plugin import __version__

parts = __version__.split(".")
if len(parts) != 4 or not all(p.isdigit() for p in parts):
    sys.exit(f"Invalid __version__ format: {__version__!r}")

manifest = Path("plugin.yaml").read_text(encoding="utf-8")
match = re.search(r"^version:\s*(\S+)\s*$", manifest, re.MULTILINE)
if match is None:
    sys.exit("plugin.yaml: missing version field")
if match.group(1) != __version__:
    sys.exit(
        f"Version mismatch: __version__={__version__!r}, "
        f"plugin.yaml={match.group(1)!r}"
    )
PY
fi

echo "==> Ensuring build backend is available"
if ! "$PYTHON" -m build --version >/dev/null 2>&1; then
    echo "    installing build into active environment"
    "$PYTHON" -m pip install -q build
fi

echo "==> Building wheel and sdist"
rm -rf dist/
"$PYTHON" -m build --outdir dist/

WHEEL="$(find dist -maxdepth 1 -name 'hermes_zim_wiki_plugin-*-py3-none-any.whl' -print -quit)"
SDIST="$(find dist -maxdepth 1 -name 'hermes_zim_wiki_plugin-*.tar.gz' ! -name 'zim-wiki-*' -print -quit)"

if [[ -z "$WHEEL" || ! -f "$WHEEL" ]]; then
    echo "Wheel not found under dist/" >&2
    ls -la dist/ >&2 || true
    exit 1
fi
if [[ -z "$SDIST" || ! -f "$SDIST" ]]; then
    echo "Sdist not found under dist/" >&2
    ls -la dist/ >&2 || true
    exit 1
fi

if [[ "$PIP_ONLY" -eq 0 ]]; then
    echo "==> Building directory plugin tarball (~/.hermes/plugins/$PLUGIN_NAME/)"
    STAGING="$(mktemp -d "${TMPDIR:-/tmp}/hermes-zim-wiki-plugin.XXXXXX")"
    trap 'rm -rf "$STAGING"' EXIT

    mkdir -p "$STAGING/$PLUGIN_NAME"
    rsync -a \
        --exclude '__pycache__/' \
        --exclude '*.py[cod]' \
        hermes_zim_wiki_plugin/ "$STAGING/$PLUGIN_NAME/"
    cp plugin.yaml "$STAGING/$PLUGIN_NAME/"

    DIR_TARBALL="dist/${PLUGIN_NAME}-${VERSION}.tar.gz"
    tar -C "$STAGING" -czf "$DIR_TARBALL" "$PLUGIN_NAME"
    echo "    $DIR_TARBALL"
fi

echo
echo "Built:"
ls -lh dist/
echo
echo "Install (pip — auto-discovered via hermes_agent.plugins entry point):"
echo "  pip install \"$WHEEL\""
echo "  hermes plugins enable $PLUGIN_NAME"
echo
if [[ "$PIP_ONLY" -eq 0 ]]; then
    echo "Install (directory plugin):"
    echo "  mkdir -p ~/.hermes/plugins/$PLUGIN_NAME"
    echo "  tar -C ~/.hermes/plugins -xzf \"dist/${PLUGIN_NAME}-${VERSION}.tar.gz\""
    echo "  hermes plugins enable $PLUGIN_NAME"
fi
