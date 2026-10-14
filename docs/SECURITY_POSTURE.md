# Security posture

This document records what Stencil does to keep the application, the build and the
release pipeline trustworthy, why each control exists, and what is deliberately left
out. It is the reference for anyone changing a workflow, a pin or a security control.

Last reviewed: 2026-10-13 (0.2.0).

## Contents

1. [Threat model in the agentic era](#1-threat-model-in-the-agentic-era)
2. [Application controls](#2-application-controls)
3. [Build integrity](#3-build-integrity)
4. [CI/CD hardening](#4-cicd-hardening)
5. [Security scanning](#5-security-scanning)
6. [Release and verification](#6-release-and-verification)
7. [Repository settings to enable](#7-repository-settings-to-enable)
8. [Pin inventory and update procedure](#8-pin-inventory-and-update-procedure)
9. [Residual risks](#9-residual-risks)
10. [Verification record](#10-verification-record)

## 1. Threat model in the agentic era

Stencil is called by an AI agent, not typed at by a person. Every tool argument is
model-generated, and the model may be steered by content it read elsewhere: a web page,
a ticket, a document. Stencil therefore treats every argument as untrusted, even though
the server only runs locally for one user.

| Threat | Example against Stencil | Control | Reference |
| --- | --- | --- | --- |
| Indirect prompt injection steering tool calls | A ticket tells the agent to embed a script in a diagram label | No caller-supplied markup; all text escaped; schema-validated scenes | OWASP LLM01, ASI01 · [CWE-79] |
| Tool misuse and excessive agency | Agent asked to "export to `../../.ssh/authorized_keys`" | No shell, no network, no file reads; exports are bare names confined to one directory | OWASP LLM06, ASI02 · [CWE-22] |
| Improper output handling | Generated SVG opened in a browser or embedded in a page | Renderer emits only static SVG elements; bundled assets are allowlisted and checksummed | OWASP LLM05 · [CWE-79] |
| Hidden instructions in text | Bidi overrides or invisible characters smuggled into labels | Control, invisible, tag-block and bidi-override characters rejected | ASI06 · [CWE-451] |
| Unbounded consumption | A 50 KB scene producing a 40 MB validation report | Size, count and issue caps (fixed in 0.2.0) | OWASP LLM10 · [CWE-400] |
| Agentic supply chain | A hijacked GitHub Action or scanner release poisons the wheel | SHA pins, checksum-pinned binaries, hash-locked build tools, cooldowns, provenance | OWASP LLM03, ASI04 · [CWE-829] |
| Tool or catalog poisoning | Tampered SVG asset or tool description | Tool definitions are static code; assets verified against catalog SHA-256 at render time | ASI04 · [CWE-494] |
| Unexpected code execution | Scene content reaching an interpreter | Nothing in the request path evaluates, imports or executes caller data | ASI05 · [CWE-94] |

OWASP references: [Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/)
(LLMxx) and [Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) (ASIxx).
ASI03 (identity), ASI07 (inter-agent communication) and ASI10 (rogue agents) do not apply:
Stencil holds no credentials, talks to no other agent and takes no autonomous action.

## 2. Application controls

| Control | Where |
| --- | --- |
| stdio transport only: no listener, no outbound requests, no telemetry | `diagramkit/server.py` |
| 1 MiB per JSON-RPC line; lone UTF-16 surrogates rejected with `-32600` | `diagramkit/server.py:15`, `:22` |
| stdout reserved for protocol; stray prints from library code go to stderr | `diagramkit/server.py:114` |
| Scene schema with full-match identifier patterns, 200 nodes / 400 edges | `diagramkit/scene.py` |
| Control, invisible, bidi-override and non-XML characters rejected | `diagramkit/scene.py:10` |
| Validation reports capped at 200 issues; oversized arrays stop traversal early | `diagramkit/scene.py:11`, `:44` |
| All text XML-escaped; callers cannot supply SVG, HTML, CSS, scripts or image URLs | `diagramkit/renderer.py` |
| Bundled asset checksum verified before use; element allowlist; `on*`, `href` (any namespace), `style` and `url()` rejected | `diagramkit/renderer.py:38-45` |
| Export names are bare stems matching `[A-Za-z0-9][A-Za-z0-9_-]{0,79}`; Windows device names refused | `diagramkit/service.py:57-59` |
| Export directory set by the operator, never by the caller; symlinks refused; no overwrite unless asked | `diagramkit/service.py:62-71` |
| Per-name lock, staged writes, atomic publish, rollback of only this call's files | `diagramkit/service.py:45` |

Regression tests for these live in `tests/test_kit.py` (`HardeningTests`). The
active-SVG test was added during this review. It showed that a namespaced
`xlink:href` passed the attribute check. The impact was low, because the element
allowlist already excluded `<use>`, `<a>` and `<image>`. The check now compares local
names.

## 3. Build integrity

- **No runtime dependencies.** The server, renderer and tests use only the Python
  standard library. The shipped dependency tree is the wheel itself.
- **Hash-locked build toolchain.** `requirements-build.txt` pins `build`, `setuptools`,
  `packaging`, `pyproject_hooks` (and `colorama` on Windows) with SHA-256 hashes.
  CI installs them with `--require-hashes --only-binary=:all:` and builds with
  `python -m build --no-isolation`. Without `--no-isolation`, pip would fetch
  whatever setuptools matches `>=77` at build time.
- **Cooldown.** Pinned versions are at least 14 days old when chosen, and Dependabot
  waits 14 days before proposing a newer one. Most hijacked releases are found and
  pulled within days.
- **Reproducible wheel.** With `SOURCE_DATE_EPOCH` set to the commit time, two builds
  produce byte-identical wheels. CI and release builds twice and fail on any
  difference, so a tampered toolchain shows up as a hash change.
- **Deterministic generated files.** Rebuilding the catalog, schema, templates and
  gallery must leave the tree unchanged; CI fails otherwise. All writes use LF bytes, and
  `.gitattributes` keeps LF on every checkout, because asset checksums are computed on
  bytes.
- **Pinned assets.** Every symbol's SHA-256 is in `catalog.json` and checked at render
  time. The original 300 symbols are also frozen in `tests/fixtures/legacy_sha256.json`.
  `MANIFEST.sha256` records every bundled file.

## 4. CI/CD hardening

Workflows: `ci.yml` (tests, drift, locked build), `security.yml` (scans), `release.yml`
(tag-triggered publish), plus `dependabot.yml`. The pattern follows Foreman's workflows.

| Control | Why |
| --- | --- |
| Every action pinned to a full commit SHA with a `# vX.Y.Z` comment | Tags are mutable. In March 2026 attackers force-pushed 76 of 77 `aquasecurity/trivy-action` tags to credential-stealing code ([GHSA-69fq-xp46-6x23](https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23)). A SHA cannot be re-pointed. [CWE-829] |
| Dependabot `github-actions` updates with a 7-day cooldown (14 for majors) | Pins without an updater rot. The cooldown keeps a just-published release out of the queue. |
| First-party actions only (`actions/*`, `github/codeql-action`), plus PyPA's official `pypa/gh-action-pypi-publish` | Third-party scanners run as checksum-pinned binaries instead (section 5). |
| Workflow-level `permissions: contents: read` (release: `{}`) and per-job grants | Least privilege for `GITHUB_TOKEN`. Every write scope carries a comment. |
| `persist-credentials: false` on every checkout | The token is not left in `.git/config` for later steps to read. |
| Event data reaches shell only through `env:` | No `${{ }}` inside `run:`, so a crafted branch name or tag cannot inject commands. [CWE-78] |
| Release split into `build` (read-only, runs project code) and `publish` (write, runs no project code) | Code under test never holds a write token. |
| `publish` runs in the `release` environment | Requires a reviewer and restricts deployment to `v*` tags (section 7). |
| Strict tag check: `^vX.Y.Z$`, equal to `pyproject.toml` and `diagramkit.__version__` | A mistyped or stray tag cannot publish. |
| Release repeats tests, build, smoke and vulnerability gate on the tagged commit | A tag push can bypass a PR, so nothing is assumed from earlier CI runs. |
| `timeout-minutes` on every job; `concurrency` groups | Bounded runtime; releases never cancel mid-publish. |
| Scheduled weekly security run (Monday 05:17 UTC) | New advisories surface without a commit. Off-the-hour to avoid queueing. |

## 5. Security scanning

All scanners run in `security.yml` on every push to `main`, every PR and weekly.

| Scanner | Version | What it covers | Gate |
| --- | --- | --- | --- |
| CodeQL (`security-extended`) | action v4.38.2 | Python source and the workflow files (`actions` language) | Code scanning alerts |
| gitleaks | 8.30.1 | Secrets in the tree and in full git history; PRs scan their commit range | Fails on any finding |
| zizmor (`pedantic`) | 1.30.1 | Workflow security: injection, excessive permissions, credential persistence, unpinned or impostor-commit actions | Fails on any finding |
| Syft | 1.52.0 | CycloneDX SBOMs of the installed wheel and of the build toolchain | Uploaded as an artifact |
| Grype | 0.119.0 | Known vulnerabilities in both SBOMs | Fails on high or critical |

**Why Grype and not Trivy.** Both would work for this repository. Trivy was the target
of the March 2026 compromise: action tags were hijacked, and a malicious `v0.69.4` binary
was published through official channels (CVE-2026-33634). Grype has no comparable
incident on record, and Syft plus Grype gives SBOM-first scanning that can also ship
with releases. Whichever scanner is used, the protection is the same: an exact version
and a verified SHA-256. A scanner is never pulled with `curl | sh`, a `latest` tag or a
third-party action.

**Binary verification.** Each binary's SHA-256 was taken from the project's release
checksums file and cross-checked against GitHub's own asset digest. The gitleaks digest
also matches the independent pin in Foreman's `security.yml`.

**Gate tested.** Grype was run against a requirements file pinning `setuptools==65.0.0`.
It reported three high-severity advisories and exited 2, so the gate fails as intended.

**Allowlist policy.** `.gitleaks.toml` allows exactly one file: the legacy checksum
fixture, where asset ids such as `secrets-vault` beside 64-character hex digests trip
the `generic-api-key` rule (11 findings, all content hashes). New entries must name an
exact file or string and say why.

## 6. Release and verification

Pushing a `vX.Y.Z` tag runs `release.yml`:

1. **build** (read-only): tag check → unit tests → locked toolchain → two builds,
   compared byte for byte → clean-venv smoke test (CLI plus an MCP render over stdio)
   → SBOMs (CycloneDX and SPDX) → Grype gate → `SHA256SUMS`.
2. **publish** (`release` environment): an SLSA build-provenance attestation, signed
   through Sigstore with the workflow's OIDC identity, for the wheel and sdist → GitHub
   Release with the wheel, sdist, both SBOMs, `MANIFEST.sha256` and `SHA256SUMS`.
3. **pypi** (`pypi` environment): uploads the same wheel and sdist to PyPI with Trusted
   Publishing. The job's OIDC token is exchanged for a short-lived upload token, so no
   PyPI API token exists anywhere. The upload carries PEP 740 attestations. This job
   runs last because a PyPI version can never be replaced once uploaded.

Users verify before installing:

```bash
gh attestation verify stencil_mcp-0.2.0-py3-none-any.whl --repo malindarathnayake/stencil-mcp
sha256sum -c SHA256SUMS --ignore-missing
```

The attestation proves the file was built by this repository's `release.yml` from a
specific commit. It does not prove the code is safe; the gates above are what back that.

## 7. Repository settings to enable

Some controls live in GitHub settings, not in files. Until they are enabled, the
`release` environment exists but has no protection.

| Setting | Value |
| --- | --- |
| Actions → General → Workflow permissions | Read repository contents; do not allow Actions to create or approve pull requests |
| Actions → General → Actions permissions | Allow GitHub-owned actions plus `pypa/gh-action-pypi-publish@*` only; enable **require actions to be pinned to a full-length commit SHA** where the plan offers it (confirmed in organization settings) |
| Environments → `release` | Required reviewer: the maintainer. Deployment branches and tags: `v*` tags only |
| Environments → `pypi` | Same as `release` |
| PyPI → Publishing | Trusted publisher: owner `malindarathnayake`, repository `stencil-mcp`, workflow `release.yml`, environment `pypi`. Enable 2FA on the PyPI account |
| Rules → Ruleset for `main` | Require a pull request and passing `CI` and `Security` checks; block force pushes and deletion |
| Rules → Ruleset for tags `v*` | Restrict creation, update and deletion to the maintainer; block force pushes |
| Code security | Private vulnerability reporting, Dependabot alerts, secret scanning with push protection, CodeQL code scanning: all on |

## 8. Pin inventory and update procedure

Pinned 2026-10-13. All versions were at least 14 days old at pin time.

| Component | Version | Pin |
| --- | --- | --- |
| `actions/checkout` | v7.0.1 | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| `actions/setup-python` | v7.0.0 | `5fda3b95a4ea91299a34e894583c3862153e4b97` |
| `actions/upload-artifact` | v7.0.1 | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` |
| `actions/download-artifact` | v8.0.1 | `3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c` |
| `github/codeql-action` | v4.38.2 | `2892aa5e19bbd11bc0cff5427e3b750a04d9e3c2` |
| `actions/attest-build-provenance` | v4.2.2 | `4d101475d8b20a2381f78447822ac1eab6504dd8` |
| `pypa/gh-action-pypi-publish` | v1.14.2 | `dc37677b2e1c63e2034f94d8a5b11f265b73ba33` |
| gitleaks `linux_x64.tar.gz` | 8.30.1 | sha256 `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb` |
| zizmor `x86_64-unknown-linux-gnu.tar.gz` | 1.30.1 | sha256 `e65324f4430c2717591937edcec90ccbefaf14c174f8ec9415e03ca875b46e1a` |
| syft `linux_amd64.tar.gz` | 1.52.0 | sha256 `caeedb81fb0491615f1ebd1761e4145d41ee86dd2cc7bf80669f9f5ad9d6133d` |
| grype `linux_amd64.tar.gz` | 0.119.0 | sha256 `3fa2dc4b924621ab65404cf08d0b8438d896d80ab949c9d5a4ca283c36004c9b` |
| Build toolchain | see `requirements-build.txt` | sha256 per wheel |

**Actions** are bumped by Dependabot PRs. Review the upstream release notes and diff
before merging; zizmor's online audit confirms the new SHA belongs to the action's
repository.

**Scanner binaries** are bumped by hand, in this order:

1. Pick a release that has been public for at least 14 days. Read its notes and any
   security advisories for the project.
2. Take the SHA-256 from the release's checksums file and confirm it equals GitHub's
   asset digest: `gh api repos/<owner>/<repo>/releases/tags/<tag> --jq '.assets[] | select(.name=="<file>") | .digest'`.
3. Update the URL and the checksum together in every workflow that uses the tool
   (`security.yml`, and `release.yml` for Syft and Grype), then update the table above.

**Build toolchain** updates arrive as Dependabot PRs that rewrite versions and hashes
together. For a manual bump, take hashes from PyPI's JSON API for the exact wheel file.

## 9. Residual risks

- **GitHub itself.** Hosted runners, the Actions platform and Sigstore's public-good
  instance are trusted. A compromise there is out of reach of repository controls.
- **Grype's vulnerability database** is downloaded at scan time. It is data, not code,
  and Grype checks the downloaded database's checksum, but its contents are not pinned. A missing advisory means
  a missed finding, not code execution.
- **PyPI name before the first release.** A pending trusted publisher does not reserve
  `stencil-mcp`; anyone can register the name until the first upload creates it.
- **PyPI is append-only.** A bad upload can be yanked but its version can never be
  reused. The `pypi` job runs only after every gate and the GitHub Release succeed.
- **Local machine.** A compromised workstation or another local process running as the
  same user is outside the MCP server's isolation model (see `docs/MCP.md`).
- **Semantic correctness.** Validation checks structure and layout. It cannot tell
  whether a diagram is accurate, and a model can still draw something misleading.
  Review the rendered output.
- **Unsigned commits.** Commit signing is not enforced. The tag ruleset and the release
  environment reviewer are the controls on what gets published.

## 10. Verification record

Run locally on 2026-10-13 against this tree:

| Check | Result |
| --- | --- |
| Unit tests | 70 run, 69 passed, 1 skipped (optional CairoSVG) |
| Hash-locked build in a clean venv | Built; `--require-hashes` rejected an unhashed transitive dependency until it was pinned |
| Wheel reproducibility with `SOURCE_DATE_EPOCH` | Two builds byte-identical |
| `scripts/smoke_wheel.py` | 324 SVGs, 24 templates, CLI and MCP render work |
| gitleaks 8.30.1, tree and history | No leaks with `.gitleaks.toml` (11 checksum false positives without it) |
| zizmor 1.30.1, pedantic, online | No findings. It first caught a YAML parse error (`--only-binary=:all:` in a plain scalar) that would have broken two workflows |
| Syft 1.52.0 SBOM + Grype 0.119.0 scan (the pinned versions) | Wheel: no vulnerabilities. Build toolchain: no vulnerabilities. Negative control (`setuptools==65.0.0`) exited 2 |

The workflows themselves only prove out on GitHub. The first push should be watched
end to end.
