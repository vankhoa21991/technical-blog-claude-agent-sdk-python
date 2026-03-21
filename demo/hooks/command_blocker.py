"""
Command Blocker Hook - Pattern 2

This hook intercepts tool execution and blocks dangerous bash commands
that could harm the system.

Hook Type: PreToolUse
Target: Bash tool with dangerous patterns
"""
import re


async def pre_tool_use_hook(input_data, tool_use_id, context):
    """
    Block dangerous bash commands like 'rm -rf', 'format', fork bombs, etc.

    Uses regex pattern matching to detect dangerous commands.

    Args:
        input_data: Dict containing tool_name and tool_input
        tool_use_id: Unique identifier for this tool use
        context: Additional context (not used in this hook)

    Returns:
        Dict with hookSpecificOutput if denying, empty dict for no-op
    """
    tool_name = input_data.get("tool_name")
    tool_input = input_data.get("tool_input", {})

    # Only check bash commands
    if tool_name == "bash":
        command = tool_input.get("command", "")

        # Define dangerous regex patterns that could harm the system
        dangerous_patterns = [
            r"rm\s+-rf\s+/",           # Recursive delete from root
            r":\(\)\{.*\|.*&.*\};:",   # Fork bomb (function with pipe and background)
            r"format",                 # Disk formatting (Windows)
            r"mkfs",                   # File system creation
            r"dd\s+if=",               # Direct disk write
            r">\s*/dev/",              # Writing to devices
            r"fdisk",                  # Partition manipulation
            r"mkswap",                 # Swap creation
        ]

        # Check if command matches any dangerous pattern
        for pattern in dangerous_patterns:
            if re.search(pattern, command):
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"Dangerous command detected: {pattern}. Command blocked for safety."
                    }
                }

    # Return empty dict for no-op (allow the command)
    return {}
