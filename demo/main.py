#!/usr/bin/env python3
"""
Claude Agent SDK Python - Progressive Demo Pattern
"""
import sys
from pathlib import Path

def print_menu():
    print("\n" + "="*60)
    print("Claude Agent SDK Python - Progressive Patterns")
    print("="*60)
    print("1. Pattern 1: Custom Tools (Calculator)")
    print("2. Pattern 2: Add Hooks (Command Blocker)")
    print("3. Pattern 3: Add Permissions (Tiered Access)")
    print("4. Pattern 4: Complete Agent (All Patterns)")
    print("0. Exit")
    print("="*60)

def main():
    while True:
        print_menu()
        choice = input("\nSelect pattern (0-4): ").strip()

        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            from patterns import pattern_01_basic_tools
            pattern_01_basic_tools.run()
        elif choice == "2":
            from patterns import pattern_02_with_hooks
            pattern_02_with_hooks.run()
        elif choice == "3":
            from patterns import pattern_03_with_permissions
            pattern_03_with_permissions.run()
        elif choice == "4":
            from patterns import pattern_04_complete_agent
            pattern_04_complete_agent.run()
        else:
            print("Invalid choice. Please select 0-4.")

if __name__ == "__main__":
    main()