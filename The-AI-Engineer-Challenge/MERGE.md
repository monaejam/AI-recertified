# Merging the PDF Chat Feature

This document provides instructions for merging the PDF chat feature from the `feature/pdf-chat` branch into `main`.

## Changes Overview

This feature adds the ability to:
1. Upload PDF files
2. Process PDFs using LangChain for text extraction and embedding
3. Chat with the PDF content using a RAG (Retrieval Augmented Generation) system
4. Persist vector stores for better performance

## Merging via GitHub Pull Request

1. Push the feature branch to GitHub:
   ```bash
   git push origin feature/pdf-chat
   ```

2. Go to the repository on GitHub and click "Compare & pull request" for the `feature/pdf-chat` branch

3. Fill in the pull request details:
   - Title: "Add PDF chat functionality using LangChain"
   - Description: Copy the changes overview from above
   - Reviewers: Add appropriate team members

4. Click "Create pull request"

5. After approval, click "Merge pull request" and then "Confirm merge"

6. Delete the feature branch (optional):
   ```bash
   git push origin --delete feature/pdf-chat
   ```

## Merging via GitHub CLI

1. Install GitHub CLI if not already installed:
   ```bash
   brew install gh
   ```

2. Authenticate with GitHub:
   ```bash
   gh auth login
   ```

3. Push the feature branch:
   ```bash
   git push origin feature/pdf-chat
   ```

4. Create and merge the pull request:
   ```bash
   gh pr create --title "Add PDF chat functionality using LangChain" --body "$(cat << 'EOF'
   This PR adds the ability to:
   1. Upload PDF files
   2. Process PDFs using LangChain for text extraction and embedding
   3. Chat with the PDF content using a RAG system
   4. Persist vector stores for better performance
   EOF
   )" --base main --head feature/pdf-chat
   
   # After approval:
   gh pr merge --merge --delete-branch
   ```

## Post-Merge Steps

1. Switch to main and pull the changes:
   ```bash
   git checkout main
   git pull origin main
   ```

2. Clean up local feature branch:
   ```bash
   git branch -d feature/pdf-chat
   ```

3. Deploy the changes to Vercel:
   ```bash
   vercel
   ```

# MERGE.md - Vercel Deployment Fix

## Changes Made

This feature branch fixes the Vercel deployment routing issues and implements auto-configuration for API URLs:

### Backend Changes (`api/app.py`)
- Added auto-detection of Vercel URL using `VERCEL_URL` environment variable
- Implemented dynamic CORS configuration that works in both development and production
- Added `/api/config` endpoint that returns the correct API URL
- Improved error handling and logging

### Frontend Changes (`frontend/app/page.tsx`)
- Removed hardcoded API URL dependency
- Added auto-detection of API URL on component mount
- Implemented fallback to local development URL
- Added proper error handling for API connection issues

### Deployment Configuration
- Removed conflicting `vercel.json` from `api/` directory
- Root `vercel.json` now handles all routing properly
- Configured proper Python and Next.js builds
- Set up correct API route handling

## How to Deploy

### Simple Deployment (Recommended)
From the project root directory:
```bash
vercel deploy
```

### Manual Deployment Steps
1. Install Vercel CLI: `npm install -g vercel`
2. Navigate to project root: `cd The-AI-Engineer-Challenge`
3. Deploy: `vercel deploy`
4. Follow the prompts to link to your Vercel project

## How to Merge

### Option 1: GitHub Pull Request (Recommended)
1. Push the feature branch:
   ```bash
   git push origin feature/vercel-deployment-fix
   ```
2. Go to GitHub and create a Pull Request from `feature/vercel-deployment-fix` to `main`
3. Review the changes and merge

### Option 2: GitHub CLI
```bash
# Create and merge PR
gh pr create --title "Fix Vercel deployment routing and auto-configure API URLs" --body "Fixes NOT_FOUND errors and implements auto-configuration for seamless deployment"
gh pr merge --squash
```

### Option 3: Direct Merge (if working locally)
```bash
git checkout main
git merge feature/vercel-deployment-fix
git push origin main
```

## Testing After Deployment

1. Visit your deployed Vercel URL
2. Enter your OpenAI API key
3. Test both regular chat and PDF upload functionality
4. Verify that API calls work without manual configuration

## Key Benefits

- **Zero Configuration**: No need to set environment variables manually
- **Auto-Detection**: API URL is automatically detected in both development and production
- **Seamless Deployment**: Works immediately after `vercel deploy`
- **Better Error Handling**: Clear error messages for debugging
- **CORS Fixed**: Proper cross-origin resource sharing configuration

## Troubleshooting

If you still get NOT_FOUND errors:
1. Check that the root `vercel.json` is properly configured
2. Ensure both `api/app.py` and `frontend/` are in the correct locations
3. Verify that the Vercel project is linked correctly
4. Check Vercel deployment logs for any build errors 