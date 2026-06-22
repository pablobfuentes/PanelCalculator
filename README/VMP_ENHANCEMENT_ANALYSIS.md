# VMP Enhancement Analysis: Integrating .cursor Skills

## Executive Summary

The VIBE MASTER PROTOCOL (v2.0) can be significantly enhanced by referencing specific `.cursor/skills` throughout each phase. This eliminates the need for manual research, provides battle-tested patterns, and ensures consistent execution. **Stack documentation would still provide value** even with skills, as skills focus on patterns while docs provide API reference and breaking changes.

---

## Phase-by-Phase Skill Integration

### PHASE 1: DISCOVERY & SCOPE

**Current Process:**
1. Search & Research: Search /docs first then web for latest 2026 documentation
2. 360-Degree Analysis: List 5 edge cases
3. Future-Proofing: Propose modular directory structure
4. The Blueprint: Create/update `/docs/PLAN.md`
5. Validation: Wait for "Vibe Check"

**Enhanced with Skills:**

```
1. Search & Research:
   → Use @typescript-expert for TypeScript/Vite stack analysis
   → Use @react-patterns for React architecture patterns
   → Use @senior-architect for system design decisions
   → Use @architecture-decision-records for documenting tech choices
   → THEN search web for 2026-specific breaking changes (skills provide patterns, docs provide versions)

2. 360-Degree Analysis:
   → Use @frontend-developer for React/Next.js edge cases
   → Use @testing-patterns for test coverage considerations
   → Use @accessibility-compliance-accessibility-audit for a11y edge cases
   → Use @mobile-design for responsive behavior edge cases

3. Future-Proofing:
   → Use @architecture-patterns for modular architecture
   → Use @javascript-typescript-typescript-scaffold for directory structure templates
   → Use @senior-fullstack for full-stack organization patterns

4. The Blueprint:
   → Use @architecture-decision-records for documenting decisions in PLAN.md
   → Use @c4-architecture-c4-architecture for visual architecture documentation
   → Use @docs-architect for documentation structure

5. Validation:
   → Use @concise-planning to present findings in structured format
```

**Skill References:**
- `.cursor/skills/skills/typescript-expert/SKILL.md`
- `.cursor/skills/skills/react-patterns/SKILL.md`
- `.cursor/skills/skills/senior-architect/SKILL.md`
- `.cursor/skills/skills/architecture-decision-records/SKILL.md`
- `.cursor/skills/skills/frontend-developer/SKILL.md`
- `.cursor/skills/skills/testing-patterns/SKILL.md`
- `.cursor/skills/skills/javascript-typescript-typescript-scaffold/SKILL.md`
- `.cursor/skills/skills/concise-planning/SKILL.md`

---

### PHASE 2: ARCHITECTURAL MANDATES

**Current Process:**
- Configuration-Driven UI: All text/media in `src/config/site-content.ts`
- Modular Design: Files < 300 lines, extract to hooks/utils
- State Management: URL-based or lightweight signals
- Type Safety: Strict TypeScript, no `any`

**Enhanced with Skills:**

```
Configuration-Driven UI:
→ Use @react-patterns for component composition patterns
→ Use @typescript-expert for type-safe config structures
→ Reference: .cursor/skills/skills/react-patterns/SKILL.md (Section: Composition Patterns)

Modular Design:
→ Use @react-patterns for hook extraction patterns
→ Use @typescript-expert for utility function organization
→ Reference: .cursor/skills/skills/react-patterns/SKILL.md (Section: Hook Patterns)

State Management:
→ Use @react-patterns for state management selection guide
→ Use @frontend-developer for URL-based state patterns
→ Reference: .cursor/skills/skills/react-patterns/SKILL.md (Section: State Management Selection)

Type Safety:
→ Use @typescript-expert for strict TypeScript configuration
→ Use @typescript-expert for eliminating `any` types
→ Reference: .cursor/skills/skills/typescript-expert/SKILL.md (Section: Type Safety Patterns)
```

---

### PHASE 3: DIRECTORY STRUCTURE

**Current Process:**
- Ensure project follows specified organization
- `/app` or `/src`: Core logic
- `/config`: `site-content.ts`
- `/services`: Third-party integrations
- `/docs`: Documentation
- `/tests`: Test files

**Enhanced with Skills:**

```
Directory Structure:
→ Use @javascript-typescript-typescript-scaffold for Vite + React structure
→ Use @senior-fullstack for full-stack organization
→ Use @architecture-patterns for scalable folder organization
→ Reference: .cursor/skills/skills/javascript-typescript-typescript-scaffold/SKILL.md (Section: Generate React + Vite Project Structure)
```

---

### PHASE 4: THE EXECUTION LOOP

**Current Process:**
1. Test First/Parallel: Write test before/alongside implementation
2. Failure Logging: Log failures in `docs/FAILURE_LOG.md`
3. Implementation Summary: Update `docs/CHANGELOG_AI.md`

**Enhanced with Skills:**

```
1. Test First/Parallel:
   → Use @test-driven-development for TDD workflow (MANDATORY)
   → Use @testing-patterns for Vitest/Jest patterns
   → Use @javascript-testing-patterns for React Testing Library patterns
   → Reference: .cursor/skills/skills/test-driven-development/SKILL.md
   → Reference: .cursor/skills/skills/testing-patterns/SKILL.md

2. Review Mode (Security & Performance):
   → Use @cc-skill-security-review for security vulnerabilities
   → Use @api-security-best-practices for API security
   → Use @frontend-security-coder for frontend security
   → Use @performance-testing-review-ai-review for performance bottlenecks
   → Reference: .cursor/skills/skills/cc-skill-security-review/SKILL.md

3. Failure Logging:
   → Use @systematic-debugging for structured failure analysis
   → Reference: .cursor/skills/skills/systematic-debugging/SKILL.md

4. Implementation Summary:
   → Use @changelog-automation for structured changelog entries
   → Reference: .cursor/skills/skills/changelog-automation/SKILL.md (if available)
```

**Critical Skill Integration:**
The `@test-driven-development` skill enforces the "Iron Law": **NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST**. This aligns perfectly with VMP Phase 4 requirements.

---

### PHASE 5: MAINTENANCE INTERFACE

**Current Process:**
- Implement "Master Config" pattern
- Example: `<Hero data={SITE_CONFIG.hero} />`

**Enhanced with Skills:**

```
Master Config Pattern:
→ Use @react-patterns for prop injection patterns
→ Use @typescript-expert for type-safe config interfaces
→ Reference: .cursor/skills/skills/react-patterns/SKILL.md (Section: Component Design Principles)
```

---

### PHASE 6: THE CONTENT REGISTRY RULE

**Current Process:**
1. Zero Hardcoding: All strings in `src/config/app-registry.ts`
2. Semantic Naming: `sectionName_elementName_property`
3. Prop Injection: Components receive data as props
4. Maintenance Mode: Only edit `app-registry.ts` for content updates

**Enhanced with Skills:**

```
Content Registry:
→ Use @typescript-expert for type-safe registry structures
→ Use @react-patterns for prop injection patterns
→ Reference: .cursor/skills/skills/typescript-expert/SKILL.md (Section: Type-Level Programming)
→ Reference: .cursor/skills/skills/react-patterns/SKILL.md (Section: Component Design Principles)
```

---

## Recommended VMP v2.1 Updates

### Updated Phase 1: Discovery & Scope

```
Before writing any code, you must execute the following:

1. **Skill-Based Research:**
   - Use @typescript-expert for TypeScript/Vite stack patterns
   - Use @react-patterns for React architecture guidance
   - Use @senior-architect for system design decisions
   - THEN search web for 2026-specific breaking changes (skills provide patterns, docs provide versions)

2. **360-Degree Analysis:**
   - Use @frontend-developer for React/Next.js edge cases
   - Use @testing-patterns for test coverage considerations
   - Use @accessibility-compliance-accessibility-audit for a11y edge cases
   - List 5 edge cases I overlooked

3. **Future-Proofing:**
   - Use @architecture-patterns for modular architecture
   - Use @javascript-typescript-typescript-scaffold for directory structure templates
   - Propose modular directory structure

4. **The Blueprint:**
   - Use @architecture-decision-records for documenting decisions
   - Create or update `/docs/PLAN.md` with technical architecture

5. **Validation:**
   - Use @concise-planning to present findings
   - Wait for my "Vibe Check" (approval)
```

### Updated Phase 4: The Execution Loop

```
For every feature implementation:

1. **Test First (MANDATORY):**
   - Use @test-driven-development: Write failing test FIRST
   - Use @testing-patterns for Vitest/Jest patterns
   - NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
   - Watch test fail, then write minimal code to pass

2. **Review Mode:**
   - Use @cc-skill-security-review for security vulnerabilities (SQL injection, leaked env vars)
   - Use @performance-testing-review-ai-review for performance bottlenecks
   - Self-critique before marking complete

3. **Failure Logging:**
   - Use @systematic-debugging for structured analysis
   - Log in `docs/FAILURE_LOG.md`: What was tried, why it failed, lesson learned

4. **Implementation Summary:**
   - Update `docs/CHANGELOG_AI.md` with feature logic and connection to `site-content.ts`
```

---

## Stack Documentation Value Assessment

### YES, Stack Documentation Still Provides Value

**Why Skills + Docs Work Together:**

1. **Skills = Patterns & Best Practices**
   - How to structure code
   - When to use patterns
   - Common pitfalls
   - Architecture decisions

2. **Docs = API Reference & Breaking Changes**
   - Exact API signatures
   - Version-specific features
   - Migration guides
   - Breaking changes in 2026
   - Configuration options

**Example Workflow:**
```
1. Use @react-patterns → "Use React Query for server state"
2. Check React Query docs → "useQuery hook signature changed in v5"
3. Use @typescript-expert → "Type the new hook correctly"
4. Implement with confidence
```

**Recommended Documentation Sources:**
- **Vite**: https://vitejs.dev/ (check for 2026 breaking changes)
- **React**: https://react.dev/ (React 19 features)
- **TypeScript**: https://www.typescriptlang.org/ (TS 5.x features)
- **Vitest**: https://vitest.dev/ (testing patterns)
- **Tailwind CSS**: https://tailwindcss.com/ (v4 changes)
- **Radix UI**: https://www.radix-ui.com/ (component APIs)

**Value Proposition:**
- Skills prevent reinventing the wheel
- Docs ensure you're using current APIs correctly
- Together = faster, more accurate implementation

---

## Quick Reference: Skill Mapping

| VMP Phase | Primary Skills | Secondary Skills |
|----------|---------------|------------------|
| **Phase 1: Discovery** | `@typescript-expert`, `@react-patterns`, `@senior-architect` | `@frontend-developer`, `@testing-patterns`, `@concise-planning` |
| **Phase 2: Architecture** | `@react-patterns`, `@typescript-expert` | `@architecture-patterns` |
| **Phase 3: Structure** | `@javascript-typescript-typescript-scaffold` | `@senior-fullstack` |
| **Phase 4: Execution** | `@test-driven-development` (MANDATORY), `@cc-skill-security-review` | `@testing-patterns`, `@systematic-debugging` |
| **Phase 5: Maintenance** | `@react-patterns` | `@typescript-expert` |
| **Phase 6: Content Registry** | `@typescript-expert`, `@react-patterns` | - |

---

## Implementation Checklist

- [ ] Update VMP document with skill references
- [ ] Create skill quick-reference card
- [ ] Add skill invocation examples to each phase
- [ ] Document when to use skills vs. web search
- [ ] Create stack documentation bookmarks
- [ ] Test skill integration in next feature

---

## Conclusion

Integrating `.cursor/skills` into the VMP transforms it from a manual process to an automated, pattern-driven workflow. Skills eliminate guesswork, provide battle-tested solutions, and ensure consistency. Stack documentation remains valuable for API references and version-specific details.

**Key Benefits:**
1. ✅ Faster execution (no research needed for patterns)
2. ✅ Consistent quality (proven patterns)
3. ✅ Reduced errors (security and testing built-in)
4. ✅ Better documentation (ADR patterns)
5. ✅ Type safety (TypeScript expertise)

**Next Steps:**
1. Review this analysis
2. Update VMP with skill references
3. Test on next feature implementation
4. Iterate based on results
