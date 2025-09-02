#!/usr/bin/env python3
"""
Validation script to check project structure and imports.
"""

import os
import sys
from pathlib import Path

def check_structure():
    """Check that all required directories and files exist."""
    
    base_dir = Path(__file__).parent
    
    required_dirs = [
        "agents/inquiry",
        "agents/availability", 
        "agents/booking",
        "agents/upsell",
        "agents/confirmation",
        "agents/precheckin",
        "agents/survey",
        "orchestrator",
        "mcp_servers/firestore",
        "memory",
        "utils",
        "tests/test_agents",
        "tests/test_integration",
        "config"
    ]
    
    required_files = [
        "pyproject.toml",
        "requirements.txt",
        "README.md",
        ".env.example",
        "config/settings.py",
        "config/firestore_indexes.json",
        "config/feature_flags.yaml"
    ]
    
    print("Checking directory structure...")
    missing_dirs = []
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        if not full_path.exists():
            missing_dirs.append(dir_path)
            print(f"  ❌ Missing: {dir_path}")
        else:
            print(f"  ✅ Found: {dir_path}")
    
    print("\nChecking required files...")
    missing_files = []
    for file_path in required_files:
        full_path = base_dir / file_path
        if not full_path.exists():
            missing_files.append(file_path)
            print(f"  ❌ Missing: {file_path}")
        else:
            print(f"  ✅ Found: {file_path}")
    
    # Check agent files
    print("\nChecking agent implementations...")
    agents = ["inquiry", "availability", "booking", "upsell", 
              "confirmation", "precheckin", "survey"]
    
    for agent in agents:
        agent_file = base_dir / f"agents/{agent}/agent.py"
        if agent_file.exists():
            print(f"  ✅ {agent} agent implemented")
        else:
            print(f"  ❌ {agent} agent missing")
    
    # Summary
    print("\n" + "="*50)
    if not missing_dirs and not missing_files:
        print("✅ All required directories and files are present!")
        return True
    else:
        print(f"❌ Missing {len(missing_dirs)} directories and {len(missing_files)} files")
        return False

def check_imports():
    """Try to import key modules."""
    print("\nChecking module imports...")
    
    modules_to_check = [
        ("agents.inquiry", "inquiry_agent"),
        ("agents.availability", "availability_agent"),
        ("agents.booking", "booking_agent"),
        ("agents.upsell", "upsell_agent"),
        ("agents.confirmation", "confirmation_agent"),
        ("agents.precheckin", "precheckin_agent"),
        ("agents.survey", "survey_agent"),
        ("orchestrator.main", "HospitalityOrchestrator"),
        ("memory.short_term", "ShortTermMemory"),
        ("memory.long_term", "LongTermMemory"),
    ]
    
    failed_imports = []
    for module_name, attr_name in modules_to_check:
        try:
            module = __import__(module_name, fromlist=[attr_name])
            if hasattr(module, attr_name):
                print(f"  ✅ Successfully imported {module_name}.{attr_name}")
            else:
                print(f"  ⚠️  Module {module_name} imported but {attr_name} not found")
                failed_imports.append(module_name)
        except ImportError as e:
            print(f"  ❌ Failed to import {module_name}: {e}")
            failed_imports.append(module_name)
    
    if not failed_imports:
        print("\n✅ All module imports successful!")
        return True
    else:
        print(f"\n❌ {len(failed_imports)} import failures")
        return False

def main():
    """Run all validation checks."""
    print("="*50)
    print("HOSPITALITY BOOKING SYSTEM - STRUCTURE VALIDATION")
    print("="*50)
    
    structure_ok = check_structure()
    
    # Only check imports if structure is OK and dependencies might be installed
    if structure_ok:
        try:
            # Try importing a core dependency
            import pydantic
            imports_ok = check_imports()
        except ImportError:
            print("\n⚠️  Dependencies not installed. Run: pip install -r requirements.txt")
            imports_ok = False
    else:
        imports_ok = False
    
    print("\n" + "="*50)
    if structure_ok and imports_ok:
        print("✅ VALIDATION PASSED - System structure is complete!")
    elif structure_ok:
        print("⚠️  Structure is complete but imports failed (install dependencies)")
    else:
        print("❌ VALIDATION FAILED - Please fix missing components")
    
    return 0 if structure_ok else 1

if __name__ == "__main__":
    sys.exit(main())