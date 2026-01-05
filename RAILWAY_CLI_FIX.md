# Fix Railway CLI "command not found" on Mac

If you installed Railway CLI with `npm i -g @railway/cli` but get `command not found: railway`, here's how to fix it.

## Quick Fix

Run this command in your terminal (it will ask for your Mac password):

```bash
sudo ln -sf /opt/homebrew/Cellar/node/25.2.1/lib/node_modules/@railway/cli/bin/railway /opt/homebrew/bin/railway
```

Then verify:
```bash
railway --version
```

## Alternative: Use npx (No Fix Needed)

You can use Railway CLI without fixing PATH by using `npx`:

```bash
# Instead of: railway login
npx @railway/cli login

# Instead of: railway link
npx @railway/cli link

# Instead of: railway connect postgres
npx @railway/cli connect postgres
```

## Alternative: Add to PATH

If the symlink doesn't work, add npm's global bin directory to your PATH:

1. **Find where npm installs global packages:**
   ```bash
   npm root -g
   # Usually: /opt/homebrew/lib/node_modules
   ```

2. **Find the Railway binary:**
   ```bash
   find /opt/homebrew -name "railway" -type f | grep "@railway/cli"
   ```

3. **Add to your PATH in `~/.zshrc`:**
   ```bash
   # Add this line to ~/.zshrc
   export PATH="/opt/homebrew/Cellar/node/25.2.1/lib/node_modules/@railway/cli/bin:$PATH"
   
   # Then reload
   source ~/.zshrc
   ```

## Verify Installation

After fixing, test:
```bash
railway --version
# Should output: railway 4.16.1 (or similar)
```

## About the Deprecation Warning

The warning you saw:
```
npm warn deprecated node-domexception@1.0.0: Use your platform's native DOMException instead
```

This is **harmless** - it's just a dependency warning. Railway CLI will work fine. It's coming from one of Railway's dependencies and doesn't affect functionality.

## Still Having Issues?

1. **Reinstall Railway CLI:**
   ```bash
   npm uninstall -g @railway/cli
   npm install -g @railway/cli
   ```

2. **Check your Node/npm installation:**
   ```bash
   which node
   which npm
   node --version
   npm --version
   ```

3. **Use Railway Web Interface Instead:**
   - You don't actually need the CLI for deployment!
   - Use Railway's web dashboard for everything
   - See [RAILWAY_DATABASE_DEPLOYMENT.md](./RAILWAY_DATABASE_DEPLOYMENT.md) for web-based deployment

