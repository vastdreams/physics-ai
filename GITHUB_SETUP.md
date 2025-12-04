# GitHub Repository Setup Instructions

This guide will help you set up the GitHub repository for Physics AI.

## Prerequisites

- GitHub account
- Git installed and configured
- GitHub CLI (optional, but helpful)

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Fill in the repository details:
   - **Owner**: Your GitHub username (abhisheksehgal)
   - **Repository name**: `physics-ai` (or your preferred name)
   - **Description**: "Neurosymbotic Rule-Based Modular AI for Physics - Breaking through the barriers of reality"
   - **Visibility**: Public (for open source)
   - **Important**: Do NOT initialize with README, .gitignore, or license (we already have them)
3. Click "Create repository"

## Step 2: Connect Local Repository to GitHub

Run the following commands in your terminal:

```bash
cd "/Users/abhisheksehgal/Physics AI"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/physics-ai.git

# Or if you prefer SSH:
# git remote add origin git@github.com:YOUR_USERNAME/physics-ai.git
```

## Step 3: Initial Commit and Push

```bash
# Make sure you're on the main branch
git checkout main

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Physics AI - Neurosymbotic Rule-Based Modular AI

- Core neurosymbotic engine
- Rule-based system
- Self-evolution module
- Physics integration
- Validation and logging framework
- Test suite
- CI/CD pipelines
- Documentation"

# Push to GitHub
git push -u origin main
```

## Step 4: Push Development Branch

```bash
# Switch to development branch
git checkout development

# Push development branch
git push -u origin development
```

## Step 5: Configure GitHub Repository Settings

1. Go to your repository on GitHub
2. Click on "Settings"
3. Under "General" → "Default branch", set it to `main`
4. Under "Actions" → "General", enable GitHub Actions
5. Under "Branches", add branch protection rules for `main`:
   - Require pull request reviews
   - Require status checks to pass
   - Require branches to be up to date

## Step 6: Verify Setup

1. Check that both `main` and `development` branches are visible on GitHub
2. Verify that the MIT license is displayed
3. Check that README.md is properly displayed
4. Verify that GitHub Actions workflows are set up (check the Actions tab)

## Branching Workflow

### For Development

1. Create feature branch from `development`:
   ```bash
   git checkout development
   git pull origin development
   git checkout -b feature/your-feature-name
   ```

2. Make changes and commit:
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

3. Push feature branch:
   ```bash
   git push -u origin feature/your-feature-name
   ```

4. Create Pull Request from feature branch to `development`

### For Releases

1. Merge `development` into `main`:
   ```bash
   git checkout main
   git pull origin main
   git merge development
   git push origin main
   ```

2. Create a release tag:
   ```bash
   git tag -a v0.1.0 -m "Release version 0.1.0"
   git push origin v0.1.0
   ```

## Using the Setup Script

Alternatively, you can use the provided setup script:

```bash
./setup_github.sh
```

The script will guide you through the process and provide the exact commands to run.

## Verification Checklist

- [ ] Repository created on GitHub
- [ ] Remote added to local repository
- [ ] Initial commit pushed to `main` branch
- [ ] `development` branch pushed
- [ ] Default branch set to `main` on GitHub
- [ ] GitHub Actions enabled
- [ ] MIT license visible on GitHub
- [ ] README.md displays correctly
- [ ] All files are present in the repository

## Troubleshooting

### If you get authentication errors:

1. Use GitHub Personal Access Token instead of password
2. Or set up SSH keys for GitHub
3. Or use GitHub CLI: `gh auth login`

### If branches don't show up:

1. Make sure you've pushed both branches:
   ```bash
   git push -u origin main
   git push -u origin development
   ```

### If GitHub Actions don't run:

1. Check that workflows are in `.github/workflows/` directory
2. Enable GitHub Actions in repository settings
3. Check Actions tab for any errors

## Next Steps

After setup is complete:

1. Review and customize the CI/CD workflows if needed
2. Add collaborators if working in a team
3. Set up issue templates (optional)
4. Configure branch protection rules
5. Start developing on the `development` branch!

