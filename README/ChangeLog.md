# Change Log

## [Unreleased] — Reach-based minimal alley layout

### Rationale
- Minimize alley count while keeping every panel within an adjustable 2–4 panel reach of a parallel alley. Add one perpendicular edge spine for maintenance access.

### Changes
- **`core/layout.py`** — Added `compute_alley_positions(num_cols, reach)`; parallel alleys are placed at the midpoint of each `2 * reach` panel group; one edge spine connects all parallel alleys.
- **`core/models.py`** — Added `LayoutConfig.alley_reach` constrained to 2–4 panels.
- **`core/visualization.py`**, **`app.py`** — Added adjustable alley reach and updated the Plotly bbox/legend for the new model.
- **Tests** — Added coverage for reach=2 / 8 columns (`[1, 5]`), no trailing alley, reach coverage, and single-spine behavior.

### Verification
- `pytest tests/` — 34 passed.
- App module import check passes.

---


### Rationale
- Complete Phase 2 with full pytest coverage and a Plotly reference layout per PBS §2.3.

### Changes
- **`core/layout.py`** — Added `collect_row_alley_rects` and `collect_alley_rects` for service-gap geometry.
- **`core/visualization.py`** — `build_layout_figure` and `save_layout_figure` (panels, alleys, layout bbox, max area).
- **`tests/test_layout.py`** — Additional tests for `grid_bbox` and validation edge cases.
- **`tests/test_visualization.py`** — Figure structure tests; writes `outputs/reference_layout.html`.
- **`docs/Panel_Calculator_PBS.md`** — Phase 2 complete (tasks 2.3.1–2.3.2).

### Verification
- `pytest tests/test_layout.py tests/test_visualization.py` — 19 passed.
- Open `outputs/reference_layout.html` in a browser to confirm visual layout (3 pairs × 2 rows).

---


### Rationale
- Implement panel pairing, row/grid accumulation, and area fitting per PBS §2.2.

### Changes
- **`core/layout.py`** — `pair_panels`, `accumulate_row`, `accumulate_grid`, `fit_to_area`, `grid_bbox`, and `GridLayout` result type. Panels pair along +X; service alleys every 2 pairs (row) and every 2 rows (grid).
- **`core/__init__.py`** — Re-exports layout API.
- **`tests/test_layout.py`** — Unit tests for all layout functions.
- **`docs/Panel_Calculator_PBS.md`** — Tasks 2.2.1–2.2.4 marked complete.

### Verification
- `pytest tests/test_layout.py` — 10 passed.

---


### Rationale
- Define core panel and layout configuration types per PBS §2.1 before layout logic.

### Changes
- **`core/models.py`** — `PanelSpec` (length, width, weight, tilt_angle) and `LayoutConfig` (mid_clamp_gap, alley_width, max_area_x, max_area_y) with validation; default mid-clamp gap = 1 in (0.0254 m).
- **`core/__init__.py`** — Re-exports `PanelSpec`, `LayoutConfig`.
- **`tests/test_models.py`** — Unit tests for valid/invalid inputs and defaults.
- **`docs/Panel_Calculator_PBS.md`** — Tasks 2.1.1–2.1.2 marked complete.

### Verification
- `pytest tests/test_models.py` — 7 passed.

---


### Rationale
- Install and pin runtime dependencies; verify FEA and Streamlit per PBS §1.2; publish project to GitHub.

### Changes
- **`requirements.txt`** — Pinned numpy, pandas, plotly, PyniteFEA, streamlit, openpyxl, reportlab, pytest.
- **`app.py`** — Streamlit hello-world entry point.
- **`tests/test_fea_smoke.py`** — PyNite single-beam midspan load test (M_max = PL/4).
- **`README.md`** — Project setup and run instructions.
- **Git remote** — `https://github.com/pablobfuentes/PanelCalculator`
- **`docs/Panel_Calculator_PBS.md`** — Phase 1.2 tasks marked complete.

### Verification
- `pytest tests/test_fea_smoke.py` — 1 passed.
- `streamlit run app.py` — HTTP 200 on `http://localhost:8501`.

---


### Rationale
- Establish Python package layout and version control per `docs/Panel_Calculator_PBS.md` §1.1.

### Changes
- **`core/`**, **`ui/`**, **`tests/`**, **`outputs/`** — Project folders with package `__init__.py` files; `outputs/.gitkeep` retains empty export directory.
- **`.gitignore`** — Python venv, `__pycache__`, `.env`, generated files under `outputs/`.
- **Git** — Repository initialized; first commit `fa6c1ab` (`Initialize Panel Calculator folder scaffold`).
- **`docs/Panel_Calculator_PBS.md`** — Tasks 1.1.1–1.1.4 marked complete.

### Verification
- `git status` shows scaffold committed; `core/`, `ui/`, `tests/`, `outputs/` present on disk.

---


### Rationale
- Admin-only feature to export all customer/service data into a single CSV for operations and customer service. Access enforced by RLS; no backend endpoint or secrets in client.

### Changes
- **DB:** `docs/supabase_admin_export_customers_view.sql` — New view `admin_export_customers` (one row per user) joining profiles, get_user_email, subscriptions, order count, last_payment_date, admin_notes aggregate, next order and last shipment laterals. Run in Supabase SQL Editor after Phase 1 and Phase 2.
- **`docs/PLAN_EXPORT_USERS_CSV.md`:** Implementation plan, field mapping, and migration reference.
- **`src/lib/admin-export-csv.ts`:** Fetch all rows from view (chunked 500), build CSV with human-readable headers, date format YYYY-MM-DD HH:mm, filename `users_export_YYYY-MM-DD_HH-mm.csv`, download with BOM for Excel/Sheets.
- **`src/pages/admin/AdminCustomers.tsx`:** "Export Customer Data" button (primary); loading state and success/error message; existing "Export CSV (page)" unchanged.
- **`src/lib/admin-export-csv.test.ts`:** Tests for fetchAllExportRows (chunking), buildAndDownloadCsv (headers + filename), runExportCustomerData (fetch + download flow), and error propagation.

### Verification
- `npm run test -- --run src/lib/admin-export-csv.test.ts` passes (5 tests). After running the new SQL migration in Supabase, as admin: open /admin/customers → "Export Customer Data" → CSV downloads with one row per user and expected columns; open in Excel/Sheets to confirm.

---

## [Unreleased] — Homepage SEO copy comparison document

### Rationale
- User requested a side-by-side review artifact for conversion-first homepage SEO copy decisions before any page or registry implementation.

### Changes
- **`docs/HOMEPAGE_SEO_COPY_COMPARISON.md`:** Added a review-only comparison document covering homepage metadata, hero copy, pricing intro, selected FAQ rewrites, trust-block proposal, final CTA refinements, and an approval matrix. The document compares current copy vs proposed copy and explains why each recommendation supports SEO and conversion.

### Verification
- Confirmed the document was created in `docs/` only. No page code, component code, or registry content was modified as part of this request.

---

## [Unreleased] — Mobile-only Past Editions + Experience optimizations

### Rationale
- Apply improvements only on mobile (max-md: / md:). Past Editions: selected card expands vertically when selected. Experience: cards at least 1/3 viewport width, tighter spacing and edges.

### Changes
- **PastEditionsSection.tsx:** On mobile, inactive cards keep `h-40`; active card uses `max-md:min-h-[40vh] max-md:max-h-[55vh]` so the selected picture expands vertically. Desktop layout unchanged (md:h-full, md:w-[8%], md:[&[aria-current='true']]:w-[52%]).
- **ExperienceSection.tsx:** Mobile-only: section `max-md:px-4`; timeline line `left-4` (was left-6); step row `max-md:gap-4 max-md:mb-4`; timeline dot `left-4` on mobile; card wrapper `max-md:min-w-[33.33vw]` (cards at least 1/3 viewport width), `max-md:pl-4`; inner card `max-md:p-4`. Desktop unchanged (md: values preserved).

### Verification
- `npm run build` succeeds. Manual: desktop (≥768px) Past Editions and Experience unchanged; mobile: Past Editions selected card expands vertically; Experience cards wider (min 1/3 width), less padding/gaps.

---

## [Unreleased] — Admin Portal Phase 2 (execution)

### Rationale
- Execute PLAN_ADMIN_PORTAL.md: database schema, RLS, admin list view, audit triggers; admin UI; audit display. SYNC (customer dashboard from Supabase) deferred.

### Changes
- **DB-1:** `docs/ORDERS_CREATION_FLOW.md` — Documented orders creation (Stripe/webhook); where to attach subscription_id.
- **DB-2–DB-5:** `docs/supabase_admin_portal_phase2_migration.sql` — Extended profiles; created subscriptions, products, order_items, admin_notes, audit_logs; extended orders with backfill; RLS; view `admin_customers_list`; triggers for audit_logs.
- **UI-1:** `src/components/AdminLayout.tsx`, routes in `App.tsx` — Admin layout with nav (Overview, Customers, Registry Editor); routes `/admin`, `/admin/customers`, `/admin/customers/:userId`.
- **UI-2:** `src/pages/admin/AdminOverview.tsx` — KPI cards from Supabase (active subscriptions, upcoming shipments, failed payments, pending fulfillment, delayed shipments).
- **UI-3:** `src/pages/admin/AdminCustomers.tsx` — Customers table from `admin_customers_list`; sort, search (name/email), pagination; Export CSV (current page).
- **UI-4:** `src/pages/admin/AdminCustomerDetail.tsx` — Customer detail with tabs: Profile, Subscription, Next Order, Order History, Shipment History, Notes, Audit Log; loads profile, email, subscriptions, orders+order_items, admin_notes, audit_logs.
- **UI-5:** Edit modals on customer detail — Update subscription status; Update order status; Add tracking (carrier, tracking_number, shipped_at); Add internal note. All persist via Supabase; toast + query invalidate.
- **UI-6:** Export CSV button on customers table (client-side, current page).
- **AUDIT:** Triggers write to audit_logs; Audit Log tab shows entries for customer’s orders/subscriptions/notes.
- **Plan:** `docs/PLAN_ADMIN_PORTAL.md` — DB-1–DB-5, UI-1–UI-6, AUDIT-1–AUDIT-2, LOG marked complete; SYNC deferred with note; TEST-1–TEST-4 left for manual verification after migration.

### Verification
- `npm run build` succeeds. Run `docs/supabase_admin_portal_phase2_migration.sql` in Supabase SQL Editor after phase1; then verify admin routes, KPIs, customers table, customer detail, and edit modals. SYNC (customer dashboard from Supabase) to be implemented separately.

---

## [Unreleased] — Perimeter hardening (security scan remediation)

### Rationale
- Address three perimeter-hardening findings from security scan: (1) missing recommended security headers, (2) CSP overly permissive, (3) external assets loaded without Subresource Integrity. Preserve evidence-driven verification for future scans.

### Changes
- **`vercel.json`:** Added **Permissions-Policy** (`camera=(), microphone=(), geolocation=(), interest-cohort=()`) and **X-DNS-Prefetch-Control** (`off`). Removed `'unsafe-eval'` from Content-Security-Policy `script-src`; retained `'unsafe-inline'` for script and style (documented as Vite/React trade-off).
- **`src/index.css`:** Replaced Google Fonts `@import url('https://fonts.googleapis.com/...')` with self-hosted fonts via **@fontsource/playfair-display** and **@fontsource/dm-sans** (same families/weights). No external CSS or font URLs in production.
- **`package.json`:** Added dependencies `@fontsource/playfair-display`, `@fontsource/dm-sans` (installed with `--legacy-peer-deps`).
- **`docs/Security_Phase1_Results.md`:** New section "Perimeter Hardening (post-scan remediation)" documenting the three findings, fixes, residual risk (CSP unsafe-inline), and verification steps so future scans stay deterministic and explainable.

### Verification
- `npm run build` succeeds. Production bundle serves fonts from same origin; no requests to fonts.googleapis.com or fonts.gstatic.com. CSP without `'unsafe-eval'` verified; Permissions-Policy and X-DNS-Prefetch-Control apply on Vercel deploy per vercel.json.

---

## [Unreleased] — Security Phase 3 verification

### Rationale
- Execute Phase 3 of the security checklist: re-scan and test after Phase 2 remediation; update logs.

### Changes
- **Secrets re-scan:** No hardcoded secrets in `src/`; only env-based VITE_SUPABASE_*; `.gitignore` confirms `.env`, `.env.local`, `.env.*.local`.
- **Dependency audit:** `npm audit` re-run; 5 vulnerabilities unchanged (documented accepted risk); no new vulns.
- **Headers:** `vercel.json` confirmed; local `vite preview` does not send these (expected); they apply on Vercel deploy.
- **Cookies:** Code verified (sidebar SameSite=Lax, Secure on HTTPS); manual check on live HTTPS recommended.
- **Version/debug:** Production build succeeds; RegistryEditor font logs guarded by devLog/devWarn (DEV-only).
- **`docs/Security_Phase1_Results.md`:** Added "Phase 3 — Verification (Executed)" with task 11–12 results and checklist status.
- **`docs/Security_Checklist.md`:** Phase 3 section marked executed; tasks 11–12 checkboxes and summary reference added.

### Verification
- Phase 3 tasks 11–12 completed. No FAIL_LOG entries. Security checklist Phases 1–3 complete.

---

## [Unreleased] — Security Phase 2 remediation

### Rationale
- Execute Phase 2 of the security checklist: apply remediations for secrets, headers, cookies, version/debug exposure, and dependencies per Phase 1 findings.

### Changes
- **`.gitignore`:** Added `.env`, `.env.local`, `.env.*.local` so env files with secrets are never committed.
- **`README.md`:** New section "Environment variables and security" (no committing secrets; use `.env.local` and host env; reference to security docs).
- **`vercel.json`:** Created. Security headers for all routes: X-Frame-Options: DENY, X-Content-Type-Options: nosniff, Referrer-Policy: strict-origin-when-cross-origin, Strict-Transport-Security, Content-Security-Policy (self + Supabase connect/font/img). Documented as applying on Vercel; other hosts need equivalent config.
- **`src/components/ui/sidebar.tsx`:** When setting `sidebar:state` cookie, added `SameSite=Lax` and `Secure` when `window.location.protocol === "https:"`.
- **`src/pages/RegistryEditor.tsx`:** Added `devLog`/`devWarn` (run only when `import.meta.env.DEV`); replaced font-scanning `console.log`/`console.warn`/`console.error` in `scanAvailableFonts` and `handleRefreshFonts` with these helpers.
- **Dependencies:** Ran `npm audit fix --legacy-peer-deps` (fixes applied; 5 vulns remain—jsdom, vite/esbuild—documented as accepted risk for dev/test only).
- **`docs/Security_Phase1_Results.md`:** Added "Phase 2 — Remediation Applied" section describing all changes and remaining vulns.
- **`docs/Security_Checklist.md`:** Phase 2 heading set to "Remediation (Executed)"; tasks 6–10 updated with checkboxes and summary reference to Phase 1 results doc.

### Verification
- Build and tests: `npm run build` and test run (as applicable). Remaining 5 vulnerabilities documented in `Security_Phase1_Results.md`; production bundle not affected by dev-server CVE.

---

## [Unreleased] — Security checklist and Phase 1 discovery

### Rationale
- User requested security testing (secrets, headers, cookies, version/debug exposure, dependencies) and to follow workflow Prompt.md. Plan written as checklist; Phase 1 (discovery) executed.

### Changes
- **`docs/Security_Checklist.md`:** Created. Full security plan: Phase 1 (discovery), Phase 2 (remediation design), Phase 3 (verification and logs). Skills, risks, assumptions, improvements, things to consider.
- **`docs/Security_Phase1_Results.md`:** Created. Phase 1 inventory: (1) No hardcoded secrets; .gitignore missing explicit `.env`. (2) No security headers; app served by Vite dev/preview or host. (3) Cookie `sidebar:state` in `src/components/ui/sidebar.tsx` without Secure/SameSite; Supabase auth cookies documented. (4) RegistryEditor and supabase.ts console logging; vite.config dev-only logging. (5) `npm audit`: 10 vulnerabilities (4 high, 3 moderate, 3 low)—ajv, esbuild/vite, minimatch, rollup, tar/supabase, @tootallnate/once/jsdom—with fix options.
- **`docs/Security_Checklist.md`:** Phase 1 checklist items marked complete; results reference added.

### Verification
- Phase 1 tasks 1–5 completed; findings documented in `Security_Phase1_Results.md`. No code or config changed (discovery only). Phase 2 remediation executed and documented above.

---

## [Unreleased] — Registry/Editor parity and documentation

### Rationale
- User requested that every variable be present in the Registry Editor and in `app-registry.ts` / `style-registry.ts`, and that everything be documented according to workflow documents.

### Changes
- **Style registry (`src/config/style-registry.ts`):**
  - `compatibilityTest.questionCard` and `compatibilityTest.resultCard` added (backgroundIndex each) so the Compatibility Test panel colors are editable in Registry Editor and defined in the registry.
- **Documentation:**
  - **`docs/WEBSITE_TEXT_CONTENT.md`:** Regenerated as a full path inventory for all user-facing text. Every top-level section in `app-registry.ts` is listed with every registry path (string leaf). Notes added: single source of truth, Registry Editor usage, list normalization.
  - **`docs/STYLE_VARIABLES_INVENTORY.md`:** Updated last-updated date; added explicit note that every variable is editable in Registry Editor. Documented `compatibilityTest.questionCard` and `compatibilityTest.resultCard`. Added “Registry Editor coverage” section listing content vs style and section keys.
- **Registry Editor:** No code change. Content is discovered from `APP_REGISTRY` via `getContentEntries()`; style controls already cover all sections. `SECTION_DISPLAY_NAMES` already includes every app-registry section (nav, hero, why, … checkout, account).

### Verification
- All app-registry top-level keys (nav, hero, why, compatibilityTest, howItWorks, whatYouReceive, pastEditions, experience, testimonials, pricing, faq, finalCta, footer, login, register, forgotPassword, resetPassword, dashboard, checkout, account) are present in Registry Editor and in `WEBSITE_TEXT_CONTENT.md`.
- All style-registry section keys are present in Registry Editor; compatibilityTest now has question/result panel controls.

---

## [Unreleased] — Past Editions carousel: placeholder pictures and registry image URLs

### Rationale
- User requested pictures on the Past Editions carousel, with image URLs in the registry and editable in RegistryEditor.
- The carousel previously showed only text (category, name, month) on colored cards.

### Changes
- **App registry (`src/config/app-registry.ts`):**
  - `pastEditions.fallbackImage`: added (URL used when an edition has no image or load fails).
  - Each `pastEditions.editions[i]` now has an `image` field with a placeholder URL (picsum.photos seed per edition).
- **Past Editions component (`src/components/PastEditionsSection.tsx`):**
  - Each card renders an `<img>` with `src` from `edition.image` or `data.fallbackImage`; `onError` switches to `fallbackImage`.
  - Image fills the card (absolute, object-cover); active card is full color + scale, inactive cards are grayscale.
- **Tests:** New test "renders one image per edition card" in `PastEditionsSection.test.tsx`.
- **RegistryEditor:** No code change; `getContentEntries` already exposes all section content, so `pastEditions.fallbackImage` and `pastEditions.editions[i].image` appear as Content rows for Past Editions.

### Verification
- `npm test -- PastEditionsSection.test.tsx` passes (3 tests). In Registry Editor → Past Editions → Content, `fallbackImage` and each edition’s `image` are editable; Save and reload to see updated carousel images.

## [Unreleased] — Registry list normalization (no content changes)

### Rationale
- Registry and localStorage can provide list data as either arrays or objects with numeric keys. Components that call `.map()` on these values throw when the value is an object. Using `Object.values()` without key ordering can display items in the wrong order (e.g. first slot showing second item), which was reported as "missing" cards.
- Fix: normalize to an array in **numeric index order** (0,1,2,...) in the UI layer only. No changes to app-registry content or to any variable values.

### Files touched
- `src/lib/utils.ts` — add `registryListToArray<T>(value)` (array or object with numeric keys → array in index order).
- `src/components/ProblemSection.tsx` — `cards = registryListToArray(data.cards)`.
- `src/components/HowItWorksSection.tsx` — `steps = registryListToArray(data.steps)`; key `step?.label ?? step-${index}`; StepCard type allows optional `label`.
- `src/components/ExperienceSection.tsx` — `registryListToArray(data.steps).map(...)`; key `step?.number ?? index`.
- `src/components/TestimonialsSection.tsx` — `registryListToArray(data.items).map(...)`; key `item?.author ?? index`.
- `src/components/WhatYouReceiveSection.tsx` — `registryListToArray(data.products).map(...)`; key `product?.number ?? index`.
- `src/components/FAQSection.tsx` — `registryListToArray(data.items).map(...)`.
- `src/components/PastEditionsSection.tsx` — `registryListToArray(data.editions).map(...)`; key `edition?.name ?? index`.
- `src/components/CompatibilityTestSection.tsx` — `questions = registryListToArray(data.questions)`; use `questions` for length, indexing, reset, progress.
- `src/components/PricingSection.tsx` — `registryListToArray(data.plans).map(...)`; key `plan?.id ?? index`; `registryListToArray(plan.features).map(...)` for features.

### Verification
- With app-registry as-is (e.g. why.cards object with "1","2"; howItWorks.steps object with "0","1"): page must render without error and show those cards/steps in order (card at index 0 = key "0" if present, else key "1" first, etc.).
- With localStorage overrides that store lists as objects: same behavior, correct order.
- No edits to `src/config/app-registry.ts` or to any copy/text.

## [Unreleased] — Orbit testimonials & Past Editions registry coverage

### Rationale
- User requested that **all variables** (text, images, colors) used by the Testimonials and Past Editions sections be fully editable via `RegistryEditor` and defined in `app-registry.ts` / `style-registry.ts`.
- Recent UI updates introduced:
  - A **testimonial orbit carousel** with scientist avatars.
  - A **Past Editions expanding carousel** with center-focused edition cards.
- Some literals (emoji prefixes, fallback avatar URL, generic card backgrounds) still lived directly in components instead of the registries, and section-specific card colors in `style-registry.ts` were not yet consumed by the components.

### Changes
- **App registry (`src/config/app-registry.ts`):**
  - `pastEditions.subtitleEmoji`: added so the header chip emoji (`📚`) is registry-driven.
  - `testimonials.subtitleEmoji`: added so the subtitle prefix star (`⭐`) is registry-driven.
  - `testimonials.fallbackAvatar`: added so the orbit carousel’s fallback avatar URL is configurable.
  - `testimonials.people[*].quote`: added a `quote` field for each scientist so the central card shows a registry-driven quote instead of hardcoded contact info.
- **Past Editions component (`src/components/PastEditionsSection.tsx`):**
  - Uses `data.subtitleEmoji` from the registry instead of a hardcoded `📚`.
  - Imports `useStyleRegistry()` and uses `registry.pastEditions.cards` length to map each edition card to the corresponding CSS variable `--pastEditions-card-{i}-bg` (set by `apply-style-registry.ts`), making card fill colors fully controlled by `STYLE_REGISTRY.pastEditions.cards` and editable from `RegistryEditor`.
- **Testimonials component (`src/components/TestimonialsSection.tsx`):**
  - Uses `data.subtitleEmoji` from the registry instead of a hardcoded `⭐`.
  - Reads `data.fallbackAvatar` and passes it to a factory `makeSafeImage()` so fallback image behavior is registry-driven.
  - Imports `useStyleRegistry()` and uses `registry.testimonials.cards` length to choose a card background index based on `activeIndex`, applying `backgroundColor: hsl(var(--testimonials-card-{i}-bg))` to the central card so testimonial backgrounds are driven by `STYLE_REGISTRY.testimonials.cards`.

### Verification
- Tests:
  - `npm test -- HeroSection.test.tsx PastEditionsSection.test.tsx TestimonialsSection.test.tsx`
  - All 6 tests pass (no regressions in hero guardrails; Past Editions and Testimonials carousel tests still green).
- Visual:
  - **Testimonials:** Subtitle line shows configured emoji + text; orbiting avatars still animate; central card shows registry quotes and uses per-section card colors; fallback avatar comes from the new registry key.
  - **Past Editions:** Subtitle chip shows emoji from registry; edition cards use per-card background colors defined in `STYLE_REGISTRY.pastEditions.cards` and exposed in `RegistryEditor`.

---

## [Unreleased] — Dashboard Quick Actions & Account consolidation

### Rationale
- Consolidate user-facing account functionality into the authenticated `Dashboard` experience.
- Give each Dashboard Quick Action (Order History, Subscription, Settings, Notifications) a real, protected destination instead of `#` anchors.
- Deprecate the standalone `/account` route while keeping the Account page and registry section available for history/RegistryEditor.

### Changes
- **Routing (`src/App.tsx`):**
  - Added protected routes for `/orders`, `/subscription`, `/settings`, and `/notifications`, each wrapped in `ProtectedRoute` and pointing to new page components.
  - Removed the `/account` route so all account navigation flows through Dashboard + Quick Actions.
- **Pages (`src/pages`):**
  - Implemented `OrderHistory.tsx`, `SubscriptionManagement.tsx`, `SettingsPage.tsx`, and `NotificationsPage.tsx` using the shared shell (`Navbar`, padded main, centered content) and `useRegistryContent().getSectionContent("<sectionKey>")` for all copy.
  - Left `Account.tsx` and `Account.test.tsx` in place as a documented, unused page; no longer reachable via routing but still visible in RegistryEditor and tests.
- **Registry (`src/config/app-registry.ts`):**
  - Uses previously added `dashboard.orderHistoryHref`, `subscriptionActionHref`, `settingsHref`, and `notificationsHref` to point to the new routes.
  - Uses previously added `orderHistory`, `subscriptionManagement`, `settings`, and `notifications` sections for page titles/subtitles/body/empty states.
- **Tests (`src/pages`):**
  - Extended `Dashboard.test.tsx` to assert that each Quick Action link has the correct non-`#` `href` (`/orders`, `/subscription`, `/settings`, `/notifications`).
  - Added page-level tests: `OrderHistory.test.tsx`, `SubscriptionManagement.test.tsx`, `SettingsPage.test.tsx`, `NotificationsPage.test.tsx` to verify each page renders its registry-driven heading and description/placeholder in the shared shell.
  - Updated `Account.test.tsx` to tolerate the user’s display name appearing both in Navbar and in the Account card (`getAllByText("Test User")`).

### Verification
- `npm test` (Vitest) passes for the full suite, including:
  - `src/pages/Dashboard.test.tsx`
  - `src/pages/OrderHistory.test.tsx`
  - `src/pages/SubscriptionManagement.test.tsx`
  - `src/pages/SettingsPage.test.tsx`
  - `src/pages/NotificationsPage.test.tsx`
  - `src/pages/Account.test.tsx`
- Manual reasoning: all new pages are read-only views that:
  - Are only reachable via `ProtectedRoute`-guarded routes.
  - Use `useRegistryContent` for text and do not introduce new network calls, forms, or side effects.

---

## [Unreleased] — Social sign-in with Google and Facebook

### Rationale
- Add Google/Facebook sign-in to the existing auth flow while keeping Supabase Auth as the single source of truth for registered users.
- Ensure new social users still flow through `auth.users` and the existing `public.profiles` trigger path instead of introducing a parallel user store.

### Changes
- **Auth (`src/contexts/AuthContext.tsx`):**
  - Added `signInWithOAuth(provider)` for `google` and `facebook`.
  - Uses `supabase.auth.signInWithOAuth(...)` with a safe redirect derived from the current `?redirect=` query when present, else `/`.
- **Shared UI (`src/components/SocialAuthButtons.tsx`):**
  - Added a reusable divider + provider button block for auth pages.
- **Auth pages (`src/pages/Login.tsx`, `src/pages/Register.tsx`):**
  - Added Google/Facebook buttons below the existing form.
  - Wired provider clicks to `signInWithOAuth`.
  - Reused existing inline error area for provider-level failures.
- **Registry (`src/config/app-registry.ts`):**
  - Added auth-page copy for social divider text, Google/Facebook button labels, and provider error message.
- **Tests (`src/contexts/AuthContext.test.tsx`, `src/pages/Login.test.tsx`, `src/pages/Register.test.tsx`, `src/test/render-with-auth.tsx`):**
  - Added focused coverage for provider dispatch and page rendering.
  - Extended the auth render helper with a default `signInWithOAuth` stub.

### Verification
- `npm run test -- src/pages/Login.test.tsx src/pages/Register.test.tsx src/contexts/AuthContext.test.tsx` passes.
- `npm run build` passes.
- Manual rendered-product check on `http://127.0.0.1:8081/login` and `/register`:
  - Desktop (`1280x800`): buttons visible, no overlap, layout remains usable.
  - Mobile (`390x844`): buttons visible and stack correctly.

---

## [Unreleased] — Temporary Google-only social-auth rollout

### Rationale
- Google credentials are configured and ready to validate.
- Facebook credentials are still pending, so the Facebook entry point should be hidden from users for now.
- The underlying OAuth support should remain in place so Facebook can be re-enabled later without reworking `AuthContext`.

### Changes
- **Shared UI (`src/components/SocialAuthButtons.tsx`):**
  - Added `showFacebook?: boolean` so the component can selectively hide Facebook while preserving the existing Google/Facebook provider handling contract.
- **Auth pages (`src/pages/Login.tsx`, `src/pages/Register.tsx`):**
  - Passed `showFacebook={false}` so only `Continuar con Google` is rendered in the current rollout.
- **Tests (`src/pages/Login.test.tsx`, `src/pages/Register.test.tsx`):**
  - Updated the page tests to assert that Google is visible, Facebook is absent, and Google still calls `signInWithOAuth("google")`.
- **Workflow docs/logs:**
  - Logged the red-phase failure where Facebook was still rendering.
  - Added changelog + VMP audit evidence for the Google-only rollout and browser verification.

### Verification
- `npm run test -- src/pages/Login.test.tsx src/pages/Register.test.tsx src/contexts/AuthContext.test.tsx` passes (7 tests).
- `npm run build` passes.
- Browser smoke test on `http://127.0.0.1:8081/login` and `/register` confirms:
  - Google button visible.
  - No Facebook button or Facebook text rendered.
  - Clicking Google redirects to Google Accounts with Supabase callback `https://rtnispswkyybiliynezz.supabase.co/auth/v1/callback`.

---

## [Unreleased] — Hostinger deploy folder refreshed from latest build with in-place history snapshot

### Rationale
- The `Hostinger` upload folder was stale and still referenced an older built JS entry bundle than the current production build.
- The old deploy surface needed to be preserved for rollback, but the live upload folder needed the latest generated `index.html` and `assets`.

### Changes
- **Regression test (`src/hostinger-deploy-sync.test.ts`):**
  - Added a focused file-system test that reads `dist/index.html`, extracts the current JS/CSS entry asset names, and verifies `Hostinger/index.html` references the same files and that those files exist under `Hostinger/assets`.
- **Build output refresh:**
  - Ran `npm run build` to generate the latest production output in `dist/`.
- **Hostinger archive + sync:**
  - Created `Hostinger/history/20260311-224505/`.
  - Moved the previous `Hostinger/index.html` and full `Hostinger/assets/` directory into that timestamped history snapshot.
  - Copied the fresh `dist/index.html` and `dist/assets/` back into `Hostinger/`.
- **Workflow docs/logs:**
  - Logged the stale-deploy red phase, the stale hardcoded bundle test assumption, and the PowerShell command-separator mismatch.

### Verification
- `npm run build` passes.
- `npm run test -- src/hostinger-deploy-sync.test.ts` passes.
- `Hostinger/index.html` now references:
  - `/assets/index-Cm9BMrr-.js`
  - `/assets/index-CNNEYgXU.css`
- The previous generated deploy surface is archived at `Hostinger/history/20260311-224505/`.

---

## [Unreleased] — One-command Hostinger refresh automation

### Rationale
- The Hostinger refresh workflow was still manual even after the deploy-sync regression test was added.
- A single command is safer and faster than repeating build/archive/copy steps by hand, especially with timestamped history snapshots.

### Changes
- **PowerShell script (`scripts/sync-hostinger.ps1`):**
  - Added a parameterized script that refreshes `Hostinger` from `dist`.
  - Supports optional `-HostingerDir`, `-DistDir`, and `-Timestamp` arguments for testability and controlled snapshots.
  - Moves the current generated deploy surface (`index.html` and `assets/`) into `Hostinger/history/<timestamp>/`.
  - Copies the latest `dist/index.html` and `dist/assets/` back into `Hostinger/`.
- **Package scripts (`package.json`):**
  - Added `hostinger:sync` to run the PowerShell sync script directly.
  - Added `hostinger:refresh` to run `build` and then `hostinger:sync` in one command.
- **Tests (`src/hostinger-sync-script.test.ts`):**
  - Added coverage that asserts `package.json` exposes the one-command script.
  - Added a temp-directory integration test that executes the PowerShell script and verifies:
    - old generated deploy files are archived,
    - new built files are copied in,
    - non-generated Hostinger files are preserved.

### Verification
- `npm run test -- src/hostinger-sync-script.test.ts` passes (2 tests).
- `npm run hostinger:refresh` passes end-to-end.
- `npm run test -- src/hostinger-sync-script.test.ts src/hostinger-deploy-sync.test.ts` passes (3 tests).
- `Hostinger/index.html` now references:
  - `/assets/index-MQghwU3t.js`
  - `/assets/index-CQTMGJSs.css`
- The latest real refresh snapshot is archived at `Hostinger/history/20260312-095329/`.
