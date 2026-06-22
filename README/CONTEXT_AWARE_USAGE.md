# Context-Aware Usage Guide

## 🎯 You Don't Need to Remember Commands!

**Good news:** I (the AI) automatically use the right tools and skills based on what you say. You don't need to remember specific commands or skill names.

---

## 🤖 How I Automatically Use Tools

### When You Say "Commit" or "Push"

**You say:**
- "Help me commit these changes"
- "Commit this"
- "Push to GitHub"
- "Save this to git"

**I automatically:**
1. Use the `@git-pushing` skill
2. Run the `smart-commit.sh` script
3. Ask you for the commit message
4. Show you what will be committed
5. **Ask for your confirmation** (MANDATORY)
6. Only commit after you confirm

**You don't need to say:**
- ❌ "Use @git-pushing"
- ❌ "./scripts/smart-commit.sh"
- ❌ "Run the commit script"

**Just say:**
- ✅ "Help me commit this"
- ✅ "Commit these changes"
- ✅ "Push to GitHub"

---

### When You Give Input/Requests

**You say:**
- "Add a new feature"
- "Fix this bug"
- "I need help with..."

**I automatically:**
1. Use `@concise-planning` to structure your request
2. Use `@brainstorming` if needed for edge cases
3. Gather context from codebase
4. Ask clarifying questions if needed
5. **Wait for your confirmation** before implementing

**You don't need to say:**
- ❌ "Use @concise-planning"
- ❌ "Use @brainstorming"
- ❌ "Plan this first"

**Just say:**
- ✅ "Add a login form"
- ✅ "Fix the navigation bug"
- ✅ "Help me implement authentication"

---

### When Implementing Code

**I automatically:**
1. Use `@test-driven-development` (write test first)
2. Use `@react-patterns` for React components
3. Use `@typescript-expert` for TypeScript
4. Use `@lint-and-validate` after changes
5. Use `@cc-skill-security-review` before completion

**You don't need to specify:**
- ❌ "Use TDD"
- ❌ "Use React patterns"
- ❌ "Check security"

**I do it automatically based on:**
- What you're asking for
- The codebase context
- The VMP protocol

---

## 🔒 Safety: Confirmation Required

### Commits Always Require Your Approval

**Before any commit, I will:**
1. ✅ Show you what will be committed
2. ✅ Show you the commit message
3. ✅ **Ask for your explicit confirmation**
4. ✅ Only commit if you say "yes"

**The script asks:**
```
⚠️  CONFIRMATION REQUIRED
Do you want to commit and push these changes? (yes/no):
```

**You must type "yes" (not just "y")** - this prevents accidental commits.

---

## 📋 Example Conversations

### Example 1: Committing Changes

**You:** "I'm done with the feature, help me commit it"

**I will:**
1. Check what files changed
2. Run quality checks
3. Ask: "What commit message should I use?"
4. Show you: "Here's what will be committed: [list of files]"
5. Ask: "Do you want to commit and push these changes? (yes/no)"
6. **Wait for your "yes"**
7. Then commit and push

**You don't need to:**
- Remember the script name
- Type the command yourself
- Worry about forgetting steps

---

### Example 2: New Feature Request

**You:** "Add a contact form to the homepage"

**I will:**
1. Use `@concise-planning` automatically
2. Read relevant files
3. Ask: "Should this follow the existing form pattern?"
4. Summarize: "I'll add a contact form component that..."
5. **Wait for your confirmation**
6. Then implement using TDD, React patterns, etc.

**You don't need to:**
- Say "plan this first"
- Specify which skills to use
- Remember the workflow

---

## 🎯 What You Need to Remember

### Nothing! Just talk naturally.

**Instead of:**
- ❌ "Use @concise-planning to plan adding a feature"
- ❌ "./scripts/smart-commit.sh 'feat: new feature'"
- ❌ "Use @test-driven-development for this"

**Just say:**
- ✅ "Add a new feature"
- ✅ "Help me commit this"
- ✅ "Fix this bug"

---

## 🛡️ Safety Features

### 1. Commit Confirmation (MANDATORY)
- Script asks: "Do you want to commit and push? (yes/no)"
- Must type "yes" (not "y" or "Y")
- Shows exactly what will be committed first

### 2. Quality Checks Before Commit
- Runs linting, tests, type checking
- Shows warnings/errors
- Asks if you want to continue despite issues

### 3. Pre-Commit Hooks (Automatic)
- Auto-formats code
- Auto-fixes linting
- Runs tests (blocking)
- Type checks (blocking)

### 4. Push Confirmation (Optional)
- After commit, asks: "Push to remote? (yes/no)"
- You can commit without pushing
- Push separately when ready

---

## 📝 Summary

### You Don't Need To:
- ❌ Remember skill names
- ❌ Remember script paths
- ❌ Type commands manually
- ❌ Worry about workflow steps

### You Just Need To:
- ✅ Talk naturally
- ✅ Confirm when asked
- ✅ Review what I show you

### I Automatically:
- ✅ Use the right skills
- ✅ Follow the right workflow
- ✅ Ask for confirmation
- ✅ Show you what's happening

---

## 🎉 Bottom Line

**Just talk to me like you're talking to a colleague.** I'll handle the technical details, use the right tools, and always ask for your approval before committing anything.

**Safety first, automation second!** 🛡️
