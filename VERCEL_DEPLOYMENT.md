# Deploying doc2mkdocs to Vercel

This guide will help you deploy the doc2mkdocs landing page and API to Vercel.

## Important Note

⚠️ **Vercel Serverless Limitations:**

Due to Vercel's serverless architecture (10-second timeout on free tier), **full document conversion is NOT available** in the deployed version. The Vercel deployment provides:

- ✅ Landing page with project information
- ✅ API endpoints for validation
- ✅ Links to GitHub and documentation
- ❌ Full document conversion (use CLI locally instead)

**For full conversion capabilities, users should install the CLI tool locally.**

## Prerequisites

- Vercel account (free tier works)
- GitHub repository connected to Vercel
- Project imported in Vercel dashboard

## Vercel Configuration Settings

When configuring your project in Vercel, use these settings:

### Framework Preset
**Select:** `Other`

### Root Directory
**Leave as:** `./` (root of repository)

### Build Settings

**Build Command:**
```bash
# Leave empty or use:
echo "No build required"
```

**Output Directory:**
```
public
```

**Install Command:**
```bash
pip install -r requirements.txt
```

### Environment Variables

No environment variables are required for basic deployment. However, you can optionally add:

| Key | Value | Description |
|-----|-------|-------------|
| `PYTHON_VERSION` | `3.11` | Python version to use |
| `MAX_FILE_SIZE` | `52428800` | Max upload size in bytes (50MB default) |

## File Structure for Vercel

The repository includes these Vercel-specific files:

- **`vercel.json`** - Vercel configuration
- **`api/index.py`** - Serverless function entry point
- **`requirements.txt`** - Python dependencies

## Step-by-Step Deployment

### 1. In Vercel Dashboard

1. Go to your Vercel dashboard
2. Click on your imported project
3. Go to **Settings** → **General**

### 2. Configure Build Settings

**Framework Preset:** Other

**Root Directory:** `./`

**Build Command:**
```
pip install -r requirements.txt
```

**Output Directory:**
```
.
```

**Install Command:**
```
pip install -r requirements.txt
```

### 3. Deploy

1. Go to **Deployments** tab
2. Click **Deploy** or push to your `main` branch
3. Wait for deployment to complete (usually 1-2 minutes)

### 4. Access Your App

Once deployed, Vercel will provide a URL like:
```
https://your-project-name.vercel.app
```

## Important Notes

### Limitations on Vercel

⚠️ **Serverless Function Limits:**
- **Execution time:** 10 seconds (Hobby), 60 seconds (Pro)
- **Memory:** 1024 MB (Hobby), 3008 MB (Pro)
- **Payload size:** 4.5 MB request, 4.5 MB response

⚠️ **File Upload Considerations:**
- Large file conversions may timeout on Hobby plan
- Consider upgrading to Pro for longer execution times
- Alternatively, use the CLI version for large files

### Recommended Settings

For best performance on Vercel:

1. **File size limit:** Keep under 10MB per file
2. **Batch conversions:** Limit to 5 files at a time
3. **PDF OCR:** May timeout on complex PDFs (use CLI instead)

## Alternative: Deploy to Other Platforms

If Vercel's serverless limits are too restrictive, consider:

### Railway.app
- Longer execution times
- Better for large file processing
- Simple deployment from GitHub

### Render.com
- Free tier with 512MB RAM
- No execution time limits
- Docker support

### Fly.io
- Free tier available
- Better for CPU-intensive tasks
- Global deployment

## Troubleshooting

### Build Fails

**Error:** `Module not found`
- Check `requirements.txt` includes all dependencies
- Verify Python version is 3.11+

### Deployment Succeeds but App Doesn't Work

**Error:** `500 Internal Server Error`
- Check Vercel logs in dashboard
- Verify `api/index.py` is correctly configured
- Ensure all imports work

### File Upload Fails

**Error:** `Request Entity Too Large`
- Reduce file size
- Check `MAX_FILE_SIZE` environment variable
- Vercel has 4.5MB payload limit on Hobby plan

### Conversion Timeout

**Error:** `Function execution timed out`
- Upgrade to Vercel Pro (60s timeout)
- Use CLI for large/complex files
- Reduce file size or complexity

## Testing Locally Before Deploy

Test the Vercel setup locally:

```bash
# Install Vercel CLI
npm install -g vercel

# Run locally
vercel dev
```

This will start a local server that mimics Vercel's environment.

## Post-Deployment

After successful deployment:

1. ✅ Test file upload with small files
2. ✅ Test conversion with DOCX, PDF, XLSX
3. ✅ Test download functionality
4. ✅ Check conversion quality
5. ✅ Monitor Vercel logs for errors

## Custom Domain (Optional)

To add a custom domain:

1. Go to **Settings** → **Domains**
2. Add your domain
3. Configure DNS records as instructed
4. Wait for SSL certificate provisioning

---

**Need Help?**

- Check Vercel logs in dashboard
- Review [Vercel Python documentation](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- Open an issue on GitHub

