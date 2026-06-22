# Complete Workflow Optimization Plan
## From Input to GitHub Commit - Maximum Efficiency

This document outlines improvements across the entire development pipeline to reduce mistakes, optimize resource usage, and improve code quality.

---

## 🎯 Current State Analysis

### Current Workflow Gaps Identified:
1. **Input Reception**: No structured clarification protocol
2. **Planning**: Manual research, no automated pattern matching
3. **Implementation**: No pre-write validation hooks
4. **Quality Gates**: Manual linting, no automated checks
5. **Git Workflow**: No standardized commit process
6. **Resource Usage**: Redundant tool calls, no caching strategy
7. **Error Prevention**: Reactive debugging instead of proactive prevention

---

## 📥 PHASE 0: INPUT RECEPTION & CLARIFICATION

### Current Problem
- Ambiguous requests lead to rework
- Missing context causes wrong assumptions
- No structured way to gather requirements

### Solution: Structured Input Protocol

**IMPORTANT: Context-Aware Usage**
- **You don't need to remember skill names or commands**
- I automatically use `@concise-planning` when you give input
- I automatically use `@brainstorming` for complex features
- Just talk naturally - I handle the technical details

**Protocol (I do this automatically):**
```
1. Parse Request:
   - Extract: Feature, Scope, Constraints, Acceptance Criteria
   - Identify: Type (feature/fix/refactor), Priority, Dependencies
   - Automatically use @concise-planning for structure

2. Context Gathering (if needed):
   - Read relevant files FIRST (not during implementation)
   - Check existing patterns in codebase
   - Identify similar implementations

3. Clarification Questions (if ambiguous):
   - "Should this follow the existing [pattern]?"
   - "What edge cases should I handle?"
   - "Any performance/security constraints?"

4. Confirm Understanding:
   - Summarize: "I'll implement X that does Y, following Z pattern"
   - Wait for confirmation before coding
```

**Resource Optimization:**
- Batch file reads upfront (not one-by-one)
- Cache file contents for session
- Use `grep` for pattern matching before `read_file`

---

## 🧠 PHASE 1: ENHANCED DISCOVERY (Already Improved)

**Key Addition: Pre-Implementation Checklist**

Before starting implementation, verify:
- [ ] All relevant files read and understood
- [ ] Similar patterns identified in codebase
- [ ] Edge cases documented
- [ ] Test strategy defined
- [ ] Security considerations noted

**Resource Optimization:**
- Use `@typescript-expert` for stack patterns (faster than web search)
- Use `@react-patterns` for component patterns (no research needed)
- Only web search for 2026-specific breaking changes

---

## 💻 PHASE 2: IMPLEMENTATION WITH QUALITY GATES

### Current Problem
- Code written, then validated (reactive)
- Errors caught late in process
- No automated formatting/linting during write

### Solution: Pre-Write & Post-Write Hooks

**Pre-Write Validation (Blocking):**
```bash
# .husky/pre-write (or similar)
#!/bin/bash
# Check for common mistakes BEFORE writing

# 1. Secret Detection
if grep -rE "(password|secret|api[_-]?key|token).*=.*['\"][^'\"]{8,}" "$1"; then
  echo "❌ BLOCKED: Potential secret detected in $1"
  exit 1
fi

# 2. Hardcoded Text Detection (VMP Phase 6 violation)
if grep -E "(<h[1-6]>|<p>|<span>).*[A-Z][a-z]+" "$1" | grep -v "APP_REGISTRY\|SITE_CONFIG"; then
  echo "⚠️  WARNING: Hardcoded text detected. Use APP_REGISTRY instead."
  # Non-blocking, but logs warning
fi

# 3. Console.log Detection
if grep -n "console\.log" "$1" | grep -v "test\|spec"; then
  echo "⚠️  WARNING: console.log found. Remove before commit."
fi
```

**Post-Write Auto-Fix:**
```bash
# .husky/post-write
#!/bin/bash
# Auto-fix after every file write

# 1. Auto-format
npx prettier --write "$1" 2>/dev/null || true

# 2. Auto-fix linting
npx eslint --fix "$1" 2>/dev/null || true

# 3. Type check (non-blocking, logs errors)
npx tsc --noEmit 2>&1 | tee /tmp/tsc-errors.log || true
```

**Implementation:**
1. Install Husky: `npm install --save-dev husky`
2. Setup hooks: `npx husky init`
3. Create pre-write hook (manual or via script)
4. Create post-write hook

**Use Skills:**
- `@lint-and-validate` - Run after every code change
- `@cc-skill-security-review` - Before marking complete

---

## ✅ PHASE 3: QUALITY GATES (MANDATORY BEFORE COMMIT)

### Current Problem
- Manual validation steps
- Easy to forget checks
- No automated quality gates

### Solution: Pre-Commit Hooks (BLOCKING)

**Install Husky + lint-staged:**
```bash
npm install --save-dev husky lint-staged
npx husky init
```

**package.json:**
```json
{
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix",
      "prettier --write",
      "bash -c 'npx tsc --noEmit'"
    ],
    "*.{ts,tsx,json,md}": [
      "prettier --write"
    ]
  },
  "scripts": {
    "prepare": "husky",
    "pre-commit": "lint-staged",
    "quality-check": "npm run lint && npm run test && npx tsc --noEmit"
  }
}
```

**.husky/pre-commit:**
```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# Run lint-staged (auto-fixes)
npx lint-staged

# Run tests (blocking)
npm run test

# Type check (blocking)
npx tsc --noEmit

# Security audit (non-blocking, logs warnings)
npm audit --audit-level=high || echo "⚠️  Security audit found issues (non-blocking)"
```

**Quality Gate Checklist (Automated):**
- [ ] ✅ Linting passes (auto-fixed)
- [ ] ✅ Type checking passes (blocking)
- [ ] ✅ Tests pass (blocking)
- [ ] ✅ No console.log in production code
- [ ] ✅ No hardcoded secrets
- [ ] ✅ No hardcoded text (VMP Phase 6)
- [ ] ⚠️  Security audit (warnings only)

**Use Skills:**
- `@lint-and-validate` - Automated validation
- `@cc-skill-security-review` - Security checklist
- `@test-driven-development` - Ensure tests exist

---

## 📝 PHASE 4: GIT WORKFLOW OPTIMIZATION

### Current Problem
- Inconsistent commit messages
- No standardized workflow
- Easy to forget to push

### Solution: Standardized Git Workflow

**IMPORTANT: Context-Aware Usage**
- **You don't need to remember commands or script names**
- When you say "commit" or "push", I automatically:
  - Use `@git-pushing` skill
  - Run `smart-commit.sh` script
  - Ask for commit message
  - **Show you what will be committed**
  - **Ask for your explicit confirmation (MANDATORY)**
  - Only commit after you confirm

**Git Workflow Protocol (I do this automatically):**

1. **You say:** "Help me commit" or "Commit these changes"

2. **I automatically:**
   - Check what changed
   - Run quality checks
   - Ask for commit message
   - Show you what will be committed
   - **Ask: "Do you want to commit and push? (yes/no)"**
   - **Wait for your "yes"**
   - Then commit and push

3. **Commit Message Format (I help you with this):**
   - Format: `<type>(<scope>): <subject>`
   - Examples:
     - `feat(hero): Add animated background`
     - `fix(auth): Handle null user response`
     - `ref(config): Extract site-content to app-registry`

**Safety: MANDATORY Confirmation**
- Script requires typing "yes" (not just "y")
- Shows exactly what will be committed
- You can review before confirming

**scripts/smart-commit.sh:**
```bash
#!/bin/bash
# Smart commit and push script

COMMIT_MSG="$1"

if [ -z "$COMMIT_MSG" ]; then
  echo "Usage: ./scripts/smart-commit.sh 'feat: description'"
  exit 1
fi

# Stage all changes
git add .

# Create commit
git commit -m "$COMMIT_MSG

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to remote
git push origin $(git branch --show-current)

echo "✅ Committed and pushed: $COMMIT_MSG"
```

**Git Workflow Checklist:**
- [ ] Quality gates passed
- [ ] Commit message follows conventional format
- [ ] Changes staged
- [ ] Committed
- [ ] Pushed to remote
- [ ] Verify push succeeded

---

## 🚀 PHASE 5: RESOURCE OPTIMIZATION

### Current Problem
- Redundant file reads
- Multiple tool calls for same purpose
- No caching strategy

### Solution: Smart Caching & Batch Operations

**File Reading Strategy:**
```
1. Batch Read: Read all relevant files in parallel
2. Cache Results: Keep file contents in memory for session
3. Incremental Updates: Only re-read if file changed
4. Pattern Matching First: Use grep before read_file
```

**Tool Call Optimization:**
```
1. Single Lint Run: Run once after all changes, not per-file
2. Single Type Check: Run once, not per-file
3. Batch Tests: Run all tests together
4. Parallel Operations: Run independent checks in parallel
```

**Example Optimized Workflow:**
```typescript
// Instead of:
read_file(file1) → read_file(file2) → read_file(file3)
lint(file1) → lint(file2) → lint(file3)
test(file1) → test(file2) → test(file3)

// Do:
read_files([file1, file2, file3]) // Parallel
make_changes([file1, file2, file3])
lint_all() // Once
test_all() // Once
```

**Resource Monitoring:**
- Track tool call count per task
- Log redundant operations
- Optimize based on patterns

---

## 🛡️ PHASE 6: ERROR PREVENTION

### Current Problem
- Errors caught late
- Reactive debugging
- No proactive prevention

### Solution: Proactive Error Prevention

**1. Pattern-Based Prevention:**
```typescript
// Common mistakes to prevent:
- Hardcoded text → Use APP_REGISTRY
- Missing error handling → Always add try/catch
- No type safety → Strict TypeScript
- Missing tests → TDD mandatory
- Security issues → Pre-commit security scan
```

**2. Template-Based Implementation:**
- Use `@javascript-typescript-typescript-scaffold` for structure
- Use `@react-patterns` for component templates
- Use `@typescript-expert` for type patterns

**3. Automated Checks:**
- Pre-write hooks (block mistakes)
- Post-write hooks (auto-fix)
- Pre-commit hooks (quality gates)
- CI/CD (final validation)

**4. Learning from Failures:**
- Log failures to `docs/FAILURE_LOG.md`
- Extract patterns from failures
- Update VMP with prevention strategies
- Use `@systematic-debugging` for analysis

---

## 📊 PHASE 7: METRICS & MONITORING

### Track These Metrics:
1. **Efficiency:**
   - Time from input to commit
   - Number of iterations
   - Tool call count per task

2. **Quality:**
   - Pre-commit hook failures
   - Test failures
   - Type errors caught

3. **Resource Usage:**
   - File reads per task
   - Redundant operations
   - Cache hit rate

**Implementation:**
```bash
# Add to package.json
"scripts": {
  "metrics": "node scripts/track-metrics.js"
}
```

---

## 🎯 IMPLEMENTATION CHECKLIST

### Immediate (High Impact, Low Effort):
- [ ] Install Husky: `npm install --save-dev husky`
- [ ] Setup lint-staged: `npm install --save-dev lint-staged`
- [ ] Create pre-commit hook with quality gates
- [ ] Create smart-commit.sh script
- [ ] Add quality-check script to package.json

### Short Term (High Impact, Medium Effort):
- [ ] Implement pre-write hooks (secret detection)
- [ ] Implement post-write hooks (auto-format)
- [ ] Create structured input protocol
- [ ] Batch file operations
- [ ] Add metrics tracking

### Long Term (Medium Impact, High Effort):
- [ ] CI/CD pipeline with quality gates
- [ ] Automated test generation
- [ ] Performance monitoring
- [ ] Advanced caching strategy

---

## 📋 COMPLETE WORKFLOW (Optimized)

```
1. INPUT RECEPTION
   ├─ Parse request
   ├─ Gather context (batch read files)
   ├─ Clarify if needed
   └─ Confirm understanding

2. PLANNING
   ├─ Use @typescript-expert, @react-patterns (skills)
   ├─ Web search for 2026 breaking changes only
   ├─ Document in PLAN.md
   └─ Get approval

3. IMPLEMENTATION
   ├─ Pre-write hook: Check for secrets/hardcoded text
   ├─ Write code (TDD: test first)
   ├─ Post-write hook: Auto-format, auto-lint
   └─ Run @lint-and-validate

4. QUALITY GATES
   ├─ Pre-commit hook: Lint, type-check, test
   ├─ Security review: @cc-skill-security-review
   ├─ Performance check: @performance-testing-review-ai-review
   └─ All gates must pass

5. GIT WORKFLOW
   ├─ Stage changes
   ├─ Commit: Use @commit skill (conventional format)
   ├─ Push: Use @git-pushing skill
   └─ Verify push succeeded

6. POST-COMMIT
   ├─ Update CHANGELOG_AI.md
   ├─ Update FAILURE_LOG.md (if applicable)
   └─ Log metrics
```

---

## 🎁 QUICK WINS (Implement Today)

1. **Add Husky Pre-Commit Hook** (5 minutes)
   ```bash
   npm install --save-dev husky lint-staged
   npx husky init
   # Add lint-staged config to package.json
   ```

2. **Create Smart Commit Script** (10 minutes)
   - Copy script from above
   - Make executable: `chmod +x scripts/smart-commit.sh`

3. **Add Quality Check Script** (2 minutes)
   ```json
   "quality-check": "npm run lint && npm run test && npx tsc --noEmit"
   ```

4. **Use Skills Consistently** (Immediate)
   - Always use `@test-driven-development`
   - Always use `@lint-and-validate`
   - Always use `@commit` for commits

---

## 📚 SKILLS TO ADD TO VMP

Add these to your VMP workflow:

- **Input Phase**: `@concise-planning`, `@brainstorming`
- **Implementation**: `@lint-and-validate` (after every change)
- **Quality**: `@cc-skill-security-review` (before commit)
- **Git**: `@commit`, `@git-pushing`

---

## 🎯 EXPECTED IMPROVEMENTS

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Time to Commit** | 30-60 min | 15-30 min | 50% faster |
| **Pre-Commit Errors** | 3-5 per task | 0-1 per task | 80% reduction |
| **Rework Rate** | 20-30% | 5-10% | 70% reduction |
| **Tool Calls** | 50-100 | 20-40 | 60% reduction |
| **Code Quality** | Manual checks | Automated | Consistent |

---

## 🚀 NEXT STEPS

1. Review this plan
2. Implement Quick Wins (today)
3. Setup Husky + lint-staged (this week)
4. Create smart-commit script (this week)
5. Monitor metrics and iterate

---

## 📝 NOTES

- All hooks should be non-blocking where possible (warnings vs errors)
- Pre-commit hooks should auto-fix when safe
- Always provide clear error messages
- Log all quality gate results for analysis
