#!/bin/bash

# Kill any running instances of the Telegram bot
pkill -f "python keygenie_bot.py" && sleep 2

# Set git user config globally if not already set
if ! git config --global user.name &>/dev/null; then
  git config --global user.name "UltronFTW"
fi

if ! git config --global user.email &>/dev/null; then
  git config --global user.email "ultronftw@hotmail.com"
fi

# Navigate to the project directory or current directory if none specified
PROJECT_DIR="${1:-.}"
cd "$PROJECT_DIR" || { echo "Directory not found: $PROJECT_DIR"; exit 1; }

# Initialize git repository if not initialized
if [ ! -d ".git" ]; then
  git init
fi

# Check if remote 'origin' exists, set or add accordingly
if git remote | grep -q ^origin$; then
  # Set remote URL for origin (do not create new remote name)
  git remote set-url origin https://github.com/ultronftw/Keygenie.git
else
  git remote add origin https://github.com/ultronftw/Keygenie.git
fi

# Stage all changes (respecting .gitignore to exclude junk and large files)
git add .

# Commit only if there are staged changes
if ! git diff --cached --quiet; then
  git commit -m "Commit changes pushing code to GitHub"
fi

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
git push -u origin "$CURRENT_BRANCH"

# Verify and output status
git status
