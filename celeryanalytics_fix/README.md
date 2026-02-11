# Celeryanalytics Asset Manifest Fix

## Problem

When installing `allianceauth-celeryanalytics` from PyPI, the React app build artifacts are not properly packaged. This causes 404 errors when trying to load the dashboard:

```
Failed to load resource: the server responded with a status of 404 ()
/static/celeryanalytics/asset-manifest.json?version=0.0.7
unable to load react app, manifest file not accessible or corrupted
```

The installed package is missing the `asset-manifest.json` file that the React app needs to load its CSS and JavaScript files.

## Solution

This fix provides a properly configured `asset-manifest.json` file that:
- Points to the correct static file paths for celeryanalytics
- Uses relative paths in entrypoints to prevent path duplication
- Persists through package updates and collectstatic operations

## What's Included

- `asset-manifest.json` - Manifest file with correct paths for AllianceAuth deployment

## Installation

### 1. Add volume mount to docker-compose.yml

Add this line to the `x-allianceauth-base` volumes section:

```yaml
- ./aa-customizations/celeryanalytics_fix/asset-manifest.json:/var/www/myauth/static/celeryanalytics/asset-manifest.json
```

### 2. Restart containers

```bash
docker compose restart allianceauth_gunicorn nginx
```

### 3. Verify the fix

Check that the manifest exists:
```bash
docker compose exec allianceauth_gunicorn cat /var/www/myauth/static/celeryanalytics/asset-manifest.json
```

Refresh your browser and navigate to the celeryanalytics dashboard. The React app should load without 404 errors.

## What Changed

**Before:**
- Missing `asset-manifest.json` → 404 error
- React app couldn't find CSS/JS files
- Dashboard showed error message

**After:**
- ✅ Manifest file present with correct paths
- ✅ React app loads CSS and JS successfully
- ✅ Dashboard displays task statistics

## File Contents

The manifest tells the React app where to find its assets:

```json
{
  "files": {
    "main.css": "/static/celeryanalytics/css/main.881b38e4.css",
    "main.js": "/static/celeryanalytics/js/main.b931496b.js",
    ...
  },
  "entrypoints": [
    "css/main.881b38e4.css",
    "js/main.b931496b.js"
  ]
}
```

**Key points:**
- `files` uses absolute paths: `/static/celeryanalytics/...`
- `entrypoints` uses relative paths: `css/...` and `js/...`
- This prevents path duplication like `/static/celeryanalytics/static/celeryanalytics/...`

## Troubleshooting

### Still getting 404 errors after applying fix

1. Verify volume mount in docker-compose.yml
2. Check file exists in container:
   ```bash
   docker compose exec allianceauth_gunicorn ls -la /var/www/myauth/static/celeryanalytics/
   ```
3. Clear browser cache (hard refresh: Ctrl+Shift+R)
4. Check nginx logs:
   ```bash
   docker compose logs nginx | grep celeryanalytics
   ```

### After package update, fix stops working

The volume mount should persist, but verify:
```bash
docker compose exec allianceauth_gunicorn cat /var/www/myauth/static/celeryanalytics/asset-manifest.json
```

If missing, restart containers:
```bash
docker compose restart allianceauth_gunicorn
```

### Different file versions after update

If celeryanalytics updates and uses different CSS/JS file hashes:

1. Check what files exist:
   ```bash
   docker compose exec allianceauth_gunicorn ls /var/www/myauth/static/celeryanalytics/css/
   docker compose exec allianceauth_gunicorn ls /var/www/myauth/static/celeryanalytics/js/
   ```

2. Update the asset-manifest.json with new filenames
3. Restart containers

## Why This Happens

The celeryanalytics package on PyPI (version 0.0.7) was built without including the frontend build artifacts. The package maintainers likely:
- Built the Python package before running the frontend build
- Didn't include the `frontend/build/` directory in the package manifest
- The static files are there, but the manifest that references them is missing

This is a packaging issue that will likely be fixed in future versions.

## Related Links

- [allianceauth-celeryanalytics GitHub](https://github.com/pvyParts/allianceauth-celeryanalytics)
- [Issue with missing manifest files](https://github.com/pvyParts/allianceauth-celeryanalytics/issues)

## Notes

- This fix is version-specific (0.0.7)
- Future package updates may include the manifest and not need this fix
- The mounted file takes precedence over any file in the static directory
- Safe to keep even if future versions fix the issue
