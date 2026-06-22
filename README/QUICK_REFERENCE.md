# Workflow Quick Reference

## 🚀 Daily Commands

### Make Changes & Commit

**You don't need to remember commands! Just tell me:**

1. **Make your changes**

2. **Say to me:**
   - "Help me commit these changes"
   - "Commit this"
   - "Push to GitHub"

3. **I will automatically:**
   - Run quality checks
   - Ask for commit message
   - Show you what will be committed
   - **Ask for your confirmation (MANDATORY)**
   - Only commit after you say "yes"

**Manual Usage (optional):**
```bash
# Run quality check (optional)
npm run quality-check

# Commit and push (requires confirmation)
./scripts/smart-commit.sh "feat: your feature description"
```

### Quality Checks
```bash
# Run all checks
npm run quality-check

# Individual checks
npm run lint          # Linting
npm run test          # Tests
npm run typecheck     # Type checking
```

## 📝 Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `ref`: Refactoring
- `docs`: Documentation
- `test`: Tests
- `chore`: Maintenance

**Examples:**
```bash
./scripts/smart-commit.sh "feat(hero): add animated background"
./scripts/smart-commit.sh "fix(auth): handle null user response"
./scripts/smart-commit.sh "ref(config): extract to app-registry"
```

## 🔍 Pre-Commit Hooks (Automatic)

When you commit, these run automatically:
1. ✅ Auto-format (Prettier)
2. ✅ Auto-fix linting (ESLint)
3. ✅ Run tests (blocking)
4. ✅ Type check (blocking)
5. ⚠️  Security audit (warnings)
6. ⚠️  Check for console.log (warnings)
7. ⚠️  Check for secrets (warnings)

## 🎯 VMP + Skills Integration

### Phase 1: Discovery
- Use `@typescript-expert` for patterns
- Use `@react-patterns` for components
- Web search only for 2026 breaking changes

### Phase 4: Execution
- Use `@test-driven-development` (MANDATORY)
- Use `@lint-and-validate` after changes
- Pre-commit hooks enforce quality

### Phase 6: Content Registry
- Pre-commit checks for hardcoded text
- Use `@typescript-expert` for type-safe config

## 🛠️ Troubleshooting

### Pre-commit hook not running
```bash
npx husky init
chmod +x .husky/pre-commit
```

### Tests failing
```bash
# Fix tests first
npm run test

# Or skip (not recommended)
git commit --no-verify
```

### Type errors
```bash
# Fix type errors
npm run typecheck

# Or skip (not recommended)
git commit --no-verify
```

## 📊 Workflow Checklist

- [ ] Made changes
- [ ] Ran quality check (optional)
- [ ] Used smart-commit script
- [ ] Pre-commit hooks passed
- [ ] Changes pushed to remote

## 🎁 Quick Wins

1. **Always use smart-commit script**
2. **Fix pre-commit failures** (don't skip)
3. **Use skills for patterns** (not web search)
4. **Monitor improvements** over time

---

**For detailed info, see:**
- WORKFLOW_OPTIMIZATION_PLAN.md (complete strategy)
- SETUP_INSTRUCTIONS.md (setup guide)
- WORKFLOW_IMPROVEMENTS_SUMMARY.md (overview)
