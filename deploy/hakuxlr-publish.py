#!/usr/bin/env python3
"""Checks and publishes the compatibility page for hakuxlr-sync.

Installed on the server as /usr/local/lib/hakuxlr-sync/hakuxlr-publish.py and always run
from there, never from the checkout, so a commit cannot change its own checks.

  hakuxlr-publish.py commit <repo> <rev>   before checkout: no symlinks or submodules anywhere,
                                           and site/ holds only site/packs/<pack>.webp files
  hakuxlr-publish.py tree <repo>           after checkout: no symlinks or special files on disk
  hakuxlr-publish.py publish <site> <www>  check the export against its manifest, then publish
                                           exactly the manifest's packs and the page

The manifest (site/manifest.json, written by export_page.py) must list exactly the packs
web.html references. site/packs must hold exactly those files, as regular WebP files with
the listed size and SHA-256 and no metadata chunks. Anything else fails the run, and the
previous page stays online.
"""
import hashlib
import json
import os
import re
import stat
import struct
import subprocess
import sys

PACK = re.compile(r"g\d{3}-[0-9a-f]{8}-[tf]\.webp")
PAGE_REF = re.compile(r'"pack":"packs/(g\d{3}-[0-9a-f]{8})"')
SITE_FILES = {"web.html", "index.html", "manifest.json"}
WEBP_CHUNKS = {b"VP8 ", b"VP8L", b"VP8X", b"ALPH", b"ICCP"}  # image data only: no EXIF, XMP or animation
MAX_PACK = 16 << 20
TMP = ".hakuxlr-tmp-"


class Reject(Exception):
    pass


def check_commit(repo, rev):
    out = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "-z", "--full-tree", rev],
                         check=True, capture_output=True).stdout
    for rec in filter(None, out.split(b"\0")):
        meta, raw = rec.split(b"\t", 1)
        mode, path = meta.split(b" ")[0], raw.decode("utf-8", "surrogateescape")
        if mode == b"120000":
            raise Reject(f"symlink in commit: {path}")
        if mode == b"160000":
            raise Reject(f"submodule in commit: {path}")
        if mode not in (b"100644", b"100755"):
            raise Reject(f"unexpected entry (mode {mode.decode()}) in commit: {path}")
        if path.startswith("site/"):
            name = path[len("site/packs/"):] if path.startswith("site/packs/") else ""
            if mode != b"100644" or not PACK.fullmatch(name):
                raise Reject(f"unexpected file in site/: {path}")


def check_tree(repo):
    for root, dirs, files in os.walk(repo):
        if root == repo and ".git" in dirs:
            dirs.remove(".git")
        for name in dirs + files:
            path = os.path.join(root, name)
            mode = os.lstat(path).st_mode
            if stat.S_ISLNK(mode):
                raise Reject(f"symlink in checkout: {os.path.relpath(path, repo)}")
            if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                raise Reject(f"special file in checkout: {os.path.relpath(path, repo)}")


def real_dir(path):
    if not stat.S_ISDIR(os.lstat(path).st_mode):
        raise Reject(f"not a directory: {path}")


def read_regular(path):
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    except OSError as e:
        raise Reject(f"cannot open {path}: {e.strerror}")
    with os.fdopen(fd, "rb") as f:
        if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):
            raise Reject(f"not a regular file: {path}")
        return f.read()


def check_webp(name, data):
    if len(data) > MAX_PACK:
        raise Reject(f"{name}: larger than {MAX_PACK >> 20} MiB")
    if len(data) < 20 or data[:4] != b"RIFF" or data[8:12] != b"WEBP" \
            or struct.unpack("<I", data[4:8])[0] + 8 != len(data):
        raise Reject(f"{name}: not a WebP file")
    i = 12
    while i < len(data):
        if i + 8 > len(data):
            raise Reject(f"{name}: truncated WebP chunk")
        fourcc, size = data[i:i + 4], struct.unpack("<I", data[i + 4:i + 8])[0]
        if fourcc not in WEBP_CHUNKS:
            raise Reject(f"{name}: WebP chunk {fourcc!r} is not allowed")
        i += 8 + size + (size & 1)
    if i != len(data):
        raise Reject(f"{name}: WebP chunks overrun the file")


def check_site(site):
    """Returns the page and {pack name: bytes}, exactly as the manifest lists them."""
    packs = os.path.join(site, "packs")
    real_dir(site)
    real_dir(packs)
    entries = set(os.listdir(site))
    if entries - SITE_FILES - {"packs"}:
        raise Reject(f"unexpected entries in site/: {sorted(entries - SITE_FILES - {'packs'})}")
    for name in entries - {"packs"}:
        read_regular(os.path.join(site, name))

    try:
        manifest = json.loads(read_regular(os.path.join(site, "manifest.json")))
    except ValueError as e:
        raise Reject(f"manifest.json: {e}")
    files = manifest.get("files") if isinstance(manifest, dict) else None
    if not isinstance(files, list) or not files:
        raise Reject("manifest.json: no files")
    listed = {}
    for e in files:
        if not isinstance(e, dict) or set(e) != {"path", "size", "sha256"} \
                or not isinstance(e["path"], str) or not e["path"].startswith("packs/") \
                or not PACK.fullmatch(e["path"][len("packs/"):]) \
                or not isinstance(e["size"], int) or not isinstance(e["sha256"], str) \
                or not re.fullmatch(r"[0-9a-f]{64}", e["sha256"]):
            raise Reject(f"manifest.json: bad entry {e!r}"[:300])
        name = e["path"][len("packs/"):]
        if name in listed:
            raise Reject(f"manifest.json: {name} listed twice")
        listed[name] = e

    page = read_regular(os.path.join(site, "web.html"))
    used = {f"{base}-{kind}.webp" for base in PAGE_REF.findall(page.decode("utf-8")) for kind in "tf"}
    if used != set(listed):
        raise Reject(f"manifest.json does not match the page: missing {sorted(used - set(listed))[:5]}, "
                     f"unused {sorted(set(listed) - used)[:5]}")
    present = set(os.listdir(packs))
    if present != set(listed):
        raise Reject(f"site/packs does not match the manifest: unexpected {sorted(present - set(listed))[:5]}, "
                     f"missing {sorted(set(listed) - present)[:5]}")

    data = {}
    for name, e in listed.items():
        b = read_regular(os.path.join(packs, name))
        if len(b) != e["size"] or hashlib.sha256(b).hexdigest() != e["sha256"]:
            raise Reject(f"{name}: size or SHA-256 differs from the manifest")
        check_webp(name, b)
        data[name] = b
    return page, data


def write_file(dst, data):
    tmp = os.path.join(os.path.dirname(dst), TMP + os.path.basename(dst))
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, "wb") as f:
        f.write(data)
    os.chmod(tmp, 0o644)
    os.replace(tmp, dst)


def publish(site, www):
    page, data = check_site(site)
    packs = os.path.join(www, "packs")
    real_dir(www)
    if not os.path.lexists(packs):
        os.mkdir(packs, 0o755)
    real_dir(packs)
    # The web root holds only index.html and packs/ (plus temporary files of an interrupted run).
    for d, allowed in ((www, lambda n: n in ("index.html", "packs")), (packs, PACK.fullmatch)):
        for name in os.listdir(d):
            path = os.path.join(d, name)
            mode = os.lstat(path).st_mode
            if name.startswith(TMP) and stat.S_ISREG(mode):
                os.unlink(path)
            elif not allowed(name) or (name != "packs" and not stat.S_ISREG(mode)):
                raise Reject(f"unexpected entry in the web root: {os.path.relpath(path, www)}")
    # New packs first, then the page, then stale packs, so the page never names a missing pack.
    for name, b in data.items():
        dst = os.path.join(packs, name)
        if not (os.path.exists(dst) and read_regular(dst) == b):
            write_file(dst, b)
    write_file(os.path.join(www, "index.html"), page)
    stale = [n for n in os.listdir(packs) if n not in data]
    for name in stale:
        os.unlink(os.path.join(packs, name))
    print(f"published {len(data)} packs, removed {len(stale)}")


def main():
    cmd, args = sys.argv[1] if len(sys.argv) > 1 else "", sys.argv[2:]
    actions = {"commit": (check_commit, 2), "tree": (check_tree, 1), "publish": (publish, 2)}
    if cmd not in actions or len(args) != actions[cmd][1]:
        sys.exit(__doc__)
    try:
        actions[cmd][0](*args)
    except Reject as e:
        print(f"rejected: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
