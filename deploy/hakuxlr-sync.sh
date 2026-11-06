#!/bin/bash
# Publish the compatibility page from main. Run by hakuxlr-sync.timer as the hakuxlr user.
# Fetches the repository and, for a new commit, rebuilds web.html from compat.json with the
# committed packs (site/packs) and copies both to the web root.
set -euo pipefail
umask 022

REPO=${HAKUXLR_REPO:-https://github.com/portare-ch/hakux-lr-compat.git}
BRANCH=${HAKUXLR_BRANCH:-main}
WWW=${HAKUXLR_WWW:-/var/www/hakuxlr}
STATE=${STATE_DIRECTORY:-/var/lib/hakuxlr-sync}
SRC=$STATE/repo

[ -d "$SRC/.git" ] || git clone --quiet --depth 1 --single-branch --branch "$BRANCH" "$REPO" "$SRC"
git -C "$SRC" fetch --quiet --depth 1 origin "$BRANCH"
rev=$(git -C "$SRC" rev-parse FETCH_HEAD)
old=$(cat "$STATE/deployed" 2>/dev/null || true)
[ "$rev" = "$old" ] && exit 0

git -C "$SRC" reset --quiet --hard "$rev"
git -C "$SRC" clean --quiet -ffdx
if [ ! -d "$SRC/site/packs" ]; then
    echo "$rev has no site/packs; nothing to publish" >&2
    exit 0
fi
# The server has no captures, so the export fails if a result's pack is not committed.
if ! (cd "$SRC" && python3 -I export_page.py site); then
    echo "export of $rev failed (is site/packs up to date?); still serving ${old:-the previous page}" >&2
    exit 1
fi

# New packs first, then the page, then stale packs, so the page never names a missing pack.
rsync -rlt --chmod=D755,F644 "$SRC/site/packs/" "$WWW/packs/"
rsync -rlt --chmod=F644 "$SRC/site/web.html" "$WWW/index.html"
rsync -rlt --delete --chmod=D755,F644 "$SRC/site/packs/" "$WWW/packs/"
echo "$rev" > "$STATE/deployed"
echo "published $rev"
