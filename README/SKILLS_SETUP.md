# .cursor Skills Setup Guide

## 🎯 Quick Answer

**Yes, you need to clone the skills repository for each project** (or use a global location with symlinks).

The VMP protocol relies on `.cursor/skills` to automatically use the right patterns and best practices.

---

## 📋 Installation Options

### Option 1: Per-Project (Recommended)

**Clone skills into each project:**

```bash
git clone https://github.com/sickn33/antigravity-awesome-skills.git .cursor/skills
```

**Pros:**
- ✅ Each project is self-contained
- ✅ Easy to update skills per-project
- ✅ No symlink issues
- ✅ Works well with version control

**Cons:**
- ❌ Uses more disk space (duplicates skills)
- ❌ Need to clone for each project

**Best for:** Most users, especially if you want project-specific skill versions.

---

### Option 2: Global Location (Alternative)

**Clone once globally, then symlink:**

```bash
# Clone once to a global location
git clone https://github.com/sickn33/antigravity-awesome-skills.git ~/.cursor/skills

# In each project, create symlink
ln -s ~/.cursor/skills .cursor/skills
```

**Pros:**
- ✅ Saves disk space (one copy)
- ✅ Easy to update (update once, all projects benefit)

**Cons:**
- ❌ Symlink issues on Windows (need Developer Mode)
- ❌ All projects share same skill versions
- ❌ Less portable (symlinks can break)

**Best for:** Users who want to save space and don't mind symlinks.

---

## 🪟 Windows Users

If you encounter symlink issues on Windows:

### Option A: Enable Developer Mode
1. Open Windows Settings
2. Go to "Update & Security" → "For developers"
3. Enable "Developer Mode"
4. Then clone normally

### Option B: Use Git Flag
```bash
git clone -c core.symlinks=true https://github.com/sickn33/antigravity-awesome-skills.git .cursor/skills
```

### Option C: Run Git as Administrator
Right-click Git Bash → "Run as Administrator", then clone.

---

## 🔄 Updating Skills

### Per-Project Setup
```bash
cd .cursor/skills
git pull
```

### Global Setup
```bash
cd ~/.cursor/skills
git pull
# All projects using symlinks will get updates automatically
```

---

## 📁 What Gets Cloned

The repository contains:
- **626+ skills** - Specialized instruction files
- **Documentation** - Guides, bundles, examples
- **Scripts** - Helper utilities
- **Catalog** - Skill index and metadata

**Size:** ~50-100 MB (depending on git history)

---

## ✅ Verification

After cloning, verify it worked:

```bash
# Check if skills directory exists
ls -la .cursor/skills

# Check if skills are accessible
ls .cursor/skills/skills | head -5
```

You should see skill folders like:
- `test-driven-development/`
- `react-patterns/`
- `typescript-expert/`
- etc.

---

## 🎯 Integration with VMP

The VMP protocol automatically uses skills from `.cursor/skills/`:

- **Phase 1 (Discovery):** Uses `@typescript-expert`, `@react-patterns`, etc.
- **Phase 4 (Execution):** Uses `@test-driven-development`, `@lint-and-validate`, etc.
- **Phase 6 (Content Registry):** Uses `@typescript-expert` for type-safe configs

**You don't need to manually invoke skills** - the VMP protocol does it automatically based on context.

---

## ❓ FAQ

### Q: Do I need all 626+ skills?
**A:** No! Skills are only loaded when needed. The AI only reads the skills you actually use.

### Q: Can I customize skills?
**A:** Yes! Skills are just markdown files. You can modify them in `.cursor/skills/skills/`.

### Q: What if I don't clone skills?
**A:** The VMP will still work, but you'll miss out on automated pattern matching and best practices. The AI will need to research patterns instead of using proven ones.

### Q: Can I use a subset of skills?
**A:** Yes! You can delete skill folders you don't need, or use the "bundles" feature to install only specific skill categories.

---

## 📝 Summary

**For this project:**
```bash
git clone https://github.com/sickn33/antigravity-awesome-skills.git .cursor/skills
```

**For new projects:**
- Clone skills (per-project recommended)
- Or symlink from global location

**Time:** 2-3 minutes to clone (depends on internet speed)

**Required:** Yes, for full VMP functionality
