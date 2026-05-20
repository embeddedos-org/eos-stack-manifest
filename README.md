<div align="center">

# 🏭 eFab

<!-- begin: org-uniform badges (audit-2026-05) -->
[![CI](https://github.com/embeddedos-org/eFab/actions/workflows/ci.yml/badge.svg)](https://github.com/embeddedos-org/eFab/actions/workflows/ci.yml)
[![CodeQL](https://github.com/embeddedos-org/eFab/actions/workflows/codeql.yml/badge.svg)](https://github.com/embeddedos-org/eFab/actions/workflows/codeql.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/embeddedos-org/eFab/badge)](https://securityscorecards.dev/viewer/?uri=github.com/embeddedos-org/eFab)
[![Release](https://img.shields.io/github/v/tag/embeddedos-org/eFab?label=release&sort=semver)](https://github.com/embeddedos-org/eFab/releases)
[![License](https://img.shields.io/github/license/embeddedos-org/eFab)](LICENSE)
<!-- end: org-uniform badges (audit-2026-05) -->


### EmbeddedOS — Stack Fabricator (Manifest-Only Meta-Repo)

*A recipe repo that pins versions, fetches sources, and runs end-to-end
smoke tests for opinionated bundles of EmbeddedOS canonical products. **eFab
ships no product code of its own**; it is a manifest, a CMake superproject,
and an integration test, nothing more.*

<br>

[![License](https://img.shields.io/badge/license-MIT-yellow?style=flat-square)](LICENSE)
[![Profiles](https://img.shields.io/badge/profiles-1-58a6ff?style=flat-square)](manifests/)
[![Canon](https://img.shields.io/badge/canon-13_repos_·_14_books-3fb950?style=flat-square)](https://github.com/embeddedos-org)

</div>

## Why eFab exists

The EmbeddedOS organisation publishes 13 small, independently-versioned
product repositories. That is a deliberate choice — eIPC alone is a useful
secure-IPC layer, eAI alone is a useful on-device inference framework, and
so on.

But there is a recurring class of consumer that wants a **single, named,
version-pinned bundle** for one specific use case (intelligent edge node,
production AI MCU, BCI prototype). For that audience, this repo provides
recipes called **profiles** that fetch a known-good combination of canonical
repos, build them as a CMake superproject, and run a smoke test that
exercises the dataflow.

eFab is the *fabricator*: it composes; it does not contain.

## What eFab is **not**

- **Not** a 14th product. The canonical list is still **13 repos / 14
  books**. eFab is a meta-repo, in the same category as
  `embeddedos-org/.github` and `embeddedos-org/embeddedos-org.github.io`.
  It is intentionally excluded from the canon count and from the per-product
  books library.
- **Not** a fork or a copy of any product code. There is zero kernel /
  framework / library source under this repo. A `git grep` for source
  files turns up only manifests, CMake, smoke tests, and docs.
- **Not** a replacement for `ebuild`. `ebuild` is the build tool. eFab
  is a curated set of input recipes for it.

## Profiles shipped at v0.1.0

| Profile | Repos pulled | Use case |
|---|---|---|
| **eai-edge** | eNI + eIPC + eAI | Intelligent edge node with neural-interface input. Pipeline: `ENI ➜ EIPC ➜ eAI`. |

More profiles (`embedded-core`, `smart-edge`, `full-system`, `devkit`,
`appsuite`) are tracked in [`docs/roadmap.md`](docs/roadmap.md) and will
land as separate v0.2 / v0.3 releases when each one has a working
integration test.

## Quick start

```bash
git clone https://github.com/embeddedos-org/eFab.git
cd eFab/superproject/eai-edge

# Configure the superproject — FetchContent will clone eNI, eIPC, eAI
# at the versions pinned in ../../manifests/eai-edge.yml.
cmake -B build -DCMAKE_BUILD_TYPE=Release

# Build all three repos as one tree
cmake --build build -j

# Run the end-to-end smoke test (ENI -> EIPC -> eAI loopback)
python3 ../../tests/eai-edge/smoke_test.py
```

If you already have a clone of `ebuild`, you can also drive eFab through
the `ebuild` profile mechanism:

```bash
ebuild build --profile eai-edge --manifest path/to/eFab/manifests/eai-edge.yml
```

## Repo layout

```
eFab/
├── manifests/
│   └── eai-edge.yml            ← profile definition (repos + versions)
├── superproject/
│   └── eai-edge/
│       └── CMakeLists.txt      ← FetchContent superproject for the profile
├── tests/
│   └── eai-edge/
│       └── smoke_test.py       ← end-to-end integration smoke test
├── scripts/
│   └── check-product-canon.py  ← shared canon validator (drop-in)
├── docs/
│   ├── architecture.md         ← how eFab fits between ebuild and the products
│   └── roadmap.md              ← upcoming profiles and version pins
├── .github/workflows/
│   ├── ci.yml                  ← build the superproject + run smoke tests
│   └── check-canon.yml         ← lock 13/14 canon
├── CHANGELOG.md
├── LICENSE                     ← MIT
├── README.md                   ← (this file)
└── SECURITY.md
```

## Versioning

eFab's own semver tracks **profile schema and recipe stability**, not the
products it pulls. Each profile manifest declares its own per-repo
version pins. A pin bump in a manifest is a minor version bump for eFab.

## Contributing

eFab is a recipe repo — most contributions belong upstream:

- A bug in inference behaviour → file in [`eAI`](https://github.com/embeddedos-org/eAI).
- A bug in transport / authentication → file in [`eIPC`](https://github.com/embeddedos-org/eIPC).
- A bug in sensor / decoder → file in [`eNI`](https://github.com/embeddedos-org/eNI).
- A profile that fails to build, a missing pin, a missing smoke test, or
  a new profile request → file *here*.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) (this repo) for stack/manifest contributions.
For changes inside an upstream product, follow that product's own `CONTRIBUTING.md`.

<!-- begin: release-model (audit-2026-05) -->
## Release model

`master` is the line of development; every PR lands here. `release` is a
rolling pointer to the latest released `vX.Y.Z` tag, updated automatically
by [`.github/workflows/sync-release-branch.yml`](.github/workflows/sync-release-branch.yml).
Tags are immutable.

See [embeddedos-org/.github/STANDARDS.md](https://github.com/embeddedos-org/.github/blob/master/STANDARDS.md)
for the org-wide tag scheme, release model, and the compliance frameworks
every product targets.
<!-- end: release-model (audit-2026-05) -->

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

**Part of the [EmbeddedOS](https://embeddedos-org.github.io) ecosystem.**

[🌐 Website](https://embeddedos-org.github.io) · [📖 Docs](https://embeddedos-org.github.io/docs/) · [🏭 Stacks](https://embeddedos-org.github.io/stacks/) · [📚 Books](https://embeddedos-org.github.io/books.html)

</div>
