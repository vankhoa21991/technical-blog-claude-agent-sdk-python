#!/usr/bin/env python3
"""
Claude Agent SDK Python - Interactive Demo Menu System.

This module provides an interactive menu system for running progressive
demonstrations of Claude Agent SDK Python patterns. Each pattern builds
on the previous one, showcasing how to build production-ready AI agents
with custom tools, hooks, and permissions.

Patterns:
    1. Custom Tools - Learn how to extend Claude with custom tools
    2. Hooks for Control - Intercept agent behavior for security
    3. Permission Management - Control tool access with tiers
    4. Complete Agent - All patterns combined in production-ready agent

Usage:
    python main.py

    The menu will display and you can select a pattern (1-4) to run.
    Select 0 to exit the menu.

Example:
        $ python main.py

        ============================================================
        Claude Agent SDK Python - Progressive Patterns
        ============================================================
        1. Pattern 1: Custom Tools (Calculator)
        2. Pattern 2: Add Hooks (Command Blocker)
        3. Pattern 3: Add Permissions (Tiered Access)
        4. Pattern 4: Complete Agent (All Patterns)
        0. Exit
        ============================================================

        Select pattern (0-4): 1

        Running Pattern 1: Custom Tools...
        ...
"""
import sys
from pathlib import Path


def print_menu():
    """Display the interactive menu for pattern selection.

    Prints a formatted menu with options to run each pattern or exit.
    The menu displays pattern names and brief descriptions to help
    users understand what each pattern demonstrates.

    Menu Options:
        1: Pattern 1 - Custom Tools (Calculator)
        2: Pattern 2 - Add Hooks (Command Blocker)
        3: Pattern 3 - Add Permissions (Tiered Access)
        4: Pattern 4 - Complete Agent (All Patterns)
        0: Exit the program

    Returns:
        None: This function only prints the menu and returns nothing.

    Example:
        >>> print_menu()

        ============================================================
        Claude Agent SDK Python - Progressive Patterns
        ============================================================
        1. Pattern 1: Custom Tools (Calculator)
        2. Pattern 2: Add Hooks (Command Blocker)
        3. Pattern 3: Add Permissions (Tiered Access)
        4. Pattern 4: Complete Agent (All Patterns)
        0. Exit
        ============================================================
    """
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
    """Run the interactive demo menu system.

    This function implements the main event loop for the demo application.
    It continuously displays the menu, accepts user input, and executes
    the selected pattern demo. The loop continues until the user selects
    option 0 to exit.

    Workflow:
        1. Display the menu
        2. Get user input (0-4)
        3. Execute the selected pattern
        4. Repeat until user exits

    Pattern Details:
        Pattern 1: Custom Tools
            Demonstrates the @tool decorator for extending Claude's
            capabilities with custom tools. Shows tool registration,
            input validation, and error handling.

        Pattern 2: Hooks for Control
            Demonstrates PreToolUse and PostToolUse hooks for intercepting
            agent behavior. Shows command blocking, validation, and audit
            logging.

        Pattern 3: Permission Management
            Demonstrates allowed_tools whitelist and permission_mode for
            controlling tool access. Shows tiered permission levels and
            dynamic permission changes.

        Pattern 4: Complete Agent
            Demonstrates all patterns working together in a production-ready
            agent. Shows comprehensive security, logging, and error handling.

    Error Handling:
        Invalid choices are caught and the user is prompted to select
        a valid option (0-4). Import errors are caught and reported
        with helpful messages.

    Returns:
        None: This function runs the event loop and exits when the user
        selects option 0.

    Example:
        >>> main()
        # Menu displays
        # User selects: 1
        # Pattern 1 runs
        # Menu displays again
        # User selects: 0
        # Goodbye!
    """
    while True:
        print_menu()
        choice = input("\nSelect pattern (0-4): ").strip()

        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            try:
                from patterns import pattern_01_basic_tools
                pattern_01_basic_tools.run()
            except ImportError as e:
                print(f"Error importing pattern 1: {e}")
                print("Make sure you're in the demo directory.")
        elif choice == "2":
            try:
                from patterns import pattern_02_with_hooks
                pattern_02_with_hooks.run()
            except ImportError as e:
                print(f"Error importing pattern 2: {e}")
                print("Make sure you're in the demo directory.")
        elif choice == "3":
            try:
                from patterns import pattern_03_with_permissions
                pattern_03_with_permissions.run()
            except ImportError as e:
                print(f"Error importing pattern 3: {e}")
                print("Make sure you're in the demo directory.")
        elif choice == "4":
            try:
                from patterns import pattern_04_complete_agent
                pattern_04_complete_agent.run()
            except ImportError as e:
                print(f"Error importing pattern 4: {e}")
                print("Make sure you're in the demo directory.")
        else:
            print("Invalid choice. Please select 0-4.")


if __name__ == "__main__":
    main()