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
  git remote set-url origin https://github.com/ultronftw/Keygenie.git
else
  git remote add origin https://github.com/ultronftw/Keygenie.git
fi

# Stage all changes
git add .

# Commit only if there are staged changes
if ! git diff --cached --quiet; then
  git commit -m "Initial commit pushing code to GitHub"
fi

# Push to main branch; create upstream tracking if none set
git push -u origin main

# Verify and output status
git status
