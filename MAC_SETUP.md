# Mac Setup Guide for Railway Deployment

Quick setup guide for Mac users deploying to Railway.

## 🍎 Mac-Specific Setup

### 1. Install Homebrew (if not installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Node.js (for Railway CLI)

```bash
brew install node
```

Verify installation:
```bash
node --version
npm --version
```

### 3. Install Railway CLI

```bash
npm i -g @railway/cli
```

**If `railway` command is not found after installation:**

On Mac with Homebrew, you may need to create a symlink:

```bash
# Find where Railway was installed
RAILWAY_PATH=$(find /opt/homebrew -name "railway" -type f 2>/dev/null | grep "@railway/cli" | head -1)

# Create symlink (if found)
if [ -n "$RAILWAY_PATH" ]; then
  sudo ln -sf "$RAILWAY_PATH" /opt/homebrew/bin/railway
fi
```

Or add npm's global bin to your PATH:

```bash
# Add to ~/.zshrc
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Verify installation:
```bash
railway --version
```

**Note**: The deprecation warning about `node-domexception` is harmless - it's just a dependency warning and won't affect functionality.

### 4. Install PostgreSQL Client (Optional - for local psql)

If you want to use `psql` from your Mac terminal:

```bash
# Install PostgreSQL (includes psql client)
brew install postgresql@15

# Add to PATH (for Apple Silicon Macs)
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc

# For Intel Macs, use:
# echo 'export PATH="/usr/local/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc

# Reload shell
source ~/.zshrc
```

Verify installation:
```bash
psql --version
```

**Note**: You don't need psql installed if you use Railway's web interface (Option A in the deployment guide).

## 🚀 Quick Commands for Mac

### Railway CLI Commands

```bash
# Login (opens browser)
railway login

# Link to project
cd /Users/danialamin/Documents/GitHub/customer-support
railway link

# View variables
railway variables

# Connect to PostgreSQL
railway connect postgres

# View logs
railway logs

# Open project in browser
railway open
```

### File Operations on Mac

```bash
# Open SQL file in default editor
open backend/db/init_fuel_management.sql

# Or use VS Code
code backend/db/init_fuel_management.sql

# Copy file contents to clipboard (for pasting into Railway)
pbcopy < backend/db/init_fuel_management.sql
```

### Terminal Shortcuts (Mac)

- **Cmd+K**: Clear terminal
- **Cmd+T**: New tab
- **Cmd+W**: Close tab
- **Ctrl+C**: Cancel command
- **Ctrl+D**: Exit psql or other interactive sessions

## 📝 Mac-Specific Tips

### Using Railway Web Interface (Easiest)

Since you're on Mac, the easiest way is to use Railway's web interface:

1. Open `backend/db/init_fuel_management.sql` in your Mac editor
2. Select All (`Cmd+A`) and Copy (`Cmd+C`)
3. Go to Railway dashboard → PostgreSQL service → Data tab → Query
4. Paste (`Cmd+V`) and Run (`Cmd+Enter`)

### Using Terminal

If you prefer terminal:

1. Open Terminal (Applications → Utilities → Terminal)
2. Navigate to project:
   ```bash
   cd /Users/danialamin/Documents/GitHub/customer-support
   ```
3. Use Railway CLI commands as shown above

### Copying Connection Strings

On Mac, you can quickly copy the DATABASE_URL:

```bash
# Using Railway CLI
railway variables | grep DATABASE_URL

# Or in Railway dashboard, click the copy icon next to the variable
```

### Viewing Logs

```bash
# Railway CLI
railway logs

# Or in Railway dashboard, click on service → Logs tab
```

## 🔧 Troubleshooting on Mac

### "Command not found: railway"

```bash
# Check if npm global bin is in PATH
npm config get prefix

# Add to PATH if needed
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### "Command not found: psql"

```bash
# Install PostgreSQL
brew install postgresql@15

# Add to PATH (see installation section above)
```

### Permission Denied

```bash
# Fix npm global permissions
sudo chown -R $(whoami) $(npm config get prefix)/{lib/node_modules,bin,share}
```

### Terminal Not Finding Commands

Make sure you're using zsh (default on modern Macs):

```bash
# Check shell
echo $SHELL

# Should be /bin/zsh or /usr/bin/zsh
# If not, switch: chsh -s /bin/zsh
```

## ✅ Mac Deployment Checklist

- [ ] Homebrew installed
- [ ] Node.js installed (`node --version`)
- [ ] Railway CLI installed (`railway --version`)
- [ ] PostgreSQL client installed (optional, `psql --version`)
- [ ] Logged into Railway (`railway login`)
- [ ] Project linked (`railway link`)
- [ ] Can access Railway dashboard in browser

## 🎯 Next Steps

Once setup is complete, follow the main deployment guide:
- [RAILWAY_DATABASE_DEPLOYMENT.md](./RAILWAY_DATABASE_DEPLOYMENT.md)

