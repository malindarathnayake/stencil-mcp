# Security Policy

Stencil is a local MCP server and SVG symbol library (package `stencil-mcp`). How the
project is built, released and defended is described in
[docs/SECURITY_POSTURE.md](docs/SECURITY_POSTURE.md).

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 0.2.x   | ✅        |
| < 0.2   | ❌        |

Security fixes land on the latest minor release only; users on older versions should upgrade.

## Reporting a Vulnerability

**Do not open a public GitHub issue for security reports.**

Report vulnerabilities through GitHub **private vulnerability reporting** on this repository:
[https://github.com/malindarathnayake/stencil-mcp/security/advisories/new](https://github.com/malindarathnayake/stencil-mcp/security/advisories/new).

When reporting, please include:

- Vulnerability type
- Affected file/path
- Reproduction steps (a scene JSON or MCP request is ideal)
- Proof of concept, if available
- Impact assessment

## What to Expect

Stencil is a single-maintainer project. The following are best-effort targets, not a security team SLA:

- **Acknowledgment:** within 72 hours.
- **Assessment/severity triage:** within 7 days.
- **Fix:** critical/high issues target a patched release within 14 days of triage; medium/low severity issues are batched into the next scheduled release.
- **Credit:** reporters are credited in the published advisory with their permission.

## Verifying a Release

Every release wheel and source archive carries a Sigstore-signed SLSA build-provenance
attestation and is listed in `SHA256SUMS`:

```bash
gh attestation verify stencil_mcp-<version>-py3-none-any.whl --repo malindarathnayake/stencil-mcp
sha256sum -c SHA256SUMS --ignore-missing
```

## Scope

**In scope:**

- The `stencil-mcp` package: MCP server, tools, renderer, scene validation, export
- The bundled symbol catalog and templates
- The repository's GitHub Actions workflows and the published release artifacts

**Out of scope:**

- MCP host applications and the models driving them (Claude Code, Codex, Claude Desktop) — report to their vendors
- What a model chooses to draw. Validation checks structure and layout, not whether a diagram is accurate
- Issues requiring an already-compromised local machine or user account
- Social engineering
