# tv-web-shell

Web build of an upstream GPL-3.0 project, rebuilt daily from the latest upstream release.

- Upstream source: https://github.com/NuvioMedia/NuvioTVSmart
- License: GPL-3.0, see [LICENSE](LICENSE)

The web files come from the upstream release package. The only modifications
are made by [scripts/build.py](scripts/build.py): the platform-specific script
imports are removed, the platform marker is set to `browser`, and a `noindex`
meta tag is added. Packaging, signature and platform service files are not
included.
