# Glossary — terms, actors, enums

## TPS terms

- **TPS** — Travel Protection Scheme licence. A scheme protecting consumers' advance travel payments.
- **Authority** — Travel Regulation Authority. The regulator running TPS.
- **TPS certificate** — the legal PDF a consumer receives proving their money is financially protected.
- **Confirmation** — separate package-sale document (the standard terms), distinct from the certificate. See `01`.
- **SPC (Scheme Protection Contribution)** — £2.50 per passenger aged ≥2, paid to the Protection Trust, due on **every** booking on a **booking-date basis** (the declared issue date); the **departure date** drives **revenue recognition** + the passengers-departed report only. Still owed on cancellation. See `04`. (`G1` — binned by the period the booking event lands, **per increment**: a later-added passenger owes in the month it was added.)
- **PT (Protection Trust)** — fund SPC is paid into.
- **Licence** — a holder's TPS authorisation for one **renewal period** — its facts (`scheme_number`, type, renewal cohort) plus that period's limits. One record per `(holder, period)`, cohort-anchored; a new one each renewal, past read-only. Subsumes the old per-holder "accreditation". See `05`.
- **Licence limit** — Authority-imposed limit on passengers and revenue, per category of business, per **calendar quarter**, carried on the period's licence (Standard). An SBS limit is instead a single annual passenger figure. See `05`.
- **Variation** — a formal request to the Authority to change a licence limit.
- **The Return** — the figures a holder files with the Authority (the SPC Return) via the Authority Scheme Portal: **Part A booked** (booking-date basis — the £2.50 levy) **+ Part B departed** (departure-date basis — passengers departed + revenue). See `06`. Cadence depends on licence tier.
- **Lock-in** — the act of marking a Return as submitted, freezing a snapshot of its figures so later changes are detectable. See `06`.
- **Opening balance** — an existing operator's position-as-of-onboarding (booked / departing / forward), carried forward so no dual-system catch-up. See `07`.

## Licence types & reporting cadence ✅ VERIFIED (Authority SPC docs · the guidance note · the standard terms Apr-2026)

Two licence **types**; cadence is driven by **licensable turnover**, not a third type:

- **SBS (Small Business Scheme)** — ≤500 licensable passengers/year. Reports **quarterly** (booking **and** departure basis); **SPC paid annually**, within 6 weeks of licence expiry. **Not required to report forward bookings.**
- **Standard TPS** — every holder that isn't SBS. Cadence by turnover:
  - **< £5m → quarterly** (booking **and** departure basis).
  - **≥ £5m → monthly**.
  - SPC paid **within 6 weeks** of each reporting-period end.
- **Scheme-to-Scheme** sales → separate **quarterly** return even for monthly filers.

There is **no separate "Larger Standard" licence** — "monthly" is just the ≥£5m turnover band within Standard. (the consultant to confirm which type each client is — `Q6`.)

## Booking / certificate types

- **Single Contract** — one package holiday (flights + accommodation as a single product).
- **Multi Contract** — package from separate components (flight, accommodation, car hire, other), each itemised.
- **Flight Only** — flights, no holiday package.
- **Flight-Inclusive Day Trip** — the Authority's standard terms (Apr-2026) prescribe this as a **4th** certificate format. ⚠️ in scope? `Q12`.

(**Scheme-to-Scheme** is a sales/reporting **category** — separate quarterly return, `06` — not a certificate template.)

## Actors / roles

- **Operator** — runs the platform (cross-tenant role). Onboards/suspends holders, toggles enabled regimes, audited impersonation, reads the fleet.
- **Holder (TPS holder)** — a licensed travel organiser (an organisation). Manages its agents, authors its per-period licence (facts + limits), files/locks returns. The `scheme_number` is a fact on the licence, holder-set.
- **Agent** — front-line staff of a holder. Issues, amends, cancels certificates for consumers. Sees only its own bookings.
- **Consultancy** — an advisory organisation (e.g. the consultant's firm) with a read-mostly cross-holder view, advising multiple holders. Generic by design — a second consultancy, or the Authority as auditor, plugs into the same seam. See `09`. ⚠️ powers/access `Q13`.
- **Consumer** — the travelling customer who receives the certificate. Not a system user.

## Key enums

- **Cancellation reason** — `Cancellation` · `Certificate Created in Error` · `Duplicate Certificate`. The last two are excluded from "after errors" totals.
- **Passenger-decrease reason** — `Passenger Cancelled` · `Passenger Added in Error`. Treated differently in reporting (`08`).
- **Threshold warning** — `Half` (over 50% of cap) · `Full` (over cap) · none.
- **Three-tier reconciliation** — `Written` · `After errors` · `After cancellations and changes`. See `06`.

## Money & counting

- Currency **GBP** (assumed; confirm). Money stored as integer minor units (pence) — no penny loss.
- Passenger counts are integers derived from a **manifest with ages**; the billable/limit count excludes infants (<2).
