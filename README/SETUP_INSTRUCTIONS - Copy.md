# Workflow Optimization Setup Instructions

## ⚠️ IMPORTANT: Per-Project Setup

**This setup is PER-PROJECT** - you need to do this for each new project you create.

**Why?** Each project has its own:
- `package.json` (different dependencies)
- Git repository (different commits)
- Quality gates (project-specific)
- `.cursor/skills` (project-specific skills for VMP)

**However:** The documentation and scripts can be reused across projects.

**For new projects:** See `NEW_PROJECT_SETUP.md` in this folder for a quick setup guide.

---

Follow these steps to implement the optimized workflow **for this project**.

## 🚀 Quick Setup (5-10 minutes)

### Step 1: Install .cursor Skills (Required for VMP)

The VMP protocol uses `.cursor/skills` for automated pattern matching and best practices. You need to clone the skills repository for this project:

```bash
git clone https://github.com/sickn33/antigravity-awesome-skills.git .cursor/skills
```

**Note:** This clones the skills into your project. Each project needs its own copy so skills are available when working on that project.

**Alternative (if you prefer a global location):**
```bash
# Clone to a global location (optional)
git clone https://github.com/sickn33/antigravity-awesome-skills.git ~/.cursor/skills

# Then symlink to project (optional)
ln -s ~/.cursor/skills .cursor/skills
```

**Windows Users:** If you encounter symlink issues, enable Developer Mode or run Git as Administrator:
```bash
git clone -c core.symlinks=true https://github.com/sickn33/antigravity-awesome-skills.git .cursor/skills
```

### Step 2: Install Dependencies

```bash
npm install --save-dev husky lint-staged prettier
```

**Note:** If you see a Node version warning (requires >=20.17, you have 20.14), you have two options:

**Option A (Recommended):** Upgrade Node.js to 20.17 or later:
- Download from [nodejs.org](https://nodejs.org/)
- Or use nvm: `nvm install 20.17`

**Option B:** Use compatible versions (works with Node 20.14):
```bash
npm install --save-dev husky@latest lint-staged@15.2.0 prettier
```

The warning is non-blocking - it will still work, but upgrading is recommended.

### Step 3: Initialize Husky

```bash
npx husky init
```

This creates the `.husky` directory and sets up git hooks.

### Step 4: Make Smart Commit Script Executable

**Windows (CMD/PowerShell):**
```cmd
# The script will work without chmod on Windows
# Git Bash will handle permissions automatically
# No action needed - you can skip this step on Windows
```

**Windows (Git Bash):**
```bash
chmod +x scripts/smart-commit.sh
```

**Linux/Mac:**
```bash
chmod +x scripts/smart-commit.sh
```

**Note:** On Windows, if you're using CMD or PowerShell, you can skip the `chmod` step. The script will work fine. If you're using Git Bash, use the `chmod` command.

### Step 5: Verify Setup

```bash
# Test quality check
npm run quality-check

# Test smart commit (dry run - don't actually commit)
git status
```

## ✅ What's Now Automated

### Pre-Commit Hooks (Automatic)
- ✅ Auto-format code (Prettier)
- ✅ Auto-fix linting issues (ESLint)
- ✅ Run tests (blocking)
- ✅ Type check (blocking)
- ✅ Security audit (warnings)
- ✅ Check for console.log (warnings)
- ✅ Check for secrets (warnings)

### Smart Commit Script
- ✅ Quality checks before commit
- ✅ Conventional commit format
- ✅ Auto-push to remote
- ✅ Error handling

## 📝 Usage

### Normal Workflow

**IMPORTANT: You don't need to remember commands!**

1. **Make changes**

2. **Just tell me:**
   - "Help me commit these changes"
   - "Commit this"
   - "Push to GitHub"

3. **I will:**
   - Run quality checks
   - Ask for commit message
   - Show you what will be committed
   - **Ask for your confirmation**
   - Only commit after you confirm

**Manual Usage (if you prefer):**

**Windows (CMD):**
```cmd
REM Run quality check (optional)
npm run quality-check

REM Commit and push (requires confirmation)
scripts\smart-commit.bat "feat: add new feature"
```

**Windows (Git Bash) / Linux / Mac:**
```bash
# Run quality check (optional)
npm run quality-check

# Commit and push (requires confirmation)
./scripts/smart-commit.sh "feat: add new feature"
```

### Commit Message Format

Follow conventional commits:
- `feat: add user authentication`
- `fix: resolve null pointer error`
- `ref: extract validation logic`
- `docs: update README`
- `test: add unit tests for auth`
- `chore: update dependencies`

## 🔧 Configuration Files

### package.json
- Added `lint-staged` configuration
- Added `quality-check` script
- Added `prepare` script for Husky

### .husky/pre-commit
- Runs lint-staged (auto-fix)
- Runs tests (blocking)
- Runs type check (blocking)
- Security checks (warnings)

### scripts/smart-commit.sh
- Quality checks before commit
- Conventional commit format
- Auto-push to remote

## 🎯 Expected Behavior

### Before Commit
1. You run: `./scripts/smart-commit.sh "feat: new feature"`
2. Script runs quality checks
3. If checks pass → commits and pushes
4. If checks fail → asks if you want to continue

### During Commit (Pre-Commit Hook)
1. Git triggers `.husky/pre-commit`
2. Lint-staged auto-fixes formatting
3. Tests run (must pass)
4. Type check runs (must pass)
5. Security checks run (warnings only)

### If Pre-Commit Fails
- Commit is blocked
- You see error messages
- Fix issues and try again

## 🐛 Troubleshooting

### Node Version Warning

If you see: `Unsupported engine: required: { node: '>=20.17' }, current: { node: 'v20.14.0' }`

**Solution:** Upgrade Node.js to 20.17+ or use compatible versions:
```bash
npm install --save-dev husky@latest lint-staged@15.2.0 prettier
```

**Note:** The warning is non-blocking - it will still work, but upgrading is recommended.

### "Husky not found"
```bash
npm install --save-dev husky
npx husky init
```

### "lint-staged not found"
```bash
npm install --save-dev lint-staged
```

### "Pre-commit hook not running"

**Windows (Git Bash):**
```bash
# Make sure husky is initialized
npx husky init

# Check if hook exists
ls -la .husky/pre-commit

# Make executable
chmod +x .husky/pre-commit
```

**Windows (CMD/PowerShell):**
```cmd
REM Make sure husky is initialized
npx husky init

REM Check if hook exists
dir .husky\pre-commit

REM On Windows, hooks should work without chmod
REM If issues persist, use Git Bash for git operations
```

### "chmod is not recognized" (Windows)

**This is normal on Windows CMD/PowerShell!** You can skip the `chmod` step:
- The script will work without it on Windows
- Use `scripts\smart-commit.bat` for Windows CMD
- Or use Git Bash which supports `chmod`

### "Tests failing in pre-commit"
- Fix failing tests first
- Or temporarily skip: `git commit --no-verify` (not recommended)

### "Type errors in pre-commit"
- Fix type errors first
- Or temporarily skip: `git commit --no-verify` (not recommended)

## 📊 Monitoring

Track these metrics:
- Pre-commit hook failures (should decrease)
- Time to commit (should decrease)
- Rework rate (should decrease)

## 🎉 You're Done!

Your workflow is now optimized with:
- ✅ Automated quality gates
- ✅ Smart commit script
- ✅ Pre-commit hooks
- ✅ Consistent commit messages

Start using:

**Windows (CMD):**
```cmd
scripts\smart-commit.bat "feat: your feature description"
```

**Windows (Git Bash) / Linux / Mac:**
```bash
./scripts/smart-commit.sh "feat: your feature description"
```
