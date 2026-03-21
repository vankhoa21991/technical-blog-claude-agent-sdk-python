"""
Command Blocker Hook - Pattern 2

This hook intercepts tool execution and blocks dangerous bash commands
that could harm the system.

Hook Type: PreToolUse
Target: Bash tool with dangerous patterns
"""
from datetime import datetime


async def block_dangerous_commands(input_data, tool_use_id, context):
    """
    Block dangerous bash commands like 'rm -rf', 'format', etc.

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

        # Define dangerous patterns that could harm the system
        dangerous_patterns = [
            "rm -rf",           # Recursive delete
            "format",           # Disk formatting (Windows)
            "mkfs",             # File system creation
            "dd if=",           # Direct disk write
            "> /dev/",          # Writing to devices
            "fdisk",            # Partition manipulation
            "mkswap",           # Swap creation
        ]

        # Check if command contains any dangerous pattern
        for pattern in dangerous_patterns:
            if pattern in command:
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"Dangerous command detected: {pattern}. Command blocked for safety."
                    }
                }

    # Return empty dict for no-op (allow the command)
    return {}
