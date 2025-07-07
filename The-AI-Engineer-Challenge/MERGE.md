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