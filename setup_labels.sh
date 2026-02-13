#!/bin/bash
# Setup custom labels for the repository

echo "Adding custom labels to repository..."

# Add custom labels one by one
gh label create "priority: high" --description "High priority issue" --color "b60205" --repo beyondfrontier/beyondfrontier 2>/dev/null || echo "Label 'priority: high' already exists"
gh label create "priority: medium" --description "Medium priority issue" --color "fbca04" --repo beyondfrontier/beyondfrontier 2>/dev/null || echo "Label 'priority: medium' already exists"
gh label create "priority: low" --description "Low priority issue" --color "0e8a16" --repo beyondfrontier/beyondfrontier 2>/dev/null || echo "Label 'priority: low' already exists"
gh label create "dependencies" --description "Pull requests that update a dependency file" --color "0366d6" --repo beyondfrontier/beyondfrontier 2>/dev/null || echo "Label 'dependencies' already exists"
gh label create "python" --description "Python-related" --color "3776ab" --repo beyondfrontier/beyondfrontier 2>/dev/null || echo "Label 'python' already exists"
gh label create "github-actions" --description "GitHub Actions related" --color "2088ff" --repo beyondfrontier/beyondfrontier 2>/dev/null || echo "Label 'github-actions' already exists"
gh label create "core" --description "Core engine related" --color "8B4513" --repo beyondfrontier/beyondfrontier 2>/dev/null || echo "Label 'core' already exists"
gh label create "rules" --description "Rule system related" --color "FF6347" --repo beyondfrontier/beyondfrontier 2>/dev/null || echo "Label 'rules' already exists"
gh label create "evolution" --description "Self-evolution related" --color "32CD32" --repo beyondfrontier/beyondfrontier 2>/dev/null || echo "Label 'evolution' already exists"
gh label create "physics" --description "Physics integration related" --color "4169E1" --repo beyondfrontier/beyondfrontier 2>/dev/null || echo "Label 'physics' already exists"
gh label create "neurosymbotic" --description "Neurosymbotic AI related" --color "9370DB" --repo beyondfrontier/beyondfrontier 2>/dev/null || echo "Label 'neurosymbotic' already exists"

echo "Labels setup complete!"

