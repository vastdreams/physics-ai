#!/bin/bash
# setup_github.sh
# Script to help set up GitHub repository

echo "Beyond Frontier - GitHub Repository Setup"
echo "====================================="
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Error: Git repository not initialized"
    exit 1
fi

# Get repository name from user or use default
read -p "Enter GitHub repository name (default: beyondfrontier): " repo_name
repo_name=${repo_name:-beyondfrontier}

# Get GitHub username
read -p "Enter your GitHub username: " github_username

if [ -z "$github_username" ]; then
    echo "Error: GitHub username is required"
    exit 1
fi

echo ""
echo "Setting up repository..."
echo ""

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Beyond Frontier - Neurosymbotic Rule-Based Modular AI

- Core neurosymbotic engine
- Rule-based system
- Self-evolution module
- Physics integration
- Validation and logging framework
- Test suite
- CI/CD pipelines
- Documentation"

# Set up branches
echo "Setting up branches..."
git checkout -b development 2>/dev/null || git checkout development
git checkout -b main 2>/dev/null || git checkout main

echo ""
echo "Repository setup complete!"
echo ""
echo "Next steps:"
echo "1. Create a new repository on GitHub: https://github.com/new"
echo "   - Repository name: $repo_name"
echo "   - Description: Neurosymbotic Rule-Based Modular AI for Physics"
echo "   - Visibility: Public (for open source)"
echo "   - DO NOT initialize with README, .gitignore, or license (we already have them)"
echo ""
echo "2. Add the remote and push:"
echo "   git remote add origin https://github.com/$github_username/$repo_name.git"
echo "   git push -u origin main"
echo "   git push -u origin development"
echo ""
echo "3. Set default branch to 'main' in GitHub repository settings"
echo ""
echo "4. Enable GitHub Actions in repository settings"
echo ""

