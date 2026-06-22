# New Project Setup Guide

## 🎯 Quick Answer

**Yes, you need to do this setup for each new project.**

But it's quick (5-10 minutes) and the scripts/documentation can be reused.

---

## 📋 Setup Checklist for New Projects

### Step 1: Install .cursor Skills (2 minutes)

**Required for VMP protocol** - Clone the skills repository:

```bash
git clone https://github.com/sickn33/antigravity-awesome-skills.git .cursor/skills
```

**Why per-project?** Each project needs its own `.cursor/skills` folder so the AI can access skills when working on that specific project.

**Windows Users:** If you encounter symlink issues:
```bash
git clone -c core.symlinks=true https://github.com/sickn33/antigravity-awesome-skills.git .cursor/skills
```

**Alternative (Global Location):** If you prefer to share skills across projects:
```bash
# Clone once globally
git clone https://github.com/sickn33/antigravity-awesome-skills.git ~/.cursor/skills

# Then symlink in each project (optional)
ln -s ~/.cursor/skills .cursor/skills
```

### Step 2: Copy Scripts (2 minutes)

Copy the `scripts/smart-commit.sh` to your new project:

```bash
# From your current project
cp scripts/smart-commit.sh /path/to/new-project/scripts/
chmod +x /path/to/new-project/scripts/smart-commit.sh
```

Or create the script fresh in the new project (it's in `docs/workflow/` for reference).

### Step 3: Install Dependencies (1 minute)

In your new project:

```bash
npm install --save-dev husky lint-staged prettier
```

### Step 4: Initialize Husky (1 minute)

```bash
npx husky init
```

### Step 5: Copy Pre-Commit Hook (1 minute)

Copy `.husky/pre-commit` from this project, or create it:

```bash
# Create .husky/pre-commit
cat > .husky/pre-commit << 'EOF'
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

echo "🔍 Running pre-commit quality gates..."

# Run lint-staged (auto-fixes formatting and linting)
npx lint-staged

# Run tests (blocking)
npm run test || exit 1

# Type check (blocking)
npx tsc --noEmit || exit 1

# Security audit (non-blocking)
npm audit --audit-level=high || echo "⚠️  Security audit found issues (non-blocking)"
EOF

chmod +x .husky/pre-commit
```

### Step 6: Update package.json (2 minutes)

Add to your `package.json`:

```json
{
  "scripts": {
    "typecheck": "tsc --noEmit",
    "quality-check": "npm run lint && npm run test && npm run typecheck",
    "prepare": "husky"
  },
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{ts,tsx,json,md,css}": [
      "prettier --write"
    ]
  }
}
```

### Step 7: Test It (1 minute)

```bash
# Make a small change
echo "// test" >> src/App.tsx

# Test commit (will ask for confirmation)
./scripts/smart-commit.sh "test: verify setup"
```

---

## 🚀 Quick Setup Script

You can create a setup script to automate this:

```bash
#!/bin/bash
# setup-workflow.sh - Quick setup for new projects

echo "🚀 Setting up workflow optimization..."

# Install dependencies
npm install --save-dev husky lint-staged prettier

# Initialize husky
npx husky init

# Create pre-commit hook
cat > .husky/pre-commit << 'EOF'
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"
npx lint-staged
npm run test || exit 1
npx tsc --noEmit || exit 1
EOF

chmod +x .husky/pre-commit

# Create smart-commit script
mkdir -p scripts
# Copy smart-commit.sh from docs/workflow or create it

echo "✅ Setup complete!"
echo "📝 Next: Update package.json with lint-staged config"
echo "📝 Next: Copy scripts/smart-commit.sh"
```

---

## 📁 What to Copy vs. What's Project-Specific

### Copy These (Reusable):
- ✅ `scripts/smart-commit.sh` - Commit script
- ✅ `.husky/pre-commit` - Pre-commit hook
- ✅ `docs/workflow/` - Documentation (optional, for reference)

### Project-Specific (Configure Each Time):
- ⚙️ `.cursor/skills` - Skills repository (clone for each project)
- ⚙️ `package.json` - Dependencies and scripts
- ⚙️ `.husky/` - Git hooks (but can copy the hook file)
- ⚙️ Git repository - Each project has its own

---

## 🎯 Per-Project vs. Global

### Per-Project (Required):
- ✅ `.cursor/skills` - Skills repository (clone for each project)
- ✅ Husky installation
- ✅ lint-staged configuration
- ✅ Pre-commit hooks
- ✅ package.json scripts
- ✅ Smart commit script

### Global (Optional):
- 📚 Documentation (can be in one place, referenced)
- 📚 Scripts (can be in a shared location)
- 📚 Skills (can be cloned globally and symlinked, but per-project is recommended)

**Recommendation:** Keep scripts in each project for portability, but you can maintain a "template" project with everything set up.

---

## 🔄 Template Project Approach

**Best Practice:** Create a template project with everything set up:

1. **Create template project:**
   ```bash
   mkdir my-project-template
   cd my-project-template
   # Setup workflow once
   # Commit as template
   ```

2. **For new projects:**
   ```bash
   # Copy from template
   cp -r my-project-template/.husky new-project/
   cp my-project-template/scripts/smart-commit.sh new-project/scripts/
   cp my-project-template/package.json new-project/package.json
   # Then install dependencies
   npm install
   ```

---

## ⏱️ Time Investment

- **First time setup:** 10-15 minutes (learning + setup)
- **Each new project:** 7-12 minutes (clone skills + copy + configure)
- **With template:** 3-5 minutes (copy + install + clone skills)

---

## 📝 Summary

**Yes, setup is per-project**, but:
- ✅ Quick to set up (5-10 minutes)
- ✅ Scripts can be reused
- ✅ Template project makes it faster
- ✅ Worth it for quality + efficiency gains

**For this project:** Follow `SETUP_INSTRUCTIONS.md` in this folder.

**For new projects:** Use this guide or copy from a template.
