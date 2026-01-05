# Fix: VITE_API_URL Not Working on Railway

If you've set `VITE_API_URL` in Railway but the frontend still uses the wrong URL, here's how to fix it.

## The Problem

**Vite environment variables are embedded at BUILD TIME, not runtime.**

This means:
- If you set `VITE_API_URL` after the frontend is built, it won't work
- The value must be available during the Docker build process
- Railway needs to rebuild the frontend after you set the variable

## The Solution

### Step 1: Set VITE_API_URL Correctly

1. Go to your **frontend service** in Railway
2. Click **"Variables"** tab
3. Add or update:
   ```
   Variable Name: VITE_API_URL
   Value: https://your-backend-service.up.railway.app
   ```
   **⚠️ Use your BACKEND URL, not frontend URL!**

### Step 2: Trigger a Rebuild

Railway should automatically rebuild when you change environment variables, but if it doesn't:

1. Go to frontend service → **"Deployments"** tab
2. Click **"Redeploy"** or **"Deploy"**
3. Wait for the build to complete
4. Check build logs to ensure no errors

### Step 3: Verify It's Working

1. **Check Build Logs:**
   - Look for the build process
   - Ensure no errors about missing variables

2. **Check Browser Console:**
   - Open your deployed frontend
   - Press F12 → Console tab
   - Look for: `🔧 API Configuration:`
   - Verify `API_BASE_URL` shows your backend URL

3. **Test API Calls:**
   - Try using the frontend
   - Check Network tab in DevTools
   - API requests should go to your backend URL

## Common Mistakes

### ❌ Wrong: Setting VITE_API_URL to Frontend URL
```
VITE_API_URL=https://frontend-production-xyz.up.railway.app
```
This causes API calls to go to the frontend, which doesn't have the API!

### ✅ Correct: Setting VITE_API_URL to Backend URL
```
VITE_API_URL=https://backend-production-abc.up.railway.app
```

### ❌ Wrong: Setting Variable After Build
If you set `VITE_API_URL` after the frontend is already built, the old value is still embedded in the JavaScript bundle.

**Fix**: Set the variable, then trigger a rebuild.

## Debugging

### Check What Value Is Being Used

1. Open browser console on your deployed frontend
2. Run:
   ```javascript
   console.log('API Base URL:', import.meta.env.VITE_API_URL)
   ```
3. This shows what value was embedded at build time

### Check Railway Build Logs

1. Go to frontend service → "Deployments"
2. Click on the latest deployment
3. Check build logs for:
   - Environment variables being passed
   - Any build errors
   - Successful build completion

### Manual Verification

1. **Test Backend Directly:**
   ```bash
   curl https://your-backend.up.railway.app/api/v1/health
   ```
   Should return: `{"status": "healthy", ...}`

2. **Test Frontend API Call:**
   - Open browser DevTools → Network tab
   - Use the frontend
   - Check where API requests are going
   - Should be: `https://your-backend.up.railway.app/api/v1/...`

## Still Not Working?

1. **Double-check the variable name:**
   - Must be exactly: `VITE_API_URL` (case-sensitive)
   - Must start with `VITE_` for Vite to include it

2. **Verify the backend URL:**
   - Copy the exact URL from your backend service
   - Include `https://` but no trailing slash
   - Example: `https://backend-production-abc123.up.railway.app`

3. **Force a clean rebuild:**
   - Delete the frontend service
   - Recreate it
   - Set `VITE_API_URL` FIRST
   - Then deploy

4. **Check Dockerfile:**
   - Ensure the Dockerfile accepts `ARG VITE_API_URL`
   - The updated Dockerfile should handle this automatically

## Alternative: Runtime Configuration

If build-time configuration is problematic, you could:
1. Use a config file that's loaded at runtime
2. Use Railway's service discovery
3. Use a reverse proxy setup

But the build-time approach (VITE_API_URL) is the recommended method for Vite apps.

