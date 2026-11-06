#!/bin/bash
# Publish the compatibility page from main. Run by hakuxlr-sync.timer as the hakuxlr user.
# For a new commit: check it, rebuild web.html from compat.json with the committed packs,
# check the export against its manifest and publish exactly the listed files.
# The checks run from the installed hakuxlr-publish.py, never from the checkout.
set -euo pipefail
umask 022

REPO=${HAKUXLR_REPO:-https://github.com/portare-ch/hakux-lr-compat.git}
BRANCH=${HAKUXLR_BRANCH:-main}
WWW=${HAKUXLR_WWW:-/var/www/hakuxlr}
STATE=${STATE_DIRECTORY:-/var/lib/hakuxlr-sync}
CHECK=${HAKUXLR_PUBLISH:-/usr/local/lib/hakuxlr-sync/hakuxlr-publish.py}
SRC=$STATE/repo

[ -d "$SRC/.git" ] || git clone --quiet --no-checkout --depth 1 --single-branch --branch "$BRANCH" "$REPO" "$SRC"
git -C "$SRC" fetch --quiet --depth 1 origin "$BRANCH"
rev=$(git -C "$SRC" rev-parse FETCH_HEAD)
old=$(cat "$STATE/deployed" 2>/dev/null || true)
[ "$rev" = "$old" ] && exit 0

fail() {
    echo "$rev not published: $1; still serving ${old:-the previous page}" >&2
    exit 1
}

# Symlinks, submodules or unexpected files under site/ are rejected before checkout.
python3 -I "$CHECK" commit "$SRC" "$rev" || fail "commit check failed"
git -C "$SRC" reset --quiet --hard "$rev"
git -C "$SRC" clean --quiet -ffdx
python3 -I "$CHECK" tree "$SRC" || fail "checkout check failed"
if [ ! -d "$SRC/site/packs" ]; then
    echo "$rev has no site/packs; nothing to publish" >&2
    exit 0
fi
# The server has no captures, so the export fails if a result's pack is not committed.
(cd "$SRC" && python3 -I export_page.py site) || fail "export failed (is site/packs up to date?)"
python3 -I "$CHECK" publish "$SRC/site" "$WWW" || fail "manifest check failed"
echo "$rev" > "$STATE/deployed"
echo "published $rev"
