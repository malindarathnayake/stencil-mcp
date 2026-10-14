# Primary implementation references

Checked while preparing this kit on 2026-10-10. The asset geometry and example
scene files are original kit material, not copied vendor icon collections.

MCP stdio framing and stdout/stderr requirements:
`https://modelcontextprotocol.io/specification/2025-06-18/basic/transports`

MCP lifecycle and version negotiation:
`https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle`

MCP tools, content results and annotations:
`https://modelcontextprotocol.io/specification/2025-06-18/server/tools`

Codex local MCP registration:
`https://developers.openai.com/codex/mcp`

Claude Code local MCP registration and configuration:
`https://code.claude.com/docs/en/mcp`

Official Python SDK for a future maintained transport adapter:
`https://github.com/modelcontextprotocol/python-sdk`

The MRC teaching scene preserves the user-provided packet story and subtitle:
packet 4 is lost, receive state is 1/2/3/5 with gap 4, feedback identifies that gap,
and only packet 4 is retransmitted. It is an explanatory drawing rather than a
wire-level specification, simulator or verified implementation of MRC.
