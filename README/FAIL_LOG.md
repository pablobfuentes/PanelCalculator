# Failure Log

## Entry 1: Registry list as object caused .map is not a function (initial report)
- **Date**: Session 1
- **Failure**: After save/refresh, console error `data.cards.map is not a function` (and later `data.steps.map is not a function`). Page broke.
- **Root cause**: Registry and/or localStorage overrides store some section lists as **objects** with string keys (e.g. `{ "0": item0, "1": item1 }`). Components assumed **arrays** and called `.map()` on the value. Objects do not have `.map()`, so the app threw.
- **Fix attempt 1**: Replaced with `Object.values(data.cards ?? {})` in ProblemSection. Page worked but **cards could appear in wrong order** because `Object.values()` order follows object key enumeration, which is not guaranteed to be 0,1,2 when keys were set in a different order (e.g. after merge: "1","2" then "0").
- **Result**: User reported "some cards were missing" — likely wrong order (first slot showing content from key "1", etc.) or perceived as missing.

## Entry 2: Normalize to array with sort — still "missing" cards (user did not accept)
- **Date**: Session 2
- **Failure**: User reported: "the third card from the Why section and the last 2 cards in How it works are missing". User did not accept changes.
- **Root cause (analysis)**:
  1. **Order**: When `deepMergeSection` merges base (object with keys "1","2") with override (object or array), the merged object’s key **insertion order** can be "1", "2", "0". `Object.values()` then returns [item1, item2, item0]. So the **first** rendered card shows content that belongs to index 1 (second card), and the **third** slot shows content for index 0 — so the user sees "third card" as wrong or "missing" (or the first card looks wrong).
  2. **No content change rule**: Previous attempts added or changed content in `app-registry.ts` (e.g. converting `why.cards` from object to array and adding a third card). User rule: **do not change any variable content**; only make the page resilient to array vs object so that **existing** data is displayed correctly.
  3. **Correct fix**: Normalize list to array by **numeric key order** (0,1,2,...) so that whatever is in the registry/merge is shown in the right order and nothing is dropped. Do not add/remove/edit any content in app-registry or elsewhere.
- **Fix to apply**: Add a single helper that converts value to array: if already array return as-is; if object, collect keys that match `^\d+$`, sort by `Number(key)`, and return `keys.map(k => value[k])`. Use this in every component that does `.map()` on a registry list. Do not change any content in app-registry or in any section copy.

## Entry 3: (This session) Full analysis and fix without content changes
- **Goal**: Page works as intended; any change in variables only changes values, not behavior. No content/variable changes without permission.
- **Implementation**: Add `registryListToArray` in `src/lib/utils.ts`; use it in all sections that read list-like registry data (why.cards, howItWorks.steps, testimonials.items, etc.). Ensure key for StepCard is stable when `step.label` is missing (use `index` or `step.label ?? index`). No edits to app-registry.ts or to any copy/variable values.

## Entry 4: ExperienceSection data-step roadmap markers
- **Date**: This session
- **Failure**: New TDD test `renders one step marker per experience step using data-step attributes` in `src/components/ExperienceSection.test.tsx` expected one `[data-step]` marker per `APP_REGISTRY.experience.steps` entry, but `ExperienceSection` did not render any `data-step` attributes (markers length 0 vs expected 4).
- **Root cause**: The Experience section’s timeline layout did not expose per-step markers for scroll-aware roadmap behavior as in the Loveable Roadmap example. Steps were rendered, but there was no structural hook (`data-step`) for navigation or progress indicators.
- **Fix**: Updated `src/components/ExperienceSection.tsx` so each mapped step `motion.div` includes `data-step={index}` and a `minHeight: "40vh"` style, aligning structure with the roadmap pattern while preserving the existing color palette and registry-driven content.

## Entry 5: Social auth AuthContext test hoisting failure
- **Date**: 2026-03-10
- **Failure**: New TDD test `src/contexts/AuthContext.test.tsx` failed before reaching the intended OAuth assertion with `ReferenceError: Cannot access 'signInWithOAuth' before initialization`.
- **Root cause**: Vitest hoisted the `vi.mock("@/lib/supabase", ...)` factory, but the factory referenced top-level mock bindings that had not been initialized yet.
- **Reproduction**: Run `npm run test -- src/pages/Login.test.tsx src/pages/Register.test.tsx src/contexts/AuthContext.test.tsx`.
- **Fix attempt**: Move mocked Supabase auth methods into a `vi.hoisted(...)` object so the module factory can safely reference them during hoisting.
- **Verification**: Re-run the focused auth/social Vitest command and confirm the AuthContext test reaches the intended red/green assertion path.

## Entry 6: Social auth page tests missing async mock return shape
- **Date**: 2026-03-10
- **Failure**: After implementing `handleOAuth`, the page tests for `Login` and `Register` produced unhandled rejections: `Cannot destructure property 'error' ... as it is undefined`.
- **Root cause**: The page-level `signInWithOAuth` spies did not have `mockResolvedValue({ error: null })`, so the async handler received `undefined` instead of the expected auth result shape.
- **Reproduction**: Run `npm run test -- src/pages/Login.test.tsx src/pages/Register.test.tsx src/contexts/AuthContext.test.tsx` after adding the new OAuth handlers.
- **Fix attempt**: Update the page tests to resolve the same `{ error: null }` structure returned by the auth context method.
- **Verification**: Re-run the focused auth/social Vitest command and confirm there are no unhandled rejections and both page tests assert the provider clicks correctly.

## Entry 7: Social auth page tests clicked disabled second provider too early
- **Date**: 2026-03-10
- **Failure**: The login/register social-button tests expected Google then Facebook clicks in immediate sequence, but only the first provider call was recorded and React warned about updates not wrapped in `act(...)`.
- **Root cause**: The new UI intentionally sets `socialSubmitting` while the OAuth promise resolves, disabling the provider buttons briefly. The test clicked the second provider before the first async state cycle settled.
- **Reproduction**: Run `npm run test -- src/pages/Login.test.tsx src/pages/Register.test.tsx src/contexts/AuthContext.test.tsx` with the original back-to-back click assertions.
- **Fix attempt**: Update the tests to await the first async click path before asserting/clicking again, or split provider assertions so each test follows one complete async UI cycle.
- **Verification**: Re-run the focused auth/social tests and confirm page tests pass without `act(...)` warnings.

## Entry 8: Google-only rollout tests failed because Facebook still rendered
- **Date**: 2026-03-10
- **Failure**: New TDD assertions for the temporary Google-only rollout failed in both `src/pages/Login.test.tsx` and `src/pages/Register.test.tsx` because `Continuar con Facebook` was still present in the DOM.
- **Root cause**: The temporary rollout decision had only been approved verbally; the shared `SocialAuthButtons` component still unconditionally rendered both provider buttons.
- **Reproduction**: Run `npm run test -- src/pages/Login.test.tsx src/pages/Register.test.tsx` after changing the tests to expect Google visible and Facebook hidden.
- **Fix attempt**: Make the social-auth UI render providers conditionally so Google remains enabled while Facebook is hidden without removing the underlying OAuth support from `AuthContext`.
- **Verification**: Re-run the focused auth-page tests and confirm Google renders, Facebook is absent, and the Google click still calls `signInWithOAuth("google")`.

## Entry 9: Hostinger deploy folder still referenced stale built entry bundles
- **Date**: 2026-03-10
- **Failure**: New regression test `src/hostinger-deploy-sync.test.ts` failed because `Hostinger/index.html` still referenced `/assets/index-Dmx6LUBb.js` and `/assets/index-CNNEYgXU.css` instead of the latest expected build entry files.
- **Root cause**: The deployment mirror in `Hostinger` had not been refreshed after the latest frontend changes, so its top-level `index.html` and entry assets were out of sync with the current production build output.
- **Reproduction**: Run `npm run test -- src/hostinger-deploy-sync.test.ts`.
- **Fix attempt**: Generate the current production build, archive the stale `Hostinger` entry files into `Hostinger/history`, then copy the latest built `index.html` and referenced assets into `Hostinger`.
- **Verification**: Re-run `npm run test -- src/hostinger-deploy-sync.test.ts` and confirm the refreshed `Hostinger` folder references the latest bundle names and contains those files.

## Entry 10: Initial Hostinger sync test hardcoded a stale latest bundle hash
- **Date**: 2026-03-10
- **Failure**: The first version of `src/hostinger-deploy-sync.test.ts` hardcoded `index-DCegv0xG.js` / `index-eTEYPA51.css`, but a fresh build produced `index-Cm9BMrr-.js` and `index-CNNEYgXU.css`.
- **Root cause**: The test relied on a previously observed build output instead of deriving the current expected entry assets from the latest `dist/index.html`.
- **Reproduction**: Build the project with `npm run build`, then run `npm run test -- src/hostinger-deploy-sync.test.ts` using the hardcoded bundle names.
- **Fix attempt**: Update the regression test to read `dist/index.html`, extract the current JS/CSS asset references, and compare `Hostinger/index.html` against those dynamically.
- **Verification**: Re-run `npm run test -- src/hostinger-deploy-sync.test.ts` and confirm it fails only when `Hostinger` differs from the freshly built `dist` output.

## Entry 11: PowerShell rejected bash-style command chaining during Hostinger sync
- **Date**: 2026-03-10
- **Failure**: A verification command using `&&` failed with `The token '&&' is not a valid statement separator in this version.`
- **Root cause**: The workspace shell is PowerShell, not a shell that accepts `&&` in that invocation context.
- **Reproduction**: Run a multi-command `functions.Shell` call with `Get-ChildItem ... && Get-ChildItem ...` in this workspace.
- **Fix attempt**: Re-run the command using PowerShell-compatible sequencing (for example `;`) instead of `&&`.
- **Verification**: Confirm the directory-inspection command succeeds and the sync proceeds with the corrected separator.

## Entry 12: Hostinger refresh automation test failed because no npm shortcut existed
- **Date**: 2026-03-10
- **Failure**: New red-phase test `src/hostinger-sync-script.test.ts` failed because `package.json` did not expose a `hostinger:refresh` command.
- **Root cause**: The repo had no package-level automation entry for the Hostinger refresh flow; the process was still manual.
- **Reproduction**: Run `npm run test -- src/hostinger-sync-script.test.ts`.
- **Fix attempt**: Add a package script that performs the one-command Hostinger refresh flow.
- **Verification**: Re-run `npm run test -- src/hostinger-sync-script.test.ts` and confirm the package-script assertion passes.

## Entry 13: Hostinger refresh automation test failed because the PowerShell script was missing
- **Date**: 2026-03-10
- **Failure**: The same red-phase test failed because `scripts/sync-hostinger.ps1` did not exist yet.
- **Root cause**: There was no reusable script implementing the archive-and-copy behavior for the Hostinger deployment mirror.
- **Reproduction**: Run `npm run test -- src/hostinger-sync-script.test.ts`.
- **Fix attempt**: Create `scripts/sync-hostinger.ps1` with parameterized Hostinger/dist paths and timestamped history archiving.
- **Verification**: Re-run `npm run test -- src/hostinger-sync-script.test.ts` and confirm the script existence/behavior assertions pass.

## Entry 14: Hostinger refresh PowerShell script failed because param block was not first
- **Date**: 2026-03-10
- **Failure**: After creating `scripts/sync-hostinger.ps1`, the focused test still failed and a direct script run exited with `StrictModeFunctionCallWithParens` at the `param(` line.
- **Root cause**: In PowerShell, the `param(...)` block must appear before executable statements. The script set `$ErrorActionPreference` and `Set-StrictMode` before `param`, so PowerShell treated `param(` as a function-style invocation instead of a valid script parameter block.
- **Reproduction**: Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\sync-hostinger.ps1 ...`.
- **Fix attempt**: Move the `param(...)` block to the top of the script, then apply strict mode and error settings after parameters are declared.
- **Verification**: Re-run the direct script invocation and `npm run test -- src/hostinger-sync-script.test.ts` and confirm the script exits 0 and performs the expected archive/copy behavior.
