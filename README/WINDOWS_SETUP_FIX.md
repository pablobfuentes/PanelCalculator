# Windows Setup Quick Fix

## ✅ Issues Fixed

### 1. Node Version Warning
**Problem:** `lint-staged@16.2.7` requires Node >=20.17, but you have 20.14.0

**Solution (Choose One):**

**Option A - Upgrade Node (Recommended):**
```bash
# Download and install Node.js 20.17+ from nodejs.org
# Or use nvm-windows:
nvm install 20.17
nvm use 20.17
```

**Option B - Use Compatible Version:**
```bash
npm install --save-dev husky@latest lint-staged@15.2.0 prettier
```

**Note:** The warning is non-blocking - everything will still work, but upgrading is recommended for best compatibility.

---

### 2. chmod Command Not Found
**Problem:** `chmod` is a Unix command and doesn't work in Windows CMD

**Solution:** 
- ✅ **Skip the chmod step** - it's not needed on Windows CMD/PowerShell
- ✅ Use `scripts\smart-commit.bat` instead of `./scripts/smart-commit.sh`
- ✅ Or use Git Bash which supports `chmod`

---

## 🚀 Quick Setup (Windows CMD)

### Step 1: Install Dependencies
```cmd
npm install --save-dev husky lint-staged prettier
```

If you see Node version warnings, you can either:
- Upgrade Node to 20.17+ (recommended)
- Or use: `npm install --save-dev husky@latest lint-staged@15.2.0 prettier`

### Step 2: Initialize Husky
```cmd
npx husky init
```

### Step 3: Skip chmod (Not Needed on Windows)
**You can skip this step!** The script will work without it.

### Step 4: Test It
```cmd
REM Make a small change, then:
scripts\smart-commit.bat "test: verify setup"
```

---

## 📝 Using the Scripts

### Windows CMD:
```cmd
scripts\smart-commit.bat "feat: add new feature"
```

### Windows Git Bash:
```bash
./scripts/smart-commit.sh "feat: add new feature"
```

### PowerShell:
```powershell
.\scripts\smart-commit.bat "feat: add new feature"
```

---

## ✅ What's Working Now

- ✅ Dependencies installed (with warnings, but functional)
- ✅ Husky initialized
- ✅ Windows batch script created (`smart-commit.bat`)
- ✅ No chmod needed on Windows

---

## 🎯 Next Steps

1. **Continue with setup** - Everything should work now
2. **Test the commit script:**
   ```cmd
   scripts\smart-commit.bat "test: verify setup"
   ```
3. **Optional:** Upgrade Node to 20.17+ to remove warnings

---

## 💡 Pro Tips

- **Use Git Bash** if you prefer Unix-style commands
- **Use CMD/PowerShell** with the `.bat` script (easier on Windows)
- **Upgrade Node** when convenient to remove warnings
- **The warnings are non-blocking** - everything works fine

---

## ❓ Still Having Issues?

See `SETUP_INSTRUCTIONS.md` for detailed troubleshooting, or check:
- Node version: `node --version`
- Git version: `git --version`
- npm version: `npm --version`
