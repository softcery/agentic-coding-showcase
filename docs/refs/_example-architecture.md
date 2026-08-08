# Architecture

Concise reference. Source = truth. Explains _why_, not _what_.

Certus v2 — a **compliance API platform**. Issue legally-binding TPS
Certificates, track licence limits, report to the Authority — exposed as one public API
anyone can integrate (CRMs, third-party frontends, our own reference web app).
Greenfield rebuild of a legacy Laravel app. `spec/*` numbered docs = the binding
business rules + acceptance criteria (the build target); `spec/compliance.md` =
the TPS regulation the rules are anchored to (`G#` citations point there);
`spec-archive/business-spec.md` = reverse-engineered legacy behaviour, reference
only — we do **not** build to it. **We build to the compliance-corrected rules, not
legacy parity.** Not byte-parity: certs are rebuilt to Authority-prescribed format;
figures must be **correct and reproducible**, not byte-identical to legacy CSV.

Roadmap shapes the bones: (1) public API first-class day 1, (2) heavy reporting to
absorb manual compliance work, (3) more regimes (Cargo…) beyond TPS.

Runtime topology, providers, stack table, and scaling triggers live in
`infrastructure.md`. This ref is code structure + domain rules.

## Build right, defer only leaves

> Foundations, seams, and abstractions are built correct and complete from day 1.
> The only things deferred are **leaves** with no current driver — and only when
> deferring can't compromise correctness. Premature **abstraction** is not building
> right, it's building wrong: an abstraction can't be built correctly from one
> example. So the regime generalization and OAuth wait — their _seams_ are built
> now, the leaf plugs in when a real driver (2nd regime / 1st third-party
> frontend) appears. Everything foundational — event ledger, concurrency, PII,
> idempotency, gates, published events, webhooks — is built now.

## The product is the API

There is **one API**. No public/private split, no privileged client. Every
capability — issue · amend · cancel · report · licence config · tenant admin ·
impersonation — is a versioned, perm-gated API operation. The web app is a
**reference client — its own fenced deployable** (`web/`, lint-fenced to the public
contract type, zero workspace internals) with zero special access; it calls the same
contract a CRM does. The API is provably complete because the first-party app
cannot cheat. (Own-repo extraction is a leaf — `infrastructure.md` Conditional.)

## Layers (deps point inward only)

```
contexts/      bounded contexts. The vertical slices. Own their full stack.
kernel/ minimal regime-neutral primitives (ids, Money, base Event, Result,
               bitemporal fold).
platform/      generic tech behind ports. zero business logic.
apps/          composition roots: api, worker.  Composition only — no logic.
web/           reference SPA — the customer UI. Its own deployable, fenced to the
               public contract type; zero workspace internals. Not under apps/
               (that folder is no-logic composition; web is all logic).
```

- `contexts/*/domain` imports nothing but `kernel`. Never `platform`, never
  another context, never a framework.
- `platform/` knows no business. `contexts/` reach it only through ports declared
  in their own `domain`.
- `apps/` wire contexts + platform together. Composition only — no logic.
- **Structure is a ceiling, not a floor.** A thin CRUD context (licence config)
  needs no event sourcing and may collapse `application/` into trivial handlers.
  Full hexagon + ES only where invariants demand it (certification).

## Invariants

Hard rules. Break one = the design is gone.

- **The API is the product.** Every capability is a versioned, perm-gated operation
  on the one contract. No client is privileged; the reference web app has zero
  special access. Anything it can do, any integrator can do.
- **Events are the ledger.** Certification state is a pure fold over an append-only
  event stream. `replay(events) === live`. Any Authority figure for any past date = fold
  to that date. No figure reconstructed from mutable rows or JSON blobs (the legacy
  sin, `spec/05`,`06`).
- **Append is version-checked.** Events append against an **expected stream
  version**; a concurrent amend that changed the version is rejected and retried.
  No lost updates, no corrupt stream.
- **PII lives behind `PiiVault`.** Consumer PII (names, emails) never enters an event
  body or a blob as plaintext — events hold a `SubjectRef`, resolved through the
  `PiiVault` port. _That seam_ is the foundation built now: keeping PII out of the
  append-only log cannot be retrofitted (you can't rewrite history to pull names out
  of old events). The day-1 adapter is a plain table — erasure = delete the row + the
  PII-bearing blob, while the cert version-event chain (figures, TPS number, dates —
  all non-PII) survives and still replays. Crypto-shred (per-subject keys, encrypted
  blobs, KMS) is a _deferred_ adapter swap behind the same port — no log migration.
  **Consumer PII never enters the auth provider**; Better Auth holds B2B principals
  only, so the auth store's blast radius stays tiny.
- **Reactors are idempotent.** The outbox is at-least-once. Every reactor — render,
  email, webhook — is keyed to dedupe. A redelivery never double-issues, double-
  emails, or double-charges.
- **Writes are idempotent.** Every write command carries an idempotency key. A CRM
  retry must never double-issue a legal certificate. The event-sourced side dedupes in
  the append (stores the key's `eventIds`, re-folds the reply); the relational side
  (identity's `onboard`, `issue-key`) keeps a sibling ledger that stores a **reference,
  never the artifact** — scoped by `(op, actor)`, with shown-once secrets projected away.
  A retry replays an id or honestly refuses (a secret is unrecoverable by design), and a
  leaked row yields no usable credential. Authz runs **before** the dedup, so a known key
  alone never returns an artifact.
- **Contexts are sealed.** A context owns its event streams and read models.
  Nothing outside writes them; nothing inside writes another's. No cross-context
  table reads. Integration is two channels only — published integration events, and
  a context's typed `contract/` query API.
- **One drain site.** Every client — web, CRM, third-party frontend — submits
  through one oRPC handler per use-case: same zod validation, same gates, same emit
  path. No privileged or parallel write path (kills legacy's duplicated SC-update,
  `spec/02`#9). Client parity is a property of the type system.
- **The contract is anti-corruption.** Public DTOs are stable, versioned, and
  mapped to internal commands/events at the `apps/api` edge. Internal churn —
  including the future regime generalization — never breaks an integrator. The oRPC
  contract is the deliverable; typed client + OpenAPI generate from it.
- **Credential → principal.** Auth is credential resolution at the edge; endpoints
  are auth-method-agnostic. API key (M2M) + Better Auth session (first-party) day 1;
  OAuth2 user-delegation slots in as a new resolver, zero endpoint change.
- **Legality is gates.** Every authorization + legality predicate (tenancy `class`,
  ownership, `perms`, regime-enabled, licence-window, status) is a `Gate` owned by the
  verb's context. The UI affordance, the API handler, and the typed client sample the
  **same** gate → validator-vs-display drift is unrepresentable → the legacy IDOR
  class (`spec/07`) cannot exist.
- **Regime-neutral substrate.** TPS vocabulary (`scheme_number`, Authority report formats,
  cert layout, "Holder", "Agent") lives only inside `contexts/scheme/`. Generic
  tenancy (Org · User · Role-preset → `perms`), `Money`, event/outbox machinery, the
  API + webhooks stay regime-neutral. No "TPS" leaks into `kernel` / `platform` /
  `identity`. Authority is `perms`, never a role read by a gate — see `authz.md`.
- **New code never edits central files.** New context = folder + one registry row.
  New command = variant + handler + contract op. New event = variant + fold arm +
  emit site.
- **Total dispatch.** Command/event unions discriminated; every switch ends in
  `assertNever`. New variant fails compile at every unhandled site. No `default`.
- **Money is integer minor-units.** `Money` VO over `bigint` pence; passenger counts
  integers. No string arithmetic (kills legacy penny loss, `spec/01`,`04`).
- **IDs are branded + minted.** `HolderId`, `AgentId`, `BookingId` from a typed
  allocator. Never a bare string.
- **Issue is atomic and render-free.** Issuing appends `CertificateIssued` + an
  outbox row in one transaction — nothing else. PDF, email, webhooks are downstream
  reactions. A render crash never rolls back a legally-issued cert.
- **Projections are derived, never authored.** Default **fold-on-read** — the query
  _is_ the replay, drift impossible. Materialize a projection behind the query port
  only when latency demands it (a swap, not a retrofit). Materialized or not: pure
  function of the stream, rebuildable, divergence from replay = bug.
- **The read side is one bitemporal fold.** Every period figure — filed return,
  SPC liability, licence usage, backdated/forecast report, usage metering — is
  `fold(events, asOf?, businessWindow)`: `asOf` ceilings on **transaction time**
  (when an event was appended), `businessWindow` filters on **business date**
  (departure date). The temporal/windowing engine lives in `kernel`; each
  context supplies only its reducer. A manual figure edit is itself a foldable event
  (a delta), so the filed number is always exactly a deterministic fold — never
  hand-authored read-model state.

## Pillars

### The one contract — `apps/api` (contract-first)

- One contract definition → **typed TS client** + **OpenAPI/REST** + **webhook
  docs**. (No packaged SDK — the typed client + OpenAPI spec are the integration
  surface; an external integrator generates their own client from OpenAPI. A
  published multi-language SDK is a leaf to add when an integrator needs one.)
  Public DTOs versioned + anti-corruption-mapped to internal
  commands. Per-op version metadata; deprecation policy. Idempotency key on every
  write; scopes + rate limits on keys.
- **Framework: oRPC — decided, eyes open.** OpenAPI-native, Zod, one definition →
  typed client + REST. It is the product surface, the **least-swappable** thing
  in the system — chosen deliberately, not "swappable behind a port."

### Auth — credential → principal

```
credential ─┬─ API key (hashed, scoped, expiry)  → principal   [M2M / CRM backend]
            ├─ Better Auth session / bearer token → principal   [1st-party web]
            └─ OAuth2 access token (deferred)      → principal   [3rd-party frontend]
endpoints take the resolved principal; never the credential.
```

**Better Auth** is a TS library in our Node process (tables in our Postgres) behind
`IdentityPort` — it owns _credentials, sessions, 2FA (TOTP/WebAuthn — the `spec/07`
upgrade), and hashed/scoped API keys_. It does **not** own the regulated access
graph: ownership chain, agent quota, consultancy↔holder grants, regime-enabled flags
live in the `identity` _domain_, keyed by Better Auth's `userId`. Gates read that
graph from our own Postgres — never a live auth-provider round-trip. The principal
abstraction is the seam: OAuth2 user-delegation = a new resolver when the first
third-party frontend ships. (Cross-origin note: the separate-repo SPA uses a bearer
token, not a cookie — already token-bearer, OAuth-adjacent.) Folding auth into our
own DB also makes residency a deploy-region choice, not a vendor question — see
`infrastructure.md`.

### Webhooks — `WebhookDispatcher` (platform reactor, built now)

CRMs are push-consumers; integration is the product. The same ▶ integration events
that feed reporting feed an outbound dispatcher: signed payloads, retries with
backoff, idempotent delivery, per-subscriber filtering. First integrator just
registers a subscription — no surgery.

### Bounded context = sealed vertical slice

```
contexts/
  identity/                    generic tenancy: Org · User · Role · membership
                               · API keys · impersonation (audited)
  scheme/                        the TPS regime
    certification/             event-sourced Booking/cert core; passenger manifest
                               (name+age); versioned certs (never deleted)
    licensing/                 TPS licence limits + usage + alerts (thin-ish)
    spc/                       SPC liability = a projection (£2.50 × Σpax≥2, a 1-line
                               fold). Becomes a context only once payment-tracking
                               state lands (Q8); PT remittance ≠ the Authority "return"
    returns/                   event-sourced: the Authority SPC Return. Lock-in is a
                               bitemporal fold (filed = fold @ lock txTime), NOT a
                               stored snapshot; manual edits are delta events. Discrepancy
                               = fold(now) − fold(@lock) over the locked window. An
                               onboarded holder re-enters its still-live book as ordinary
                               backdated `CertificateIssued` imports (a reduced outbox +
                               an `imported` provenance flag — never a returns event); a
                               period it already filed with the Authority is transcribed as a
                               DISPLAY-only `ExternalReturnRecorded` anchor, never folded.
                               A period is filed in exactly ONE lane — Certus lock XOR
                               external transcription, enforced both directions.
    reporting/                 stateless: reconciliation reports + dashboards as
                               replay projections (owns no state)
  (future) cargo/ { ... }       sibling regime, same substrate, zero TPS edits

each context (as thick as it needs, no thicker):
  domain/        aggregates, domain events, value objects, ports
  application/   command + query handlers (CQRS). depend on domain only
  infra/         adapters implementing this context's ports
  contract/      PUBLIC surface: published integration events + typed query API
  index.ts       composition root — exposes only contract/. internals hidden.
```

Rules: owner writes its state; others read via `contract/` only. Cross-context
write forbidden → integration event, or it belongs in one context. A context exists
when it owns ≥1 aggregate with its own invariants. Empty placeholder folder OK.

"TPS Holder" + `scheme_number` are TPS _views_ over identity's generic Org/User:
the `scheme/` context attaches its accreditation profile to a tenant read via
identity's contract. Better Auth holds credentials; the regulated access graph and
accreditation profile live in `identity`, not the auth store.

### TPS regulated rules (live in `scheme/`, from `compliance.md`)

These are domain rules of the TPS regime, not platform invariants — they stay
inside `scheme/`. We build to these _corrected_ rules, not legacy behavior.

- **Certs are versioned, never deleted.** Every amend yields a new cert version;
  all retained (append-only artifacts). Legacy hard-deleted the prior PDF (G6).
  Amend >72h before travel → re-supply the consumer; <72h → record-only.
- **Append time is server-authoritative; the issue date is declared.** The system
  stamps `txTime` — the append instant, never agent-settable, what replay,
  `@expected-version`, and idempotency stand on. The **business issue date**
  (`issueDate`) is **agent-declared** (defaults to the clock's local day, clamped
  ≤ today), versioned, and provenance-tracked — it is what the cert prints and what
  Part A booked basis windows on. Backdating is a real declared path under the
  agent's responsibility; backdating into a **locked** period surfaces as a booked-axis
  discrepancy with the `txTime − issueDate` gap (Report 2), never a silent rewrite of
  the ledger (G2).
- **SPC is tracked money, never on the cert.** £2.50 × passengers(age ≥2), every
  booking, **booking-date basis** (the declared issue date — departure date drives
  only revenue recognition + the passengers-departed report, the guidance note §2.16), a
  booking-event headcount that never refunds on cancellation, paid to PT within
  6 weeks of period end (G1). Liability is a **pure projection** over published cert
  events (a 1-line fold); payment-tracking — the PT remittance aggregate — is
  deferred until Q8. Never rendered on the certificate.
- **Passengers are a manifest with ages.** `Passenger{name, age}`, not an int.
  SPC + licence-limit base count passengers age ≥2. Flight-Only renders all names;
  Single/Multi render lead only (G4).
- **Cert format is Authority-prescribed + unbranded.** No issuer logo/branding on the
  certificate or its email (G3). Renderer maps to Authority artwork behind the port.
- **Reports are reconciliation aids, not the return.** The statutory submission is
  the Authority Portal SPC Return (Part A booked basis / Part B departed basis; quarterly
  <£5m turnover, monthly ≥£5m). SBS vs Standard holder drives cadence (G5).
- **No silent truncation.** Cert fields that overflow are validated on input or
  flowed to extra pages — never silently cut (legacy did, on a legal doc).

### Operator + usage metering (no billing)

`Operator` = a cross-tenant platform role, **not a context** — modeling it as one
would force a god-module that reaches everywhere. Operator exercises wide-scoped
operations on existing contracts: onboard/suspend tenant, toggle a tenant's
**enabled regimes** (TPS now, Cargo later — a gated capability flag, partner-set),
audited impersonation, read the fleet.

`Consultancy` = a cross-**holder** advisory role (a consultancy org advises N
holders, many-to-many; holder grants/revokes). Read-mostly + lock-in / file-return
on the holder's behalf (audited), never issuance. Generic by design: a second
consultancy or the **Authority auditor** is the same seam, zero special-casing. Just more
gates over existing contracts — not a context. See `spec/09`.

No billing context, no Stripe, no subscriptions — the partner invoices manually.
The dashboard gives him the numbers via a **usage-metering projection**: fold
published `CertificateIssued ▶` per tenant / period / regime, excluding `imported`
migrations (a brought-over booking is not a new issuance). Falls out of the
ledger for free. A future billing integration is a _consumer_ of this projection —
the data it needs already exists; build the integration when a driver appears.

### Event spine + CQRS

```
client → oRPC op
  → zod command           (validate at edge; spec/08#33 = legacy had none)
  → credential → principal
  → Gate.check            (authz + legality; same gate the UI sampled)
  → command handler       (idempotent; load aggregate → decide → events)
  → append events @expected-version + outbox   (ONE transaction)
  → read side: fold-on-read (materialize only where slow)
  → reactors (outbox-driven, idempotent): PDF · email · webhooks · usage
```

Certification published set (▶ integration): `CertificateIssued ▶`,
`PassengersAmended ▶`, `CostAmended`, `DateChanged`, `BookingCancelled ▶`,
`CertificateRendered ▶`. Internal events stay private. Cancellation is a
first-class audited event. Each figure-affecting ▶ event carries a **no-PII figure
core** — `bookingRef, version, departureDate, paxCount(≥2), protectedRevenue,
txTime` — plus the **reason classifications** the 3-tier reconciliation needs:
`BookingCancelled ▶` carries its reason (`Cancellation` / `Certificate Created in
Error` / `Duplicate Certificate`, `spec/03-R10`) so the _after-errors_ tier can
exclude error/duplicate cancels; `PassengersAmended ▶` carries its decrease reason
(`Passenger Cancelled` / `Passenger Added in Error`, `spec/03-R6`). Amend events
carry the full new figure-state, not just "changed". So `returns`, `spc`,
`licensing`, `reporting` fold them independently and replay in isolation, never
reaching back into certification. The figure in the event _is_ the record; there is
no second source to drift.

Returns owned events: `ReturnLocked` (period + lock txTime + actor + attestation +
optional Authority Portal ref & date-filed (`spec/06-R9a`, `14-R7`) — **not** a stored
figure snapshot; the filed figures are `fold(@lockTime)`). The lock is returns' ONLY
write: a figure that diverges from the Portal is reconciled through the post-lock
discrepancy + amendment loop, never a manual edit at lock. Supersede = a _later_
`ReturnLocked` for the same period; latest wins, the chain retained for free.
`ExternalReturnRecorded` (an onboarded holder's already-filed period, transcribed off its
real Authority submission, on the SAME period stream) is a declared-fact anchor: a DISPLAY-only
A/B/C-by-type table the read shows but NEVER folds (the anti-double-count guard), doubling
as the period's backdate anchor so a sale later dated into the filed period surfaces as a
prescribed amendment off the live fold. `resolveAnchor` is the single anchor authority —
the last anchor of the one populated lane, since a period is filed in exactly ONE lane
(lock XOR transcription), making the cross-lane "latest wins" race unreachable.
Published (▶): `ReturnLocked ▶`,
`DiscrepancyFlagged ▶` (a booking departing in a locked period changed _after_ its
lock — booking ref + delta + the filed figure it breaks). Discrepancy =
`fold(now) − fold(@lock)` over the locked window — late certs surface as a query,
never a manual hunt. See `spec/06`, `spec/07`.

### Reporting = pluggable projections

Each report = a projection + query over the same stream. Adding a report = a
projection definition, not a rewrite. Historical slices = replay to date T.
Partner's report list maps straight onto projection definitions when it lands.

### Gates — authz + legality, no drift

```ts
interface Gate<Ctx, Pass> {
  check(read: Ctx): Result<Pass, Refusal>
}
```

A `Gate` is owned by the verb's context. `check` returns a branded `Pass` proof
(e.g. `OwnedBooking`) minted only on success — a private-constructor brand the
handler consumes with no re-fetch, no null check. Handlers take the `Pass`, never a
raw id; foreign / wrong-tenant / unknown branches fall out of the type. The same
gate backs the UI affordance, so button and action cannot disagree. Ownership is
not a check you might forget — it is the only way to obtain the capability to act.
Structural fix for every `spec/07` IDOR finding. Entitlement/regime checks are just
more gates.

### Plug-in registration

```ts
// apps/registry.ts — the ONLY central list
export const contexts = [identity, schemeCertification, schemeLicensing, schemeReturns, schemeReporting]
// spc liability is a projection registered against the event broadcast — not a context (until Q8 payment-tracking)
```

`apps/api` folds each `contract` into the one oRPC surface; `apps/worker` folds each
context's reactors into the outbox drainer; projections register against the event
broadcast. New context = `mkdir` + fill slice + one row. A whole new regime
(`cargo/`) = a few rows, zero TPS edits.

Stack (tech picks + swap notes) lives in `infrastructure.md`.

## Conventions

- TS strict + type-aware ESLint + Prettier.
- Imports: same-dir `./x`, cross-dir `@/…`. **Cross-context import of anything but
  `contract/` is an eslint error.** Deep import = the bug.
- Naming (mandatory, greppable): commands verb (`IssueCertificate`); events past
  tense (`CertificateIssued`); handlers `issueCertificate`; ports `*Port`; adapters
  `*Adapter`; projections `*Projection`; gates `*Gate`; branded ids `HolderId`.
- Every command/event switch ends in `assertNever`. Zod schema is the single source
  of a command's shape.
- **Telemetry is edge-instrumented.** Domain + application stay pure — no PostHog
  imports. Product events + errors are captured at the delivery edge (oRPC
  middleware, SPA) and via a `TelemetryPort` adapter fed by published ▶ events.
  PostHog feature flags are for product rollout only — never domain legality (that
  is gates).

### Enforcement honesty (TS ≠ Rust)

The exemplars enforce "no cross-cell write" with the borrow checker. TS cannot.
"Contexts are sealed" is held by three weaker, layered guards: (1) `index.ts`
exports only `contract/`; (2) eslint import-boundary rules; (3) handlers receive
only their own context's repo. Convention + lint, not a compiler proof. A boundary
violation is a build break, not a style nit.

Deferred leaves + their install triggers (Conditional table) live in
`infrastructure.md`.

## Tests (minimal — CLAUDE.md)

- **Replay determinism.** `fold(events)` equals live state.
- **Report reproducibility.** Replay a fixed event fixture → assert standard /
  quarterly / backdated figures. The regulatory contract.
- **Domain invariants.** Aggregate refuses illegal transitions (amend after cancel,
  negative passengers, version conflict).

No tests for config, DTOs, framework glue, or data. When in doubt, no test.

---

The API is the product. No client is privileged; the web app is a reference client.
Events are the ledger. State is a pure fold. Replay must equal live.
Append is version-checked. Reactors are idempotent. PII lives behind `PiiVault`.
One drain site: every client through one validated, gated handler.
The contract is anti-corruption: integrators never feel an internal refactor.
Legality is gates: the UI button and the write path are the same predicate.
Contexts are sealed: integrate through `contract/`, never through tables.
TPS is one regime, not the core. Keep it concrete; generalize on the second.
Build the seam right now; plug the leaf in when a driver appears.
Money is pence as `bigint`. Ids are branded. Switches end in `assertNever`.
Issue appends an event and an outbox row — nothing more. The rest comes after.
