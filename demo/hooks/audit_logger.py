"""
Audit Logger Hook - Pattern 2

This hook logs all tool invocations to both console and file.
Useful for debugging, auditing, and monitoring agent behavior.

Hook Types: PreToolUse, PostToolUse
Target: All tools
"""
import json
from datetime import datetime
from pathlib import Path


def _log_to_file(log_entry):
    """Helper function to write log entry to file"""
    # Get the demo directory (parent of hooks directory)
    demo_dir = Path(__file__).parent.parent
    audit_log_path = demo_dir / "audit.log"

    with open(audit_log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


async def pre_tool_use_hook(input_data, tool_use_id, context):
    """
    Log tool invocations BEFORE execution (PreToolUse).

    Args:
        input_data: Dict containing tool_name and tool_input
        tool_use_id: Unique identifier for this tool use
        context: Additional context (not used in this hook)

    Returns:
        Empty dict (no interception, just logging)
    """
    tool_name = input_data.get("tool_name")
    tool_input = input_data.get("tool_input", {})

    # Create log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "PreToolUse",
        "tool": tool_name,
        "input": tool_input,
        "tool_use_id": tool_use_id
    }

    # Console log (with visual marker)
    print(f"[AUDIT:PRE] {json.dumps(log_entry)}")

    # File log
    _log_to_file(log_entry)

    # Return empty dict for no-op (don't intercept)
    return {}


async def post_tool_use_hook(tool_use_id, tool_output, context):
    """
    Log tool execution results AFTER execution (PostToolUse).

    Args:
        tool_use_id: Unique identifier for this tool use
        tool_output: The result/output from the tool execution
        context: Additional context (not used in this hook)

    Returns:
        Empty dict (no interception, just logging)
    """
    # Create log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "PostToolUse",
        "tool_use_id": tool_use_id,
        "output": tool_output
    }

    # Console log (with visual marker)
    print(f"[AUDIT:POST] {json.dumps(log_entry)}")

    # File log
    _log_to_file(log_entry)

    # Return empty dict for no-op (don't modify output)
    return {}
