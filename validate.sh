#!/bin/bash

echo "=================================================="
echo "HOSPITALITY BOOKING SYSTEM - STRUCTURE VALIDATION"
echo "=================================================="

# Check directories
echo -e "\nChecking directory structure..."
dirs=(
    "agents/inquiry"
    "agents/availability"
    "agents/booking"
    "agents/upsell"
    "agents/confirmation"
    "agents/precheckin"
    "agents/survey"
    "orchestrator"
    "mcp_servers/firestore"
    "memory"
    "utils"
    "tests/test_agents"
    "tests/test_integration"
    "config"
)

missing_dirs=0
for dir in "${dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✅ Found: $dir"
    else
        echo "  ❌ Missing: $dir"
        ((missing_dirs++))
    fi
done

# Check files
echo -e "\nChecking required files..."
files=(
    "pyproject.toml"
    "requirements.txt"
    "README.md"
    ".env.example"
    "config/settings.py"
    "config/firestore_indexes.json"
    "config/feature_flags.yaml"
)

missing_files=0
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ Found: $file"
    else
        echo "  ❌ Missing: $file"
        ((missing_files++))
    fi
done

# Check agent implementations
echo -e "\nChecking agent implementations..."
agents=(
    "inquiry"
    "availability"
    "booking"
    "upsell"
    "confirmation"
    "precheckin"
    "survey"
)

missing_agents=0
for agent in "${agents[@]}"; do
    if [ -f "agents/$agent/agent.py" ]; then
        echo "  ✅ $agent agent implemented"
    else
        echo "  ❌ $agent agent missing"
        ((missing_agents++))
    fi
done

# Check key components
echo -e "\nChecking key components..."
components=(
    "orchestrator/main.py"
    "memory/short_term.py"
    "memory/long_term.py"
    "mcp_servers/firestore/server.py"
    "mcp_servers/firestore/models.py"
    "mcp_servers/firestore/transactions.py"
)

missing_components=0
for component in "${components[@]}"; do
    if [ -f "$component" ]; then
        echo "  ✅ Found: $component"
    else
        echo "  ❌ Missing: $component"
        ((missing_components++))
    fi
done

# Summary
echo "=================================================="
total_missing=$((missing_dirs + missing_files + missing_agents + missing_components))

if [ $total_missing -eq 0 ]; then
    echo "✅ VALIDATION PASSED - All components present!"
    echo "Total files/directories checked: $((${#dirs[@]} + ${#files[@]} + ${#agents[@]} + ${#components[@]}))"
    exit 0
else
    echo "❌ VALIDATION FAILED"
    echo "Missing directories: $missing_dirs"
    echo "Missing files: $missing_files"
    echo "Missing agents: $missing_agents"
    echo "Missing components: $missing_components"
    echo "Total missing: $total_missing"
    exit 1
fi