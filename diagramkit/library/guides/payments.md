# Payment and financial transaction flows

> Use this guide when drawing card, wallet or account-to-account payment flows: authorisation, capture, clearing and settlement, tokenisation, 3-D Secure, recurring charges, payouts, refunds, chargebacks and reconciliation.

## Questions to ask first

Ask only the questions the brief leaves open, in one round, so the user can answer "yes to all" or correct one.

1. Which payment method is this: card, wallet (device-token payments such as Apple Pay or Google Pay), account-to-account, or several? (default: card, customer not present, online checkout)
2. What role does the user's organisation play: merchant, payment service provider or gateway, marketplace or platform paying out to sellers, acquirer, or issuer? (default: merchant using one third-party gateway)
3. Which hops should appear: customer, merchant, gateway, acquirer, card network, issuer, or a shorter view with one "payment provider" participant? Is there more than one provider, with an orchestration layer routing or retrying across them? (default: all six hops for an authorisation diagram, collapsed for an architecture view; one provider)
4. Which stages are in scope: authorisation only, authorisation plus capture, or the full chain through clearing, settlement, payout and reconciliation? (default: authorisation and capture, with clearing and settlement as a later batch path)
5. How is card data entered and stored: hosted page or redirect, hosted fields or iframe, a provider JavaScript SDK, or the merchant's own form? Is the card a gateway token, a network token, or a raw card number? Should PCI DSS scope boundaries be drawn? (default: hosted fields from the gateway, gateway vault token, card data never touches merchant servers, scope boundaries drawn)
6. Is 3-D Secure or another strong-customer-authentication step in the flow? (default: 3-D Secure 2, frictionless path drawn as the main line, challenge branch drawn as a numbered alternative)
7. How is capture done: immediately with authorisation, delayed (for example at shipment), partial, multiple partial captures, or with incremental authorisations? (default: one delayed full capture after fulfilment, before the authorisation expires)
8. Are there recurring or merchant-initiated charges on a stored card? (default: no)
9. How does the merchant learn the outcome, and what happens when the authorisation times out: retry with the same idempotency key, reverse, or query status? (default: synchronous response for the authorisation; webhooks for later changes; on timeout, reverse and query status)
10. Should refunds, voids, disputes and chargebacks be included? Are payouts to third parties (sellers, drivers, vendors) in scope, with seller onboarding and KYC before payout? (default: refunds as a separate flow; chargebacks, payouts and KYC left out unless the role is marketplace)
11. Is reconciliation in scope, against which sources (settlement reports, bank statements, internal ledger), and is the ledger double-entry? Is more than one currency involved, and who does the FX? (default: settlement report matched to a double-entry ledger with one debit and one credit row per movement; single currency)
12. For account-to-account: is it a push credit transfer or a pull debit (direct debit or ACH debit with a mandate), who initiates it, and in which scheme or region (for example SEPA Inst, Faster Payments, FedNow or RTP, ACH, Pix, UPI)? (default: push, instant scheme via a payment-initiation provider, UK/EU)

## Push back when

- **"Payment confirmed" at authorisation.** An approval means the issuer approved the transaction and normally holds the cardholder's funds. No money has moved to the merchant. Capture, clearing and settlement come later, and an uncaptured authorisation can expire. Ask whether the user means "authorised" or "settled".
- **The full card number outside the vault.** If the brief puts the full card number (PAN) in the order database, logs or analytics, say this brings those systems into PCI DSS scope and defeats tokenisation. Truncated values (last four digits, BIN) and tokens are fine on merchant systems; the full PAN is not. Ask whether they mean a token. Do not quietly draw a token instead.
- **The security code (CVV/CVC) stored after authorisation.** PCI DSS does not allow storing it after authorisation, even encrypted. Leave it out of every data store.
- **"Exactly-once" payments without idempotency keys.** Clients and gateways retry on timeout, a timed-out authorisation may still have been approved by the issuer, and webhooks are delivered at least once and can arrive out of order. The flow needs an idempotency key, receiver de-duplication, a ledger that rejects duplicates, and a timeout-reversal or status-inquiry path for unknown outcomes. If these are missing, say the claim is not supported and ask which mechanism they use.
- **"Refund" used for every reversal.** There are three different operations: a void or authorisation reversal before capture; a void of a capture before it is sent for clearing (same batch, before cutoff), which moves no money; and a refund after clearing, which is a new credit transaction, usually authorised online first and then cleared and settled. Ask which case is meant.
- **Partial capture drawn as a refund.** Capturing less than was authorised is a partial capture; the rest of the hold is released, not refunded.
- **A chargeback started by the merchant.** The cardholder disputes with the issuer, and the issuer raises the chargeback through the card network to the acquirer. The merchant responds with evidence.
- **3-D Secure drawn as the authorisation, or as merchant-to-issuer.** In 3-D Secure 2 the merchant or gateway's 3DS Server sends the request to the card network's Directory Server, which routes it to the issuer's access control server (ACS). The result (CAVV/AAV and ECI) is then carried in the authorisation request. Successful authentication does not mean the issuer will approve.
- **A wallet drawn as the issuer.** The wallet provisions a device token through the network's token service and passes a cryptogram; the card's issuer still authorises.
- **Disputes on account-to-account payments.** Push credit transfers have no card-style chargeback, though some schemes have fraud-reimbursement rules (for example UK authorised-push-payment reimbursement). Pull debits have scheme return and refund rights (for example SEPA Direct Debit refunds within eight weeks, ACH returns). Ask which applies before drawing a dispute or return flow.
- **Direct debit drawn as instant or irrevocable.** Direct debits run in scheduled batches against a mandate and can be returned after collection.
- **Card settlement drawn as real time.** Scheme clearing and settlement between issuer and acquirer is a batch process, usually settling the next business day, and merchant funding typically takes one to three days. If the brief shows funds arriving in real time, ask whether it means an instant-payout product, a push-to-card credit, or scheme settlement, and label it accordingly.

## How we draw it here

**Two views, not one.** Draw authorisation and 3-D Secure as a sequence, and clearing, settlement, payout and reconciliation as a left-to-right flow. When both share a figure, put them in separate `panel` groups ("Real time, at checkout" and "Batch, after capture").

**Sequence form.** Follow the sequence guide and the `sequence-request` template: participant cards across the top, lifelines as `control` edges with `palette: "slate"`, `arrow: "none"` and `width: 1` down to empty `text` anchors, and time running downward. Each message runs between its own pair of empty 1x1 `text` anchors placed on the two lifelines at that message's y, with `route: "straight"`. Use source_port `e` / target_port `w` for a rightward message (reverse them for a return) and set `label_x`/`label_y` above the line. Use `data` for requests and `feedback` for responses. Number every message. Add a `presentation/decision` symbol only where the flow really branches (approved or declined, frictionless or challenge).

**Participant assets.** Keep cards generic and labelled by role, never by brand.

- Customer or cardholder: `identity/user`. Device: `software/browser` or `compute/mobile`.
- Merchant checkout: `software/frontend`; merchant server: `software/backend`; ledger: `data/relational-db`.
- Gateway or payment provider: `software/external-service` (`network/api-gateway` only for the user's own gateway). Provider orchestration retries: `resilience/retry`.
- Acquirer, card network, issuer, 3DS Server, Directory Server, ACS, payment-initiation provider and payer's bank: `presentation/external-entity` or `software/external-service`, labelled by role ("Directory Server (card network)").
- Fraud or risk scoring: `security/policy-engine`. Cardholder challenge: `identity/mfa` or `identity/passkey`. Seller KYC check: `security/policy-engine` labelled "KYC".
- Token vault: `identity/secrets-vault` labelled "Token vault"; `hardware/hsm-device` for the HSM and `identity/key` for a named key. Never `identity/access-token` for a card token.
- Money objects: `business/payment` for a payment, payout or direct-debit mandate; `business/invoice`; `business/report` for a settlement or reconciliation report; `business/vendor` for a seller; `business/approval` and `business/rejection` for outcomes.
- Batch steps: `software/batch-job` or `software/scheduler` for clearing and reconciliation runs, `data/dataset` for a settlement file, `software/webhook` for the notification sender, `business/timer` for a settlement window or authorisation expiry.
- States: place `status/pending`, `status/approved` or `status/expired` as small `symbol` nodes with a `caption` where the state matters. The `marker` node kind has only the states normal, missing, dropped, received, pending, down and blocked, and no approved or expired.

**Edge meanings.** Real-time messages are `data` edges in `palette: "blue"`; batch clearing and settlement messages are `data` edges in `palette: "purple"`. Funds movement, when it must be distinguished, is `data` in `palette: "green"` with its own legend entry. Webhooks are `feedback` edges labelled "webhook (at least once)" with their own legend entry (`dashed: true`). Use `replication` only for data replication, never money.

**PCI scope.** When card data appears, draw scope exactly as the security-architecture guide does (cardholder data environment, connected, and out-of-scope `boundary` groups). Do not invent or rename zones.

**Legend and footer.** Add a `legend` whenever two of real-time, batch, funds movement and webhooks appear. Keep the standard footer and add that scheme rules, timings and fees vary. State payment method, role and stages in `description`.

## Common mistakes

- Ending the flow at "Approved" and implying the merchant has been paid.
- Drawing the merchant payout as equal to total captures; payouts are net of fees, refunds, chargebacks and reserves (and FX), which the settlement report itemises.
- Drawing settlement money from the card network's own account; the network coordinates settlement between issuer and acquirer.
- Collapsing acquirer, network and issuer into one "bank" card when the user asked for the hops.
- Drawing 3-D Secure straight from merchant to issuer, or not passing CAVV/ECI into the authorisation.
- Putting the full card number on the merchant server, in logs or in a webhook payload when the flow is tokenised, or drawing a merchant-built card form when the default is hosted fields.
- Drawing the token vault inside the out-of-scope zone, or with no boundary.
- Showing a webhook as the only confirmation without retry or de-duplication, or in guaranteed order.
- Drawing a timed-out authorisation as declined, with no reversal or status-inquiry path.
- Drawing a refund after clearing as an arrow back along the authorisation path. It is a new credit with its own online refund authorisation and clearing; draw the online leg on the real-time path and the money on the batch path.
- Drawing each recurring charge with 3-D Secure, or the first stored-credential charge without it.
- Picking stand-ins when guessing: `network/load-balancer` for the gateway, `security/firewall` for fraud scoring, `identity/access-token` for a card token, `data/cache` for the vault, a `marker` for an approved state.
- Adding components the user did not mention (a second provider, a fraud vendor, a separate HSM). Ask instead.
- Mixing real-time and batch arrows in one sequence.

## Start from

- `sequence-request` for authorisation, capture, 3-D Secure and timeout handling.
- `threat-model-dfd` for tokenisation, vault and PCI scope-reduction views.
- `fin-procurement-approval` only as a swimlane pattern for dispute, refund-approval, seller-onboarding or reconciliation-exception processes; it covers procure-to-pay, not the payment rail.
- No template yet for clearing, settlement, payouts or reconciliation; use `layout_diagram`.

Read alongside: `brief`, `sequence`, `security-architecture` and `style`.
