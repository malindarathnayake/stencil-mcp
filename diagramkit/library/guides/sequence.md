# Sequence and interaction diagrams

> Use this guide when the drawing shows who sends which message to whom, in what order: request/response calls, token and SSO flows, webhooks, queues and events, protocol handshakes, agent tool calls, and timeout or failure paths.

## Questions to ask first

Ask only the questions the brief leaves open. If the user skips a question, say out loud the default you will use.

1. Which participants take part, and in what order do they first act? (default: the order they first send or receive a message, with the initiator on the left)
2. What is the full message list, in order, with the sender and receiver of each? (default: one request and one response per hop, nothing else)
3. Which messages are synchronous (the sender waits) and which are asynchronous (queued, published, fire-and-forget or callback)? (default: every call is synchronous)
4. Which replies should be drawn? (default: every response to a synchronous request. For async messages, draw only the transport-level acknowledgement, such as a broker ack or HTTP 202/2xx, as a dashed reply from the broker or endpoint. Draw no reply from the eventual consumer.)
5. Which failure branches should be shown: timeout, error response, retry, invalid or expired token, duplicate delivery, compensation? (default: the success path only)
6. For token or SSO flows: is a user present at all? If yes, what kind of client is it (SPA, native app, server-side web app, or backend-for-frontend), and is the flow OIDC or SAML? If no user is present, is it client credentials, the device authorization grant, or token exchange? Should the refresh-token renewal be drawn, and does the resource server validate tokens locally or by introspection? (default: a user with a server-side web app, authorization code with PKCE, local signature validation, and no refresh path drawn. With no user, client credentials with no browser and no IdP login.)
7. Does anything in the path intercept traffic, such as a gateway, load balancer, reverse proxy or cache, and should it have its own lifeline? (default: show only intermediaries the brief names; responses return through the same hops)
8. Should connection setup be drawn before the application messages: DNS lookup, TCP handshake, TLS (which version, any session resumption or 0-RTT, any client certificate for mTLS), or QUIC? (default: the connection already exists, and no setup is drawn)
9. For webhooks: does the receiver only acknowledge receipt, or does the provider read instructions from the response body (as TwiML-style or chat-command webhooks do)? (default: an immediate 2xx acknowledgement only. Delivery guarantees and retries are not drawn unless the user confirms them, and can be noted in `description` instead.)
10. Should repetition be drawn out or summarised: polling, pagination, retries, or long-running work answered with 202 Accepted and then polled or called back? (default: draw it once with a "loop:" frame label; a plain synchronous response with no 202)
11. Is any of the following in scope: a cache hit/miss branch, a CORS preflight, an HTTP redirect, a streaming connection (WebSocket, SSE, gRPC streaming, long-poll), fan-out to several subscribers, concurrent calls, transaction or saga compensation steps, logout, MFA step-up, or human approval of an agent tool call? (default: none of these is drawn unless the user names it)
12. Where does the flow start and stop, and should latency, RTT or timeout values appear as labels? (default: from the first client action to the response that reaches that client; no timing values)

## Push back when

- **The user wants vertical spacing to show real elapsed time.** In this house style, spacing shows logical order only. Tell them you can slant the arrows to suggest transit time, as in a classic ladder diagram, but the spacing is not to scale. Exact RTT, latency or timeout values go in labels.
- **A TCP open is drawn with other than three segments, or data is drawn on the SYN.** The TCP open is SYN, SYN-ACK, ACK. The final ACK may carry the first data. Data on the SYN only happens with TCP Fast Open, so ask before you draw it. Simultaneous open uses four segments and is rare.
- **TLS is drawn in place of TCP, or before it.** TLS over TCP starts after the TCP handshake. The exception is QUIC (HTTP/3), which combines the transport handshake and TLS 1.3 over UDP with no TCP at all. A full TLS 1.2 handshake takes two round trips. TLS 1.3 takes one, and can send 0-RTT data on resumption. Ask which version applies.
- **UDP is drawn with its own handshake or acknowledgements.** UDP has neither. Any handshake or ack over UDP belongs to the protocol on top, such as QUIC, DTLS, WireGuard or the application, and must be labelled with that protocol's name.
- **The application collects the user's password in a redirect-based OIDC or SAML flow.** The identity provider collects the credentials. The app receives either a code (OIDC, redeemed at the token endpoint) or a signed assertion (SAML POST binding, validated directly). If the user describes the resource owner password grant, say it is deprecated by current OAuth security guidance (RFC 9700), but do not deny that it exists.
- **The authorization code is drawn going to the API.** The code is redeemed only at the token endpoint. Ask what kind of client it is. A confidential web app or BFF redeems the code over a server back channel and keeps the tokens on the server. An SPA or native app redeems it from the browser or device with PKCE and holds the tokens there.
- **A service-to-service call is drawn with a browser login or user consent.** Client credentials involves no user and no browser. The service authenticates directly at the token endpoint.
- **The user asks for the implicit flow as a recommended design.** Current guidance advises against it. Suggest authorization code with PKCE, or draw implicit only to document a legacy system.
- **The resource server calls the identity provider on every request without the user saying so.** Many systems validate JWTs locally with the issuer's public keys. Draw introspection only if the user confirms it.
- **An async message gets a direct return arrow from the eventual consumer.** The producer's reply comes from the broker or endpoint. If they use request-reply over messaging, draw the reply as a separate async message from the consumer through a reply queue to the producer, labelled with the correlation id.
- **A publisher is drawn sending to each subscriber itself.** In pub/sub, the publisher sends one message to the topic or event bus. The broker delivers a copy to each subscriber, and the publisher does not know who they are.
- **A response is drawn bypassing a gateway or proxy it came through.** A proxy that terminates the connection returns the response over the same hop. Only some designs, such as direct server return load balancing, skip it, so ask before you draw one.
- **A client timeout is shown as cancelling the server's work.** A timeout ends the client's wait. The server may still finish unless it honours propagated deadlines or cancellation (for example, gRPC deadlines). Ask which, and offer an idempotency key on the retry.
- **Several services are drawn committing as one atomic step.** Ask whether they use a saga with compensating messages or a real two-phase commit. Draw two-phase commit only if they confirm it.
- **The model is drawn calling a tool or MCP server directly.** The model emits a tool-call request. The agent host or MCP client executes it against the MCP server and returns the result to the model.

## How we draw it here

- **Layout.** Lifeline heads sit in one row across the top, in first-touch order from left to right. Lifelines run straight down. Messages go from top to bottom in order.
- **Lifeline heads.** Use `component` nodes, evenly spaced and at the same `y`. Typical role assets:
  - People and clients: `identity/user`, `identity/admin`, `software/browser`, `compute/mobile`, `software/frontend`, `identity/service-account`.
  - Edge: `network/api-gateway`, `network/load-balancer`, `network/reverse-proxy`, `network/internet` (for DNS, use a labelled `software/external-service`).
  - Services: `software/backend`, `software/rest-api`, `software/grpc-api`, `software/microservice`, `software/background-worker`, `software/external-service`, `software/websocket`.
  - Messaging: `software/message-queue`, `software/message-broker`, `software/event-bus`, `software/topic`, `software/webhook`.
  - Data: `data/relational-db`, `data/cache`, `data/key-value-db`.
  - Identity: `identity/identity-provider`, `identity/mfa`, `identity/secrets-vault`, `identity/certificate-authority`.
  - Agents: `ai/ai-agent`, `ai/llm`, `ai/mcp-client`, `ai/mcp-server`, `ai/tool`, `ai/guardrail`, `ai/human-approval`.
  - Hosts in protocol ladders: `compute/laptop`, `compute/rack-server`, `network/router`.
- **Lifelines.** For each participant, add an empty `text` end anchor at the bottom. Draw an edge from the head (`source_port` `s`) to that anchor (`target_port` `n`) with `kind` `control`, `palette` `slate`, `arrow` `none` and `width` `1`. Do not use `presentation/sequence-lifeline` as the line; it is an icon and does not stretch.
- **Late-created participants.** Stencil cannot start a lifeline partway down from the top row. Place that participant's head at the row where it is created, start its lifeline there, and point the creating message at the head. Show a destroyed participant by ending its lifeline anchor at that row and adding a short note.
- **Messages.** Each message has two empty `text` anchors (`w` and `h` of 1), one at the sender's lifeline x and one at the receiver's, at the same `y`. Connect them with `route` `straight` and ports `e`/`w` (or `w`/`e` for leftward messages). Keep about 80 to 90 units between rows. To slant a message on purpose, put the receiver's anchor lower.
- **Edge kinds.** Requests, one-way messages and protocol signalling are `data` (solid). Responses and acknowledgements are `feedback` (dashed). Use `control` only for lifelines, because it renders with the same dash as `feedback`. Put "(async)" in async labels, and use a prefix such as "SYN" or "event:" for signalling. Colour never carries meaning on its own.
- **Numbering.** Start every label with its number, such as "1. POST /orders". Numbers follow drawing order and do not restart inside frames.
- **Self-calls.** Use two anchors on one lifeline about 40 units apart, plus `points` that step out to the right and back, for example `(x+60, y1)` and `(x+60, y2)`.
- **Frames (alt, opt, loop, par).** Use a `panel` group spanning the affected lifelines and rows, with the operator and condition in the title: "alt: cache miss", "loop: until page is empty", "par: notify all". Put the message anchors in that group. In a `par` frame, the rows are concurrent even though they are stacked. Streaming gets a "loop: stream" frame after the opening request. There are no activation bars, so do not fake them with narrow cards.
- **Failures.** Draw the failing message in `red`. A lost or timed-out message ends at a `marker` node with a failure `state`, not at the receiver. Use `status/down` or `status/expired` for outcomes, and `resilience/timeout`, `resilience/retry` or `resilience/circuit-breaker` as small `symbol` nodes when that policy is the point.
- **Palettes.** Use one palette per hop or concern, `red` for failures and `slate` for lifelines.
- **Legend and footer.** Add a `legend` with one entry per meaning, with `dashed` set for the response entry. Keep the standard footer. State in `description` that the drawing is a logical sequence with no timing guarantee.
- **Size.** `validate_diagram` gives a `density` warning when a panel holds more than 28 nodes, or when ungrouped nodes exceed 28. Each lifeline uses 2 nodes and each message uses 2, so keep 2 x lifelines + 2 x messages at 28 or fewer: about 10 messages with 4 lifelines. Frame panels spread the count. Treat the warning as the signal to split the flow, for example "Sign-in" then "API call with token".

## Common mistakes

- Running `layout_diagram` on a sequence. It produces a layered graph, not ordered rows, so place coordinates by hand.
- Connecting messages between head cards instead of per-row anchors, which loses the order.
- Drawing responses as `data`, or signalling as `control`, so it looks like a response.
- Leaving out message numbers.
- Drawing async calls as if the sender waits, or adding a consumer reply the system never sends.
- Inventing a handshake, retry, refresh or token check the user never described. Ask instead.
- Using `presentation/process`, `presentation/step` or `presentation/decision` as lifeline heads.
- Using stand-ins such as `software/rest-api` for an identity provider, `security/policy-engine` for a gateway that only forwards traffic, or `ai/llm` for the host that runs tools.
- Placing a participant in the middle because it "feels central", which makes messages cross.
- Letting a failure branch share rows with the success path, instead of putting it in its own `alt` panel.
- Drawing dropped messages reaching the receiver.
- Ignoring the `density` warning.

## Start from

- Template: `sequence-request` (client, gateway, service, database). Load it with `get_template`. Its last message returns from the service straight to the client. Replace it with "5. Response" (service to gateway, `feedback`) and "6. Response" (gateway to client, `feedback`).
- Companion topology templates: `agent-mcp-tools` for the agent tool-call cast, `event-driven` for publish/subscribe, and `zero-trust-access` for identity-aware access. Use `mrc-loss-recovery` instead of a ladder to show packet loss and recovery over multiple paths.
- Read alongside: `brief` first, then topics such as `network`, `security-architecture`, `software-architecture` and `style`. Call `stencil_guide` with no topic to list the ids installed.
- Check `get_guidelines` for connector meanings. Then run `validate_diagram` and `preview_diagram`, and check the result at display size.
