#!/usr/bin/env python3
"""Extract the web app files from an upstream Tizen .wgt into a static site.

usage: python3 -I build.py WGT_FILE OUT_DIR LICENSE_FILE

Kept: index.html, js, css, assets, res, icon.
Dropped: config.xml, signature/author files, Tizen service code.
Changes to the upstream files (all in this script):
  - index.html: remove the Tizen webapis script and the wrt:service module
    import; add a robots noindex meta tag.
  - main.js: platform marker "tizen" -> "browser".
Fails if any expected pattern is missing, so an upstream change is never
published half-patched.
"""
import os
import re
import stat
import sys
import zipfile

DROP_NAMES = {"config.xml", "author-signature.xml", ".manifest.tizen"}
DROP_PREFIXES = ("services/", "META-INF/")
SIGNATURE = re.compile(r"^signature\d*\.xml$")

WEBAPIS = re.compile(rb'[ \t]*<script src="\$WEBAPIS/[^"]*"></script>\r?\n')
WRT_SERVICE = re.compile(
    rb'[ \t]*<script type="module">(?:(?!</script>).)*?wrt:service(?:(?!</script>).)*?</script>\r?\n',
    re.S,
)
PLATFORM = b'window.__NUVIO_PLATFORM__ = "tizen";'
NOINDEX = b'  <meta name="robots" content="noindex, nofollow" />\n'


def fail(message):
    sys.exit("build: FAIL: " + message)


def patch_index(data):
    data, n = WEBAPIS.subn(b"", data)
    if n != 1:
        fail("index.html: expected 1 $WEBAPIS script, found %d" % n)
    data, n = WRT_SERVICE.subn(b"", data)
    if n != 1:
        fail("index.html: expected 1 wrt:service block, found %d" % n)
    if data.count(b"<head>\n") != 1:
        fail("index.html: no single <head> line")
    return data.replace(b"<head>\n", b"<head>\n" + NOINDEX, 1)


def patch_main(data):
    if data.count(PLATFORM) != 1:
        fail("main.js: platform marker not found exactly once")
    return data.replace(PLATFORM, b'window.__NUVIO_PLATFORM__ = "browser";', 1)


PATCHES = {"index.html": patch_index, "main.js": patch_main}


def keep(name):
    if name in DROP_NAMES or SIGNATURE.match(name):
        return False
    return not name.startswith(DROP_PREFIXES)


def main(argv):
    if len(argv) != 4:
        sys.exit(__doc__)
    wgt, out, license_file = argv[1:]
    if not zipfile.is_zipfile(wgt):
        fail("not a zip file: " + wgt)
    os.makedirs(out)
    root = os.path.realpath(out)
    count = 0
    with zipfile.ZipFile(wgt) as archive:
        if archive.testzip() is not None:
            fail("corrupt zip")
        names = [i.filename for i in archive.infolist()]
        for required in ("index.html", "main.js", "app.bundle.js", "css/bundle.css"):
            if required not in names:
                fail("missing in archive: " + required)
        for info in archive.infolist():
            name = info.filename
            parts = name.rstrip("/").split("/")
            if name.startswith("/") or "\\" in name or any(p in ("", ".", "..") for p in parts):
                fail("unsafe entry name: %r" % name)
            if stat.S_ISLNK(info.external_attr >> 16):
                fail("symlink entry: %r" % name)
            if info.is_dir() or not keep(name):
                continue
            data = archive.read(info)
            if name in PATCHES:
                data = PATCHES[name](data)
            target = os.path.realpath(os.path.join(out, *parts))
            if not target.startswith(root + os.sep):
                fail("path escape: %r" % name)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "wb") as handle:
                handle.write(data)
            count += 1
    with open(license_file, "rb") as source, open(os.path.join(out, "LICENSE"), "wb") as handle:
        handle.write(source.read())
    with open(os.path.join(out, "robots.txt"), "w") as handle:
        handle.write("User-agent: *\nDisallow: /\n")
    with open(os.path.join(out, ".nojekyll"), "w"):
        pass
    print("wrote %d files to %s" % (count, out))


if __name__ == "__main__":
    main(sys.argv)
