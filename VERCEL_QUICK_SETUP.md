# Vercel Quick Setup Guide

## Copy-Paste Settings for Vercel Dashboard

### 1. Framework Preset
```
Other
```

### 2. Root Directory
```
./
```

### 3. Build Command
```
pip install -r requirements.txt
```

### 4. Output Directory
```
.
```

### 5. Install Command
```
pip install -r requirements.txt
```

### 6. Environment Variables (Optional)

Click "Add" for each:

**Variable 1:**
- **Name:** `PYTHON_VERSION`
- **Value:** `3.11`

**Variable 2:**
- **Name:** `MAX_FILE_SIZE`
- **Value:** `52428800`

## After Configuration

1. Click **"Deploy"**
2. Wait 1-2 minutes for build to complete
3. Your app will be live at: `https://your-project-name.vercel.app`

## Test Your Deployment

1. Open the Vercel URL
2. Drag and drop a small DOCX file
3. Click "Convert Files"
4. Download the ZIP

## Important Notes

⚠️ **Vercel Free Tier Limits:**
- 10 second execution timeout
- 4.5 MB request/response size
- Best for files under 5MB

✅ **Recommended:**
- Test with small files first
- For large files, use the CLI version locally
- Monitor Vercel logs for errors

## Troubleshooting

**Build fails?**
- Check that all files are pushed to GitHub
- Verify `requirements.txt` exists in root

**App doesn't load?**
- Check Vercel logs in dashboard
- Verify deployment succeeded

**Upload fails?**
- File might be too large (>4.5MB on free tier)
- Try smaller files

## Next Steps

After successful deployment:
1. Share your Vercel URL
2. Test with different file types
3. Monitor usage in Vercel dashboard
4. Consider upgrading to Pro if needed

---

**Your Vercel URL will be:**
`https://any2md.vercel.app` (or similar)

