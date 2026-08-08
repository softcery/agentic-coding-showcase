# 082 — Amendment tracker names the actor

**What.** Record **who** made each certificate change. Every human-initiated mutation event
(`PassengersAmended`, `CostAmended`, `DateChanged`, `IssueDateChanged`, `ContentAmended`,
`BookingCancelled`) carries the acting principal; the amendment tracker (`HistoryEntry` +
`Cancellation`) folds it and the UI shows the resolved name — a person, or a named API key.

**Why.** The consultant's TPS reporting review (§39, `spec/reporting-notes.md`): the
amendment tracker "should reflect the date and time of the change, **and
which agent made the adjustment**." Date + time already land (`HistoryEntry.at`); the actor
does **not**. Only `CertificateIssued` records its agent — every amend/cancel drops it. The
proof the handler already holds (`OwnedBooking`) carries `agentUserId` (`domain/gates.ts:44`)
and the system throws it away at the event boundary. This is not new data — it is a dropped
field re-persisted.

**Done when.** Every mutation event carries `agentUserId`; `HistoryEntry.by` + `Cancellation.by`
fold it; the cert view's tracker shows a resolved name for each change and the cancellation;
a change made by an API key resolves to that key's label, not a blank or a raw id; repo
compiles, suite green.

## Status — BUILT

All three stages shipped, end to end, exactly as planned. No deviations.

- **a — Authorship on the ledger.** `interface Authored { agentUserId }`
  (`certification/domain/events.ts`); six mutation payloads `extends Authored`
  (`CertificateIssued` for symmetry, `ContentAmended` gains the one field, no `holderOrgId`).
  Five builders (`booking.ts`) take `agentUserId`; `amend.ts`/`cancel.ts` pass
  `owned.agentUserId` (stamped, never fetched — `R3`). `view.ts`: `HistoryEntry.by` +
  `Cancellation.by` (`AgentUserId`), folded by all six reducers. `FigureCore`/`publishedFigure`
  untouched — downstream folds (returns/spc/licensing) + the CRM webhook never see it (`R4`,
  verified: `cert.publish` delivers `publishedFigure`, not the raw payload).
- **b — Resolve principal → name.** `keyLabelsOf` port + Better-Auth adapter (batch over
  `apikey` metadata); `identity.principalNames` = the ONE read-time split (user name → key
  label, miss → absent). Wired behind certification's `agentNames` dep (`compose.ts`), so the
  bookings roster and the tracker share one resolver (`R5`).
- **c — Surface in the tracker.** Route `withActors` resolves distinct `by` ids → names at the
  edge (placeholder `—`), applied to issue/amend/cancel/view; `by: string` on the
  `historyEntry`/`cancellation` DTOs (raw credential id never crosses the wire). Web renders the
  name beside each history row + the cancellation line.

Spec: `03-R15` (acting principal on every change, cites the consultant §39), `08-R3` (change log names
the actor). Tests: `certification.test.ts` folds + builder assertions; acceptance amend+cancel
assert `by: "CRM integration"` — the journey's agent IS a key, so `A1`/`A3`/`A4` prove
end-to-end through the one contract. `keyLabelsOf` added to the identity fakes
(`acceptance/identity-fake.ts`, `identity.test.ts` stub). All suites green; typecheck + lint +
format clean.

## Stages

Three stages, shippable in order. Stage a is one atomic vertical (the mixin spans
payload → builder → fold → contract; a layer split leaves the repo uncompiling — a payload
field read by a fold that doesn't have it). b + c each ship on their own.

- **a — Authorship on the ledger.** `Authored` mixin, six payloads, builders, handlers, fold,
  contract. End state: the id is recorded and exposed; UI not yet wired.
- **b — Resolve principal → name.** `agentNames` falls back user → key label. The one place
  the human/key split lives.
- **c — Surface in the tracker.** Web panel renders `by` on each history + cancellation row.

## Rules

- `R1` **Authorship is its own concept, orthogonal to scope.** A new
  `interface Authored { readonly agentUserId: AgentUserId }` (`certification/domain/events.ts`).
  The six mutation payloads `extends Authored`; `CertificateIssued` already conforms (it has the
  field) and extends it too, for symmetry. `Authored` does **not** bundle `holderOrgId` —
  `holderOrgId` is downstream figure-scoping (returns/spc/licensing fold by it), a separate
  concern. `ContentAmended` proves the split: it carries neither `holderOrgId` (not a figure
  event) nor needs it — it gains **only** `agentUserId`.
- `R2` **Mandatory, no fallback.** No live ledger data exists, so `agentUserId` is required from
  the first write — no sentinel, no `upcastCertificationEvent` change, no optional field. Every
  event constructor (incl. tests, acceptance journeys) supplies it or fails compile.
- `R3` **The actor is already in scope — stamp it, do not fetch it.** The handler holds
  `owned.agentUserId` (`application/amend.ts`, `application/cancel.ts`); it is the value, passed
  to the builders. No route threading, no new dep, no new gate.
- `R4` **`agentUserId` stays out of `FigureCore`.** It is not a figure field; `publishedFigure`
  never copies it; downstream contexts and the CRM wire never see it. Authorship is a
  certification-internal audit concern — zero pollution of the figure contract (`data-model.md`
  one-door rule holds).
- `R5` **One name resolver, one split.** The recorded id is the opaque credential id —
  `ActorView.id` is _already_ polymorphic ("a user id for a session, a key id for a key, so the
  audit records the KEY", `kernel/acl.ts:46`). The human-vs-key distinction is resolved at **read
  time** in the existing `agentNames` port (`certification/index.ts:72`), which falls back
  user-name → key-label — mirroring `me`'s "key id misses the user lookup"
  (`identity/index.ts:152`). No discriminator on the wire, no `Principal` sum type, no new port.
- `R6` **Artifacts have no author.** `CertificateRendered` / `CertificateConfirmed` are
  reactor-generated, not human-initiated — they stay un-`Authored`. The boundary is "a person or
  key initiated this," not "this event exists."
- `R7` **`AgentUserId` brand stays as-is.** It already tolerates a key id by existing design
  (`R5`). Renaming it to an honest `PrincipalId` is a separate refactor — out of scope; do not
  start it here.

## Acceptance

- `A1` **Given** an agent amends a booking's passenger count, **when** the cert tracker is
  viewed, **then** that change row shows the agent's name beside its date/time.
- `A2` **Given** one amend command changing pax **and** cost **and** departure at once, **when**
  the tracker is viewed, **then** each of the three change rows (same version) names the same
  agent.
- `A3` **Given** a booking cancelled by an agent, **when** the cert is viewed, **then** the
  cancellation fact names that agent.
- `A4` **Given** a change made via an API key (CRM path), **when** the tracker is viewed,
  **then** the row names the **key's label** (e.g. `Acme CRM`), not a blank or a raw id.
- `A5` **Given** any amend, **when** downstream figures (returns/spc/licensing) or the CRM
  webhook fold the published event, **then** they observe no `agentUserId` — `FigureCore` is
  unchanged (`R4`).

## Approach

### a — Authorship on the ledger

**`certification/domain/events.ts`**

- Add `interface Authored { readonly agentUserId: AgentUserId }` (`AgentUserId` already imported).
- `PassengersAmendedPayload` (`:108`), `CostAmendedPayload` (`:115`), `DateChangedPayload`
  (`:121`), `IssueDateChangedPayload` (`:132`), `BookingCancelledPayload` (`:154`) — each
  `extends Authored` (they already carry `holderOrgId`; add the one field).
- `ContentAmendedPayload` (`:145`, currently `{ version, content }`) — `extends Authored`; gains
  `agentUserId` only, no `holderOrgId`.
- `CertificateIssuedPayload` (`:68`) — `extends Authored` (no value change, it has the field).
- `publishedFigure` (`:271`) untouched — confirm it does not copy `agentUserId` (`R4`).

**`certification/domain/booking.ts`** — builders take the actor:

- `amendPassengers` (`:158`), `amendCost` (`:172`), `amendDepartureDate` (`:182`),
  `amendIssueDate` (`:197`), `cancelBooking` (`:241`) — add an `agentUserId: AgentUserId`
  parameter (alongside the existing `holderOrgId` where present); set it on the returned payload.

**`certification/application/amend.ts`** — pass `owned.agentUserId` into every builder call
(`:129`, `:147`, `:160`, `:172`) and onto the inline `CONTENT_AMENDED` payload (`:183-187`).
**`certification/application/cancel.ts`** — pass `owned.agentUserId` into `cancelBooking`.

**`certification/domain/view.ts`** — fold the actor into the tracker:

- `HistoryEntry` (`:39`) — add `readonly by: AgentUserId`.
- `Cancellation` (`:54`) — add `readonly by: AgentUserId`.
- `passengersAmended` / `costAmended` / `dateChanged` / `issueDateChanged` / `contentAmended`
  (`:143`–`:213`) — each history entry sets `by: e.payload.agentUserId`.
- `bookingCancelled` (`:233`) — set `by: e.payload.agentUserId` on the `cancellation` struct.

**Contract — `apps/api/routes/certification.ts`** — expose the actor on the view. The cert view
is resolved **server-side** (symmetric with `listBookings`, which already resolves `agentName`
via the `agentNames` dep, `application/list.ts:259`): the route collects the distinct `by` ids
across `history` + `cancellation`, calls `agentNames`, and maps each row's `by` id → resolved
name string before returning. The output DTO carries `by: string` (the resolved name), so the
web renders plain text. (Keep the raw id internal; do not leak credential ids to the client.)

### b — Resolve principal → name

**Identity composition behind `agentNames`** (the port impl wired at
`certification/index.ts:198,208`) — extend the resolver so an id that misses the users table
falls back to the API-key label (the key's name from the keys store), not dropped. Mirrors the
`me` resolver's existing "key id misses user lookup → null" branch (`identity/index.ts:152-157`)
— here the miss resolves to the key label instead of null. A still-unresolvable id (deleted
principal) yields a stable placeholder (e.g. `—`), never a raw id.

### c — Surface in the tracker

**`web/features/certificate`** — the amendment tracker panel (the component rendering
`CertificateView.history` + `cancellation`) renders the resolved `by` name beside each row's
date/time, and on the cancellation fact. Pure presentation — the name arrives resolved from the
contract.

### Spec

- `spec/03-amend-cancel.md` — append the next free `03-R` rule: every certificate mutation
  (amend + cancel) records its acting principal (agent or key); the amendment tracker surfaces
  the resolved name per change. Cite the consultant §39.
- `spec/08-reports.md` — if the amendment-tracker section enumerates the columns, add the actor
  column there too. No new spec file.

### Tests (minimal)

- `certification.test.ts` — one assertion that an amend's `HistoryEntry.by` equals the acting
  `agentUserId`, and a cancel's `Cancellation.by` likewise. Adjust existing event-construction
  helpers for the now-mandatory field (`R2`).
- No new test for the `agentNames` key fallback unless an identity unit test already covers
  `agentNames` — extend that one if so; otherwise the acceptance journey covers it. Do not add a
  standalone resolver test (`CLAUDE.md`: less tests = better).

## Notes

- Lowest-effort of the four gaps surfaced in the consultant's reporting review. Independent of the other
  three (cadence model, backdate-at-creation warning, standard-report totals footer) — ship
  alone.
- The whole design pivots on one fact: the actor was always proven (`OwnedBooking`) and always
  droppable on the wire (`ActorView.id` is user-or-key). The fix stops a drop and extends one
  resolver — it does not add a source, a table, a migration, or a port.
- No migration: events are append-only payload shape; the new field rides the JSON payload, no
  column. Synthetic seed (`apps/api/synthetic.ts`) amend/cancel calls supply an `agentUserId`.
