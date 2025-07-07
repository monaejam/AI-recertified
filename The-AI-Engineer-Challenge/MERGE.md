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

# MERGE.md - Vercel Deployment Fix (Updated)

## Changes Made

This feature branch fixes the 404 errors by restructuring the API to work properly with Vercel's serverless functions:

### API Restructuring
- **Split into individual serverless functions**: Created separate files for each API endpoint
  - `api/chat.py` - Handles chat functionality
  - `api/config.py` - Provides API configuration
  - `api/test.py` - Simple test endpoint for verification
- **Proper Vercel routing**: Updated `vercel.json` to route each endpoint to its specific function
- **Simplified CORS**: Configured CORS to work with Vercel's serverless environment

### Key Changes
1. **Individual API Files**: Each endpoint is now in its own file for better Vercel compatibility
2. **Explicit Routing**: Vercel configuration now explicitly routes each API path
3. **Test Endpoint**: Added `/api/test` for easy verification that the API is working
4. **Simplified Dependencies**: Removed complex dependencies that were causing issues

### Vercel Configuration (`vercel.json`)
```json
{
  "routes": [
    {
      "src": "/api/test",
      "dest": "/api/test.py"
    },
    {
      "src": "/api/chat", 
      "dest": "/api/chat.py"
    },
    {
      "src": "/api/config",
      "dest": "/api/config.py"
    }
  ]
}
```

## How to Deploy

### Simple Deployment (Recommended)
From the project root directory:
```bash
vercel deploy
```

### Testing After Deployment
1. Test the API is working: Visit `https://your-domain.vercel.app/api/test`
2. You should see: `{"message": "API is working!", "status": "success"}`
3. If that works, the frontend should also work properly

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
gh pr create --title "Fix 404 errors with Vercel serverless functions" --body "Restructures API into individual serverless functions for proper Vercel deployment"
gh pr merge --merge --delete-branch
```

### Option 3: Direct Merge (if working locally)
```bash
git checkout main
git merge feature/vercel-deployment-fix
git push origin main
```

## Troubleshooting

### If you still get 404 errors:
1. **Check the test endpoint first**: Visit `/api/test` to see if the API is working
2. **Verify Vercel deployment**: Check the Vercel dashboard for any build errors
3. **Check function logs**: Look at the function logs in Vercel dashboard
4. **Verify routing**: Make sure the `vercel.json` routes are correct

### Common Issues:
- **Build errors**: Check that all Python dependencies are in `requirements.txt`
- **Function timeouts**: The functions are lightweight and should work quickly
- **CORS issues**: CORS is configured to allow all origins for simplicity

## Key Benefits

- **Proper Vercel Integration**: Uses Vercel's serverless function format correctly
- **Individual Endpoints**: Each API route is isolated and easier to debug
- **Test Endpoint**: Easy way to verify the API is working
- **Simplified Structure**: Removed complex dependencies that were causing issues
- **Better Error Handling**: Each function can handle errors independently

## Next Steps

After successful deployment:
1. Test the `/api/test` endpoint
2. Test the chat functionality
3. Add more endpoints as needed (PDF upload, etc.)
4. Consider adding proper error logging
5. Add rate limiting if needed

# Merge Instructions for fix-pdf-session-id Branch

## Summary
This branch fixes the PDF session ID issue where PDF uploads were failing because the frontend was sending `file_content` instead of `pdf_content` to the backend.

## Changes Made
1. **Frontend (page.tsx)**: 
   - Fixed the request body to send `pdf_content` for PDF files and `file_content` for CSV files
   - Added comprehensive debugging to track session ID changes
   - Added validation to ensure session IDs exist before sending chat requests
   - Added detailed logging for upload responses and base64 processing

2. **Backend (index.py)**:
   - Added debugging to PDF upload endpoint to track content reception
   - Added success logging when PDF sessions are created

## How to Merge

### Option 1: GitHub Pull Request (Recommended)
1. Push the branch to GitHub:
   ```bash
   git push origin fix-pdf-session-id
   ```

2. Go to the GitHub repository and create a new Pull Request:
   - Base branch: `main`
   - Compare branch: `fix-pdf-session-id`
   - Title: "Fix PDF session ID issue"
   - Description: "Fixes PDF upload functionality by correcting field name mismatch between frontend and backend"

3. Review the changes and merge the PR

### Option 2: GitHub CLI
```bash
# Create and merge the PR using GitHub CLI
gh pr create --title "Fix PDF session ID issue" --body "Fixes PDF upload functionality by correcting field name mismatch between frontend and backend"
gh pr merge --merge
```

### Option 3: Local Merge
```bash
# Switch to main branch
git checkout main

# Merge the feature branch
git merge fix-pdf-session-id

# Push to remote
git push origin main

# Delete the feature branch (optional)
git branch -d fix-pdf-session-id
git push origin --delete fix-pdf-session-id
```

## Testing
After merging, test the following:
1. Upload a PDF file
2. Verify the session ID is properly set
3. Send a chat message about the PDF
4. Verify the response is generated correctly

## Files Changed
- `frontend/app/page.tsx`
- `api/index.py` 